"""
Generates the custom SVG assets for kicode01's GitHub profile README.

Everything here is dependency-free: no external image services, no rate limits,
no broken cards. Re-run this any time to refresh the numbers.

Usage:
    python generate.py            # uses stats.json if present, else fetches
    python generate.py --fetch    # force a fresh pull from the GitHub API

In CI, set GITHUB_TOKEN. Locally it falls back to the `gh` CLI.
"""
import json
import os
import subprocess
import sys
import datetime as dt
from collections import defaultdict
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ROOT, "assets")
LOGIN = "kicode01"

TAGLINE = "I write compilers, flash firmware, and ship the web apps on top."
CARD_W = 880          # every card shares this width so the README lines up

# ---------------------------------------------------------------- palettes ---
THEMES = {
    "dark": {
        "bg0": "#0b0f16", "bg1": "#10151f", "panel": "#0d131c",
        "panel_edge": "#1e2733", "text": "#e9eef6", "muted": "#8d99aa",
        "faint": "#4a5567", "accent": "#5ce0a8", "accent2": "#9d8cff",
        "grid": "#ffffff", "grid_op": "0.035", "glow_op": "0.15",
        "heat": ["#161c26", "#123a2b", "#1a6b4c", "#2ba574", "#5ce0a8"],
        "dot": "#2a3340", "card_shadow": "none",
    },
    "light": {
        "bg0": "#ffffff", "bg1": "#f4f7fb", "panel": "#fbfcfe",
        "panel_edge": "#dbe3ed", "text": "#0c141f", "muted": "#586575",
        "faint": "#9aa6b5", "accent": "#0a8f5f", "accent2": "#6b52e0",
        "grid": "#0c141f", "grid_op": "0.05", "glow_op": "0.09",
        "heat": ["#e7ecf2", "#bdeed8", "#74d5ae", "#2cb184", "#0a8f5f"],
        "dot": "#c6ced9", "card_shadow": "none",
    },
}

SANS = ("-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,"
        "'Noto Sans',sans-serif")
MONO = ("ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,"
        "'Liberation Mono',monospace")


# ------------------------------------------------------------------- data ----
def gh(args):
    out = subprocess.run(["gh"] + args, capture_output=True, text=True,
                         encoding="utf-8", shell=False)
    if out.returncode != 0:
        raise RuntimeError(out.stderr)
    return out.stdout


QL = """
query {
  user(login: "%s") {
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalRepositoriesWithContributedCommits
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
      nodes { name isPrivate stargazerCount pushedAt createdAt primaryLanguage { name }
              languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
                edges { size node { name color } } } }
    }
  }
}
""" % LOGIN


def fetch():
    q = " ".join(QL.split())
    gql = json.loads(gh(["api", "graphql", "-f", "query=" + q]))["data"]["user"]
    repos = json.loads(gh(["api", "users/%s/repos?per_page=100&sort=pushed" % LOGIN]))
    user = json.loads(gh(["api", "user"]))

    days = []
    for w in gql["contributionsCollection"]["contributionCalendar"]["weeks"]:
        for d in w["contributionDays"]:
            days.append([d["date"], d["contributionCount"]])

    colors = {}
    for n in gql["repositories"]["nodes"]:
        for e in n["languages"]["edges"]:
            colors[e["node"]["name"]] = e["node"]["color"]

    # Primary-language share across repos that actually contain code. Raw byte
    # totals mislead (one repo carries 3 MB of generated HTML), and what a
    # reader wants to know is simply "what do you build with".
    by_lang = defaultdict(int)
    for r in repos:
        if r["language"]:
            by_lang[r["language"]] += 1

    stats = {
        "login": user["login"],
        "name": user["name"],
        "bio": user["bio"],
        "created_at": user["created_at"],
        "public_repos": user["public_repos"],
        "followers": user["followers"],
        "total_contributions": gql["contributionsCollection"]["contributionCalendar"]["totalContributions"],
        "commits": gql["contributionsCollection"]["totalCommitContributions"],
        "prs": gql["contributionsCollection"]["totalPullRequestContributions"],
        "repos_contributed": gql["contributionsCollection"]["totalRepositoriesWithContributedCommits"],
        "total_stars": sum(r["stargazers_count"] for r in repos),
        "days": days,
        "lang_counts": dict(by_lang),
        "lang_colors": colors,
        "generated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d"),
        "repos": [{
            "name": r["name"], "description": r["description"],
            "language": r["language"], "stars": r["stargazers_count"],
            "homepage": r["homepage"], "topics": r["topics"],
            "pushed_at": r["pushed_at"], "license": (r.get("license") or {}).get("spdx_id"),
        } for r in repos],
    }
    with open(os.path.join(ROOT, "stats.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    return stats


def derive(stats):
    """Metrics that are cheaper to compute here than to store."""
    days = [(dt.date.fromisoformat(d), c) for d, c in stats["days"]]
    stats["active_days"] = sum(1 for _, c in days if c > 0)

    longest = cur = 0
    run_start = None
    best_range = None
    for date, c in days:
        if c > 0:
            if cur == 0:
                run_start = date
            cur += 1
            if cur > longest:
                longest, best_range = cur, (run_start, date)
        else:
            cur = 0
    stats["longest_streak"] = longest
    stats["longest_streak_range"] = (
        [d.isoformat() for d in best_range] if best_range else None)

    cur_streak = 0
    for date, c in reversed(days):
        if c > 0:
            cur_streak += 1
        elif date == days[-1][0]:
            continue
        else:
            break
    stats["current_streak"] = cur_streak
    stats["best_day"] = max(days, key=lambda x: x[1])
    stats["best_day"] = [stats["best_day"][0].isoformat(), stats["best_day"][1]]
    return stats


def load():
    if "--fetch" in sys.argv:
        return derive(fetch())
    p = os.path.join(ROOT, "stats.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return derive(json.load(f))
    return derive(fetch())


# ------------------------------------------------------------- svg helpers ---
def head(w, h):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" fill="none" role="img">')


def text(x, y, s, size=14, fill="#000", weight="400", family=SANS,
         anchor="start", ls=0, op=1.0, style=""):
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"'
            + (f' letter-spacing="{ls}"' if ls else "")
            + (f' opacity="{op}"' if op != 1.0 else "")
            + (f' style="{style}"' if style else "")
            + f'>{escape(str(s))}</text>')


def card_bg(W, H, P, radius=12):
    """Panel with a soft top edge highlight — reads as a surface, not a box."""
    return (
        f'<rect width="{W}" height="{H}" rx="{radius}" fill="{P["bg0"]}"/>'
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="{radius-0.5}" '
        f'fill="none" stroke="{P["panel_edge"]}" stroke-width="1"/>'
    )


def eyebrow(x, y, label, P, size=11.5, ls=2.2):
    return (f'<circle cx="{x+5}" cy="{y-4.5}" r="{size*0.30:.1f}" fill="{P["accent"]}"/>'
            + text(x + 5 + size * 1.0, y, label, size=size, fill=P["accent"],
                   weight="700", ls=ls))


# -------------------------------------------------------------------- hero ---
def hero(t):
    """1280x340 banner: identity on the left, a terminal that earns its place."""
    W, H = 1280, 348
    P = THEMES[t]
    o = [head(W, H)]

    o.append(f"""<defs>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{P['bg0']}"/><stop offset="1" stop-color="{P['bg1']}"/>
</linearGradient>
<radialGradient id="glow" cx="0.16" cy="0.12" r="0.7">
  <stop offset="0" stop-color="{P['accent']}" stop-opacity="{P['glow_op']}"/>
  <stop offset="1" stop-color="{P['accent']}" stop-opacity="0"/>
</radialGradient>
<radialGradient id="glow2" cx="0.95" cy="0.95" r="0.62">
  <stop offset="0" stop-color="{P['accent2']}" stop-opacity="{P['glow_op']}"/>
  <stop offset="1" stop-color="{P['accent2']}" stop-opacity="0"/>
</radialGradient>
<linearGradient id="topline" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{P['accent']}" stop-opacity="0"/>
  <stop offset="0.3" stop-color="{P['accent']}" stop-opacity="0.9"/>
  <stop offset="0.7" stop-color="{P['accent2']}" stop-opacity="0.9"/>
  <stop offset="1" stop-color="{P['accent2']}" stop-opacity="0"/>
</linearGradient>
<pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
  <path d="M32 0H0V32" stroke="{P['grid']}" stroke-opacity="{P['grid_op']}" stroke-width="1"/>
</pattern>
</defs>""")

    o.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
    o.append(f'<rect width="{W}" height="{H}" fill="url(#grid)"/>')
    o.append(f'<rect width="{W}" height="{H}" fill="url(#glow)"/>')
    o.append(f'<rect width="{W}" height="{H}" fill="url(#glow2)"/>')
    o.append(f'<rect x="0" y="0" width="{W}" height="2" fill="url(#topline)"/>')

    # ---- left: identity
    o.append(eyebrow(66, 101, "COMPUTER ENGINEERING  ·  SYSTEMS & WEB", P, size=14))
    o.append(text(64, 186, "Kian", size=76, fill=P["text"], weight="800", ls=-1.8))
    o.append(text(67, 216, "@" + STATS["login"], size=15, fill=P["faint"],
                  weight="600", family=MONO, ls=0.6))
    o.append(text(66, 256, TAGLINE, size=22, fill=P["muted"], weight="400",
                  ls=-0.15))

    # facts strip
    fx = 66
    facts = [
        (f"{STATS['public_repos']}", "public repos"),
        (f"{STATS['total_contributions']}", "contributions / yr"),
        (f"{STATS['commits']}", "commits / yr"),
        (f"since {STATS['created_at'][:4]}", "on GitHub"),
    ]
    for i, (big, small) in enumerate(facts):
        o.append(text(fx, 292, big, size=20, fill=P["text"], weight="700",
                      family=MONO))
        o.append(text(fx, 312, small, size=13, fill=P["faint"], weight="500", ls=0.4))
        fx += 154
        if i < len(facts) - 1:
            o.append(f'<rect x="{fx-38}" y="274" width="1" height="40" '
                     f'fill="{P["panel_edge"]}"/>')

    # ---- right: terminal card, tied to blackmamba-lang
    cx, cy, cw, ch = 848, 72, 370, 206
    o.append(f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="14" '
             f'fill="{P["panel"]}" stroke="{P["panel_edge"]}" stroke-width="1"/>')
    o.append(f'<rect x="{cx+1}" y="{cy+1}" width="{cw-2}" height="22" rx="13" '
             f'fill="{P["grid"]}" fill-opacity="0.02"/>')

    for i, c in enumerate([P["dot"], P["dot"], P["accent"]]):
        o.append(f'<circle cx="{cx+24+i*15}" cy="{cy+23}" r="4" fill="{c}"'
                 + (' opacity="0.95"/>' if i == 2 else '/>'))
    o.append(text(cx + cw - 20, cy + 27, "blackmamba", size=12.5, fill=P["faint"],
                  weight="500", family=MONO, anchor="end"))
    o.append(f'<rect x="{cx}" y="{cy+42}" width="{cw}" height="1" fill="{P["panel_edge"]}"/>')

    tx = cx + 24
    o.append(text(tx, cy + 78, "$", size=14.5, fill=P["accent"], weight="700", family=MONO))
    o.append(text(tx + 19, cy + 78, "bmb run hello.bmb", size=14.5,
                  fill=P["text"], weight="400", family=MONO))
    o.append(text(tx, cy + 106, "hello, world", size=14.5, fill=P["accent"],
                  weight="600", family=MONO))
    o.append(text(tx + 116, cy + 106, "· 0.9ms", size=14.5, fill=P["faint"],
                  weight="400", family=MONO))
    o.append(text(tx, cy + 138, "# no interpreter", size=14, fill=P["muted"],
                  weight="400", family=MONO, style="font-style:italic"))
    o.append(text(tx, cy + 158, "# no GIL", size=14, fill=P["muted"],
                  weight="400", family=MONO, style="font-style:italic"))
    o.append(f'<rect x="{tx}" y="{cy+172}" width="{cw-48}" height="1" fill="{P["panel_edge"]}"/>')
    o.append(text(tx, cy + 192, "native x86-64  ·  wasm  ·  llvm ir", size=12.5,
                  fill=P["faint"], weight="500", family=MONO, ls=0.4))

    o.append("</svg>")
    return "".join(o)


# ------------------------------------------------------------- language bar ---
def langbar(t):
    W, H = CARD_W, 122
    P = THEMES[t]
    counts = STATS["lang_counts"]
    colors = STATS["lang_colors"]
    total = sum(counts.values()) or 1
    items = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))

    o = [head(W, H)]
    o.append(card_bg(W, H, P))
    o.append(eyebrow(30, 32, "LANGUAGE MIX", P))
    o.append(text(W - 30, 32, f"by primary language  ·  {total} repos",
                  size=11, fill=P["faint"], weight="500", family=MONO, anchor="end"))

    bx, by, bw, bh = 30, 50, W - 60, 14
    o.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="7" fill="{P["heat"][0]}"/>')
    o.append(f'<defs><clipPath id="barc"><rect x="{bx}" y="{by}" width="{bw}" '
             f'height="{bh}" rx="7"/></clipPath></defs>')
    o.append('<g clip-path="url(#barc)">')
    cursor = bx
    for i, (name, c) in enumerate(items):
        seg = bw * c / total
        if i == len(items) - 1:
            seg = bx + bw - cursor
        col = colors.get(name, P["muted"])
        o.append(f'<rect x="{cursor:.2f}" y="{by}" width="{seg:.2f}" '
                 f'height="{bh}" fill="{col}"/>')
        cursor += seg
        # hairline separators keep adjacent similar hues from merging
        if i < len(items) - 1:
            o.append(f'<rect x="{cursor-1:.2f}" y="{by}" width="2" height="{bh}" '
                     f'fill="{P["bg0"]}" opacity="0.85"/>')
    o.append("</g>")

    # legend, single row, evenly spaced
    lx, ly = 30, 96
    for name, c in items:
        pct = round(100 * c / total, 1)
        label = f"{name} {pct:g}%"
        wpx = 6.55 * len(label) + 26
        col = colors.get(name, P["muted"])
        o.append(f'<circle cx="{lx+4}" cy="{ly-4}" r="3.6" fill="{col}"/>')
        o.append(text(lx + 14, ly, label, size=11, fill=P["muted"],
                      weight="600", family=MONO, ls=0.2))
        lx += wpx
    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------- heatmap ---
def heatmap(t):
    """53-week contribution heatmap drawn from real data."""
    P = THEMES[t]
    cells = [(dt.date.fromisoformat(d), c) for d, c in STATS["days"]]
    while cells and cells[0][0].weekday() != 6:          # 6 = Sunday
        cells.insert(0, (cells[0][0] - dt.timedelta(days=1), -1))
    while len(cells) % 7:
        cells.append((cells[-1][0] + dt.timedelta(days=1), -1))

    weeks = len(cells) // 7
    size, gap = 12, 3
    grid_w = weeks * (size + gap) - gap
    left, top = 38, 80
    W = left + grid_w + 38
    H = top + 7 * (size + gap) - gap + 52

    o = [head(W, H)]
    o.append(card_bg(W, H, P))
    o.append(eyebrow(left, 32, "CONTRIBUTION ACTIVITY", P))
    o.append(text(left, 54, f"{STATS['total_contributions']} contributions in the last year",
                  size=12.5, fill=P["muted"], weight="500"))
    o.append(text(W - left, 54,
                  f"{STATS['active_days']} active days  ·  best streak {STATS['longest_streak']}d",
                  size=11, fill=P["faint"], weight="500", family=MONO, anchor="end"))

    mx = max([c for _, c in cells if c > 0] or [1])

    def level(c):
        if c <= 0:
            return 0
        r = c / mx
        return 4 if r > 0.66 else 3 if r > 0.33 else 2 if r > 0.10 else 1

    # month labels: first column of each new month, skip if it crowds the last
    seen = set()
    last_x = -99
    for i, (d, _) in enumerate(cells):
        col = i // 7
        key = d.strftime("%Y-%m")
        if d.day <= 7 and key not in seen and col > 0:
            seen.add(key)
            x = left + col * (size + gap)
            if x - last_x >= 34:
                o.append(text(x, top - 12, d.strftime("%b"), size=10,
                              fill=P["faint"], weight="600", ls=0.3))
                last_x = x

    for i, (d, c) in enumerate(cells):
        if c < 0:
            continue
        col, row = i // 7, i % 7
        o.append(f'<rect x="{left + col*(size+gap)}" y="{top + row*(size+gap)}" '
                 f'width="{size}" height="{size}" rx="2.2" fill="{P["heat"][level(c)]}"/>')

    for row, lbl in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        o.append(text(left - 10, top + row * (size + gap) + size - 3, lbl,
                      size=9.5, fill=P["faint"], weight="600", anchor="end"))

    # footer: timestamp left, scale right, on its own row clear of the grid
    fy = top + 7 * (size + gap) + 18
    o.append(text(left, fy, f"updated {STATS['generated']}", size=10,
                  fill=P["faint"], weight="500", family=MONO))

    sw = 5 * (size + gap)
    sx = W - left - sw - 76
    o.append(text(sx - 10, fy, "less", size=10, fill=P["faint"], weight="600", anchor="end"))
    for k in range(5):
        o.append(f'<rect x="{sx + k*(size+gap)}" y="{fy-9}" width="{size}" '
                 f'height="{size}" rx="2.2" fill="{P["heat"][k]}"/>')
    o.append(text(sx + sw + 8, fy, "more", size=10, fill=P["faint"],
                  weight="600", anchor="start"))
    o.append("</svg>")
    return "".join(o)


def main():
    global STATS
    STATS = load()
    os.makedirs(ASSETS, exist_ok=True)

    for name, fn in {"hero": hero, "langs": langbar, "activity": heatmap}.items():
        for theme in ("dark", "light"):
            svg = fn(theme)
            path = os.path.join(ASSETS, f"{name}-{theme}.svg")
            with open(path, "w", encoding="utf-8") as f:
                f.write(svg)
            print(f"  {name}-{theme}.svg  {len(svg)/1024:.1f} KB")

    print(f"\nRepos {STATS['public_repos']}  contributions {STATS['total_contributions']}  "
          f"active days {STATS['active_days']}  best streak {STATS['longest_streak']}d")
    print("Languages:", STATS["lang_counts"])


if __name__ == "__main__":
    main()
