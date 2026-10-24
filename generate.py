"""
Generates the animated SVG assets for kicode01's GitHub profile README.

The trick this file is built around: GitHub strips <script>, <style>, and inline
SVG from READMEs, but it happily serves an .svg file as an <img>. Inside that
image, CSS animations still run. So the banner can type itself, and the charts
can draw themselves, with no JavaScript and no third-party service.

Two rules keep that from becoming a liability:
  1. The base state of every element is its *final* state. Animation only ever
     adds motion — if a renderer ignores CSS, the page still reads correctly.
  2. `prefers-reduced-motion` disables everything inside the SVG, and the README
     swaps in a genuinely static file for anyone who asks for it.

Usage:
    python generate.py            # uses stats.json if present, else fetches
    python generate.py --fetch    # force a fresh pull from the GitHub API
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
CARD_W = 880

# GitHub's language colours, hardcoded so the language bar does not depend on
# the GraphQL round-trip succeeding.
LANG_COLORS = {
    "Python": "#3572A5", "TypeScript": "#3178c6", "JavaScript": "#f1e05a",
    "HTML": "#e34c26", "CSS": "#663399", "Jupyter Notebook": "#DA5B0B",
    "C++": "#f34b7d", "C": "#555555", "PHP": "#4F5D95", "LLVM": "#185619",
    "WebAssembly": "#04133b", "Dockerfile": "#384d54", "OpenSCAD": "#e5cd45",
    "Batchfile": "#C1F12E", "MDX": "#fcb32c", "Shell": "#89e051",
    "Java": "#b07219", "Go": "#00ADD8", "Rust": "#dea584", "Vue": "#41b883",
}

# Transcribed from blackmamba-lang's own benchmark table (README, "Performance").
# Re-run that suite in the repo before trusting these after a compiler change.
BENCH = [
    ("fib(32)", 288.62, 11.078, "26.1x"),
    ("collatz(40k)", 227.84, 8.291, "27.5x"),
    ("mandelbrot(120²)", 39.14, 3.368, "11.6x"),
    ("count_primes(30k)", 22.05, 1.730, "12.7x"),
]

# ---------------------------------------------------------------- palettes ---
THEMES = {
    "dark": {
        "bg0": "#0b0f16", "bg1": "#10151f", "panel": "#0d131c",
        "panel_edge": "#1e2733", "text": "#e9eef6", "muted": "#8d99aa",
        "faint": "#4a5567", "accent": "#5ce0a8", "accent2": "#9d8cff",
        "grid": "#ffffff", "grid_op": "0.035", "glow_op": "0.15",
        "heat": ["#161c26", "#123a2b", "#1a6b4c", "#2ba574", "#5ce0a8"],
        "dot": "#2a3340", "track": "#1b2330",
    },
    "light": {
        "bg0": "#ffffff", "bg1": "#f4f7fb", "panel": "#fbfcfe",
        "panel_edge": "#dbe3ed", "text": "#0c141f", "muted": "#586575",
        "faint": "#9aa6b5", "accent": "#0a8f5f", "accent2": "#6b52e0",
        "grid": "#0c141f", "grid_op": "0.05", "glow_op": "0.09",
        "heat": ["#e7ecf2", "#bdeed8", "#74d5ae", "#2cb184", "#0a8f5f"],
        "dot": "#c6ced9", "track": "#e8edf4",
    },
}

SANS = ("-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,"
        "'Noto Sans',sans-serif")
MONO = ("ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,"
        "'Liberation Mono',monospace")

# Every keyframe starts hidden and ends at the element's real state, and every
# animated element uses fill-mode "both". Nothing here is load-bearing: strip the
# animation and the layout is unchanged.
#
# Wipes use a <mask> with an animated rect width. clip-path:inset() resolves
# against the SVG viewport rather than the element's own box, and SMIL <animate>
# does not run here, so both were tested and rejected.
CSS = """
.a-fade{animation:fadeIn .55s ease-out both}
.a-rise{animation:riseIn .7s cubic-bezier(.22,.68,.2,1) both}
.a-slide{animation:slideIn .7s cubic-bezier(.22,.68,.2,1) both}
.a-grow{transform-box:fill-box;transform-origin:0 50%;animation:growX .85s cubic-bezier(.3,.8,.25,1) both}
.a-col{animation:fadeIn .5s ease-out both}
.wmKian{animation:wKian .9s cubic-bezier(.65,0,.25,1) both}
.wmCmd{animation:wCmd .95s steps(17,end) both}
.wmBar{animation:wBar .85s cubic-bezier(.65,0,.25,1) both}
@keyframes fadeIn{from{opacity:0}to{opacity:1}}
@keyframes riseIn{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
@keyframes slideIn{from{opacity:0;transform:translateX(-16px)}to{opacity:1;transform:translateX(0)}}
@keyframes growX{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes wKian{from{width:0}to{width:300px}}
@keyframes wCmd{from{width:0}to{width:148px}}
@keyframes wBar{from{width:0}to{width:820px}}
@keyframes blink{0%,48%{opacity:1}49%,100%{opacity:0}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


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
  }
}
""" % LOGIN


def fetch():
    # REST profile + repos. These work with the default Actions GITHUB_TOKEN.
    # (`gh api user` does not — it is a user-scoped endpoint and an installation
    # token has no user context, so it 403s in CI.)
    user = json.loads(gh(["api", "users/" + LOGIN]))
    repos = json.loads(gh(["api", "users/%s/repos?per_page=100&sort=pushed" % LOGIN]))

    # Contribution data needs GraphQL and a user-scoped token. Losing it should
    # degrade the heatmap, not break the build.
    contrib, prev = None, {}
    try:
        q = " ".join(QL.split())
        gql = json.loads(gh(["api", "graphql", "-f", "query=" + q]))["data"]["user"]
        contrib = gql["contributionsCollection"]
    except Exception as exc:  # noqa: BLE001 — any failure here is non-fatal
        prev = _previous_stats()
        print("! contribution data unavailable (%s)" % exc, file=sys.stderr)
        if not prev:
            raise

    if contrib:
        cal = contrib["contributionCalendar"]
        days = [[d["date"], d["contributionCount"]]
                for w in cal["weeks"] for d in w["contributionDays"]]
        totals = {
            "total_contributions": cal["totalContributions"],
            "commits": contrib["totalCommitContributions"],
            "prs": contrib["totalPullRequestContributions"],
            "repos_contributed": contrib["totalRepositoriesWithContributedCommits"],
        }
    else:
        print("  reusing the contribution series already in stats.json", file=sys.stderr)
        days = prev["days"]
        totals = {k: prev[k] for k in
                  ("total_contributions", "commits", "prs", "repos_contributed")}

    # Primary-language share across repos that actually contain code. Raw byte
    # totals mislead (one repo carries 3 MB of generated HTML). The profile repo
    # itself is excluded — it is tooling for this page, not a project.
    by_lang = defaultdict(int)
    for r in repos:
        if r["language"] and r["name"] != LOGIN:
            by_lang[r["language"]] += 1

    stats = {
        "login": user["login"],
        "name": user["name"],
        "bio": user["bio"],
        "created_at": user["created_at"],
        "public_repos": user["public_repos"],
        "followers": user["followers"],
        "total_stars": sum(r["stargazers_count"] for r in repos),
        "days": days,
        "lang_counts": dict(by_lang),
        "lang_colors": LANG_COLORS,
        "generated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d"),
        "repos": [{
            "name": r["name"], "description": r["description"],
            "language": r["language"], "stars": r["stargazers_count"],
            "homepage": r["homepage"], "topics": r["topics"],
            "pushed_at": r["pushed_at"], "license": (r.get("license") or {}).get("spdx_id"),
        } for r in repos],
        **totals,
    }
    with open(os.path.join(ROOT, "stats.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    return stats


def _previous_stats():
    p = os.path.join(ROOT, "stats.json")
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


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
    best = max(days, key=lambda x: x[1])
    stats["best_day"] = [best[0].isoformat(), best[1]]
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
def head(w, h, extra=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" fill="none" role="img">{extra}')


def AC(motion, cls):
    """Animation class, or nothing when this is the static build."""
    return cls if motion else ""


def DL(motion, delay):
    """Animation delay, or None when this is the static build."""
    return delay if motion else None


def anim(motion, cls="", delay=None, style=""):
    """Build class/style attributes in one place so `style` is never emitted twice."""
    parts = []
    if style:
        parts.append(style)
    if motion and delay is not None:
        parts.append(f"animation-delay:{delay:.2f}s")
    out = f' class="{cls}"' if (motion and cls) else ""
    if parts:
        out += f' style="{";".join(parts)}"'
    return out


def text(x, y, s, size=14, fill="#000", weight="400", family=SANS,
         anchor="start", ls=0, op=1.0, style="", cls="", delay=None, tlen=None):
    parts = []
    if style:
        parts.append(style)
    if delay is not None:
        parts.append(f"animation-delay:{delay:.2f}s")
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"'
            + (f' letter-spacing="{ls}"' if ls else "")
            + (f' opacity="{op}"' if op != 1.0 else "")
            + (f' class="{cls}"' if cls else "")
            + (f' style="{";".join(parts)}"' if parts else "")
            + (f' textLength="{tlen}" lengthAdjust="spacingAndGlyphs"' if tlen else "")
            + f'>{escape(str(s))}</text>')


def card_bg(W, H, P, radius=12):
    return (
        f'<rect width="{W}" height="{H}" rx="{radius}" fill="{P["bg0"]}"/>'
        f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="{radius-0.5}" '
        f'fill="none" stroke="{P["panel_edge"]}" stroke-width="1"/>'
    )


def eyebrow(x, y, label, P, size=11.5, ls=2.2, motion=None, delay=None):
    return (f'<circle cx="{x+5}" cy="{y-4.5}" r="{size*0.30:.1f}" '
            f'fill="{P["accent"]}" {anim(motion, "a-fade", delay) if motion is not None else ""}/>'
            + text(x + 5 + size * 1.0, y, label, size=size, fill=P["accent"],
                   weight="700", ls=ls,
                   cls=AC(motion, "a-fade") if motion is not None else "",
                   delay=DL(motion, delay) if motion is not None else None))


# -------------------------------------------------------------------- hero ---
def hero(t, motion=True):
    """1280x348 banner that types itself once, then holds still."""
    W, H = 1280, 348
    P = THEMES[t]
    o = [head(W, H, f"<style>{CSS}</style>" if motion else "")]

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
</pattern>""")

    # masks are only emitted for the animated build; the static file needs none.
    # Coordinates are absolute — the command text sits at y = cy + 78.
    if motion:
        o.append(f"""
<mask id="mKian" maskUnits="userSpaceOnUse" x="40" y="110" width="320" height="100">
  <rect x="64" y="110" width="300" height="100" fill="#fff"
        class="wmKian" style="animation-delay:.30s"/>
</mask>
<mask id="mCmd" maskUnits="userSpaceOnUse" x="885" y="{72+58}" width="175" height="36">
  <rect x="891" y="{72+58}" width="148" height="36" fill="#fff"
        class="wmCmd" style="animation-delay:1.05s"/>
</mask>""")

    o.append("</defs>")

    o.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
    o.append(f'<rect width="{W}" height="{H}" fill="url(#grid)"/>')
    o.append(f'<rect width="{W}" height="{H}" fill="url(#glow)"/>')
    o.append(f'<rect width="{W}" height="{H}" fill="url(#glow2)"/>')
    o.append(f'<rect x="0" y="0" width="{W}" height="2" fill="url(#topline)" '
             f'{anim(motion, "a-fade", 0.05)}/>')

    # ---- left: identity
    o.append(eyebrow(66, 101, "COMPUTER ENGINEERING  ·  SYSTEMS & WEB", P,
                     size=14, motion=motion, delay=0.15))
    kian = text(64, 186, "Kian", size=76, fill=P["text"], weight="800", ls=-1.8)
    o.append(f'<g mask="url(#mKian)">{kian}</g>' if motion else kian)
    o.append(text(67, 216, "@" + STATS["login"], size=15, fill=P["faint"],
                  weight="600", family=MONO, ls=0.6,
                  cls=AC(motion, "a-fade"), delay=DL(motion, 0.95)))
    o.append(text(66, 256, TAGLINE, size=22, fill=P["muted"], weight="400",
                  ls=-0.15, cls=AC(motion, "a-rise"), delay=DL(motion, 1.05)))

    fx = 66
    facts = [
        (f"{STATS['public_repos']}", "public repos"),
        (f"{STATS['total_contributions']}", "contributions / yr"),
        (f"{STATS['commits']}", "commits / yr"),
        (f"since {STATS['created_at'][:4]}", "on GitHub"),
    ]
    for i, (big, small) in enumerate(facts):
        d = 1.20 + i * 0.10
        o.append(text(fx, 292, big, size=20, fill=P["text"], weight="700",
                      family=MONO, cls=AC(motion, "a-rise"), delay=DL(motion, d)))
        o.append(text(fx, 312, small, size=13, fill=P["faint"], weight="500",
                      ls=0.4, cls=AC(motion, "a-rise"), delay=DL(motion, d + 0.05)))
        fx += 154
        if i < len(facts) - 1:
            o.append(f'<rect x="{fx-38}" y="274" width="1" height="40" '
                     f'fill="{P["panel_edge"]}" {anim(motion, "a-fade", d)}/>')

    # ---- right: terminal card, tied to blackmamba-lang
    cx, cy, cw, ch = 848, 72, 370, 206
    o.append(f'<g {anim(motion, "a-fade", 0.45)}>'
             f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="14" '
             f'fill="{P["panel"]}" stroke="{P["panel_edge"]}" stroke-width="1"/>'
             f'<rect x="{cx+1}" y="{cy+1}" width="{cw-2}" height="22" rx="13" '
             f'fill="{P["grid"]}" fill-opacity="0.02"/></g>')

    for i, c in enumerate([P["dot"], P["dot"], P["accent"]]):
        o.append(f'<circle cx="{cx+24+i*15}" cy="{cy+23}" r="4" fill="{c}"'
                 + (' opacity="0.95"/>' if i == 2 else '/>'))
    o.append(text(cx + cw - 20, cy + 27, "blackmamba", size=12.5, fill=P["faint"],
                  weight="500", family=MONO, anchor="end"))
    o.append(f'<rect x="{cx}" y="{cy+42}" width="{cw}" height="1" fill="{P["panel_edge"]}"/>')

    tx = cx + 24
    # textLength pins the command to an exact width so the steps() wipe below
    # advances by whole characters whatever monospace font the viewer has.
    CLEN = 148
    o.append(text(tx, cy + 78, "$", size=14.5, fill=P["accent"], weight="700",
                  family=MONO))
    cmd = text(tx + 19, cy + 78, "bmb run hello.bmb", size=14.5,
               fill=P["text"], weight="400", family=MONO, tlen=CLEN)
    o.append(f'<g mask="url(#mCmd)">{cmd}</g>' if motion else cmd)

    cur_style = ("opacity:0;animation:fadeIn .2s ease-out both 1.95s,"
                 "blink 1.05s steps(1) infinite 2.15s" if motion
                 else "opacity:0.85")
    o.append(f'<rect x="{tx + 19 + CLEN + 5}" y="{cy + 64}" width="8" height="17" '
             f'rx="1.5" fill="{P["accent"]}" style="{cur_style}"/>')

    o.append(text(tx, cy + 106, "hello, world", size=14.5, fill=P["accent"],
                  weight="600", family=MONO, cls=AC(motion, "a-fade"),
                  delay=DL(motion, 2.05)))
    o.append(text(tx + 116, cy + 106, "· 0.9ms", size=14.5, fill=P["faint"],
                  weight="400", family=MONO, cls=AC(motion, "a-fade"),
                  delay=DL(motion, 2.20)))
    o.append(text(tx, cy + 138, "# no interpreter", size=14, fill=P["muted"],
                  weight="400", family=MONO, style="font-style:italic",
                  cls=AC(motion, "a-fade"), delay=DL(motion, 2.30)))
    o.append(text(tx, cy + 158, "# no GIL", size=14, fill=P["muted"],
                  weight="400", family=MONO, style="font-style:italic",
                  cls=AC(motion, "a-fade"), delay=DL(motion, 2.42)))
    o.append(f'<rect x="{tx}" y="{cy+172}" width="{cw-48}" height="1" '
             f'fill="{P["panel_edge"]}" {anim(motion, "a-fade", 2.50)}/>')
    o.append(text(tx, cy + 192, "native x86-64  ·  wasm  ·  llvm ir", size=12.5,
                  fill=P["faint"], weight="500", family=MONO, ls=0.4,
                  cls=AC(motion, "a-fade"), delay=DL(motion, 2.60)))

    o.append("</svg>")
    return "".join(o)


# ---------------------------------------------------------------- heatmap ---
def heatmap(t, motion=True):
    """53-week contribution heatmap; columns sweep in left to right."""
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

    o = [head(W, H, f"<style>{CSS}</style>" if motion else "")]
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

    seen, last_x = set(), -99
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

    # one <g> per week keeps the cascade cheap: 53 animations, not 364
    for col in range(weeks):
        o.append(f'<g {anim(motion, "a-col", 0.15 + col * 0.016)}>')
        for row in range(7):
            idx = col * 7 + row
            if idx >= len(cells):
                break
            _, c = cells[idx]
            if c < 0:
                continue
            o.append(f'<rect x="{left + col*(size+gap)}" y="{top + row*(size+gap)}" '
                     f'width="{size}" height="{size}" rx="2.2" '
                     f'fill="{P["heat"][level(c)]}"/>')
        o.append("</g>")

    for row, lbl in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        o.append(text(left - 10, top + row * (size + gap) + size - 3, lbl,
                      size=9.5, fill=P["faint"], weight="600", anchor="end"))

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


# ------------------------------------------------------------- language bar ---
def langbar(t, motion=True):
    W, H = CARD_W, 122
    P = THEMES[t]
    counts = STATS["lang_counts"]
    colors = STATS["lang_colors"]
    total = sum(counts.values()) or 1
    items = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))

    o = [head(W, H, f"<style>{CSS}</style>" if motion else "")]
    o.append(card_bg(W, H, P))
    o.append(eyebrow(30, 32, "LANGUAGE MIX", P))
    o.append(text(W - 30, 32, f"by primary language  ·  {total} repos",
                  size=11, fill=P["faint"], weight="500", family=MONO, anchor="end"))

    bx, by, bw, bh = 30, 50, W - 60, 14
    o.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="7" fill="{P["track"]}"/>')
    o.append(f'<defs><clipPath id="barc"><rect x="{bx}" y="{by}" width="{bw}" '
             f'height="{bh}" rx="7"/></clipPath>'
             + (f'<mask id="mBar" maskUnits="userSpaceOnUse" x="{bx}" y="{by}" '
                f'width="{bw}" height="{bh}">'
                f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="#fff" '
                f'class="wmBar" style="animation-delay:.15s"/></mask>' if motion else "")
             + '</defs>')
    # the whole bar wipes in as one gesture — cleaner than segments racing
    o.append(f'<g clip-path="url(#barc)"'
             + (' mask="url(#mBar)"' if motion else '') + '>')
    cursor = bx
    for i, (name, c) in enumerate(items):
        seg = bw * c / total
        if i == len(items) - 1:
            seg = bx + bw - cursor
        o.append(f'<rect x="{cursor:.2f}" y="{by}" width="{seg:.2f}" '
                 f'height="{bh}" fill="{colors.get(name, P["muted"])}"/>')
        cursor += seg
        if i < len(items) - 1:
            o.append(f'<rect x="{cursor-1:.2f}" y="{by}" width="2" height="{bh}" '
                     f'fill="{P["bg0"]}" opacity="0.85"/>')
    o.append("</g>")

    lx, ly = 30, 96
    for i, (name, c) in enumerate(items):
        pct = round(100 * c / total, 1)
        label = f"{name} {pct:g}%"
        wpx = 6.55 * len(label) + 26
        col = colors.get(name, P["muted"])
        o.append(f'<g {anim(motion, "a-fade", 0.45 + i * 0.07)}>'
                 f'<circle cx="{lx+4}" cy="{ly-4}" r="3.6" fill="{col}"/>'
                 + text(lx + 14, ly, label, size=11, fill=P["muted"],
                        weight="600", family=MONO, ls=0.2) + "</g>")
        lx += wpx
    o.append("</svg>")
    return "".join(o)


# -------------------------------------------------------------- benchmark ---
def bench(t, motion=True):
    """Black Mamba vs CPython on its own kernels. Bars grow from the left."""
    W, H = CARD_W, 330
    P = THEMES[t]
    o = [head(W, H, f"<style>{CSS}</style>" if motion else "")]
    o.append(card_bg(W, H, P))
    o.append(eyebrow(30, 34, "BENCHMARK  ·  BLACK MAMBA vs CPYTHON 3.14", P))
    o.append(text(W - 30, 34, "lower is better  ·  ms per kernel",
                  size=11, fill=P["faint"], weight="500", family=MONO, anchor="end"))

    ly = 62
    o.append(f'<rect x="30" y="{ly-9}" width="18" height="9" rx="4.5" '
             f'fill="{P["faint"]}" opacity="0.55"/>')
    o.append(text(54, ly - 1, "CPython", size=10.5, fill=P["muted"],
                  weight="600", family=MONO))
    o.append(f'<rect x="128" y="{ly-9}" width="18" height="9" rx="4.5" fill="{P["accent"]}"/>')
    o.append(text(152, ly - 1, "Black Mamba", size=10.5, fill=P["muted"],
                  weight="600", family=MONO))

    x0, bar_max = 30, 486
    scale = bar_max / 300.0
    y = 96
    for i, (label, cpy, bmb, speedup) in enumerate(BENCH):
        d = 0.25 + i * 0.14
        o.append(f'<g {anim(motion, "a-fade", d)}>'
                 + text(x0, y + 14, label, size=11.5, fill=P["text"],
                        weight="600", family=MONO) + "</g>")

        w1 = max(6.0, cpy * scale)
        w2 = max(6.0, bmb * scale)
        o.append(f'<rect x="{x0+172}" y="{y}" width="{w1:.1f}" height="13" rx="3" '
                 f'fill="{P["faint"]}" opacity="0.55" {anim(motion, "a-grow", d)}/>')
        o.append(f'<rect x="{x0+172}" y="{y+19}" width="{w2:.1f}" height="13" rx="3" '
                 f'fill="{P["accent"]}" {anim(motion, "a-grow", d + 0.06)}/>')

        o.append(text(x0 + 172 + w1 + 9, y + 10, f"{cpy:g}", size=10.5,
                      fill=P["faint"], weight="500", family=MONO,
                      cls=AC(motion, "a-fade"), delay=DL(motion, d + 0.25)))
        o.append(text(x0 + 172 + w2 + 9, y + 29, f"{bmb:g}", size=10.5,
                      fill=P["accent"], weight="600", family=MONO,
                      cls=AC(motion, "a-fade"), delay=DL(motion, d + 0.31)))

        o.append(f'<g {anim(motion, "a-fade", d + 0.20)}>'
                 + text(W - 30, y + 24, speedup, size=15, fill=P["accent"],
                        weight="700", family=MONO, anchor="end") + "</g>")
        y += 52

    o.append(text(30, H - 20,
                  "measured with the repo's own suite  ·  tail-call case omitted (CPython recurses out)",
                  size=10, fill=P["faint"], weight="500", family=MONO))
    o.append("</svg>")
    return "".join(o)


# --------------------------------------------------------------- readme glue --
MD_START = "<!-- activity:start -->"
MD_END = "<!-- activity:end -->"


def update_readme(S):
    """Rewrite the one sentence in README.md that quotes live numbers."""
    p = os.path.join(ROOT, "README.md")
    if not os.path.exists(p):
        return
    with open(p, encoding="utf-8") as f:
        md = f.read()
    if MD_START not in md or MD_END not in md:
        return

    monthly = defaultdict(int)
    for d, c in S["days"]:
        monthly[d[:7]] += c
    if not monthly:
        return

    month_key, peak = max(monthly.items(), key=lambda kv: kv[1])
    total = S["total_contributions"] or 1
    name = dt.date.fromisoformat(month_key + "-01").strftime("%B")

    if peak / total >= 0.35:
        line = (f"Most of that activity is recent — {peak} of the {total} "
                f"contributions landed in {name} alone. The ramp is steep, and "
                f"the graph shows it.")
    else:
        line = (f"{total} contributions across the year, peaking at {peak} in "
                f"{name}. The graph shows it honestly.")

    head_, rest = md.split(MD_START, 1)
    _, tail = rest.split(MD_END, 1)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"{head_}{MD_START}\n{line}\n{MD_END}{tail}")
    print("  README.md activity sentence updated")


def main():
    global STATS
    STATS = load()
    os.makedirs(ASSETS, exist_ok=True)

    # --static renders every asset in its settled state, which is how the page
    # looks once the animations finish. Used for layout review and screenshots.
    still = "--static" in sys.argv
    jobs = {"hero": hero, "activity": heatmap, "langs": langbar, "bench": bench}
    for name, fn in jobs.items():
        for theme in ("dark", "light"):
            svg = fn(theme, motion=not still)
            path = os.path.join(ASSETS, f"{name}-{theme}.svg")
            with open(path, "w", encoding="utf-8") as f:
                f.write(svg)
            print(f"  {name}-{theme}.svg  {len(svg)/1024:.1f} KB")

    # genuinely static banner for prefers-reduced-motion
    for theme in ("dark", "light"):
        svg = hero(theme, motion=False)
        path = os.path.join(ASSETS, f"hero-{theme}-static.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"  hero-{theme}-static.svg  {len(svg)/1024:.1f} KB")

    update_readme(STATS)
    print(f"\nRepos {STATS['public_repos']}  contributions {STATS['total_contributions']}  "
          f"active days {STATS['active_days']}  best streak {STATS['longest_streak']}d")


if __name__ == "__main__":
    main()
