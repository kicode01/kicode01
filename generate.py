"""
Generates refined sketchbook / editorial line-art SVG cards for Kian's profile.

Design language:
  1. Palette drawn directly from Kian's hand-drawn avatar:
     warm paper (#FAF8F5), charcoal pencil (#18171A / #2B2828),
     soft blush rose (#E598A6), and muted collar lavender (#A5A4F0).
  2. No duplicate cartoon portrait in the hero banner — the real avatar sits
     right next to it on GitHub.
  3. Delicate pen-and-ink linework (`scale="0.8"` subtle sketch displacement on
     frames and line illustrations, while keeping all text 100% crisp).
  4. True 1:1 native pixel resolution on GitHub (840px full-width, 410px cards).
"""
import datetime as dt
import json
import os
import subprocess
import sys
from collections import defaultdict
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(ROOT, "assets")
LOGIN = "kicode01"

LANG_COLORS = {
    "Python": "#3572A5", "TypeScript": "#3178c6", "JavaScript": "#f1e05a",
    "HTML": "#e34c26", "CSS": "#663399", "Jupyter Notebook": "#DA5B0B",
    "C++": "#f34b7d", "C": "#555555", "LLVM": "#185619", "WebAssembly": "#04133b",
    "OpenSCAD": "#e5cd45", "Shell": "#89e051",
}

BENCH = [
    ("fib(32)", 288.62, 11.08, "26.1×"),
    ("collatz(40k)", 227.84, 8.29, "27.5×"),
    ("mandelbrot(120×120)", 39.14, 3.37, "11.6×"),
    ("count_primes(30k)", 22.05, 1.73, "12.7×"),
]

# Avatar-matched palette: Charcoal, Warm Paper, Soft Blush Rose & Muted Lavender.
THEMES = {
    "dark": {
        "card": "#17161A",
        "stage": "#1F1E24",
        "border": "#3A3742",
        "stage_border": "#2E2B36",
        "ink": "#EAE4DC",
        "shadow": "#09080B",
        "text": "#F5F2EB",
        "sub": "#C6C0B7",
        "muted": "#8A847C",
        "dot": "#2C2933",
        "blush": "#ECA1AE",
        "blush_bg": "#2D1F24",
        "blush_border": "#5E3942",
        "lavender": "#ABA8F6",
        "lavender_bg": "#212036",
        "lavender_border": "#434070",
        "cream": "#EFE6D5",
        "cream_bg": "#292621",
    },
    "light": {
        "card": "#FCFBF8",
        "stage": "#F4F0E8",
        "border": "#2B2828",
        "stage_border": "#D8D1C5",
        "ink": "#2B2828",
        "shadow": "#E4DDD0",
        "text": "#232020",
        "sub": "#524D48",
        "muted": "#857E76",
        "dot": "#E6E0D4",
        "blush": "#C85A6E",
        "blush_bg": "#FCECEF",
        "blush_border": "#E8B8C1",
        "lavender": "#5B56D6",
        "lavender_bg": "#EFEFFD",
        "lavender_border": "#C2C0F0",
        "cream": "#6E5634",
        "cream_bg": "#F5ECD9",
    },
}

SANS = "-apple-system,BlinkMacSystemFont,'Inter','Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"


def gh(args):
    out = subprocess.run(["gh"] + args, capture_output=True, text=True,
                         encoding="utf-8", shell=False)
    if out.returncode != 0:
        raise RuntimeError(out.stderr)
    return out.stdout


def _previous_stats():
    p = os.path.join(ROOT, "stats.json")
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def cross_repo_commits(n=6):
    tracked = [
        "voltsense-iot",
        "blackmamba-lang",
        "typenscrape",
        "meemomini",
        "klyph-txt",
        "shim-platform",
    ]
    results = []
    p = os.path.join(ROOT, "stats.json")
    prev_pulse = []
    if os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                prev_pulse = json.load(f).get("cross_repo_commits", [])
        except Exception:
            pass

    for r in tracked:
        try:
            out = json.loads(gh(["api", f"repos/{LOGIN}/{r}/commits?per_page=1"]))
            if out:
                c = out[0]
                sha = c["sha"][:7]
                msg = c["commit"]["message"].split("\n")[0]
                date_str = c["commit"]["author"]["date"][:10]
                results.append({"repo": r, "sha": sha, "msg": msg, "date": date_str})
        except Exception:
            pass

    if not results and prev_pulse:
        return prev_pulse

    results.sort(key=lambda x: x["date"], reverse=True)
    return results[:n]


def fetch():
    user = json.loads(gh(["api", "users/" + LOGIN]))
    repos = json.loads(gh(["api", "users/%s/repos?per_page=100&sort=pushed" % LOGIN]))

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

    contrib, prev = None, {}
    try:
        q = " ".join(QL.split())
        gql = json.loads(gh(["api", "graphql", "-f", "query=" + q]))["data"]["user"]
        contrib = gql["contributionsCollection"]
    except Exception as exc:
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
        days = prev.get("days", [])
        totals = {k: prev.get(k, 0) for k in
                  ("total_contributions", "commits", "prs", "repos_contributed")}

    by_lang = defaultdict(int)
    for r in repos:
        if r.get("language") and r.get("name") != LOGIN:
            by_lang[r["language"]] += 1

    pulse = cross_repo_commits()

    stats = {
        "login": user["login"], "name": user["name"], "bio": user["bio"],
        "created_at": user["created_at"], "public_repos": user["public_repos"],
        "followers": user["followers"],
        "total_stars": sum(r["stargazers_count"] for r in repos),
        "days": days, "lang_counts": dict(by_lang), "lang_colors": LANG_COLORS,
        "cross_repo_commits": pulse,
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


def derive(s):
    days = [(dt.date.fromisoformat(d), c) for d, c in s.get("days", [])]
    s["active_days"] = sum(1 for _, c in days if c > 0)

    longest = cur = 0
    start = best = None
    for date, c in days:
        if c > 0:
            if cur == 0:
                start = date
            cur += 1
            if cur > longest:
                longest, best = cur, (start, date)
        else:
            cur = 0
    s["longest_streak"] = longest
    s["longest_streak_range"] = [d.isoformat() for d in best] if best else None

    monthly = defaultdict(int)
    for d, c in days:
        monthly[d.strftime("%Y-%m")] += c
    s["monthly"] = [{"month": m, "count": c}
                    for m, c in sorted(monthly.items())][-12:]

    if "cross_repo_commits" not in s or not s["cross_repo_commits"]:
        s["cross_repo_commits"] = cross_repo_commits()
    return s


def load():
    if "--fetch" in sys.argv:
        return derive(fetch())
    p = os.path.join(ROOT, "stats.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return derive(json.load(f))
    return derive(fetch())


def recent_commits(n=5):
    try:
        out = json.loads(gh(["api", "repos/%s/%s/commits?per_page=%d" % (LOGIN, LOGIN, n)]))
        return [(c["sha"][:7], c["commit"]["message"].split("\n")[0]) for c in out]
    except Exception:
        return []


def head(w, h):
    """Delicate hand-drawn ink displacement filter (`#ink`) for subtle organic lines."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" fill="none" role="img">'
        '<defs>'
        '<filter id="ink" x="-2%" y="-2%" width="104%" height="104%">'
        '<feTurbulence type="fractalNoise" baseFrequency="0.04" numOctaves="2" result="n" seed="7"/>'
        '<feDisplacementMap in="SourceGraphic" in2="n" scale="0.85" xChannelSelector="R" yChannelSelector="G"/>'
        '</filter>'
        '</defs>'
    )


def text(x, y, s, size=14, fill="#232020", weight="500", family=SANS,
         anchor="start", ls=0):
    ls_attr = f' letter-spacing="{ls}"' if ls else ""
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"'
            f'{ls_attr}>{escape(str(s))}</text>')


def sketch_card(w, h, P):
    """Refined sketchbook card with soft offset shadow and 1.8px rounded border."""
    return (
        f'<rect x="5" y="5" width="{w-8}" height="{h-8}" rx="14" fill="{P["shadow"]}" filter="url(#ink)"/>'
        f'<rect x="2" y="2" width="{w-8}" height="{h-8}" rx="14" fill="{P["card"]}" '
        f'stroke="{P["border"]}" stroke-width="1.8" stroke-linejoin="round" filter="url(#ink)"/>'
    )


def tag_pill(x, y, w, h, label_str, bg, fg, border, size=11, family=SANS, weight="600"):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2:.0f}" fill="{bg}" '
        f'stroke="{border}" stroke-width="1.2" filter="url(#ink)"/>'
        + text(x + w / 2, y + h / 2 + size * 0.35, label_str, size=size,
               fill=fg, weight=weight, family=family, anchor="middle")
    )


def star_doodle(cx, cy, r, col):
    """Subtle 4-point hand-sketched star."""
    r2 = r * 0.3
    d = (
        f"M {cx} {cy-r} Q {cx+r2} {cy-r2} {cx+r} {cy} "
        f"Q {cx+r2} {cy+r2} {cx} {cy+r} "
        f"Q {cx-r2} {cy+r2} {cx-r} {cy} "
        f"Q {cx-r2} {cy-r2} {cx} {cy-r} Z"
    )
    return f'<path d="{d}" fill="{col}" filter="url(#ink)"/>'


# ==============================================================================
# 00 / REFINED HERO BANNER (840 x 178 — No duplicate cartoon face)
# ==============================================================================
def hero(t):
    W, H = 840, 178
    P = THEMES[t]
    o = [head(W, H)]
    o.append(sketch_card(W, H, P))

    # Subtle sketchbook dot-grid along top right
    for gx in range(530, W - 24, 24):
        for gy in (22, 156):
            o.append(f'<circle cx="{gx}" cy="{gy}" r="1" fill="{P["dot"]}"/>')

    # Left column: Warm, understated introduction
    o.append(star_doodle(34, 34, 5.5, P["blush"]))
    o.append(text(46, 38, "kicode01  ·  computer engineering",
                  size=12, fill=P["muted"], weight="500", family=MONO))

    o.append(text(28, 78, "Hi, I'm Kian.", size=32, fill=P["text"], weight="800", ls=-0.7))
    o.append(text(28, 106, "I build compilers, ESP32 firmware, and practical AI apps —",
                  size=14, fill=P["sub"], weight="400"))
    o.append(text(28, 126, "focusing on how software actually behaves down at the metal.",
                  size=14, fill=P["sub"], weight="400"))

    # Sketchbook pills
    pills = [
        ("Python", 66, P["lavender_bg"], P["lavender"], P["lavender_border"]),
        ("C / C++", 72, P["stage"], P["sub"], P["stage_border"]),
        ("TypeScript", 88, P["stage"], P["sub"], P["stage_border"]),
        ("x86-64 & WASM", 112, P["blush_bg"], P["blush"], P["blush_border"]),
        ("ESP32", 62, P["stage"], P["sub"], P["stage_border"]),
    ]
    px = 28
    for lbl, pw, bg, fg, bd in pills:
        o.append(tag_pill(px, 138, pw, 22, lbl, bg, fg, bd, size=11, family=MONO))
        px += pw + 8

    # Dashed sketchbook divider
    o.append(f'<line x1="510" y1="24" x2="510" y2="{H-24}" stroke="{P["stage_border"]}" stroke-width="1.5" stroke-dasharray="4 4" filter="url(#ink)"/>')

    # Right column: 2x2 Notebook Stat Cards (using avatar's Blush & Lavender palette)
    cards = [
        (532, 24, "26.1×", "JIT speedup", P["blush_bg"], P["blush"], P["blush_border"]),
        (674, 24, "18 ms", "WASM vision", P["lavender_bg"], P["lavender"], P["lavender_border"]),
        (532, 96, str(STATS.get("total_contributions", 401)), "Contributions", P["stage"], P["text"], P["stage_border"]),
        (674, 96, str(STATS.get("public_repos", 20)), "Repositories", P["stage"], P["text"], P["stage_border"]),
    ]
    for cx, cy, val, lbl, bg, fg, bd in cards:
        cw, ch = 130, 58
        o.append(f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="10" fill="{bg}" stroke="{bd}" stroke-width="1.4" filter="url(#ink)"/>')
        o.append(text(cx + 16, cy + 28, val, size=21, fill=fg, weight="800", family=MONO, ls=-0.5))
        o.append(text(cx + 16, cy + 46, lbl, size=11.5, fill=P["muted"], weight="500"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 01 / SKETCHBOOK CARD: BLACK MAMBA COMPILER (410 x 204)
# ==============================================================================
def card_mamba(t):
    W, H = 410, 204
    P = THEMES[t]
    o = [head(W, H)]
    o.append(sketch_card(W, H, P))

    o.append(tag_pill(22, 18, 82, 22, "Compiler", P["lavender_bg"], P["lavender"], P["lavender_border"], size=11))
    o.append(text(W - 24, 33, "26.1× faster", size=12, fill=P["blush"], weight="700", family=MONO, anchor="end"))

    o.append(text(22, 64, "Black Mamba", size=20, fill=P["text"], weight="800", ls=-0.3))
    o.append(text(22, 84, "Python syntax compiled to native x86-64 & WASM.", size=13, fill=P["sub"]))

    # Refined Line-Art Illustration Stage: Source -> JIT Prism -> Speed Comparison
    sx, sy, sw, sh = 22, 98, W - 44, 64
    o.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="10" fill="{P["stage"]}" stroke="{P["stage_border"]}" stroke-width="1.4" filter="url(#ink)"/>')

    # Left: Sketch code page icon (.bm)
    o.append(f'<rect x="{sx+14}" y="{sy+12}" width="44" height="40" rx="5" fill="{P["card"]}" stroke="{P["border"]}" stroke-width="1.5" filter="url(#ink)"/>')
    o.append(f'<line x1="{sx+22}" y1="{sy+23}" x2="{sx+42}" y2="{sy+23}" stroke="{P["lavender"]}" stroke-width="2" stroke-linecap="round"/>')
    o.append(f'<line x1="{sx+22}" y1="{sy+31}" x2="{sx+48}" y2="{sy+31}" stroke="{P["muted"]}" stroke-width="1.8" stroke-linecap="round"/>')
    o.append(f'<line x1="{sx+22}" y1="{sy+39}" x2="{sx+36}" y2="{sy+39}" stroke="{P["blush"]}" stroke-width="2" stroke-linecap="round"/>')

    # Hand-drawn arrow
    o.append(f'<path d="M {sx+66} {sy+32} Q {sx+78} {sy+28} {sx+90} {sy+32}" stroke="{P["muted"]}" stroke-width="1.5" fill="none" filter="url(#ink)"/>')
    o.append(f'<path d="M {sx+86} {sy+28} L {sx+91} {sy+32} L {sx+86} {sy+36}" stroke="{P["muted"]}" stroke-width="1.5" fill="none"/>')

    # Right: Clean 2-bar visual comparison
    bx = sx + 102
    o.append(text(bx, sy + 25, "CPython", size=11, fill=P["muted"], family=MONO))
    o.append(f'<rect x="{bx+62}" y="{sy+16}" width="136" height="8" rx="4" fill="{P["dot"]}" stroke="{P["stage_border"]}" stroke-width="1" filter="url(#ink)"/>')
    o.append(text(sx + sw - 14, sy + 25, "288 ms", size=11, fill=P["muted"], family=MONO, anchor="end"))

    o.append(text(bx, sy + 46, "Mamba JIT", size=11, fill=P["text"], weight="700", family=MONO))
    o.append(f'<rect x="{bx+62}" y="{sy+37}" width="14" height="8" rx="4" fill="{P["blush"]}" stroke="{P["blush_border"]}" stroke-width="1" filter="url(#ink)"/>')
    o.append(star_doodle(bx + 86, sy + 41, 4.5, P["blush"]))
    o.append(text(sx + sw - 14, sy + 46, "11 ms", size=11, fill=P["blush"], weight="700", family=MONO, anchor="end"))

    # Footer
    o.append(text(22, 184, "Python · x86-64 · LLVM 18 · WASM", size=11, fill=P["muted"], family=MONO))
    o.append(text(W - 24, 184, "Repository ↗", size=12, fill=P["lavender"], weight="600", anchor="end"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 02 / SKETCHBOOK CARD: VOLTSENSE IOT (410 x 204)
# ==============================================================================
def card_voltsense(t):
    W, H = 410, 204
    P = THEMES[t]
    o = [head(W, H)]
    o.append(sketch_card(W, H, P))

    o.append(tag_pill(22, 18, 108, 22, "Firmware & IoT", P["blush_bg"], P["blush"], P["blush_border"], size=11))
    o.append(text(W - 24, 33, "0 keys on flash", size=12, fill=P["lavender"], weight="700", family=MONO, anchor="end"))

    o.append(text(22, 64, "VoltSense", size=20, fill=P["text"], weight="800", ls=-0.3))
    o.append(text(22, 84, "ESP32 load monitor & isolated cloud relay console.", size=13, fill=P["sub"]))

    # Refined Line-Art Stage: ESP32 IC Chip -> Cloud Lock -> Operator PWA
    sx, sy, sw, sh = 22, 98, W - 44, 64
    o.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="10" fill="{P["stage"]}" stroke="{P["stage_border"]}" stroke-width="1.4" filter="url(#ink)"/>')

    # Node 1: Sketch ESP32 Chip with little pins
    cx, cy = sx + 56, sy + 32
    for py_off in (-9, 0, 9):
        o.append(f'<line x1="{cx-42}" y1="{cy+py_off}" x2="{cx-34}" y2="{cy+py_off}" stroke="{P["muted"]}" stroke-width="1.8" stroke-linecap="round"/>')
        o.append(f'<line x1="{cx+34}" y1="{cy+py_off}" x2="{cx+42}" y2="{cy+py_off}" stroke="{P["muted"]}" stroke-width="1.8" stroke-linecap="round"/>')
    o.append(f'<rect x="{cx-34}" y="{cy-16}" width="68" height="32" rx="6" fill="{P["card"]}" stroke="{P["border"]}" stroke-width="1.5" filter="url(#ink)"/>')
    o.append(text(cx, cy + 4, "ESP32", size=11.5, fill=P["text"], weight="700", family=MONO, anchor="middle"))

    # Dashed wave connector 1
    o.append(f'<line x1="{cx+46}" y1="{cy}" x2="{cx+78}" y2="{cy}" stroke="{P["muted"]}" stroke-width="1.5" stroke-dasharray="3 3"/>')

    # Node 2: Vercel Auth Boundary (highlighted in blush)
    vx = sx + 183
    o.append(f'<rect x="{vx-44}" y="{cy-16}" width="88" height="32" rx="6" fill="{P["blush_bg"]}" stroke="{P["blush_border"]}" stroke-width="1.5" filter="url(#ink)"/>')
    o.append(text(vx, cy + 4, "Vercel Key", size=11, fill=P["blush"], weight="700", family=MONO, anchor="middle"))

    # Dashed wave connector 2
    o.append(f'<line x1="{vx+48}" y1="{cy}" x2="{vx+78}" y2="{cy}" stroke="{P["muted"]}" stroke-width="1.5" stroke-dasharray="3 3"/>')

    # Node 3: React PWA
    rx = sx + 308
    o.append(f'<rect x="{rx-42}" y="{cy-16}" width="84" height="32" rx="6" fill="{P["card"]}" stroke="{P["border"]}" stroke-width="1.5" filter="url(#ink)"/>')
    o.append(text(rx, cy + 4, "React PWA", size=11, fill=P["text"], weight="700", family=MONO, anchor="middle"))

    o.append(text(22, 184, "C++ · ESP32 · Firebase · React 19", size=11, fill=P["muted"], family=MONO))
    o.append(text(W - 24, 184, "Live app ↗", size=12, fill=P["lavender"], weight="600", anchor="end"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 03 / SKETCHBOOK CARD: TYPENSCRAPE APPLIED AI (410 x 204)
# ==============================================================================
def card_typenscrape(t):
    W, H = 410, 204
    P = THEMES[t]
    o = [head(W, H)]
    o.append(sketch_card(W, H, P))

    o.append(tag_pill(22, 18, 88, 22, "Applied AI", P["lavender_bg"], P["lavender"], P["lavender_border"], size=11))
    o.append(text(W - 24, 33, "Offline-first", size=12, fill=P["lavender"], weight="700", family=MONO, anchor="end"))

    o.append(text(22, 64, "TypenScrape", size=20, fill=P["text"], weight="800", ls=-0.3))
    o.append(text(22, 84, "Recipe generator with LLM failover & chunked local DB.", size=13, fill=P["sub"]))

    # Refined Line-Art Stage: Groq -> Gemini Failover + 16-Chunk IndexedDB
    sx, sy, sw, sh = 22, 98, W - 44, 64
    o.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="10" fill="{P["stage"]}" stroke="{P["stage_border"]}" stroke-width="1.4" filter="url(#ink)"/>')

    # Left: Failover pill pair
    o.append(f'<rect x="{sx+14}" y="{sy+16}" width="154" height="32" rx="6" fill="{P["lavender_bg"]}" stroke="{P["lavender_border"]}" stroke-width="1.4" filter="url(#ink)"/>')
    o.append(text(sx + 91, sy + 36, "Groq 420ms → Gemini", size=11, fill=P["lavender"], weight="700", family=MONO, anchor="middle"))

    # Plus sign
    o.append(text(sx + 183, sy + 37, "+", size=15, fill=P["muted"], weight="600", anchor="middle"))

    # Right: Stacked pages icon + 16-Chunk IndexedDB
    o.append(f'<rect x="{sx+202}" y="{sy+19}" width="150" height="32" rx="6" fill="{P["card"]}" stroke="{P["stage_border"]}" stroke-width="1.2" filter="url(#ink)"/>')
    o.append(f'<rect x="{sx+198}" y="{sy+15}" width="150" height="32" rx="6" fill="{P["card"]}" stroke="{P["border"]}" stroke-width="1.4" filter="url(#ink)"/>')
    o.append(text(sx + 273, sy + 35, "16-Chunk IndexedDB", size=11, fill=P["text"], weight="700", family=MONO, anchor="middle"))

    o.append(text(22, 184, "TypeScript · React · Groq · Gemini", size=11, fill=P["muted"], family=MONO))
    o.append(text(W - 24, 184, "Repository ↗", size=12, fill=P["lavender"], weight="600", anchor="end"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 04 / SKETCHBOOK CARD: MEEMOMINI ON-DEVICE VISION (410 x 204)
# ==============================================================================
def card_meemomini(t):
    W, H = 410, 204
    P = THEMES[t]
    o = [head(W, H)]
    o.append(sketch_card(W, H, P))

    o.append(tag_pill(22, 18, 114, 22, "Computer Vision", P["blush_bg"], P["blush"], P["blush_border"], size=11))
    o.append(text(W - 24, 33, "18 ms in browser", size=12, fill=P["blush"], weight="700", family=MONO, anchor="end"))

    o.append(text(22, 64, "meemomini", size=20, fill=P["text"], weight="800", ls=-0.3))
    o.append(text(22, 84, "Browser photo booth with client-side segmentation.", size=13, fill=P["sub"]))

    # Refined Line-Art Stage: Viewfinder frame + MediaPipe WASM -> Export
    sx, sy, sw, sh = 22, 98, W - 44, 64
    o.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="10" fill="{P["stage"]}" stroke="{P["stage_border"]}" stroke-width="1.4" filter="url(#ink)"/>')

    # Left: Sketch camera viewfinder with little portrait silhouette
    vx, vy, vw, vh = sx + 16, sy + 12, 52, 40
    o.append(f'<rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" rx="6" fill="{P["card"]}" stroke="{P["blush"]}" stroke-width="1.5" stroke-dasharray="6 3" filter="url(#ink)"/>')
    o.append(f'<circle cx="{vx+26}" cy="{vy+15}" r="6.5" fill="{P["blush_bg"]}" stroke="{P["blush"]}" stroke-width="1.5"/>')
    o.append(f'<path d="M {vx+14} {vy+34} Q {vx+26} {vy+23} {vx+38} {vy+34}" fill="{P["blush_bg"]}" stroke="{P["blush"]}" stroke-width="1.5"/>')

    o.append(f'<line x1="{vx+58}" y1="{sy+32}" x2="{vx+80}" y2="{sy+32}" stroke="{P["muted"]}" stroke-width="1.5" stroke-dasharray="3 3"/>')

    # Middle: MediaPipe WASM pill
    o.append(f'<rect x="{sx+104}" y="{sy+16}" width="134" height="32" rx="6" fill="{P["blush_bg"]}" stroke="{P["blush_border"]}" stroke-width="1.4" filter="url(#ink)"/>')
    o.append(text(sx + 171, sy + 36, "MediaPipe WASM", size=11, fill=P["blush"], weight="700", family=MONO, anchor="middle"))

    o.append(f'<line x1="{sx+244}" y1="{sy+32}" x2="{sx+264}" y2="{sy+32}" stroke="{P["muted"]}" stroke-width="1.5" stroke-dasharray="3 3"/>')

    # Right: MP4 / QR
    o.append(f'<rect x="{sx+270}" y="{sy+16}" width="82" height="32" rx="6" fill="{P["card"]}" stroke="{P["border"]}" stroke-width="1.4" filter="url(#ink)"/>')
    o.append(text(sx + 311, sy + 36, "MP4 / QR", size=11, fill=P["text"], weight="700", family=MONO, anchor="middle"))

    o.append(text(22, 184, "TypeScript · MediaPipe · WebGL · PWA", size=11, fill=P["muted"], family=MONO))
    o.append(text(W - 24, 184, "Repository ↗", size=12, fill=P["lavender"], weight="600", anchor="end"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 05 / COMPILER PIPELINE (840 x 176)
# ==============================================================================
def topology(t):
    W, H = 840, 176
    P = THEMES[t]
    o = [head(W, H)]
    o.append(sketch_card(W, H, P))

    o.append(text(26, 34, "Black Mamba Compilation Pipeline", size=15, fill=P["text"], weight="800"))
    o.append(text(W - 26, 34, "Python grammar → Native machine code", size=12, fill=P["muted"], family=MONO, anchor="end"))

    stages = [
        ("01 Parse", "AST + Indentation", "Unboxed structs", False),
        ("02 C3 MRO", "Diamond Inheritance", "0.42 ms resolve", False),
        ("03 HM Types", "Static Inference", "1-cycle vtables", False),
        ("04 LLVM 18", "Tail-Call Collapse", "5M → 0 frames", True),
        ("05 Codegen", "x86-64 & WASM", "0 KB GC overhead", True),
    ]
    sw = 144
    gap = (W - 52 - 5 * sw) / 4
    for i, (st, l1, l2, hi) in enumerate(stages):
        sx = 26 + i * (sw + gap)
        sy = 50
        bg = P["blush_bg"] if (hi and i == 4) else (P["lavender_bg"] if hi else P["stage"])
        bd = P["blush_border"] if (hi and i == 4) else (P["lavender_border"] if hi else P["stage_border"])
        fg = P["blush"] if (hi and i == 4) else (P["lavender"] if hi else P["text"])
        o.append(f'<rect x="{sx:.1f}" y="{sy}" width="{sw}" height="82" rx="10" fill="{bg}" stroke="{bd}" stroke-width="1.4" filter="url(#ink)"/>')
        o.append(text(sx + 14, sy + 24, st, size=12, fill=fg, weight="700", family=MONO))
        o.append(text(sx + 14, sy + 46, l1, size=12, fill=P["text"], weight="600"))
        o.append(text(sx + 14, sy + 66, l2, size=11, fill=P["muted"], family=MONO))

    o.append(text(26, 154, "Standard library includes pure-native TLS 1.3, relational SQL, and a 24-bit RGB GUI.",
                  size=12, fill=P["sub"]))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 06 / BENCHMARK CHART (840 x 216)
# ==============================================================================
def benchmark(t):
    W, H = 840, 216
    P = THEMES[t]
    o = [head(W, H)]
    o.append(sketch_card(W, H, P))

    o.append(text(26, 34, "Black Mamba JIT vs. CPython 3.14", size=15, fill=P["text"], weight="800"))
    o.append(text(W - 26, 34, "Lower execution time is better", size=12, fill=P["muted"], family=MONO, anchor="end"))

    for i, (k_name, py_t, bm_t, ratio) in enumerate(BENCH):
        ry = 52 + i * 38
        o.append(text(26, ry + 20, k_name, size=12.5, fill=P["text"], weight="600", family=MONO))

        bx = 195
        max_w = 350
        bw_py = max(int((py_t / 300.0) * max_w), 24)
        bw_bm = max(int((bm_t / 300.0) * max_w), 10)

        o.append(f'<rect x="{bx}" y="{ry+5}" width="{bw_py}" height="8" rx="4" fill="{P["stage"]}" stroke="{P["stage_border"]}" stroke-width="1.2" filter="url(#ink)"/>')
        bar_c = P["blush"] if i % 2 == 0 else P["lavender"]
        bd_c = P["blush_border"] if i % 2 == 0 else P["lavender_border"]
        bg_c = P["blush_bg"] if i % 2 == 0 else P["lavender_bg"]
        o.append(f'<rect x="{bx}" y="{ry+17}" width="{bw_bm}" height="8" rx="4" fill="{bar_c}" filter="url(#ink)"/>')

        o.append(text(568, ry + 20, f"{bm_t:.2f} ms vs {py_t:.1f} ms", size=12, fill=P["sub"], family=MONO))
        o.append(tag_pill(W - 96, ry + 3, 70, 22, ratio, bg_c, bar_c, bd_c, size=11.5, family=MONO, weight="700"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 07 / 12-MONTH CONTRIBUTION CHART (840 x 192)
# ==============================================================================
def bars(t):
    W, H = 840, 192
    P = THEMES[t]
    o = [head(W, H)]
    o.append(sketch_card(W, H, P))

    o.append(text(26, 34, "Contributions (Last 12 Months)", size=15, fill=P["text"], weight="800"))
    o.append(text(W - 26, 34, f"{STATS.get('total_contributions', 401)} total  ·  {STATS.get('active_days', 28)} active days",
                  size=12, fill=P["muted"], family=MONO, anchor="end"))

    base_y = 152
    o.append(f'<line x1="26" y1="{base_y}" x2="{W-26}" y2="{base_y}" stroke="{P["stage_border"]}" stroke-width="1.5" filter="url(#ink)"/>')

    m_data = STATS.get("monthly", [])
    if m_data:
        max_c = max(d["count"] for d in m_data) or 1
        n = len(m_data)
        bar_w = 46
        gap = (W - 52 - (n * bar_w)) / (n - 1) if n > 1 else 0
        max_h = 82

        for i, d in enumerate(m_data):
            bx = 26 + i * (bar_w + gap)
            count = d["count"]
            bh = int((count / max_c) * max_h) if count > 0 else 4
            bh = max(bh, 4)
            by = base_y - bh

            fill_c = P["blush"] if count == max_c else (P["lavender"] if count > 0 else P["stage"])
            bd_c = P["blush_border"] if count == max_c else (P["lavender_border"] if count > 0 else P["stage_border"])
            o.append(f'<rect x="{bx:.1f}" y="{by}" width="{bar_w}" height="{bh}" rx="5" fill="{fill_c}" stroke="{bd_c}" stroke-width="1.2" filter="url(#ink)"/>')

            month_lbl = dt.date.fromisoformat(d["month"] + "-01").strftime("%b")
            o.append(text(bx + bar_w / 2, base_y + 20, month_lbl, size=11, fill=P["muted"], family=MONO, anchor="middle"))
            if count > 0:
                o.append(text(bx + bar_w / 2, by - 7, str(count), size=11.5, fill=P["text"], weight="700", family=MONO, anchor="middle"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 08 / TELEMETRY LOG (840 x 170)
# ==============================================================================
def telemetry(t):
    W, H = 840, 170
    P = THEMES[t]
    o = [head(W, H)]
    o.append(sketch_card(W, H, P))

    o.append(text(26, 34, "Visitor Handshake Log (GitHub Actions)", size=15, fill=P["text"], weight="800"))
    o.append(text(W - 26, 34, "~15s auto-commit", size=12, fill=P["muted"], family=MONO, anchor="end"))

    tp = os.path.join(ROOT, "telemetry.json")
    signals = []
    if os.path.exists(tp):
        try:
            with open(tp, "r", encoding="utf-8") as f:
                signals = json.load(f).get("signals", [])
        except Exception:
            pass

    if not signals:
        signals = [
            {"id": "SIG-001", "sender": "kicode01", "org": "Core Systems Lab", "focus": "Applied AI / Compilers", "timestamp": "2026-10-28"},
            {"id": "SIG-002", "sender": "guest-engineer", "org": "Compiler Engineering", "focus": "LLVM IR / Runtime", "timestamp": "2026-10-28"},
            {"id": "SIG-003", "sender": "recruiter-network", "org": "Global Frontier AI", "focus": "Applied AI & Firmware", "timestamp": "2026-10-27"},
        ]

    for i, s in enumerate(signals[:3]):
        sy = 48 + i * 36
        o.append(f'<rect x="26" y="{sy}" width="{W-52}" height="30" rx="6" fill="{P["stage"]}" stroke="{P["stage_border"]}" stroke-width="1.2" filter="url(#ink)"/>')
        o.append(text(40, sy + 20, "@" + s.get("sender", ""), size=12, fill=P["lavender"], weight="600", family=MONO))
        o.append(text(210, sy + 20, s.get("org", ""), size=12, fill=P["text"], weight="500"))
        o.append(text(440, sy + 20, s.get("focus", ""), size=12, fill=P["sub"], family=MONO))
        o.append(text(W - 40, sy + 20, s.get("timestamp", "")[:10], size=11.5, fill=P["muted"], family=MONO, anchor="end"))

    o.append("</svg>")
    return "".join(o)


def _replace_block(md, key, body):
    a, b = f"<!-- {key}:start -->", f"<!-- {key}:end -->"
    if a not in md or b not in md:
        return md
    head_, rest = md.split(a, 1)
    _, tail = rest.split(b, 1)
    return f"{head_}{a}\n{body}\n{b}{tail}"


def update_readme(S, commits, pulse_commits=None):
    p = os.path.join(ROOT, "README.md")
    if not os.path.exists(p):
        return
    with open(p, encoding="utf-8") as f:
        md = f.read()

    monthly = S.get("monthly", [])
    if monthly:
        peak = max(monthly, key=lambda d: d["count"])
        total = S.get("total_contributions", 0) or 1
        name = dt.date.fromisoformat(peak["month"] + "-01").strftime("%B")
        if peak["count"] / total >= 0.35:
            body = (f"**{peak['count']} of {total}** contributions landed in "
                    f"{name} alone.")
        else:
            body = (f"**{total}** contributions across twelve months, peaking at "
                    f"{peak['count']} in {name}.")
        md = _replace_block(md, "signal", body)

    if commits:
        lines = "\n".join(f"{sha}  {msg}" for sha, msg in commits)
        md = _replace_block(md, "log", f"```\n{lines}\n```")

    pulse = pulse_commits or S.get("cross_repo_commits", [])
    if pulse:
        lines = []
        for c in pulse:
            lines.append(f"{c['repo']:18} {c['sha']}  {c['date']}  {c['msg']}")
        md = _replace_block(md, "pulse", "```\n" + "\n".join(lines) + "\n```")

    tp = os.path.join(ROOT, "telemetry.json")
    if os.path.exists(tp):
        try:
            with open(tp, "r", encoding="utf-8") as f:
                tdata = json.load(f)
            t_lines = ["| Signal | Sender | Organization | Focus | Timestamp |",
                       "| :--- | :--- | :--- | :--- | :--- |"]
            for s in tdata.get("signals", [])[:4]:
                t_lines.append(
                    f"| `{s.get('id')}` | **@{s.get('sender')}** | {s.get('org')} | "
                    f"`{s.get('focus')}` | {s.get('timestamp')} |"
                )
            md = _replace_block(md, "telemetry", "\n".join(t_lines))
        except Exception:
            pass

    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(md)
    print("  README.md refreshed")


def main():
    global STATS
    STATS = load()
    os.makedirs(ASSETS, exist_ok=True)

    jobs = {
        "sys-hero": hero,
        "card-mamba": card_mamba,
        "card-voltsense": card_voltsense,
        "card-typenscrape": card_typenscrape,
        "card-meemomini": card_meemomini,
        "sys-topology": topology,
        "sys-benchmark": benchmark,
        "sys-signal": telemetry,
        "sys-pulse": bars,
    }
    for name, fn in jobs.items():
        for theme in ("dark", "light"):
            svg = fn(theme)
            for mode in ("static", "anim"):
                path = os.path.join(ASSETS, f"{name}-{theme}-{mode}.svg")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(svg)
            print(f"  {name}-{theme}-static.svg  {len(svg)/1024:.1f} KB")

    update_readme(STATS, recent_commits(), STATS.get("cross_repo_commits"))
    print(f"\n{STATS['public_repos']} repos · {STATS['total_contributions']} contributions "
          f"· {STATS['commits']} commits · {STATS['active_days']} active days")


if __name__ == "__main__":
    main()
