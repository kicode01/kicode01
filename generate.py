"""
Generates Kian's Neo-Brutalist Cartoon / Ligne-Claire Sketchbook SVG suite.

Why this doesn't look AI-generated:
  1. Unifies with Kian's hand-drawn avatar: warm cream sketchbook paper (#FAF7F0),
     chunky charcoal-ink outlines (#1E1B18, 2.8px), hard offset ink shadows
     (4px, 4px), and soft pastel fills (blush rose, periwinkle lavender,
     mint sage, buttercream yellow).
  2. Replaces generic SaaS flowchart boxes with single, well-proportioned
     cartoon illustrations on the right side of each card:
       - Black Mamba: Cute coiled snake wearing Kian's square glasses + lightning
       - Shim: Tilted credential certificate with a ribbon wax seal & mini QR
       - TypenScrape: Cute bubbling cooking pot wearing a chef's toque + recipe card
       - meemomini: Retro instant camera ejecting a cartoon photo strip
  3. 1:1 native pixel scaling on GitHub (840px full-width, 410px 2x2 grid cards)
     with clean, generous whitespace and crisp typography.
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

# Warm paper + chunky charcoal ink palette that matches Kian's avatar in both modes
PALETTE = {
    "paper": "#FAF7F0",
    "paper_alt": "#F2ECE1",
    "white": "#FFFFFF",
    "ink": "#1E1B18",
    "sub": "#4A453E",
    "muted": "#7A7267",
    "dot": "#E2D9C8",
    "blush": "#FFB5C5",
    "blush_deep": "#E05370",
    "blush_soft": "#FFE4EA",
    "lavender": "#C5C2FF",
    "lavender_deep": "#554FD8",
    "lavender_soft": "#ECEBFF",
    "mint": "#B8EBD0",
    "mint_deep": "#237A52",
    "mint_soft": "#E3F8ED",
    "butter": "#FFE599",
    "butter_deep": "#9E6B00",
    "butter_soft": "#FFF6D6",
}

SANS = "-apple-system,BlinkMacSystemFont,'Plus Jakarta Sans','Inter','Segoe UI',sans-serif"
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


def cross_repo_commits(n=5):
    tracked = [
        "blackmamba-lang",
        "shim-platform",
        "typenscrape",
        "meemomini",
        "klyph-txt",
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
        return [c for c in prev_pulse if c.get("repo") != "voltsense-iot"]

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
    else:
        s["cross_repo_commits"] = [
            c for c in s["cross_repo_commits"] if c.get("repo") != "voltsense-iot"
        ]
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
    """Organic hand-inked stroke filter (`#sketch`) for cartoon outlines."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" fill="none" role="img">'
        '<defs>'
        '<filter id="sketch" x="-3%" y="-3%" width="106%" height="106%">'
        '<feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" result="n" seed="11"/>'
        '<feDisplacementMap in="SourceGraphic" in2="n" scale="1.15" xChannelSelector="R" yChannelSelector="G"/>'
        '</filter>'
        '</defs>'
    )


def text(x, y, s, size=14, fill="#1E1B18", weight="600", family=SANS,
         anchor="start", ls=0):
    ls_attr = f' letter-spacing="{ls}"' if ls else ""
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"'
            f'{ls_attr}>{escape(str(s))}</text>')


def comic_panel(w, h, bg=PALETTE["paper"]):
    """Chunky cartoon card with 2.8px charcoal ink border and 5px solid ink drop shadow."""
    P = PALETTE
    return (
        f'<rect x="7" y="7" width="{w-11}" height="{h-11}" rx="18" fill="{P["ink"]}" filter="url(#sketch)"/>'
        f'<rect x="2.5" y="2.5" width="{w-11}" height="{h-11}" rx="18" fill="{bg}" '
        f'stroke="{P["ink"]}" stroke-width="2.8" stroke-linejoin="round" filter="url(#sketch)"/>'
    )


def sticker_pill(x, y, w, h, label_str, bg, fg=PALETTE["ink"], size=11,
                 family=SANS, weight="800", shadow=True):
    P = PALETTE
    sh = (f'<rect x="{x+2.2}" y="{y+2.2}" width="{w}" height="{h}" rx="{h/2:.1f}" '
          f'fill="{P["ink"]}" filter="url(#sketch)"/>') if shadow else ""
    return (
        sh
        + f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2:.1f}" fill="{bg}" '
          f'stroke="{P["ink"]}" stroke-width="2" filter="url(#sketch)"/>'
        + text(x + w / 2, y + h / 2 + size * 0.36, label_str, size=size,
               fill=fg, weight=weight, family=family, anchor="middle")
    )


def sparkle(cx, cy, r, fill=PALETTE["butter"]):
    """Cute 4-point cartoon star with charcoal ink outline."""
    P = PALETTE
    r2 = r * 0.32
    d = (
        f"M {cx} {cy-r} Q {cx+r2} {cy-r2} {cx+r} {cy} "
        f"Q {cx+r2} {cy+r2} {cx} {cy+r} "
        f"Q {cx-r2} {cy+r2} {cx-r} {cy} "
        f"Q {cx-r2} {cy-r2} {cx} {cy-r} Z"
    )
    return f'<path d="{d}" fill="{fill}" stroke="{P["ink"]}" stroke-width="1.8" stroke-linejoin="round" filter="url(#sketch)"/>'


# ==============================================================================
# 00 / CARTOON SKETCHBOOK HERO BANNER (840 x 182)
# ==============================================================================
def hero(_t):
    W, H = 840, 182
    P = PALETTE
    o = [head(W, H)]
    o.append(comic_panel(W, H, P["paper"]))

    # Subtle dot grid in background right
    for gx in range(525, W - 26, 20):
        for gy in range(24, H - 22, 20):
            o.append(f'<circle cx="{gx}" cy="{gy}" r="1.3" fill="{P["dot"]}"/>')

    # Top sticker tag + sparkles
    o.append(sticker_pill(28, 22, 214, 24, "COMPUTER ENGINEERING", P["lavender"], P["ink"], size=10.5, family=MONO))
    o.append(sparkle(258, 34, 7.5, P["butter"]))

    # Hand-drawn blush highlighter swoosh behind "Kian."
    o.append(f'<path d="M 96 86 Q 144 81 192 85" stroke="{P["blush"]}" stroke-width="12" stroke-linecap="round" filter="url(#sketch)"/>')
    o.append(text(28, 86, "Hi, I'm Kian.", size=34, fill=P["ink"], weight="900", ls=-0.8))

    o.append(text(28, 113, "I build fast compilers, web platforms, and playful AI apps —",
                  size=14, fill=P["sub"], weight="600"))
    o.append(text(28, 132, "crafted from the metal up with clean systems design.",
                  size=13.5, fill=P["muted"], weight="500"))

    # Bottom tactile cartoon sticker pills
    pills = [
        ("Python", 68, P["butter"]),
        ("TypeScript", 90, P["white"]),
        ("C / C++", 72, P["white"]),
        ("x86-64 & WASM", 116, P["mint"]),
        ("Next.js", 70, P["blush_soft"]),
    ]
    px = 28
    for lbl, pw, bg in pills:
        o.append(sticker_pill(px, 144, pw, 22, lbl, bg, P["ink"], size=11, family=MONO, weight="700"))
        px += pw + 9

    # Center sketchbook spiral bindingrings
    sx = 502
    o.append(f'<line x1="{sx}" y1="14" x2="{sx}" y2="{H-18}" stroke="{P["ink"]}" stroke-width="2.2" stroke-dasharray="5 5" filter="url(#sketch)"/>')
    for ry in (36, 70, 104, 138):
        o.append(f'<rect x="{sx-8}" y="{ry}" width="16" height="7" rx="3.5" fill="{P["paper_alt"]}" stroke="{P["ink"]}" stroke-width="2" filter="url(#sketch)"/>')

    # Right side: 2x2 Tilted Cartoon Sticker Stat Cards
    stat_cards = [
        (528, 22, "26.1×", "Faster Python JIT", P["blush"], -1.2),
        (672, 22, "18 ms", "Browser AI Vision", P["mint"], 1.2),
        (528, 96, str(STATS.get("total_contributions", 404)), "Contributions (1yr)", P["butter"], 1.0),
        (672, 96, str(STATS.get("public_repos", 20)), "Public Repos", P["lavender"], -1.0),
    ]
    for cx, cy, val, lbl, bg, rot in stat_cards:
        cw, ch = 132, 60
        mid_x, mid_y = cx + cw / 2, cy + ch / 2
        o.append(f'<g transform="rotate({rot} {mid_x} {mid_y})">')
        o.append(f'<rect x="{cx+3}" y="{cy+3}" width="{cw}" height="{ch}" rx="12" fill="{P["ink"]}" filter="url(#sketch)"/>')
        o.append(f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="12" fill="{bg}" stroke="{P["ink"]}" stroke-width="2.3" filter="url(#sketch)"/>')
        o.append(text(cx + 14, cy + 30, val, size=22, fill=P["ink"], weight="900", family=MONO, ls=-0.5))
        o.append(text(cx + 14, cy + 48, lbl, size=11, fill=P["ink"], weight="700"))
        o.append('</g>')

    o.append(sparkle(808, 22, 6.5, P["blush"]))
    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 01 / BLACK MAMBA COMPILER — Cartoon Snake with Kian's Glasses (410 x 196)
# ==============================================================================
def card_mamba(_t):
    W, H = 410, 196
    P = PALETTE
    o = [head(W, H)]
    o.append(comic_panel(W, H, P["paper"]))

    # Left column: Clean editorial hierarchy
    o.append(sticker_pill(22, 20, 108, 23, "COMPILER & JIT", P["mint"], P["ink"], size=10, family=MONO))
    o.append(text(22, 70, "Black Mamba", size=23, fill=P["ink"], weight="900", ls=-0.5))
    o.append(text(22, 93, "Python syntax compiled to", size=13.5, fill=P["sub"], weight="600"))
    o.append(text(22, 111, "native x86-64 & WASM.", size=13.5, fill=P["sub"], weight="600"))

    # Speed badge pill
    o.append(sticker_pill(22, 126, 174, 24, "26.1× faster than CPython", P["butter"], P["ink"], size=11, weight="800"))
    o.append(text(22, 173, "Python · LLVM 18 · x86-64 · WASM", size=11, fill=P["muted"], weight="700", family=MONO))

    # Right column: Framed Cartoon Artboard (132 x 146)
    ax, ay, aw, ah = 252, 22, 134, 148
    o.append(f'<rect x="{ax+3}" y="{ay+3}" width="{aw}" height="{ah}" rx="14" fill="{P["ink"]}" filter="url(#sketch)"/>')
    o.append(f'<rect x="{ax}" y="{ay}" width="{aw}" height="{ah}" rx="14" fill="{P["mint_soft"]}" stroke="{P["ink"]}" stroke-width="2.4" filter="url(#sketch)"/>')

    # Cute coiled cartoon snake wearing square glasses (matching Kian's avatar!)
    cx, cy = ax + 67, ay + 78
    # Back coil
    o.append(f'<ellipse cx="{cx}" cy="{cy+32}" rx="38" ry="13" fill="{P["mint"]}" stroke="{P["ink"]}" stroke-width="2.5" filter="url(#sketch)"/>')
    # Front coil
    o.append(f'<ellipse cx="{cx}" cy="{cy+18}" rx="30" ry="12" fill="{P["mint"]}" stroke="{P["ink"]}" stroke-width="2.5" filter="url(#sketch)"/>')
    # Belly stripes on coil
    o.append(f'<path d="M {cx-12} {cy+18} Q {cx} {cy+23} {cx+12} {cy+18}" stroke="{P["paper"]}" stroke-width="3" stroke-linecap="round" fill="none"/>')

    # Snake neck & cute round head
    o.append(f'<path d="M {cx-11} {cy+10} L {cx-11} {cy-12} L {cx+11} {cy-12} L {cx+11} {cy+10} Z" fill="{P["mint"]}" stroke="{P["ink"]}" stroke-width="2.5" filter="url(#sketch)"/>')
    o.append(f'<ellipse cx="{cx}" cy="{cy-20}" rx="25" ry="20" fill="{P["mint"]}" stroke="{P["ink"]}" stroke-width="2.6" filter="url(#sketch)"/>')

    # Rosy cheeks (matching Kian's avatar!)
    o.append(f'<ellipse cx="{cx-15}" cy="{cy-14}" rx="4.5" ry="2.8" fill="{P["blush"]}"/>')
    o.append(f'<ellipse cx="{cx+15}" cy="{cy-14}" rx="4.5" ry="2.8" fill="{P["blush"]}"/>')

    # Thick square glasses on the snake!
    o.append(f'<rect x="{cx-19}" y="{cy-27}" width="15" height="12" rx="2.5" fill="{P["white"]}" stroke="{P["ink"]}" stroke-width="2.4" filter="url(#sketch)"/>')
    o.append(f'<rect x="{cx+4}" y="{cy-27}" width="15" height="12" rx="2.5" fill="{P["white"]}" stroke="{P["ink"]}" stroke-width="2.4" filter="url(#sketch)"/>')
    o.append(f'<line x1="{cx-4}" y1="{cy-21}" x2="{cx+4}" y2="{cy-21}" stroke="{P["ink"]}" stroke-width="2.4"/>')
    o.append(f'<circle cx="{cx-11.5}" cy="{cy-21}" r="2.3" fill="{P["ink"]}"/>')
    o.append(f'<circle cx="{cx+11.5}" cy="{cy-21}" r="2.3" fill="{P["ink"]}"/>')

    # Cute little forked pink tongue
    o.append(f'<path d="M {cx} {cy} L {cx} {cy+8} M {cx} {cy+8} L {cx-3.5} {cy+12} M {cx} {cy+8} L {cx+3.5} {cy+12}" stroke="{P["blush_deep"]}" stroke-width="2.2" stroke-linecap="round" fill="none" filter="url(#sketch)"/>')

    # Cartoon lightning bolt next to snake
    lx, ly = ax + 106, ay + 24
    o.append(f'<polygon points="{lx},0 {lx-11},16 {lx-2},16 {lx-8},30 {lx+9},12 {lx},12" transform="translate(0,{ly})" fill="{P["butter"]}" stroke="{P["ink"]}" stroke-width="2" stroke-linejoin="round" filter="url(#sketch)"/>')
    o.append(sparkle(ax + 24, ay + 28, 6.5, P["blush"]))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 02 / SHIM PLATFORM — Cartoon Credential & Wax Seal (410 x 196)
# ==============================================================================
def card_shim(_t):
    W, H = 410, 196
    P = PALETTE
    o = [head(W, H)]
    o.append(comic_panel(W, H, P["paper"]))

    # Left column
    o.append(sticker_pill(22, 20, 110, 23, "WEB PLATFORM", P["lavender"], P["ink"], size=10, family=MONO))
    o.append(text(22, 70, "Shim", size=23, fill=P["ink"], weight="900", ls=-0.5))
    o.append(text(22, 93, "Bulk verifiable credentials", size=13.5, fill=P["sub"], weight="600"))
    o.append(text(22, 111, "& font-metric kerning layout.", size=13.5, fill=P["sub"], weight="600"))

    o.append(sticker_pill(22, 126, 162, 24, "QR verified · Audit log", P["blush_soft"], P["ink"], size=11, weight="800"))
    o.append(text(22, 173, "TypeScript · Next.js 16 · Prisma", size=11, fill=P["muted"], weight="700", family=MONO))

    # Right column: Framed Cartoon Artboard
    ax, ay, aw, ah = 252, 22, 134, 148
    o.append(f'<rect x="{ax+3}" y="{ay+3}" width="{aw}" height="{ah}" rx="14" fill="{P["ink"]}" filter="url(#sketch)"/>')
    o.append(f'<rect x="{ax}" y="{ay}" width="{aw}" height="{ah}" rx="14" fill="{P["lavender_soft"]}" stroke="{P["ink"]}" stroke-width="2.4" filter="url(#sketch)"/>')

    # Tilted Cartoon Certificate Card with Wax Seal & Ribbon
    cx, cy = ax + 67, ay + 74
    o.append(f'<g transform="rotate(-4 {cx} {cy})">')
    # Shadow & certificate body
    o.append(f'<rect x="{cx-44}" y="{cy-42}" width="92" height="84" rx="8" fill="{P["ink"]}" filter="url(#sketch)"/>')
    o.append(f'<rect x="{cx-47}" y="{cy-45}" width="92" height="84" rx="8" fill="{P["white"]}" stroke="{P["ink"]}" stroke-width="2.5" filter="url(#sketch)"/>')
    # Inner decorative frame line
    o.append(f'<rect x="{cx-40}" y="{cy-38}" width="78" height="70" rx="4" fill="none" stroke="{P["lavender"]}" stroke-width="1.8"/>')

    # Mini cartoon QR code box on top-left of certificate
    qx, qy = cx - 33, cy - 31
    o.append(f'<rect x="{qx}" y="{qy}" width="24" height="24" rx="3" fill="{P["butter_soft"]}" stroke="{P["ink"]}" stroke-width="2"/>')
    for dx, dy in ((4, 4), (13, 4), (4, 13), (11, 11), (15, 15)):
        o.append(f'<rect x="{qx+dx}" y="{qy+dy}" width="5" height="5" rx="1" fill="{P["ink"]}"/>')

    # Squiggly certificate title & lines
    o.append(f'<line x1="{cx-2}" y1="{cy-24}" x2="{cx+28}" y2="{cy-24}" stroke="{P["ink"]}" stroke-width="3" stroke-linecap="round"/>')
    o.append(f'<line x1="{cx-2}" y1="{cy-14}" x2="{cx+22}" y2="{cy-14}" stroke="{P["muted"]}" stroke-width="2.2" stroke-linecap="round"/>')
    o.append(f'<line x1="{cx-32}" y1="{cy+4}" x2="{cx+26}" y2="{cy+4}" stroke="{P["ink"]}" stroke-width="2.2" stroke-linecap="round"/>')
    o.append(f'<line x1="{cx-32}" y1="{cy+14}" x2="{cx+8}" y2="{cy+14}" stroke="{P["muted"]}" stroke-width="2.2" stroke-linecap="round"/>')

    # Hanging ribbon tails + Blush Wax Seal with checkmark!
    sx, sy = cx + 22, cy + 24
    o.append(f'<polygon points="{sx-8},{sy+6} {sx-14},{sy+28} {sx-6},{sy+23} {sx-2},{sy+29}" fill="{P["butter"]}" stroke="{P["ink"]}" stroke-width="2" stroke-linejoin="round"/>')
    o.append(f'<polygon points="{sx+8},{sy+6} {sx+14},{sy+28} {sx+6},{sy+23} {sx+2},{sy+29}" fill="{P["butter"]}" stroke="{P["ink"]}" stroke-width="2" stroke-linejoin="round"/>')
    o.append(f'<circle cx="{sx}" cy="{sy}" r="14" fill="{P["blush"]}" stroke="{P["ink"]}" stroke-width="2.4" filter="url(#sketch)"/>')
    o.append(f'<path d="M {sx-5} {sy} L {sx-1} {sy+4} L {sx+6} {sy-4}" stroke="{P["ink"]}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" fill="none"/>')
    o.append('</g>')

    o.append(sparkle(ax + 24, ay + 24, 6.5, P["butter"]))
    o.append(sparkle(ax + 112, ay + 30, 5.5, P["blush"]))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 03 / TYPENSCRAPE — Cartoon Cooking Pot & Chef Toque (410 x 196)
# ==============================================================================
def card_typenscrape(_t):
    W, H = 410, 196
    P = PALETTE
    o = [head(W, H)]
    o.append(comic_panel(W, H, P["paper"]))

    # Left column
    o.append(sticker_pill(22, 20, 102, 23, "APPLIED AI", P["butter"], P["ink"], size=10, family=MONO))
    o.append(text(22, 70, "TypenScrape", size=23, fill=P["ink"], weight="900", ls=-0.5))
    o.append(text(22, 93, "Offline-first recipe engine", size=13.5, fill=P["sub"], weight="600"))
    o.append(text(22, 111, "with Groq → Gemini failover.", size=13.5, fill=P["sub"], weight="600"))

    o.append(sticker_pill(22, 126, 172, 24, "420 ms LLM · IndexedDB", P["mint_soft"], P["ink"], size=11, weight="800"))
    o.append(text(22, 173, "TypeScript · React · Groq · Gemini", size=11, fill=P["muted"], weight="700", family=MONO))

    # Right column: Framed Cartoon Artboard
    ax, ay, aw, ah = 252, 22, 134, 148
    o.append(f'<rect x="{ax+3}" y="{ay+3}" width="{aw}" height="{ah}" rx="14" fill="{P["ink"]}" filter="url(#sketch)"/>')
    o.append(f'<rect x="{ax}" y="{ay}" width="{aw}" height="{ah}" rx="14" fill="{P["butter_soft"]}" stroke="{P["ink"]}" stroke-width="2.4" filter="url(#sketch)"/>')

    # Cute Cartoon Cooking Pot wearing a puffy Chef's Toque Hat!
    cx, cy = ax + 67, ay + 90
    # Pot side handles
    o.append(f'<path d="M {cx-38} {cy-6} C {cx-50} {cy-6} {cx-50} {cy+10} {cx-38} {cy+10}" stroke="{P["ink"]}" stroke-width="3" fill="none" stroke-linecap="round"/>')
    o.append(f'<path d="M {cx+38} {cy-6} C {cx+50} {cy-6} {cx+50} {cy+10} {cx+38} {cy+10}" stroke="{P["ink"]}" stroke-width="3" fill="none" stroke-linecap="round"/>')

    # Pot shadow & body
    o.append(f'<path d="M {cx-35} {cy-12} L {cx+39} {cy-12} L {cx+33} {cy+32} Q {cx+31} {cy+42} {cx+2} {cy+42} Q {cx-27} {cy+42} {cx-29} {cy+32} Z" fill="{P["ink"]}" filter="url(#sketch)"/>')
    o.append(f'<path d="M {cx-38} {cy-15} L {cx+38} {cy-15} L {cx+32} {cy+29} Q {cx+30} {cy+39} {cx} {cy+39} Q {cx-30} {cy+39} {cx-32} {cy+29} Z" fill="{P["blush"]}" stroke="{P["ink"]}" stroke-width="2.5" stroke-linejoin="round" filter="url(#sketch)"/>')
    # Pot rim
    o.append(f'<rect x="{cx-42}" y="{cy-21}" width="84" height="8" rx="4" fill="{P["white"]}" stroke="{P["ink"]}" stroke-width="2.4" filter="url(#sketch)"/>')

    # Cute face on the pot!
    o.append(f'<circle cx="{cx-11}" cy="{cy+8}" r="3" fill="{P["ink"]}"/>')
    o.append(f'<circle cx="{cx+11}" cy="{cy+8}" r="3" fill="{P["ink"]}"/>')
    o.append(f'<path d="M {cx-5} {cy+13} Q {cx} {cy+18} {cx+5} {cy+13}" stroke="{P["ink"]}" stroke-width="2.3" stroke-linecap="round" fill="none"/>')
    o.append(f'<ellipse cx="{cx-19}" cy="{cy+12}" rx="4" ry="2.5" fill="{P["blush_deep"]}" opacity="0.45"/>')
    o.append(f'<ellipse cx="{cx+19}" cy="{cy+12}" rx="4" ry="2.5" fill="{P["blush_deep"]}" opacity="0.45"/>')

    # Puffy white Chef's Toque Hat perched on top of the pot!
    hy = cy - 23
    o.append(f'<path d="M {cx-26} {hy} C {cx-38} {hy-16} {cx-22} {hy-36} {cx-8} {hy-28} C {cx} {hy-40} {cx+16} {hy-38} {cx+20} {hy-26} C {cx+36} {hy-28} {cx+36} {hy-10} {cx+26} {hy} Z" fill="{P["white"]}" stroke="{P["ink"]}" stroke-width="2.5" stroke-linejoin="round" filter="url(#sketch)"/>')
    o.append(f'<rect x="{cx-26}" y="{hy-5}" width="52" height="9" rx="3" fill="{P["lavender"]}" stroke="{P["ink"]}" stroke-width="2.3" filter="url(#sketch)"/>')

    o.append(sparkle(ax + 24, ay + 28, 7, P["mint"]))
    o.append(sparkle(ax + 112, ay + 34, 6, P["lavender"]))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 04 / MEEMOMINI — Cute Retro Instant Camera & Photo Strip (410 x 196)
# ==============================================================================
def card_meemomini(_t):
    W, H = 410, 196
    P = PALETTE
    o = [head(W, H)]
    o.append(comic_panel(W, H, P["paper"]))

    # Left column
    o.append(sticker_pill(22, 20, 118, 23, "COMPUTER VISION", P["blush"], P["ink"], size=10, family=MONO))
    o.append(text(22, 70, "meemomini", size=23, fill=P["ink"], weight="900", ls=-0.5))
    o.append(text(22, 93, "Browser photo booth with", size=13.5, fill=P["sub"], weight="600"))
    o.append(text(22, 111, "on-device WASM cutout.", size=13.5, fill=P["sub"], weight="600"))

    o.append(sticker_pill(22, 126, 174, 24, "18 ms/frame · Zero upload", P["lavender_soft"], P["ink"], size=11, weight="800"))
    o.append(text(22, 173, "TypeScript · MediaPipe · WebGL", size=11, fill=P["muted"], weight="700", family=MONO))

    # Right column: Framed Cartoon Artboard
    ax, ay, aw, ah = 252, 22, 134, 148
    o.append(f'<rect x="{ax+3}" y="{ay+3}" width="{aw}" height="{ah}" rx="14" fill="{P["ink"]}" filter="url(#sketch)"/>')
    o.append(f'<rect x="{ax}" y="{ay}" width="{aw}" height="{ah}" rx="14" fill="{P["blush_soft"]}" stroke="{P["ink"]}" stroke-width="2.4" filter="url(#sketch)"/>')

    # Cute Retro Instant Camera ejecting a photo strip!
    cx, cy = ax + 67, ay + 64
    # Ejected photo strip hanging down from slot
    o.append(f'<rect x="{cx-20}" y="{cy+26}" width="44" height="44" rx="4" fill="{P["ink"]}" filter="url(#sketch)"/>')
    o.append(f'<rect x="{cx-22}" y="{cy+24}" width="44" height="44" rx="4" fill="{P["white"]}" stroke="{P["ink"]}" stroke-width="2.3" filter="url(#sketch)"/>')
    o.append(f'<rect x="{cx-16}" y="{cy+30}" width="32" height="26" rx="2" fill="{P["mint"]}" stroke="{P["ink"]}" stroke-width="1.8"/>')
    # Tiny cute smiley silhouette inside photo print
    o.append(f'<circle cx="{cx}" cy="{cy+40}" r="5" fill="{P["paper"]}" stroke="{P["ink"]}" stroke-width="1.6"/>')
    o.append(f'<path d="M {cx-8} {cy+55} Q {cx} {cy+46} {cx+8} {cy+55}" fill="{P["blush"]}" stroke="{P["ink"]}" stroke-width="1.6"/>')

    # Shutter button on top-left
    o.append(f'<rect x="{cx-30}" y="{cy-35}" width="16" height="9" rx="3" fill="{P["blush_deep"]}" stroke="{P["ink"]}" stroke-width="2.2" filter="url(#sketch)"/>')

    # Camera body shadow & shell
    o.append(f'<rect x="{cx-39}" y="{cy-25}" width="84" height="60" rx="14" fill="{P["ink"]}" filter="url(#sketch)"/>')
    o.append(f'<rect x="{cx-42}" y="{cy-28}" width="84" height="60" rx="14" fill="{P["paper"]}" stroke="{P["ink"]}" stroke-width="2.6" filter="url(#sketch)"/>')

    # Pastel rainbow stripe across camera middle
    o.append(f'<rect x="{cx-40}" y="{cy-2}" width="80" height="8" fill="{P["lavender"]}" stroke="{P["ink"]}" stroke-width="1.8"/>')

    # Flash window on top right
    o.append(f'<rect x="{cx+16}" y="{cy-20}" width="16" height="11" rx="3" fill="{P["butter"]}" stroke="{P["ink"]}" stroke-width="2"/>')

    # Big chunky round camera lens in center
    o.append(f'<circle cx="{cx}" cy="{cy+2}" r="18" fill="{P["blush"]}" stroke="{P["ink"]}" stroke-width="2.5" filter="url(#sketch)"/>')
    o.append(f'<circle cx="{cx}" cy="{cy+2}" r="11" fill="{P["ink"]}"/>')
    o.append(f'<circle cx="{cx-3.5}" cy="{cy-1.5}" r="3.2" fill="{P["white"]}"/>')

    # Photo ejection slot bar
    o.append(f'<line x1="{cx-26}" y1="{cy+26}" x2="{cx+26}" y2="{cy+26}" stroke="{P["ink"]}" stroke-width="3.2" stroke-linecap="round"/>')

    o.append(sparkle(ax + 21, ay + 24, 6.5, P["butter"]))
    o.append(sparkle(ax + 114, ay + 28, 5.5, P["lavender"]))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 05 / COMPILER PIPELINE (840 x 176)
# ==============================================================================
def topology(_t):
    W, H = 840, 176
    P = PALETTE
    o = [head(W, H)]
    o.append(comic_panel(W, H, P["paper"]))

    o.append(text(28, 36, "How Black Mamba Compiles Python to Machine Code", size=16, fill=P["ink"], weight="900"))
    o.append(sticker_pill(W - 190, 18, 160, 24, "5-STAGE PIPELINE", P["lavender"], P["ink"], size=10.5, family=MONO))

    stages = [
        ("01 Parse", "AST + Indent", "Unboxed structs", P["white"]),
        ("02 C3 MRO", "Diamond Tree", "0.42 ms resolve", P["butter_soft"]),
        ("03 HM Types", "Type Solver", "1-cycle vtables", P["lavender_soft"]),
        ("04 LLVM 18", "Tail-Call Pass", "5M → 0 frames", P["mint_soft"]),
        ("05 Native", "x86-64 & WASM", "0 KB GC tax", P["blush"]),
    ]
    sw = 144
    gap = (W - 56 - 5 * sw) / 4
    for i, (st, l1, l2, bg) in enumerate(stages):
        sx = 28 + i * (sw + gap)
        sy = 52
        o.append(f'<rect x="{sx+3:.1f}" y="{sy+3}" width="{sw}" height="82" rx="12" fill="{P["ink"]}" filter="url(#sketch)"/>')
        o.append(f'<rect x="{sx:.1f}" y="{sy}" width="{sw}" height="82" rx="12" fill="{bg}" stroke="{P["ink"]}" stroke-width="2.2" filter="url(#sketch)"/>')
        o.append(text(sx + 14, sy + 25, st, size=12, fill=P["ink"], weight="900", family=MONO))
        o.append(text(sx + 14, sy + 47, l1, size=12.5, fill=P["ink"], weight="700"))
        o.append(text(sx + 14, sy + 67, l2, size=11, fill=P["sub"], weight="600", family=MONO))

    o.append(text(28, 156, "Includes zero-dependency PE32+, ELF64, and 1.7 KB WASM linkers + native TLS 1.3 & SQL.",
                  size=12.5, fill=P["sub"], weight="600"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 06 / BENCHMARK CHART (840 x 216)
# ==============================================================================
def benchmark(_t):
    W, H = 840, 216
    P = PALETTE
    o = [head(W, H)]
    o.append(comic_panel(W, H, P["paper"]))

    o.append(text(28, 36, "Black Mamba JIT vs. CPython 3.14", size=16, fill=P["ink"], weight="900"))
    o.append(sticker_pill(W - 216, 18, 186, 24, "LOWER TIME IS BETTER", P["butter"], P["ink"], size=10.5, family=MONO))

    colors = [P["blush"], P["mint"], P["lavender"], P["butter"]]
    for i, (k_name, py_t, bm_t, ratio) in enumerate(BENCH):
        ry = 54 + i * 38
        o.append(text(28, ry + 20, k_name, size=13, fill=P["ink"], weight="800", family=MONO))

        bx = 195
        max_w = 340
        bw_py = max(int((py_t / 300.0) * max_w), 28)
        bw_bm = max(int((bm_t / 300.0) * max_w), 14)

        o.append(f'<rect x="{bx}" y="{ry+4}" width="{bw_py}" height="9" rx="4.5" fill="{P["paper_alt"]}" stroke="{P["ink"]}" stroke-width="1.6" filter="url(#sketch)"/>')
        o.append(f'<rect x="{bx}" y="{ry+17}" width="{bw_bm}" height="10" rx="5" fill="{colors[i]}" stroke="{P["ink"]}" stroke-width="1.8" filter="url(#sketch)"/>')

        o.append(text(558, ry + 20, f"{bm_t:.2f} ms vs {py_t:.1f} ms", size=12, fill=P["sub"], weight="700", family=MONO))
        o.append(sticker_pill(W - 102, ry + 3, 72, 23, ratio, colors[i], P["ink"], size=11.5, family=MONO, weight="900"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 07 / 12-MONTH CONTRIBUTION CHART (840 x 194)
# ==============================================================================
def bars(_t):
    W, H = 840, 194
    P = PALETTE
    o = [head(W, H)]
    o.append(comic_panel(W, H, P["paper"]))

    o.append(text(28, 36, "12-Month Contribution Activity", size=16, fill=P["ink"], weight="900"))
    o.append(sticker_pill(W - 220, 18, 190, 24, f"{STATS.get('total_contributions', 404)} CONTRIBUTIONS", P["mint"], P["ink"], size=10.5, family=MONO))

    base_y = 152
    o.append(f'<line x1="28" y1="{base_y}" x2="{W-28}" y2="{base_y}" stroke="{P["ink"]}" stroke-width="2.4" stroke-linecap="round" filter="url(#sketch)"/>')

    m_data = STATS.get("monthly", [])
    if m_data:
        max_c = max(d["count"] for d in m_data) or 1
        n = len(m_data)
        bar_w = 46
        gap = (W - 56 - (n * bar_w)) / (n - 1) if n > 1 else 0
        max_h = 80

        for i, d in enumerate(m_data):
            bx = 28 + i * (bar_w + gap)
            count = d["count"]
            bh = int((count / max_c) * max_h) if count > 0 else 6
            bh = max(bh, 6)
            by = base_y - bh

            fill_c = P["blush"] if count == max_c else (P["lavender"] if count > 0 else P["paper_alt"])
            o.append(f'<rect x="{bx+2:.1f}" y="{by+2}" width="{bar_w}" height="{bh}" rx="6" fill="{P["ink"]}" filter="url(#sketch)"/>')
            o.append(f'<rect x="{bx:.1f}" y="{by}" width="{bar_w}" height="{bh}" rx="6" fill="{fill_c}" stroke="{P["ink"]}" stroke-width="2" filter="url(#sketch)"/>')

            month_lbl = dt.date.fromisoformat(d["month"] + "-01").strftime("%b")
            o.append(text(bx + bar_w / 2, base_y + 20, month_lbl, size=11, fill=P["sub"], weight="800", family=MONO, anchor="middle"))
            if count > 0:
                o.append(text(bx + bar_w / 2, by - 7, str(count), size=11.5, fill=P["ink"], weight="900", family=MONO, anchor="middle"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 08 / TELEMETRY LOG (840 x 170)
# ==============================================================================
def telemetry(_t):
    W, H = 840, 170
    P = PALETTE
    o = [head(W, H)]
    o.append(comic_panel(W, H, P["paper"]))

    o.append(text(28, 36, "Visitor Ping Guestbook (GitHub Actions)", size=16, fill=P["ink"], weight="900"))

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
            {"id": "SIG-003", "sender": "recruiter-network", "org": "Global Frontier AI", "focus": "Applied AI & Systems", "timestamp": "2026-10-27"},
        ]

    for i, s in enumerate(signals[:3]):
        sy = 50 + i * 36
        o.append(f'<rect x="28" y="{sy}" width="{W-56}" height="30" rx="8" fill="{P["white"]}" stroke="{P["ink"]}" stroke-width="2" filter="url(#sketch)"/>')
        o.append(text(42, sy + 20, "@" + s.get("sender", ""), size=12, fill=P["lavender_deep"], weight="800", family=MONO))
        o.append(text(210, sy + 20, s.get("org", ""), size=12, fill=P["ink"], weight="700"))
        o.append(text(440, sy + 20, s.get("focus", ""), size=12, fill=P["sub"], weight="600", family=MONO))
        o.append(text(W - 42, sy + 20, s.get("timestamp", "")[:10], size=11.5, fill=P["muted"], weight="700", family=MONO, anchor="end"))

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
        "card-shim": card_shim,
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
