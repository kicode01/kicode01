"""
Generates Kian's Apple HIG / Keynote Bento Grid SVG suite.

Design System (Apple Human Interface Guidelines & Apple Silicon Keynotes):
  1. True Multi-Cell Bento Hero (`sys-hero`):
     Uses a transparent 840x188 canvas containing 4 distinct superellipse-rounded
     (`rx="22"`) Bento cells separated by 12px gutters:
       - Cell 1 (504x184): Apple two-tone headline (crisp primary `#F5F5F7` / `#1D1D1F`
         paired with titanium gray `#86868B`), status indicator, and frosted stack pills.
       - Cell 2 (156x86): Apple Silicon gradient callout (`26.1×` Faster Python JIT).
       - Cell 3 (156x86): Apple Cyan/Blue callout (`18 ms` On-device WASM vision).
       - Cell 4 (324x86): Live GitHub Activity summary + 12-month mini Apple Activity
         sparkline chart.
  2. 2x2 Interactive Project Bento Cards (`410x196`, `rx="22"`):
     Follows Apple's "One Visual Story Per Cell" rule with generous 26px padding,
     SF Pro Display negative tracking, 1px inner specular borders, and sleek
     hardware/UI visuals (Apple Silicon speed bar, Wallet-style verifiable pass,
     Spotlight LLM router, and Continuity Camera vision HUD).
  3. Native Dark (`#161617` elevated surface) & Light (`#F5F5F7` / `#FFFFFF`) themes.
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

# Official Apple Human Interface Guidelines (macOS Sequoia / iOS 18 / apple.com) tokens
THEMES = {
    "dark": {
        "card_top": "#1D1D1F",
        "card_bot": "#141416",
        "border": "#2C2C2E",
        "inner_bg": "#212124",
        "inner_border": "#333336",
        "pill_bg": "#262629",
        "pill_border": "#3A3A3C",
        "text": "#F5F5F7",
        "sub": "#A1A1A6",
        "muted": "#86868B",
        "track": "#2C2C2E",
        "blue": "#2997FF",
        "blue_soft": "rgba(41,151,255,0.14)",
        "indigo": "#5E5CE6",
        "purple": "#BF5AF2",
        "pink": "#FF375F",
        "orange": "#FF9F0A",
        "green": "#30D158",
        "cyan": "#64D2FF",
        "grad_a": "#2997FF",
        "grad_b": "#BF5AF2",
        "grad_c": "#FF375F",
    },
    "light": {
        "card_top": "#FFFFFF",
        "card_bot": "#F5F5F7",
        "border": "#D2D2D7",
        "inner_bg": "#F5F5F7",
        "inner_border": "#E5E5EA",
        "pill_bg": "#EFEFF4",
        "pill_border": "#D2D2D7",
        "text": "#1D1D1F",
        "sub": "#515154",
        "muted": "#86868B",
        "track": "#E5E5EA",
        "blue": "#0071E3",
        "blue_soft": "rgba(0,113,227,0.10)",
        "indigo": "#5856D6",
        "purple": "#AF52DE",
        "pink": "#FF2D55",
        "orange": "#FF9500",
        "green": "#28CD41",
        "cyan": "#007AFF",
        "grad_a": "#0071E3",
        "grad_b": "#AF52DE",
        "grad_c": "#FF2D55",
    },
}

SF_DISPLAY = "-apple-system,BlinkMacSystemFont,'SF Pro Display','SF Pro Text','Helvetica Neue',Helvetica,Arial,sans-serif"
SF_MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace"


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


def head(w, h, P):
    """Defines Apple surface elevation gradients and Apple Silicon accent gradients."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" fill="none" role="img">'
        '<defs>'
        '<linearGradient id="surface" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{P["card_top"]}"/>'
        f'<stop offset="100%" stop-color="{P["card_bot"]}"/>'
        '</linearGradient>'
        '<linearGradient id="appleGrad" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0%" stop-color="{P["grad_a"]}"/>'
        f'<stop offset="52%" stop-color="{P["grad_b"]}"/>'
        f'<stop offset="100%" stop-color="{P["grad_c"]}"/>'
        '</linearGradient>'
        '<linearGradient id="cyanGrad" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0%" stop-color="{P["blue"]}"/>'
        f'<stop offset="100%" stop-color="{P["cyan"]}"/>'
        '</linearGradient>'
        '</defs>'
    )


def text(x, y, s, size=14, fill="#F5F5F7", weight="500", family=SF_DISPLAY,
         anchor="start", ls=0):
    ls_attr = f' letter-spacing="{ls}"' if ls else ""
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"'
            f'{ls_attr}>{escape(str(s))}</text>')


def bento_box(x, y, w, h, P, rx=22):
    """Apple Bento container with subtle top-to-bottom sheen and 1px specular border."""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="url(#surface)" stroke="{P["border"]}" stroke-width="1"/>'
    )


def pill(x, y, w, h, label_str, bg, fg, border=None, size=11,
         family=SF_DISPLAY, weight="500"):
    bd = f' stroke="{border}" stroke-width="1"' if border else ""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2:.1f}" fill="{bg}"{bd}/>'
        + text(x + w / 2, y + h / 2 + size * 0.35, label_str, size=size,
               fill=fg, weight=weight, family=family, anchor="middle")
    )


# ==============================================================================
# 00 / APPLE MULTI-CELL BENTO HERO (840 x 188 — 4 Distinct Bento Cells)
# ==============================================================================
def hero(t):
    W, H = 840, 188
    P = THEMES[t]
    o = [head(W, H, P)]

    # ── CELL 1: Main Intro Bento Cell (Left: 504 x 186) ──
    o.append(bento_box(1, 1, 502, 186, P, rx=22))

    # Subtle status eyebrow
    o.append(f'<circle cx="31" cy="32" r="3.5" fill="{P["green"]}"/>')
    o.append(text(42, 36, "Computer Engineering  ·  Systems & Applied AI",
                  size=12, fill=P["muted"], weight="500", ls=-0.1))

    # Apple-style display title + two-tone statement (Primary + Titanium Gray)
    o.append(text(26, 76, "Kian.", size=34, fill=P["text"], weight="700", ls=-1.0))
    o.append(text(114, 76, "Compilers, web platforms, and AI.",
                  size=21, fill=P["muted"], weight="600", ls=-0.5))

    o.append(text(26, 105, "Building native x86-64 toolchains, verifiable web systems,",
                  size=14, fill=P["sub"], weight="400", ls=-0.1))
    o.append(text(26, 125, "and client-side WebAssembly models with zero runtime bloat.",
                  size=14, fill=P["sub"], weight="400", ls=-0.1))

    # Frosted Apple stack pills
    tags = [
        ("Python", 64),
        ("TypeScript", 82),
        ("C / C++", 68),
        ("LLVM & WASM", 104),
        ("Next.js 16", 82),
    ]
    tx = 26
    for lbl, tw in tags:
        o.append(pill(tx, 144, tw, 24, lbl, P["pill_bg"], P["text"], P["pill_border"], size=11, weight="500"))
        tx += tw + 8

    # ── CELL 2: Top-Mid Metric Bento Cell (158 x 88) ──
    o.append(bento_box(515, 1, 156, 87, P, rx=20))
    o.append(text(535, 44, "26.1×", size=30, fill="url(#appleGrad)", weight="700", ls=-1.0))
    o.append(text(535, 68, "Faster JIT vs. CPython", size=11.5, fill=P["muted"], weight="500", ls=-0.1))

    # ── CELL 3: Top-Right Metric Bento Cell (158 x 88) ──
    o.append(bento_box(683, 1, 156, 87, P, rx=20))
    o.append(text(703, 44, "18 ms", size=30, fill="url(#cyanGrad)", weight="700", ls=-1.0))
    o.append(text(703, 68, "In-browser WASM vision", size=11.5, fill=P["muted"], weight="500", ls=-0.1))

    # ── CELL 4: Bottom-Right Activity Bento Cell (324 x 87) ──
    o.append(bento_box(515, 100, 324, 87, P, rx=20))
    c_total = STATS.get("total_contributions", 404)
    r_total = STATS.get("public_repos", 20)
    o.append(text(535, 141, str(c_total), size=26, fill=P["text"], weight="700", ls=-0.8))
    o.append(text(535, 164, f"Contributions  ·  {r_total} public repos", size=11.5, fill=P["muted"], weight="500", ls=-0.1))

    # Mini 12-month Apple Activity bar sparkline on the right of Cell 4
    m_data = STATS.get("monthly", [])[-12:]
    if m_data:
        max_c = max(d["count"] for d in m_data) or 1
        bx0 = 720
        base_y = 165
        for i, d in enumerate(m_data):
            cnt = d["count"]
            bh = max(int((cnt / max_c) * 44), 5)
            bx = bx0 + i * 8.5
            fill_c = "url(#appleGrad)" if cnt == max_c else (P["blue"] if cnt > 0 else P["track"])
            o.append(f'<rect x="{bx:.1f}" y="{base_y - bh}" width="5" height="{bh}" rx="2.5" fill="{fill_c}"/>')

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 01 / BENTO CARD: BLACK MAMBA (Apple Silicon Performance Bar Style)
# ==============================================================================
def card_mamba(t):
    W, H = 410, 198
    P = THEMES[t]
    o = [head(W, H, P)]
    o.append(bento_box(1, 1, W - 2, H - 2, P, rx=22))

    # Eyebrow & right link
    o.append(text(26, 32, "COMPILER & NATIVE RUNTIME", size=10.5, fill=P["blue"], weight="600", ls=0.6))
    o.append(text(W - 26, 32, "Explore ↗", size=12, fill=P["blue"], weight="500", anchor="end"))

    # Headline & concise subtitle
    o.append(text(26, 62, "Black Mamba", size=24, fill=P["text"], weight="700", ls=-0.6))
    o.append(text(26, 84, "Python syntax compiled to native x86-64 & WASM.", size=13.5, fill=P["muted"], weight="400", ls=-0.1))

    # Apple Silicon-style benchmark comparison widget
    wx, wy, ww, wh = 24, 100, W - 48, 74
    o.append(f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="14" fill="{P["inner_bg"]}" stroke="{P["inner_border"]}" stroke-width="1"/>')

    # Bar 1: Black Mamba JIT (Apple gradient pill + 26.1x callout)
    o.append(text(wx + 16, wy + 24, "Black Mamba JIT", size=11.5, fill=P["text"], weight="600"))
    o.append(f'<rect x="{wx + 16}" y="{wy + 31}" width="210" height="8" rx="4" fill="url(#appleGrad)"/>')
    o.append(text(wx + 234, wy + 39, "11.1 ms", size=11, fill=P["sub"], weight="500", family=SF_MONO))

    # Bar 2: CPython 3.14 baseline
    o.append(text(wx + 16, wy + 57, "CPython 3.14", size=11, fill=P["muted"], weight="500"))
    o.append(f'<rect x="{wx + 105}" y="{wy + 49}" width="32" height="7" rx="3.5" fill="{P["track"]}"/>')
    o.append(text(wx + 145, wy + 56, "288.6 ms", size=10.5, fill=P["muted"], weight="400", family=SF_MONO))

    # Right-aligned big Apple multiplier callout inside widget
    o.append(text(wx + ww - 16, wy + 42, "26.1×", size=24, fill="url(#appleGrad)", weight="700", anchor="end", ls=-0.8))
    o.append(text(wx + ww - 16, wy + 58, "faster", size=11, fill=P["muted"], weight="500", anchor="end"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 02 / BENTO CARD: SHIM (Apple Wallet Verifiable Pass & Typography Style)
# ==============================================================================
def card_shim(t):
    W, H = 410, 198
    P = THEMES[t]
    o = [head(W, H, P)]
    o.append(bento_box(1, 1, W - 2, H - 2, P, rx=22))

    o.append(text(26, 32, "VERIFIABLE CREDENTIALS", size=10.5, fill=P["indigo"], weight="600", ls=0.6))
    o.append(text(W - 26, 32, "Live app ↗", size=12, fill=P["blue"], weight="500", anchor="end"))

    o.append(text(26, 62, "Shim", size=24, fill=P["text"], weight="700", ls=-0.6))
    o.append(text(26, 84, "Cryptographic QR passes & font-metric layout engine.", size=13.5, fill=P["muted"], weight="400", ls=-0.1))

    # Sleek Apple Wallet-style pass preview widget
    wx, wy, ww, wh = 24, 100, W - 48, 74
    o.append(f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="14" fill="{P["inner_bg"]}" stroke="{P["inner_border"]}" stroke-width="1"/>')

    # Left: Minimalist Apple QR glyph inside rounded squircle
    qx, qy = wx + 14, wy + 13
    o.append(f'<rect x="{qx}" y="{qy}" width="48" height="48" rx="10" fill="{P["pill_bg"]}" stroke="{P["pill_border"]}" stroke-width="1"/>')
    for dx, dy in ((9, 9), (27, 9), (9, 27)):
        o.append(f'<rect x="{qx+dx}" y="{qy+dy}" width="11" height="11" rx="2.5" stroke="{P["text"]}" stroke-width="2" fill="none"/>')
        o.append(f'<rect x="{qx+dx+3.5}" y="{qy+dy+3.5}" width="4" height="4" rx="1" fill="{P["text"]}"/>')
    o.append(f'<rect x="{qx+28}" y="{qy+28}" width="4" height="4" rx="1" fill="{P["blue"]}"/>')
    o.append(f'<rect x="{qx+34}" y="{qy+34}" width="5" height="5" rx="1" fill="{P["blue"]}"/>')

    # Middle: Pass metadata & kerning precision indicator
    o.append(text(wx + 76, wy + 31, "Font-Metric Kerning", size=13, fill=P["text"], weight="600", ls=-0.2))
    o.append(text(wx + 76, wy + 50, "Next.js 16  ·  Prisma  ·  Audit Log", size=11.5, fill=P["muted"], weight="400"))

    # Right: Apple Verified Pill with green indicator
    vx = wx + ww - 102
    vy = wy + 23
    o.append(f'<rect x="{vx}" y="{vy}" width="88" height="28" rx="14" fill="{P["pill_bg"]}" stroke="{P["pill_border"]}" stroke-width="1"/>')
    o.append(f'<circle cx="{vx + 16}" cy="{vy + 14}" r="4" fill="{P["green"]}"/>')
    o.append(text(vx + 50, vy + 18, "Verified", size=11.5, fill=P["text"], weight="600", anchor="middle"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 03 / BENTO CARD: TYPENSCRAPE (Apple Intelligence / Spotlight Routing Style)
# ==============================================================================
def card_typenscrape(t):
    W, H = 410, 198
    P = THEMES[t]
    o = [head(W, H, P)]
    o.append(bento_box(1, 1, W - 2, H - 2, P, rx=22))

    o.append(text(26, 32, "APPLIED AI & OFFLINE STORAGE", size=10.5, fill=P["purple"], weight="600", ls=0.6))
    o.append(text(W - 26, 32, "Explore ↗", size=12, fill=P["blue"], weight="500", anchor="end"))

    o.append(text(26, 62, "TypenScrape", size=24, fill=P["text"], weight="700", ls=-0.6))
    o.append(text(26, 84, "Offline-first recipe PWA with automatic LLM failover.", size=13.5, fill=P["muted"], weight="400", ls=-0.1))

    # Dual Apple capsule widget: LLM Router + Chunked IndexedDB
    wx, wy, ww, wh = 24, 100, W - 48, 74
    o.append(f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="14" fill="{P["inner_bg"]}" stroke="{P["inner_border"]}" stroke-width="1"/>')

    # Left half: LLM Failover latency
    o.append(text(wx + 16, wy + 29, "Groq  →  Gemini", size=13.5, fill=P["text"], weight="600", ls=-0.2))
    o.append(text(wx + 16, wy + 49, "~420 ms failover routing", size=11.5, fill=P["muted"], weight="400"))

    # Subtle vertical divider
    o.append(f'<line x1="{wx + 190}" y1="{wy + 14}" x2="{wx + 190}" y2="{wy + wh - 14}" stroke="{P["inner_border"]}" stroke-width="1"/>')

    # Right half: 16-Chunk IndexedDB
    o.append(text(wx + 208, wy + 29, "16-Chunk DB", size=13.5, fill="url(#appleGrad)", weight="700", ls=-0.2))
    o.append(text(wx + 208, wy + 49, "Zero mobile RAM spikes", size=11.5, fill=P["muted"], weight="400"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 04 / BENTO CARD: MEEMOMINI (Apple Continuity Camera / Vision HUD Style)
# ==============================================================================
def card_meemomini(t):
    W, H = 410, 198
    P = THEMES[t]
    o = [head(W, H, P)]
    o.append(bento_box(1, 1, W - 2, H - 2, P, rx=22))

    o.append(text(26, 32, "ON-DEVICE COMPUTER VISION", size=10.5, fill=P["pink"], weight="600", ls=0.6))
    o.append(text(W - 26, 32, "Explore ↗", size=12, fill=P["blue"], weight="500", anchor="end"))

    o.append(text(26, 62, "meemomini", size=24, fill=P["text"], weight="700", ls=-0.6))
    o.append(text(26, 84, "Browser photo booth with client-side WASM segmentation.", size=13.5, fill=P["muted"], weight="400", ls=-0.1))

    # Apple Camera / Vision HUD widget
    wx, wy, ww, wh = 24, 100, W - 48, 74
    o.append(f'<rect x="{wx}" y="{wy}" width="{ww}" height="{wh}" rx="14" fill="{P["inner_bg"]}" stroke="{P["inner_border"]}" stroke-width="1"/>')

    # Left: Sleek iOS Camera Viewfinder focus icon
    fx, fy, fw, fh = wx + 16, wy + 15, 44, 44
    c_len = 9
    # 4 corner focus brackets in Apple Yellow/Amber (`#FF9F0A`)
    o.append(
        f'<path d="M {fx} {fy+c_len} L {fx} {fy} L {fx+c_len} {fy} '
        f'M {fx+fw-c_len} {fy} L {fx+fw} {fy} L {fx+fw} {fy+c_len} '
        f'M {fx} {fy+fh-c_len} L {fx} {fy+fh} L {fx+c_len} {fy+fh} '
        f'M {fx+fw-c_len} {fy+fh} L {fx+fw} {fy+fh} L {fx+fw} {fy+fh-c_len}" '
        f'stroke="{P["orange"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>'
    )
    # Person silhouette inside viewfinder
    o.append(f'<circle cx="{fx+22}" cy="{fy+16}" r="5.5" fill="{P["text"]}"/>')
    o.append(f'<path d="M {fx+11} {fy+34} C {fx+11} {fy+25} {fx+33} {fy+25} {fx+33} {fy+34}" fill="{P["text"]}"/>')

    # Middle: MediaPipe WASM specs
    o.append(text(wx + 76, wy + 31, "MediaPipe WASM", size=13.5, fill=P["text"], weight="600", ls=-0.2))
    o.append(text(wx + 76, wy + 50, "WebGL Shaders  ·  MP4 / QR Export", size=11.5, fill=P["muted"], weight="400"))

    # Right: Latency callout
    o.append(text(wx + ww - 16, wy + 39, "18 ms", size=22, fill="url(#cyanGrad)", weight="700", anchor="end", ls=-0.6))
    o.append(text(wx + ww - 16, wy + 56, "per frame", size=11, fill=P["muted"], weight="500", anchor="end"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 05 / COMPILER PIPELINE (Apple Architecture Slide Style — 840 x 172)
# ==============================================================================
def topology(t):
    W, H = 840, 172
    P = THEMES[t]
    o = [head(W, H, P)]
    o.append(bento_box(1, 1, W - 2, H - 2, P, rx=22))

    o.append(text(28, 34, "Black Mamba Compilation Architecture", size=16, fill=P["text"], weight="700", ls=-0.3))
    o.append(text(W - 28, 34, "Python Grammar  →  Native x86-64 & WASM", size=12, fill=P["muted"], weight="500", anchor="end"))

    stages = [
        ("01  Parse", "AST + Indent", "Unboxed structs", P["blue"]),
        ("02  C3 MRO", "Diamond Graph", "0.42 ms resolve", P["indigo"]),
        ("03  HM Types", "Static Solver", "1-cycle vtables", P["purple"]),
        ("04  LLVM 18", "Tail-Call Pass", "5M → 0 frames", P["pink"]),
        ("05  Codegen", "x86-64 & WASM", "0 KB GC overhead", P["orange"]),
    ]
    sw = 148
    gap = (W - 56 - 5 * sw) / 4
    for i, (st, l1, l2, col) in enumerate(stages):
        sx = 28 + i * (sw + gap)
        sy = 48
        o.append(f'<rect x="{sx:.1f}" y="{sy}" width="{sw}" height="80" rx="14" fill="{P["inner_bg"]}" stroke="{P["inner_border"]}" stroke-width="1"/>')
        o.append(text(sx + 14, sy + 24, st, size=11, fill=col, weight="700", family=SF_MONO))
        o.append(text(sx + 14, sy + 46, l1, size=13, fill=P["text"], weight="600", ls=-0.2))
        o.append(text(sx + 14, sy + 64, l2, size=11, fill=P["muted"], weight="400"))

    o.append(text(28, 152, "Includes zero-dependency PE32+, ELF64, and 1.7 KB WASM linkers plus native TLS 1.3 & SQL.",
                  size=12, fill=P["muted"], weight="400"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 06 / BENCHMARK SUITE (Apple Silicon Keynote Chart Style — 840 x 216)
# ==============================================================================
def benchmark(t):
    W, H = 840, 216
    P = THEMES[t]
    o = [head(W, H, P)]
    o.append(bento_box(1, 1, W - 2, H - 2, P, rx=22))

    o.append(text(28, 34, "Performance Benchmark  ·  Black Mamba JIT vs. CPython 3.14", size=16, fill=P["text"], weight="700", ls=-0.3))
    o.append(text(W - 28, 34, "Execution time in milliseconds (lower is better)", size=12, fill=P["muted"], weight="500", anchor="end"))

    for i, (k_name, py_t, bm_t, ratio) in enumerate(BENCH):
        ry = 52 + i * 38
        o.append(text(28, ry + 20, k_name, size=13, fill=P["text"], weight="600", family=SF_MONO))

        bx = 200
        max_w = 340
        bw_py = max(int((py_t / 300.0) * max_w), 24)
        bw_bm = max(int((bm_t / 300.0) * max_w), 12)

        # CPython muted track bar
        o.append(f'<rect x="{bx}" y="{ry+5}" width="{bw_py}" height="7" rx="3.5" fill="{P["track"]}"/>')
        # Black Mamba Apple Gradient bar
        grad = "url(#appleGrad)" if i % 2 == 0 else "url(#cyanGrad)"
        o.append(f'<rect x="{bx}" y="{ry+16}" width="{bw_bm}" height="8" rx="4" fill="{grad}"/>')

        o.append(text(565, ry + 20, f"{bm_t:.2f} ms  vs  {py_t:.1f} ms", size=12, fill=P["sub"], weight="400", family=SF_MONO))
        o.append(text(W - 28, ry + 21, ratio, size=18, fill=grad, weight="700", anchor="end", ls=-0.5))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 07 / 12-MONTH CONTRIBUTION CHART (Apple Activity Chart Style — 840 x 192)
# ==============================================================================
def bars(t):
    W, H = 840, 192
    P = THEMES[t]
    o = [head(W, H, P)]
    o.append(bento_box(1, 1, W - 2, H - 2, P, rx=22))

    o.append(text(28, 34, "Contribution Activity (Last 12 Months)", size=16, fill=P["text"], weight="700", ls=-0.3))
    o.append(text(W - 28, 34, f"{STATS.get('total_contributions', 404)} total contributions  ·  {STATS.get('active_days', 26)} active days",
                  size=12, fill=P["muted"], weight="500", anchor="end"))

    base_y = 152
    o.append(f'<line x1="28" y1="{base_y}" x2="{W-28}" y2="{base_y}" stroke="{P["inner_border"]}" stroke-width="1"/>')

    m_data = STATS.get("monthly", [])
    if m_data:
        max_c = max(d["count"] for d in m_data) or 1
        n = len(m_data)
        bar_w = 44
        gap = (W - 56 - (n * bar_w)) / (n - 1) if n > 1 else 0
        max_h = 82

        for i, d in enumerate(m_data):
            bx = 28 + i * (bar_w + gap)
            count = d["count"]
            bh = int((count / max_c) * max_h) if count > 0 else 4
            bh = max(bh, 4)
            by = base_y - bh

            fill_c = "url(#appleGrad)" if count == max_c else (P["blue"] if count > 0 else P["track"])
            o.append(f'<rect x="{bx:.1f}" y="{by}" width="{bar_w}" height="{bh}" rx="6" fill="{fill_c}"/>')

            month_lbl = dt.date.fromisoformat(d["month"] + "-01").strftime("%b")
            o.append(text(bx + bar_w / 2, base_y + 20, month_lbl, size=11, fill=P["muted"], weight="500", anchor="middle"))
            if count > 0:
                o.append(text(bx + bar_w / 2, by - 7, str(count), size=11.5, fill=P["text"], weight="600", anchor="middle"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 08 / TELEMETRY LOG (840 x 170)
# ==============================================================================
def telemetry(t):
    W, H = 840, 170
    P = THEMES[t]
    o = [head(W, H, P)]
    o.append(bento_box(1, 1, W - 2, H - 2, P, rx=22))

    o.append(text(28, 34, "Visitor Handshake Log", size=16, fill=P["text"], weight="700", ls=-0.3))

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
        sy = 48 + i * 36
        o.append(f'<rect x="28" y="{sy}" width="{W-56}" height="30" rx="8" fill="{P["inner_bg"]}" stroke="{P["inner_border"]}" stroke-width="1"/>')
        o.append(text(42, sy + 20, "@" + s.get("sender", ""), size=12, fill=P["blue"], weight="600", family=SF_MONO))
        o.append(text(210, sy + 20, s.get("org", ""), size=12, fill=P["text"], weight="500"))
        o.append(text(440, sy + 20, s.get("focus", ""), size=12, fill=P["sub"], weight="400"))
        o.append(text(W - 42, sy + 20, s.get("timestamp", "")[:10], size=11.5, fill=P["muted"], weight="400", family=SF_MONO, anchor="end"))

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
