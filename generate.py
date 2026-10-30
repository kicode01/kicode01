"""
Generates hand-drawn, cartoon / comic-notebook SVG illustrations for Kian's profile.

Designed to match Kian's hand-drawn sketch avatar:
  1. Organic hand-inked outlines (SVG fractalNoise displacement filter `#sketch`
     applied to comic panels, speech bubbles, stickers, and cartoon characters).
  2. Tactile comic offset drop-shadows, thick rounded ink strokes, and warm
     sketchbook / pastel sticker colors.
  3. Custom cartoon characters on every card:
     - Hero: Cartoon Kian (matching his avatar: fluffy dark hair, rectangular
       glasses, blush cheeks, beauty mark) waving from his desk with sticky-note stats.
     - Black Mamba: Speedy cartoon snake in nerd glasses zooming past a slow CPython turtle.
     - VoltSense: Cute ESP32 microchip character with a lightning bolt & cloud shield.
     - TypenScrape: Cute robot chef tossing a pancake with Groq & Gemini helper spirits.
     - meemomini: Cute smiling retro camera snapping an instant cutout Polaroid.
  4. True 1:1 pixel scaling on GitHub (840px full-width, 410px half-width cards).
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

# Sketchbook & Cartoon Sticker Palette (Dark & Light)
THEMES = {
    "dark": {
        "card": "#1B1A20",
        "stage": "#24222B",
        "paper": "#FFFDF7",
        "ink": "#231F20",
        "border": "#E8E2D5",
        "stage_border": "#3D3A47",
        "shadow": "#09080C",
        "text": "#FAF6F0",
        "sub": "#D5CFC7",
        "muted": "#9E978E",
        "yellow": "#FFE58F",
        "yellow_ink": "#5C4300",
        "mint": "#B7F0AD",
        "mint_ink": "#134712",
        "pink": "#FFC2D4",
        "pink_ink": "#591227",
        "blue": "#B8E1FF",
        "blue_ink": "#0D3B66",
        "lavender": "#E2CFEA",
        "lavender_ink": "#3C1B4F",
        "orange": "#FF9F68",
        "grid": "#2D2A36",
    },
    "light": {
        "card": "#FFFDF7",
        "stage": "#F7F3E8",
        "paper": "#FFFFFF",
        "ink": "#231F20",
        "border": "#231F20",
        "stage_border": "#D8D0C0",
        "shadow": "#231F20",
        "text": "#231F20",
        "sub": "#4A4540",
        "muted": "#756E65",
        "yellow": "#FFE58F",
        "yellow_ink": "#4D3800",
        "mint": "#C2F5BB",
        "mint_ink": "#134712",
        "pink": "#FFD0DF",
        "pink_ink": "#591227",
        "blue": "#C4E5FF",
        "blue_ink": "#0D3B66",
        "lavender": "#EADAF2",
        "lavender_ink": "#3C1B4F",
        "orange": "#FF9457",
        "grid": "#ECE6D8",
    },
}

COMIC_FONT = "'Comic Neue','Chalkboard SE','Comic Sans MS','Segoe Print',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
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
    """Includes the subtle hand-drawn sketch filter (`#sketch`) for organic ink lines."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" fill="none" role="img">'
        '<defs>'
        '<filter id="sketch" x="-4%" y="-4%" width="108%" height="108%">'
        '<feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="3" result="n" seed="4"/>'
        '<feDisplacementMap in="SourceGraphic" in2="n" scale="1.6" xChannelSelector="R" yChannelSelector="G"/>'
        '</filter>'
        '</defs>'
    )


def text(x, y, s, size=14, fill="#231F20", weight="700", family=COMIC_FONT,
         anchor="start", ls=0, rotate=0):
    ls_attr = f' letter-spacing="{ls}"' if ls else ""
    rot_attr = f' transform="rotate({rotate} {x} {y})"' if rotate else ""
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"'
            f'{ls_attr}{rot_attr}>{escape(str(s))}</text>')


def comic_panel(w, h, P):
    """Draws a comic-book panel with an offset ink shadow and wobbly hand-drawn border."""
    return (
        f'<rect x="7" y="7" width="{w-10}" height="{h-10}" rx="16" fill="{P["shadow"]}" filter="url(#sketch)"/>'
        f'<rect x="3" y="3" width="{w-10}" height="{h-10}" rx="16" fill="{P["card"]}" '
        f'stroke="{P["border"]}" stroke-width="2.5" stroke-linejoin="round" filter="url(#sketch)"/>'
    )


def sticker_badge(x, y, w, h, label_str, bg, fg, ink="#231F20", rotate=0, size=11.5):
    rot = f' transform="rotate({rotate} {x+w/2} {y+h/2})"' if rotate else ""
    return (
        f'<g{rot}>'
        f'<rect x="{x+2}" y="{y+2}" width="{w}" height="{h}" rx="{h/2:.0f}" fill="{ink}" filter="url(#sketch)"/>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2:.0f}" fill="{bg}" '
        f'stroke="{ink}" stroke-width="2" filter="url(#sketch)"/>'
        + text(x + w / 2, y + h / 2 + size * 0.36, label_str, size=size, fill=fg, weight="800", anchor="middle")
        + '</g>'
    )


def sparkle(cx, cy, r, col, ink="#231F20"):
    """Draws a cute 4-point cartoon star/sparkle."""
    r2 = r * 0.35
    pts = (
        f"M {cx} {cy-r} Q {cx+r2} {cy-r2} {cx+r} {cy} "
        f"Q {cx+r2} {cy+r2} {cx} {cy+r} "
        f"Q {cx-r2} {cy+r2} {cx-r} {cy} "
        f"Q {cx-r2} {cy-r2} {cx} {cy-r} Z"
    )
    return f'<path d="{pts}" fill="{col}" stroke="{ink}" stroke-width="1.8" stroke-linejoin="round" filter="url(#sketch)"/>'


# ==============================================================================
# 00 / CARTOON HERO BANNER (840 x 220)
# Features Cartoon Kian (matching his sketch avatar!) + Speech Bubble + Sticky Notes
# ==============================================================================
def hero(t):
    W, H = 840, 220
    P = THEMES[t]
    o = [head(W, H)]
    o.append(comic_panel(W, H, P))

    # Subtle notebook dot/grid lines on the panel
    for gx in range(40, W - 20, 40):
        o.append(f'<circle cx="{gx}" cy="24" r="1" fill="{P["muted"]}" opacity="0.35"/>')
        o.append(f'<circle cx="{gx}" cy="{H-24}" r="1" fill="{P["muted"]}" opacity="0.35"/>')

    # --- LEFT: Cartoon Kian Portrait (matches the crayon/sketch avatar!) ---
    kx, ky = 92, 118
    # White sketch circle backdrop like his avatar
    o.append(f'<circle cx="{kx+3}" cy="{ky+3}" r="64" fill="{P["shadow"]}" filter="url(#sketch)"/>')
    o.append(f'<circle cx="{kx}" cy="{ky}" r="64" fill="#FFFDF9" stroke="#231F20" stroke-width="2.8" filter="url(#sketch)"/>')

    # Hoodie / shoulders at bottom of circle
    o.append(f'<path d="M {kx-36} {ky+54} Q {kx-30} {ky+28} {kx} {ky+28} Q {kx+30} {ky+28} {kx+36} {ky+54}" '
             f'fill="#C8B6FF" stroke="#231F20" stroke-width="2.8" stroke-linecap="round" filter="url(#sketch)"/>')
    # Neck
    o.append(f'<rect x="{kx-10}" y="{ky+18}" width="20" height="16" rx="4" fill="#FCEEE9" stroke="#231F20" stroke-width="2.5" filter="url(#sketch)"/>')

    # Ears
    o.append(f'<circle cx="{kx-36}" cy="{ky+2}" r="10" fill="#FCEEE9" stroke="#231F20" stroke-width="2.6" filter="url(#sketch)"/>')
    o.append(f'<circle cx="{kx+36}" cy="{ky+2}" r="10" fill="#FCEEE9" stroke="#231F20" stroke-width="2.6" filter="url(#sketch)"/>')
    # Pink blush on ears
    o.append(f'<circle cx="{kx-37}" cy="{ky+2}" r="4.5" fill="#F7A8B8" opacity="0.65"/>')
    o.append(f'<circle cx="{kx+37}" cy="{ky+2}" r="4.5" fill="#F7A8B8" opacity="0.65"/>')

    # Face / Head
    o.append(f'<rect x="{kx-34}" y="{ky-34}" width="68" height="58" rx="26" fill="#FCEEE9" stroke="#231F20" stroke-width="2.8" filter="url(#sketch)"/>')

    # Soft pink blush cheeks (signature look from avatar)
    o.append(f'<ellipse cx="{kx-20}" cy="{ky+8}" rx="8.5" ry="5" fill="#F7A8B8" opacity="0.75"/>')
    o.append(f'<ellipse cx="{kx+20}" cy="{ky+8}" rx="8.5" ry="5" fill="#F7A8B8" opacity="0.75"/>')

    # Thick rectangular glasses (exact match to avatar)
    o.append(f'<rect x="{kx-29}" y="{ky-8}" width="24" height="16" rx="3.5" fill="#FFFFFF" fill-opacity="0.5" stroke="#231F20" stroke-width="3.4" filter="url(#sketch)"/>')
    o.append(f'<rect x="{kx+5}" y="{ky-8}" width="24" height="16" rx="3.5" fill="#FFFFFF" fill-opacity="0.5" stroke="#231F20" stroke-width="3.4" filter="url(#sketch)"/>')
    o.append(f'<line x1="{kx-5}" y1="{ky}" x2="{kx+5}" y2="{ky}" stroke="#231F20" stroke-width="3.2"/>')
    o.append(f'<line x1="{kx-34}" y1="{ky-2}" x2="{kx-29}" y2="{ky-2}" stroke="#231F20" stroke-width="3"/>')
    o.append(f'<line x1="{kx+29}" y1="{ky-2}" x2="{kx+34}" y2="{ky-2}" stroke="#231F20" stroke-width="3"/>')

    # Vertical oval cartoon eyes inside glasses
    o.append(f'<ellipse cx="{kx-17}" cy="{ky}" rx="2.8" ry="4.8" fill="#231F20"/>')
    o.append(f'<ellipse cx="{kx+17}" cy="{ky}" rx="2.8" ry="4.8" fill="#231F20"/>')

    # Eyebrows
    o.append(f'<path d="M {kx-24} {ky-13} Q {kx-17} {ky-16} {kx-11} {ky-13}" stroke="#231F20" stroke-width="2.2" stroke-linecap="round"/>')
    o.append(f'<path d="M {kx+11} {ky-13} Q {kx+17} {ky-16} {kx+24} {ky-13}" stroke="#231F20" stroke-width="2.2" stroke-linecap="round"/>')

    # Cute smile + little beauty mark under left eye (just like his avatar!)
    o.append(f'<path d="M {kx-7} {ky+13} Q {kx} {ky+18} {kx+8} {ky+12}" stroke="#231F20" stroke-width="2.4" stroke-linecap="round" fill="none" filter="url(#sketch)"/>')
    o.append(f'<circle cx="{kx+7}" cy="{ky+9}" r="1.3" fill="#231F20"/>')

    # Fluffy charcoal hair with parted bangs (matching avatar)
    hair_path = (
        f"M {kx-36} {ky-6} "
        f"C {kx-42} {ky-38}, {kx-22} {ky-56}, {kx} {ky-55} "
        f"C {kx+24} {ky-56}, {kx+42} {ky-38}, {kx+36} {ky-6} "
        f"L {kx+28} {ky-14} L {kx+22} {ky-6} L {kx+14} {ky-18} "
        f"L {kx+4} {ky-7} L {kx-2} {ky-20} L {kx-10} {ky-7} "
        f"L {kx-20} {ky-16} L {kx-27} {ky-7} Z"
    )
    o.append(f'<path d="{hair_path}" fill="#3B3838" stroke="#231F20" stroke-width="2.8" stroke-linejoin="round" filter="url(#sketch)"/>')
    # Sketchy crayon texture lines in hair
    o.append(f'<path d="M {kx-18} {ky-42} Q {kx} {ky-46} {kx+18} {ky-40}" stroke="#6E6A6A" stroke-width="1.8" stroke-dasharray="3 4" stroke-linecap="round" fill="none"/>')
    o.append(f'<path d="M {kx-24} {ky-30} Q {kx} {ky-34} {kx+24} {ky-28}" stroke="#6E6A6A" stroke-width="1.8" stroke-dasharray="4 5" stroke-linecap="round" fill="none"/>')

    # Cute doodle sparkles around Kian
    o.append(sparkle(34, 52, 9, P["yellow"]))
    o.append(sparkle(154, 48, 8, P["pink"]))

    # --- CENTER: Comic Speech Bubble ---
    bx, by, bw, bh = 178, 26, 368, 166
    # Speech bubble shadow + body with tail pointing to Kian
    tail_shadow = f"M {bx+4} {by+92} L {bx-14} {by+104} L {bx+4} {by+114} Z"
    tail_body = f"M {bx+2} {by+88} L {bx-16} {by+100} L {bx+2} {by+110} Z"
    o.append(f'<rect x="{bx+4}" y="{by+4}" width="{bw}" height="{bh}" rx="20" fill="{P["shadow"]}" filter="url(#sketch)"/>')
    o.append(f'<path d="{tail_shadow}" fill="{P["shadow"]}" filter="url(#sketch)"/>')
    o.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="20" fill="{P["stage"]}" stroke="{P["border"]}" stroke-width="2.5" filter="url(#sketch)"/>')
    o.append(f'<path d="{tail_body}" fill="{P["stage"]}" stroke="{P["border"]}" stroke-width="2.5" stroke-linejoin="round" filter="url(#sketch)"/>')
    # Cover seam of tail
    o.append(f'<line x1="{bx}" y1="{by+89}" x2="{bx}" y2="{by+109}" stroke="{P["stage"]}" stroke-width="4"/>')

    o.append(text(bx + 22, by + 42, "Hey there! I'm Kian!", size=26, fill=P["text"], weight="800"))
    o.append(text(bx + 22, by + 70, "Computer Engineering student who loves", size=14, fill=P["sub"], weight="600", family=SANS))
    o.append(text(bx + 22, by + 91, "building compilers, ESP32 hardware, and", size=14, fill=P["sub"], weight="600", family=SANS))
    o.append(text(bx + 22, by + 112, "fast, friendly AI apps from scratch!", size=14, fill=P["sub"], weight="600", family=SANS))

    # Doodle sticker pills inside speech bubble
    o.append(sticker_badge(bx + 20, by + 126, 68, 24, "Python", P["yellow"], P["yellow_ink"], rotate=-2, size=11))
    o.append(sticker_badge(bx + 96, by + 126, 72, 24, "C / C++", P["mint"], P["mint_ink"], rotate=1.5, size=11))
    o.append(sticker_badge(bx + 176, by + 126, 86, 24, "TypeScript", P["blue"], P["blue_ink"], rotate=-1, size=11))
    o.append(sticker_badge(bx + 270, by + 126, 76, 24, "ESP32", P["pink"], P["pink_ink"], rotate=2, size=11))

    # --- RIGHT: 4 Tilted Cartoon Sticky Notes (2x2 Corkboard Stats) ---
    notes = [
        (568, 26, "26.1×", "Faster JIT!", P["yellow"], P["yellow_ink"], -2.5),
        (698, 28, "18 ms", "WASM Vision", P["mint"], P["mint_ink"], 2.2),
        (570, 116, str(STATS.get("total_contributions", 401)), "Contribs (1yr)", P["pink"], P["pink_ink"], 1.8),
        (696, 116, str(STATS.get("public_repos", 20)), "Public Repos", P["blue"], P["blue_ink"], -2.0),
    ]
    for nx, ny, val, lbl, bg, fg, rot in notes:
        nw, nh = 114, 76
        o.append(f'<g transform="rotate({rot} {nx+nw/2} {ny+nh/2})">')
        o.append(f'<rect x="{nx+3}" y="{ny+4}" width="{nw}" height="{nh}" rx="10" fill="{P["shadow"]}" filter="url(#sketch)"/>')
        o.append(f'<rect x="{nx}" y="{ny}" width="{nw}" height="{nh}" rx="10" fill="{bg}" stroke="#231F20" stroke-width="2.2" filter="url(#sketch)"/>')
        # Little piece of masking tape at top of sticky note
        o.append(f'<rect x="{nx+nw/2-16}" y="{ny-6}" width="32" height="11" rx="2" fill="#FFFDF7" opacity="0.85" stroke="#231F20" stroke-width="1.4" filter="url(#sketch)"/>')
        o.append(text(nx + nw / 2, ny + 41, val, size=24, fill="#231F20", weight="900", family=COMIC_FONT, anchor="middle"))
        o.append(text(nx + nw / 2, ny + 62, lbl, size=11.5, fill=fg, weight="800", family=COMIC_FONT, anchor="middle"))
        o.append('</g>')

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 01 / CARTOON CARD: BLACK MAMBA (Speedy Snake vs. CPython Turtle!)
# ==============================================================================
def card_mamba(t):
    W, H = 410, 224
    P = THEMES[t]
    o = [head(W, H)]
    o.append(comic_panel(W, H, P))

    # Top Sticker Row
    o.append(sticker_badge(22, 18, 94, 24, "COMPILER", P["yellow"], P["yellow_ink"], rotate=-1.5, size=10.5))
    o.append(sticker_badge(W - 134, 18, 110, 24, "26.1× FASTER!", P["orange"], "#231F20", rotate=1.5, size=10.5))

    # Title & Subtitle
    o.append(text(22, 66, "Black Mamba", size=22, fill=P["text"], weight="900"))
    o.append(text(22, 86, "Python syntax compiled to fast x86-64 & WASM!", size=13, fill=P["sub"], weight="600", family=SANS))

    # --- Cartoon Stage: Speedy Snake zooming past Slow Turtle ---
    sx, sy, sw, sh = 22, 98, W - 44, 84
    o.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="12" fill="{P["stage"]}" stroke="{P["stage_border"]}" stroke-width="2" filter="url(#sketch)"/>')

    # Finish line checkered post on right
    fx = sx + sw - 36
    o.append(f'<line x1="{fx}" y1="{sy+10}" x2="{fx}" y2="{sy+sh-10}" stroke="{P["border"]}" stroke-width="2.5" stroke-dasharray="5 5"/>')
    o.append(text(fx - 6, sy + 24, "FINISH!", size=9.5, fill=P["yellow"], weight="900", anchor="end"))

    # Speed lines behind snake
    o.append(f'<line x1="{sx+16}" y1="{sy+28}" x2="{sx+68}" y2="{sy+28}" stroke="{P["orange"]}" stroke-width="2.5" stroke-linecap="round" filter="url(#sketch)"/>')
    o.append(f'<line x1="{sx+26}" y1="{sy+38}" x2="{sx+60}" y2="{sy+38}" stroke="{P["yellow"]}" stroke-width="2" stroke-linecap="round" filter="url(#sketch)"/>')
    o.append(text(sx + 42, sy + 21, "ZOOM!!", size=10, fill=P["orange"], weight="900", anchor="middle", rotate=-4))

    # Cute Speedy Snake Character (at finish line: 11ms!)
    sn_x, sn_y = sx + 170, sy + 34
    o.append(f'<path d="M {sn_x-90} {sn_y+6} Q {sn_x-65} {sn_y-10} {sn_x-40} {sn_y+6} Q {sn_x-15} {sn_y+20} {sn_x+10} {sn_y}" '
             f'stroke="#4ADE80" stroke-width="12" stroke-linecap="round" fill="none" filter="url(#sketch)"/>')
    o.append(f'<path d="M {sn_x-90} {sn_y+6} Q {sn_x-65} {sn_y-10} {sn_x-40} {sn_y+6} Q {sn_x-15} {sn_y+20} {sn_x+10} {sn_y}" '
             f'stroke="#231F20" stroke-width="2.2" stroke-linecap="round" fill="none" filter="url(#sketch)"/>')
    # Snake head
    o.append(f'<ellipse cx="{sn_x+18}" cy="{sn_y-2}" rx="15" ry="12" fill="#4ADE80" stroke="#231F20" stroke-width="2.4" filter="url(#sketch)"/>')
    # Tiny nerd glasses on snake!
    o.append(f'<rect x="{sn_x+15}" y="{sn_y-8}" width="10" height="8" rx="2" fill="#FFFFFF" stroke="#231F20" stroke-width="2"/>')
    o.append(f'<circle cx="{sn_x+20}" cy="{sn_y-4}" r="1.8" fill="#231F20"/>')
    # Forked red tongue
    o.append(f'<path d="M {sn_x+33} {sn_y} L {sn_x+42} {sn_y-3} M {sn_x+38} {sn_y-1} L {sn_x+42} {sn_y+3}" stroke="#FF5C77" stroke-width="2" stroke-linecap="round"/>')
    o.append(sticker_badge(sn_x + 48, sn_y - 14, 92, 22, "JIT: 11 ms!", P["mint"], P["mint_ink"], size=10.5))

    # Cute Slow Turtle at bottom left (CPython: 288ms)
    tu_x, tu_y = sx + 74, sy + 66
    # Legs
    o.append(f'<circle cx="{tu_x-12}" cy="{tu_y+6}" r="4" fill="#86EFAC" stroke="#231F20" stroke-width="2"/>')
    o.append(f'<circle cx="{tu_x+12}" cy="{tu_y+6}" r="4" fill="#86EFAC" stroke="#231F20" stroke-width="2"/>')
    # Shell
    o.append(f'<path d="M {tu_x-18} {tu_y+4} A 18 15 0 0 1 {tu_x+18} {tu_y+4} Z" fill="#60A5FA" stroke="#231F20" stroke-width="2.2" filter="url(#sketch)"/>')
    # Head
    o.append(f'<circle cx="{tu_x+23}" cy="{tu_y}" r="6.5" fill="#86EFAC" stroke="#231F20" stroke-width="2" filter="url(#sketch)"/>')
    o.append(f'<circle cx="{tu_x+25}" cy="{tu_y-1}" r="1.5" fill="#231F20"/>')
    o.append(text(tu_x + 40, tu_y + 4, "CPython: 288 ms... 💦", size=11, fill=P["muted"], weight="700"))

    # Footer
    o.append(text(22, 204, "Python · x86-64 · LLVM · WASM", size=11, fill=P["muted"], weight="600", family=MONO))
    o.append(text(W - 22, 204, "Open repo ➔", size=12.5, fill=P["yellow"] if t == "dark" else P["ink"], weight="900", anchor="end"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 02 / CARTOON CARD: VOLTSENSE (Cute ESP32 Chip Buddy & Cloud Shield!)
# ==============================================================================
def card_voltsense(t):
    W, H = 410, 224
    P = THEMES[t]
    o = [head(W, H)]
    o.append(comic_panel(W, H, P))

    o.append(sticker_badge(22, 18, 118, 24, "FIRMWARE & IOT", P["mint"], P["mint_ink"], rotate=-1.2, size=10.5))
    o.append(sticker_badge(W - 140, 18, 116, 24, "0 KEYS ON CHIP!", P["yellow"], P["yellow_ink"], rotate=1.5, size=10.5))

    o.append(text(22, 66, "VoltSense", size=22, fill=P["text"], weight="900"))
    o.append(text(22, 86, "ESP32 power monitor & safe remote relay console!", size=13, fill=P["sub"], weight="600", family=SANS))

    # --- Cartoon Stage: ESP32 Chip Character -> Cloud Guard -> Phone ---
    sx, sy, sw, sh = 22, 98, W - 44, 84
    o.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="12" fill="{P["stage"]}" stroke="{P["stage_border"]}" stroke-width="2" filter="url(#sketch)"/>')

    # 1. Cute ESP32 Microchip Buddy on Left
    cx, cy = sx + 62, sy + 40
    # Little IC metal pins sticking out left & right
    for py_off in (-12, 0, 12):
        o.append(f'<rect x="{cx-32}" y="{cy+py_off-3}" width="10" height="6" rx="2" fill="#E2E8F0" stroke="#231F20" stroke-width="1.8"/>')
        o.append(f'<rect x="{cx+22}" y="{cy+py_off-3}" width="10" height="6" rx="2" fill="#E2E8F0" stroke="#231F20" stroke-width="1.8"/>')
    # Chip body
    o.append(f'<rect x="{cx-24}" y="{cy-22}" width="48" height="44" rx="8" fill="#4ADE80" stroke="#231F20" stroke-width="2.4" filter="url(#sketch)"/>')
    # Cute face on chip
    o.append(f'<circle cx="{cx-8}" cy="{cy-4}" r="2.5" fill="#231F20"/>')
    o.append(f'<circle cx="{cx+8}" cy="{cy-4}" r="2.5" fill="#231F20"/>')
    o.append(f'<ellipse cx="{cx-13}" cy="{cy+2}" rx="3.5" ry="2" fill="#F7A8B8"/>')
    o.append(f'<ellipse cx="{cx+13}" cy="{cy+2}" rx="3.5" ry="2" fill="#F7A8B8"/>')
    o.append(f'<path d="M {cx-5} {cy+4} Q {cx} {cy+9} {cx+5} {cy+4}" stroke="#231F20" stroke-width="2" stroke-linecap="round" fill="none"/>')
    o.append(text(cx, sy + 76, "ESP32 C++", size=10, fill=P["text"], weight="800", anchor="middle"))

    # Doodle arrow 1
    o.append(f'<path d="M {cx+38} {cy} Q {cx+60} {cy-10} {cx+80} {cy}" stroke="{P["yellow"]}" stroke-width="2.5" stroke-dasharray="4 4" fill="none"/>')

    # 2. Cute Smiling Cloud Buddy in Middle (Vercel Vault)
    cl_x, cl_y = sx + 186, sy + 40
    cloud_d = (
        f"M {cl_x-28} {cl_y+12} "
        f"A 14 14 0 0 1 {cl_x-18} {cl_y-12} "
        f"A 18 18 0 0 1 {cl_x+16} {cl_y-14} "
        f"A 14 14 0 0 1 {cl_x+28} {cl_y+12} Z"
    )
    o.append(f'<path d="{cloud_d}" fill="#FFFDF7" stroke="#231F20" stroke-width="2.4" stroke-linejoin="round" filter="url(#sketch)"/>')
    o.append(f'<circle cx="{cl_x-7}" cy="{cl_y-1}" r="2.2" fill="#231F20"/>')
    o.append(f'<circle cx="{cl_x+7}" cy="{cl_y-1}" r="2.2" fill="#231F20"/>')
    o.append(f'<path d="M {cl_x-4} {cl_y+5} Q {cl_x} {cl_y+8} {cl_x+4} {cl_y+5}" stroke="#231F20" stroke-width="2" stroke-linecap="round" fill="none"/>')
    o.append(text(cl_x, sy + 76, "Vercel Vault", size=10, fill=P["text"], weight="800", anchor="middle"))

    # Doodle arrow 2
    o.append(f'<path d="M {cl_x+36} {cy} Q {cl_x+58} {cy-10} {cl_x+78} {cy}" stroke="{P["mint"]}" stroke-width="2.5" stroke-dasharray="4 4" fill="none"/>')

    # 3. Cute Phone Character on Right (React PWA)
    ph_x, ph_y = sx + 306, sy + 38
    o.append(f'<rect x="{ph_x-20}" y="{ph_y-22}" width="40" height="46" rx="8" fill="{P["blue"]}" stroke="#231F20" stroke-width="2.4" filter="url(#sketch)"/>')
    o.append(f'<rect x="{ph_x-14}" y="{ph_y-14}" width="28" height="28" rx="4" fill="#FFFDF7" stroke="#231F20" stroke-width="1.6"/>')
    # Lightning bolt icon inside phone screen
    o.append(f'<polygon points="{ph_x+2},{ph_y-10} {ph_x-6},{ph_y+1} {ph_x},{ph_y+1} {ph_x-2},{ph_y+10} {ph_x+6},{ph_y-1} {ph_x},{ph_y-1}" fill="#F59E0B" stroke="#231F20" stroke-width="1.2"/>')
    o.append(text(ph_x, sy + 76, "React PWA", size=10, fill=P["text"], weight="800", anchor="middle"))

    o.append(text(22, 204, "C++ · ESP32 · Firebase · React 19", size=11, fill=P["muted"], weight="600", family=MONO))
    o.append(text(W - 22, 204, "Try live app ➔", size=12.5, fill=P["mint"] if t == "dark" else P["ink"], weight="900", anchor="end"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 03 / CARTOON CARD: TYPENSCRAPE (Cute Robot Chef & Recipe Jars!)
# ==============================================================================
def card_typenscrape(t):
    W, H = 410, 224
    P = THEMES[t]
    o = [head(W, H)]
    o.append(comic_panel(W, H, P))

    o.append(sticker_badge(22, 18, 98, 24, "APPLIED AI", P["lavender"], P["lavender_ink"], rotate=-1.5, size=10.5))
    o.append(sticker_badge(W - 140, 18, 116, 24, "OFFLINE-FIRST!", P["blue"], P["blue_ink"], rotate=1.5, size=10.5))

    o.append(text(22, 66, "TypenScrape", size=22, fill=P["text"], weight="900"))
    o.append(text(22, 86, "AI recipe chef with Groq → Gemini backup & local DB!", size=13, fill=P["sub"], weight="600", family=SANS))

    # --- Cartoon Stage: Robot Chef + Groq/Gemini + 16 Chunk Jars ---
    sx, sy, sw, sh = 22, 98, W - 44, 84
    o.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="12" fill="{P["stage"]}" stroke="{P["stage_border"]}" stroke-width="2" filter="url(#sketch)"/>')

    # Cute Robot Chef on Left
    rx, ry = sx + 58, sy + 48
    # Puffy white chef hat!
    hat_d = (
        f"M {rx-18} {ry-18} "
        f"C {rx-26} {ry-34}, {rx-8} {ry-42}, {rx} {ry-36} "
        f"C {rx+8} {ry-42}, {rx+26} {ry-34}, {rx+18} {ry-18} Z"
    )
    o.append(f'<path d="{hat_d}" fill="#FFFDF7" stroke="#231F20" stroke-width="2.2" stroke-linejoin="round" filter="url(#sketch)"/>')
    # Robot head
    o.append(f'<rect x="{rx-20}" y="{ry-18}" width="40" height="32" rx="9" fill="{P["lavender"]}" stroke="#231F20" stroke-width="2.4" filter="url(#sketch)"/>')
    # Happy visor eyes
    o.append(f'<circle cx="{rx-8}" cy="{ry-3}" r="3" fill="#231F20"/>')
    o.append(f'<circle cx="{rx+8}" cy="{ry-3}" r="3" fill="#231F20"/>')
    o.append(f'<ellipse cx="{rx-13}" cy="{ry+3}" rx="3.5" ry="2" fill="#F7A8B8"/>')
    o.append(f'<ellipse cx="{rx+13}" cy="{ry+3}" rx="3.5" ry="2" fill="#F7A8B8"/>')
    o.append(f'<path d="M {rx-5} {ry+4} Q {rx} {ry+9} {rx+5} {ry+4}" stroke="#231F20" stroke-width="2" stroke-linecap="round" fill="none"/>')
    o.append(text(rx, sy + 76, "AI Chef", size=10, fill=P["text"], weight="800", anchor="middle"))

    # Center: Groq -> Gemini Tag-Team Bubbles
    o.append(sticker_badge(sx + 112, sy + 16, 118, 24, "1. Groq (420ms!)", P["yellow"], P["yellow_ink"], rotate=-1, size=10))
    o.append(sticker_badge(sx + 112, sy + 46, 118, 24, "2. Gemini Backup", P["pink"], P["pink_ink"], rotate=1, size=10))

    # Right: Cute Cookie / Data Jar ("16 Chunks DB")
    jx, jy = sx + 302, sy + 42
    o.append(f'<rect x="{jx-28}" y="{jy-16}" width="56" height="38" rx="8" fill="{P["blue"]}" stroke="#231F20" stroke-width="2.2" filter="url(#sketch)"/>')
    o.append(f'<rect x="{jx-20}" y="{jy-23}" width="40" height="8" rx="3" fill="{P["orange"]}" stroke="#231F20" stroke-width="2" filter="url(#sketch)"/>')
    o.append(text(jx, jy + 7, "16-Chunk", size=10, fill="#231F20", weight="900", anchor="middle"))
    o.append(text(jx, sy + 76, "IndexedDB", size=10, fill=P["text"], weight="800", anchor="middle"))

    o.append(text(22, 204, "TypeScript · React · Groq · Gemini", size=11, fill=P["muted"], weight="600", family=MONO))
    o.append(text(W - 22, 204, "Open repo ➔", size=12.5, fill=P["lavender"] if t == "dark" else P["ink"], weight="900", anchor="end"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 04 / CARTOON CARD: MEEMOMINI (Cute Smiling Camera & Polaroid!)
# ==============================================================================
def card_meemomini(t):
    W, H = 410, 224
    P = THEMES[t]
    o = [head(W, H)]
    o.append(comic_panel(W, H, P))

    o.append(sticker_badge(22, 18, 106, 24, "AI VISION", P["pink"], P["pink_ink"], rotate=-1.5, size=10.5))
    o.append(sticker_badge(W - 144, 18, 120, 24, "18ms IN BROWSER", P["mint"], P["mint_ink"], rotate=1.5, size=10.5))

    o.append(text(22, 66, "meemomini", size=22, fill=P["text"], weight="900"))
    o.append(text(22, 86, "Web photo booth with on-device background cutout!", size=13, fill=P["sub"], weight="600", family=SANS))

    # --- Cartoon Stage: Retro Camera Character -> SNAP! -> Polaroid Photo ---
    sx, sy, sw, sh = 22, 98, W - 44, 84
    o.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" rx="12" fill="{P["stage"]}" stroke="{P["stage_border"]}" stroke-width="2" filter="url(#sketch)"/>')

    # Cute Retro Camera on Left
    cam_x, cam_y = sx + 66, sy + 44
    # Top flash button
    o.append(f'<rect x="{cam_x-18}" y="{cam_y-28}" width="16" height="8" rx="3" fill="{P["yellow"]}" stroke="#231F20" stroke-width="2" filter="url(#sketch)"/>')
    # Camera body
    o.append(f'<rect x="{cam_x-30}" y="{cam_y-20}" width="60" height="42" rx="10" fill="{P["pink"]}" stroke="#231F20" stroke-width="2.4" filter="url(#sketch)"/>')
    # Big Lens center
    o.append(f'<circle cx="{cam_x}" cy="{cam_y+1}" r="14" fill="#FFFDF7" stroke="#231F20" stroke-width="2.4" filter="url(#sketch)"/>')
    o.append(f'<circle cx="{cam_x}" cy="{cam_y+1}" r="7" fill="#231F20"/>')
    o.append(f'<circle cx="{cam_x-2}" cy="{cam_y-1}" r="2.2" fill="#FFFFFF"/>')

    # Flash sparkle + "SNAP!"
    o.append(sparkle(cam_x + 42, cam_y - 16, 10, P["yellow"]))
    o.append(text(cam_x + 76, cam_y + 4, "WASM Cutout!", size=11.5, fill=P["yellow"] if t == "dark" else P["ink"], weight="900", rotate=-4))
    o.append(text(cam_x + 76, cam_y + 20, "(0 server uploads)", size=10, fill=P["muted"], weight="700"))

    # Cute Tilted Polaroid Photo on Right
    px, py = sx + 292, sy + 42
    o.append(f'<g transform="rotate(6 {px} {py})">')
    o.append(f'<rect x="{px-28}" y="{py-28}" width="56" height="60" rx="5" fill="#FFFDF7" stroke="#231F20" stroke-width="2.2" filter="url(#sketch)"/>')
    o.append(f'<rect x="{px-21}" y="{py-22}" width="42" height="36" rx="3" fill="{P["blue"]}" stroke="#231F20" stroke-width="1.8"/>')
    # Tiny happy person cutout inside Polaroid
    o.append(f'<circle cx="{px}" cy="{py-8}" r="7" fill="#FCEEE9" stroke="#231F20" stroke-width="1.8"/>')
    o.append(f'<path d="M {px-11} {py+12} Q {px} {py+1} {px+11} {py+12}" fill="{P["mint"]}" stroke="#231F20" stroke-width="1.8"/>')
    o.append('</g>')

    o.append(text(22, 204, "TypeScript · MediaPipe · WebGL · PWA", size=11, fill=P["muted"], weight="600", family=MONO))
    o.append(text(W - 22, 204, "Open repo ➔", size=12.5, fill=P["pink"] if t == "dark" else P["ink"], weight="900", anchor="end"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 05 / CARTOON COMPILER PIPELINE (840 x 180)
# ==============================================================================
def topology(t):
    W, H = 840, 180
    P = THEMES[t]
    o = [head(W, H)]
    o.append(comic_panel(W, H, P))

    o.append(text(28, 36, "How Black Mamba Compiles Python to Machine Code", size=16, fill=P["text"], weight="900"))
    o.append(sticker_badge(W - 180, 16, 152, 24, "0 KB GC OVERHEAD!", P["mint"], P["mint_ink"], rotate=1, size=10.5))

    stages = [
        ("1. Parse", "AST + Structs", P["yellow"], P["yellow_ink"]),
        ("2. C3 MRO", "0.42ms Diamond", P["pink"], P["pink_ink"]),
        ("3. HM Types", "Static Solver", P["blue"], P["blue_ink"]),
        ("4. LLVM 18", "5M → 0 Frames", P["lavender"], P["lavender_ink"]),
        ("5. Native!", "x86-64 & WASM", P["mint"], P["mint_ink"]),
    ]
    sw = 138
    gap = (W - 56 - 5 * sw) / 4
    for i, (st, sub, bg, fg) in enumerate(stages):
        sx = 28 + i * (sw + gap)
        sy = 54
        o.append(f'<rect x="{sx+3:.1f}" y="{sy+3}" width="{sw}" height="74" rx="12" fill="{P["shadow"]}" filter="url(#sketch)"/>')
        o.append(f'<rect x="{sx:.1f}" y="{sy}" width="{sw}" height="74" rx="12" fill="{bg}" stroke="#231F20" stroke-width="2.2" filter="url(#sketch)"/>')
        o.append(text(sx + sw / 2, sy + 32, st, size=14, fill="#231F20", weight="900", anchor="middle"))
        o.append(text(sx + sw / 2, sy + 54, sub, size=11.5, fill=fg, weight="800", anchor="middle"))

    o.append(text(28, 156, "Plus pure-native standard libraries for TLS 1.3, relational SQL, and a 24-bit RGB GUI!",
                  size=12.5, fill=P["sub"], weight="700"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 06 / CARTOON BENCHMARK CHART (840 x 220)
# ==============================================================================
def benchmark(t):
    W, H = 840, 220
    P = THEMES[t]
    o = [head(W, H)]
    o.append(comic_panel(W, H, P))

    o.append(text(28, 36, "Speed Test: Black Mamba JIT vs. CPython 3.14", size=16, fill=P["text"], weight="900"))
    o.append(text(W - 28, 36, "Shorter bar = faster!", size=12.5, fill=P["muted"], weight="800", anchor="end"))

    colors = [P["yellow"], P["mint"], P["pink"], P["blue"]]
    for i, (k_name, py_t, bm_t, ratio) in enumerate(BENCH):
        ry = 52 + i * 38
        o.append(text(28, ry + 21, k_name, size=13.5, fill=P["text"], weight="800", family=MONO))

        bx = 195
        max_w = 340
        bw_py = max(int((py_t / 300.0) * max_w), 28)
        bw_bm = max(int((bm_t / 300.0) * max_w), 14)

        # CPython slow bar
        o.append(f'<rect x="{bx}" y="{ry+4}" width="{bw_py}" height="10" rx="5" fill="{P["stage"]}" stroke="{P["stage_border"]}" stroke-width="1.5" filter="url(#sketch)"/>')
        # Black Mamba fast cartoon bar
        o.append(f'<rect x="{bx}" y="{ry+17}" width="{bw_bm}" height="12" rx="6" fill="{colors[i]}" stroke="#231F20" stroke-width="2" filter="url(#sketch)"/>')

        o.append(text(555, ry + 21, f"{bm_t:.1f}ms vs {py_t:.0f}ms", size=12.5, fill=P["sub"], weight="700", family=MONO))
        o.append(sticker_badge(W - 108, ry + 2, 78, 24, ratio, colors[i], "#231F20", rotate=(-1 if i % 2 else 1), size=11.5))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 07 / CARTOON 12-MONTH ACTIVITY CHART (840 x 196)
# ==============================================================================
def bars(t):
    W, H = 840, 196
    P = THEMES[t]
    o = [head(W, H)]
    o.append(comic_panel(W, H, P))

    o.append(text(28, 36, "My Coding Activity (Last 12 Months)", size=16, fill=P["text"], weight="900"))
    o.append(sticker_badge(W - 210, 16, 180, 24, f"{STATS.get('total_contributions', 401)} CONTRIBUTIONS!", P["yellow"], P["yellow_ink"], rotate=1, size=10.5))

    base_y = 154
    o.append(f'<line x1="28" y1="{base_y}" x2="{W-28}" y2="{base_y}" stroke="{P["border"]}" stroke-width="2" stroke-linecap="round" filter="url(#sketch)"/>')

    m_data = STATS.get("monthly", [])
    palette = [P["blue"], P["mint"], P["pink"], P["lavender"], P["yellow"]]
    if m_data:
        max_c = max(d["count"] for d in m_data) or 1
        n = len(m_data)
        bar_w = 46
        gap = (W - 56 - (n * bar_w)) / (n - 1) if n > 1 else 0
        max_h = 82

        for i, d in enumerate(m_data):
            bx = 28 + i * (bar_w + gap)
            count = d["count"]
            bh = int((count / max_c) * max_h) if count > 0 else 6
            bh = max(bh, 6)
            by = base_y - bh

            fill_c = P["yellow"] if count == max_c else (palette[i % len(palette)] if count > 0 else P["stage"])
            o.append(f'<rect x="{bx:.1f}" y="{by}" width="{bar_w}" height="{bh}" rx="6" fill="{fill_c}" stroke="#231F20" stroke-width="2" filter="url(#sketch)"/>')

            month_lbl = dt.date.fromisoformat(d["month"] + "-01").strftime("%b")
            o.append(text(bx + bar_w / 2, base_y + 20, month_lbl, size=11.5, fill=P["muted"], weight="800", anchor="middle"))
            if count > 0:
                o.append(text(bx + bar_w / 2, by - 7, str(count), size=12, fill=P["text"], weight="900", anchor="middle"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 08 / CARTOON GUESTBOOK / TELEMETRY LOG (840 x 176)
# ==============================================================================
def telemetry(t):
    W, H = 840, 176
    P = THEMES[t]
    o = [head(W, H)]
    o.append(comic_panel(W, H, P))

    o.append(text(28, 36, "Visitor Ping Guestbook (GitHub Actions)", size=16, fill=P["text"], weight="900"))
    o.append(sticker_badge(W - 168, 16, 140, 24, "LIVE AUTO-COMMIT", P["mint"], P["mint_ink"], rotate=-1, size=10))

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
        sy = 50 + i * 36
        o.append(f'<rect x="28" y="{sy}" width="{W-56}" height="30" rx="8" fill="{P["stage"]}" stroke="{P["stage_border"]}" stroke-width="1.8" filter="url(#sketch)"/>')
        o.append(text(42, sy + 20, "@" + s.get("sender", ""), size=12.5, fill=P["yellow"] if t == "dark" else P["ink"], weight="800", family=MONO))
        o.append(text(215, sy + 20, s.get("org", ""), size=12.5, fill=P["text"], weight="700"))
        o.append(text(445, sy + 20, s.get("focus", ""), size=12, fill=P["sub"], weight="600", family=SANS))
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
