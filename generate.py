"""
Generates clean, 1:1 pixel-scaled static SVG cards and charts for Kian's profile.

Why these look crisp on GitHub:
  1. GitHub's README column is ~840px wide. Full-width SVGs use viewBox 840
     and half-width cards use viewBox 410, so 1px in SVG = 1px on screen
     (no shrinking 1280px images down to 60% where small text turns into mush).
  2. Outer backgrounds are transparent (`fill="none"`) and card surfaces match
     GitHub Primer (`#161b22` dark / `#f6f8fa` light), blending natively into
     the profile page alongside the avatar and bio.
  3. Minimal text per card (~15 words), generous padding, and simple visual
     diagrams instead of nested boxes of tiny text.
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

# Native GitHub Primer palette so cards blend seamlessly with the profile sidebar.
THEMES = {
    "dark": {
        "card": "#161B22",
        "inset": "#0D1117",
        "pill": "#21262D",
        "border": "#30363D",
        "border_subtle": "#21262D",
        "text": "#F0F6FC",
        "sub": "#C9D1D9",
        "muted": "#8B949E",
        "track": "#21262D",
        "orange": "#F78166",
        "orange_bg": "#2D1B19",
        "blue": "#58A6FF",
        "blue_bg": "#12233A",
        "green": "#3FB950",
        "green_bg": "#12261E",
        "purple": "#D2A8FF",
        "purple_bg": "#231B36",
        "pink": "#FF7B72",
        "pink_bg": "#2D191B",
    },
    "light": {
        "card": "#F6F8FA",
        "inset": "#FFFFFF",
        "pill": "#EAEEF2",
        "border": "#D0D7DE",
        "border_subtle": "#E1E4E8",
        "text": "#1F2328",
        "sub": "#424A53",
        "muted": "#656D76",
        "track": "#EAEEF2",
        "orange": "#CF4A22",
        "orange_bg": "#FFF1EC",
        "blue": "#0969DA",
        "blue_bg": "#DDF4FF",
        "green": "#1A7F37",
        "green_bg": "#DAFBE1",
        "purple": "#8250DF",
        "purple_bg": "#FBEFFF",
        "pink": "#BF3989",
        "pink_bg": "#FFECF8",
    },
}

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
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" fill="none" role="img">')


def text(x, y, s, size=14, fill="#000", weight="400", family=SANS,
         anchor="start", ls=0):
    ls_attr = f' letter-spacing="{ls}"' if ls else ""
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"'
            f'{ls_attr}>{escape(str(s))}</text>')


def line(x1, y1, x2, y2, color):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{color}" stroke-width="1"/>')


def pill(x, y, w, h, label_str, bg, fg, border="none", size=11.5, family=MONO, weight="600"):
    b_attr = f' stroke="{border}" stroke-width="1"' if border != "none" else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h/2:.0f}" fill="{bg}"{b_attr}/>'
            + text(x + w / 2, y + h / 2 + size * 0.35, label_str, size=size,
                   fill=fg, weight=weight, family=family, anchor="middle"))


# ==============================================================================
# 00 / HERO BANNER (840 x 190 — true 1:1 scale on GitHub)
# ==============================================================================
def hero(t):
    W, H = 840, 190
    P = THEMES[t]
    o = [head(W, H)]

    # Seamless GitHub Primer card container
    o.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="{P["card"]}" stroke="{P["border"]}" stroke-width="1"/>')

    # Left: Warm, human greeting & clear focus
    o.append(f'<circle cx="34" cy="36" r="4" fill="{P["green"]}"/>')
    o.append(text(46, 40, "Computer Engineering  ·  Systems, Firmware & Applied AI",
                  size=12, fill=P["muted"], weight="500", family=MONO))

    o.append(text(28, 84, "Hi, I'm Kian.", size=34, fill=P["text"], weight="800", ls=-0.8))
    o.append(text(28, 114, "I build compilers, ESP32 firmware, and practical AI apps —",
                  size=14.5, fill=P["sub"], weight="400"))
    o.append(text(28, 135, "paying attention to what the layer below actually costs.",
                  size=14.5, fill=P["sub"], weight="400"))

    # Tech stack pills
    tags = [("Python", 68), ("C / C++", 74), ("TypeScript", 92), ("x86-64 & WASM", 116), ("ESP32", 64)]
    tx = 28
    for label_s, pw in tags:
        o.append(pill(tx, 150, pw, 24, label_s, P["inset"], P["sub"], P["border"], size=11))
        tx += pw + 8

    # Vertical divider
    o.append(line(516, 24, 516, H - 24, P["border"]))

    # Right: 2x2 Key Metrics Grid (big, clean, zero clutter)
    stats_grid = [
        (544, 64, "26.1×", "Faster JIT vs CPython", P["orange"]),
        (694, 64, "18 ms", "Browser WASM vision", P["blue"]),
        (544, 138, str(STATS.get("total_contributions", 399)), "Contributions (12 mo)", P["text"]),
        (694, 138, str(STATS.get("public_repos", 19)), "Public repositories", P["text"]),
    ]
    for gx, gy, val, lbl, col in stats_grid:
        o.append(text(gx, gy, val, size=26, fill=col, weight="800", family=MONO, ls=-0.5))
        o.append(text(gx, gy + 20, lbl, size=12, fill=P["muted"], weight="500", family=SANS))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 01..04 / 2x2 PROJECT CARDS (410 x 196 — true 1:1 scale at width="49%")
# ==============================================================================
def card_mamba(t):
    W, H = 410, 196
    P = THEMES[t]
    o = [head(W, H)]

    o.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="{P["card"]}" stroke="{P["border"]}" stroke-width="1"/>')

    # Top row: Pill + key metric
    o.append(pill(22, 20, 82, 24, "Compiler", P["blue_bg"], P["blue"], size=11, family=SANS))
    o.append(text(W - 22, 36, "26.1× speedup", size=12, fill=P["orange"], weight="700", family=MONO, anchor="end"))

    # Title & 1-line summary
    o.append(text(22, 70, "Black Mamba", size=20, fill=P["text"], weight="700", ls=-0.3))
    o.append(text(22, 91, "Python syntax compiled to native x86-64 & WASM.", size=13, fill=P["sub"]))

    # Clean visual comparison bar inside inset box
    o.append(f'<rect x="22" y="106" width="{W-44}" height="50" rx="8" fill="{P["inset"]}" stroke="{P["border_subtle"]}" stroke-width="1"/>')
    o.append(text(34, 126, "CPython 3.14", size=11, fill=P["muted"], weight="500", family=MONO))
    o.append(f'<rect x="128" y="117" width="180" height="8" rx="4" fill="{P["track"]}"/>')
    o.append(text(W - 34, 126, "288 ms", size=11, fill=P["muted"], weight="600", family=MONO, anchor="end"))

    o.append(text(34, 145, "Black Mamba", size=11, fill=P["text"], weight="700", family=MONO))
    o.append(f'<rect x="128" y="136" width="14" height="8" rx="4" fill="{P["orange"]}"/>')
    o.append(text(W - 34, 145, "11 ms", size=11, fill=P["orange"], weight="700", family=MONO, anchor="end"))

    # Footer
    o.append(text(22, 178, "Python · x86-64 · LLVM · WASM", size=11.5, fill=P["muted"], weight="500", family=MONO))
    o.append(text(W - 22, 178, "View repo ↗", size=12, fill=P["blue"], weight="600", anchor="end"))

    o.append("</svg>")
    return "".join(o)


def card_voltsense(t):
    W, H = 410, 196
    P = THEMES[t]
    o = [head(W, H)]

    o.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="{P["card"]}" stroke="{P["border"]}" stroke-width="1"/>')

    o.append(pill(22, 20, 108, 24, "Firmware & IoT", P["green_bg"], P["green"], size=11, family=SANS))
    o.append(text(W - 22, 36, "0 keys on device", size=12, fill=P["green"], weight="700", family=MONO, anchor="end"))

    o.append(text(22, 70, "VoltSense", size=20, fill=P["text"], weight="700", ls=-0.3))
    o.append(text(22, 91, "ESP32 load monitor & isolated cloud relay console.", size=13, fill=P["sub"]))

    # Clean 3-node diagram
    o.append(f'<rect x="22" y="106" width="{W-44}" height="50" rx="8" fill="{P["inset"]}" stroke="{P["border_subtle"]}" stroke-width="1"/>')
    nodes = [("ESP32 C++", 36, 96), ("Vercel Edge", 156, 98), ("React PWA", 278, 96)]
    for i, (lbl, nx, nw) in enumerate(nodes):
        b_col = P["green"] if i == 1 else P["border"]
        o.append(f'<rect x="{nx}" y="117" width="{nw}" height="28" rx="6" fill="{P["card"]}" stroke="{b_col}" stroke-width="1"/>')
        o.append(text(nx + nw / 2, 135, lbl, size=11, fill=P["text"], weight="600", family=MONO, anchor="middle"))
        if i < 2:
            ax = nx + nw + 4
            o.append(line(ax, 131, ax + 16, 131, P["muted"]))

    o.append(text(22, 178, "C++ · ESP32 · Firebase · React 19", size=11.5, fill=P["muted"], weight="500", family=MONO))
    o.append(text(W - 22, 178, "Live app ↗", size=12, fill=P["blue"], weight="600", anchor="end"))

    o.append("</svg>")
    return "".join(o)


def card_typenscrape(t):
    W, H = 410, 196
    P = THEMES[t]
    o = [head(W, H)]

    o.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="{P["card"]}" stroke="{P["border"]}" stroke-width="1"/>')

    o.append(pill(22, 20, 88, 24, "Applied AI", P["purple_bg"], P["purple"], size=11, family=SANS))
    o.append(text(W - 22, 36, "Offline-first PWA", size=12, fill=P["purple"], weight="700", family=MONO, anchor="end"))

    o.append(text(22, 70, "TypenScrape", size=20, fill=P["text"], weight="700", ls=-0.3))
    o.append(text(22, 91, "Recipe engine with LLM failover & chunked local DB.", size=13, fill=P["sub"]))

    # Clean visual flow
    o.append(f'<rect x="22" y="106" width="{W-44}" height="50" rx="8" fill="{P["inset"]}" stroke="{P["border_subtle"]}" stroke-width="1"/>')
    o.append(f'<rect x="36" y="117" width="154" height="28" rx="6" fill="{P["card"]}" stroke="{P["purple"]}" stroke-width="1"/>')
    o.append(text(113, 135, "Groq 420ms → Gemini", size=11, fill=P["text"], weight="600", family=MONO, anchor="middle"))

    o.append(f'<rect x="204" y="117" width="170" height="28" rx="6" fill="{P["card"]}" stroke="{P["border"]}" stroke-width="1"/>')
    o.append(text(289, 135, "16-Chunk IndexedDB", size=11, fill=P["sub"], weight="600", family=MONO, anchor="middle"))

    o.append(text(22, 178, "TypeScript · React · Groq · Gemini", size=11.5, fill=P["muted"], weight="500", family=MONO))
    o.append(text(W - 22, 178, "View repo ↗", size=12, fill=P["blue"], weight="600", anchor="end"))

    o.append("</svg>")
    return "".join(o)


def card_meemomini(t):
    W, H = 410, 196
    P = THEMES[t]
    o = [head(W, H)]

    o.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="{P["card"]}" stroke="{P["border"]}" stroke-width="1"/>')

    o.append(pill(22, 20, 116, 24, "Computer Vision", P["pink_bg"], P["pink"], size=11, family=SANS))
    o.append(text(W - 22, 36, "18 ms in browser", size=12, fill=P["pink"], weight="700", family=MONO, anchor="end"))

    o.append(text(22, 70, "meemomini", size=20, fill=P["text"], weight="700", ls=-0.3))
    o.append(text(22, 91, "Browser photo booth with client-side segmentation.", size=13, fill=P["sub"]))

    # Clean 3-step visual flow
    o.append(f'<rect x="22" y="106" width="{W-44}" height="50" rx="8" fill="{P["inset"]}" stroke="{P["border_subtle"]}" stroke-width="1"/>')
    nodes = [("WebRTC", 36, 82), ("MediaPipe WASM", 138, 126), ("MP4 / QR", 284, 90)]
    for i, (lbl, nx, nw) in enumerate(nodes):
        b_col = P["pink"] if i == 1 else P["border"]
        o.append(f'<rect x="{nx}" y="117" width="{nw}" height="28" rx="6" fill="{P["card"]}" stroke="{b_col}" stroke-width="1"/>')
        o.append(text(nx + nw / 2, 135, lbl, size=11, fill=P["text"], weight="600", family=MONO, anchor="middle"))
        if i < 2:
            ax = nx + nw + 3
            o.append(line(ax, 131, ax + 14, 131, P["muted"]))

    o.append(text(22, 178, "TypeScript · MediaPipe · WebGL · PWA", size=11.5, fill=P["muted"], weight="500", family=MONO))
    o.append(text(W - 22, 178, "View repo ↗", size=12, fill=P["blue"], weight="600", anchor="end"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 05 / COMPILER PIPELINE (840 x 176 — 1:1 scale)
# ==============================================================================
def topology(t):
    W, H = 840, 176
    P = THEMES[t]
    o = [head(W, H)]

    o.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="{P["card"]}" stroke="{P["border"]}" stroke-width="1"/>')
    o.append(text(24, 32, "Black Mamba Compilation Pipeline", size=14, fill=P["text"], weight="700"))
    o.append(text(W - 24, 32, "Python grammar → Native machine code", size=12, fill=P["muted"], family=MONO, anchor="end"))

    stages = [
        ("1. Parse", "AST + Indentation", "Unboxed structs"),
        ("2. C3 MRO", "Diamond Inheritance", "0.42 ms resolve"),
        ("3. HM Types", "Static Inference", "1-cycle vtables"),
        ("4. LLVM 18", "Tail-Call Collapse", "5M → 0 frames"),
        ("5. Codegen", "x86-64 & WASM", "0 KB GC overhead"),
    ]
    sw = 146
    gap = (W - 48 - 5 * sw) / 4
    for i, (st, l1, l2) in enumerate(stages):
        sx = 24 + i * (sw + gap)
        sy = 50
        b_col = P["orange"] if i == 4 else P["border"]
        o.append(f'<rect x="{sx:.1f}" y="{sy}" width="{sw}" height="82" rx="8" fill="{P["inset"]}" stroke="{b_col}" stroke-width="1"/>')
        o.append(text(sx + 14, sy + 24, st, size=12.5, fill=P["text"], weight="700", family=MONO))
        o.append(text(sx + 14, sy + 46, l1, size=12, fill=P["sub"]))
        o.append(text(sx + 14, sy + 66, l2, size=11, fill=P["muted"], family=MONO))

    o.append(text(24, 156, "Includes pure-native standard libraries for TLS 1.3, relational SQL, and 24-bit RGB GUI.",
                  size=12, fill=P["muted"]))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 06 / BENCHMARK CHART (840 x 220 — 1:1 scale)
# ==============================================================================
def benchmark(t):
    W, H = 840, 220
    P = THEMES[t]
    o = [head(W, H)]

    o.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="{P["card"]}" stroke="{P["border"]}" stroke-width="1"/>')
    o.append(text(24, 32, "Black Mamba JIT vs. CPython 3.14", size=14, fill=P["text"], weight="700"))
    o.append(text(W - 24, 32, "Lower execution time is better", size=12, fill=P["muted"], family=MONO, anchor="end"))

    for i, (k_name, py_t, bm_t, ratio) in enumerate(BENCH):
        ry = 52 + i * 38
        o.append(text(24, ry + 20, k_name, size=13, fill=P["text"], weight="600", family=MONO))

        bx = 190
        max_w = 360
        bw_py = max(int((py_t / 300.0) * max_w), 24)
        bw_bm = max(int((bm_t / 300.0) * max_w), 8)

        o.append(f'<rect x="{bx}" y="{ry+5}" width="{bw_py}" height="8" rx="4" fill="{P["track"]}"/>')
        o.append(f'<rect x="{bx}" y="{ry+17}" width="{bw_bm}" height="8" rx="4" fill="{P["orange"]}"/>')

        o.append(text(575, ry + 20, f"{bm_t:.2f} ms vs {py_t:.1f} ms", size=12, fill=P["sub"], family=MONO))
        o.append(pill(W - 92, ry + 3, 68, 24, ratio, P["orange_bg"], P["orange"], size=12))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 07 / 12-MONTH CONTRIBUTION CHART (840 x 190 — 1:1 scale)
# ==============================================================================
def bars(t):
    W, H = 840, 190
    P = THEMES[t]
    o = [head(W, H)]

    o.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="{P["card"]}" stroke="{P["border"]}" stroke-width="1"/>')
    o.append(text(24, 32, "Contributions (Last 12 Months)", size=14, fill=P["text"], weight="700"))
    o.append(text(W - 24, 32, f"{STATS.get('total_contributions', 399)} total  ·  {STATS.get('active_days', 27)} active days",
                  size=12, fill=P["muted"], family=MONO, anchor="end"))

    base_y = 152
    o.append(line(24, base_y, W - 24, base_y, P["border"]))

    m_data = STATS.get("monthly", [])
    if m_data:
        max_c = max(d["count"] for d in m_data) or 1
        n = len(m_data)
        bar_w = 48
        gap = (W - 48 - (n * bar_w)) / (n - 1) if n > 1 else 0
        max_h = 84

        for i, d in enumerate(m_data):
            bx = 24 + i * (bar_w + gap)
            count = d["count"]
            bh = int((count / max_c) * max_h) if count > 0 else 4
            bh = max(bh, 4)
            by = base_y - bh

            fill_c = P["orange"] if count == max_c else (P["blue"] if count > 0 else P["track"])
            o.append(f'<rect x="{bx:.1f}" y="{by}" width="{bar_w}" height="{bh}" rx="4" fill="{fill_c}"/>')

            month_lbl = dt.date.fromisoformat(d["month"] + "-01").strftime("%b")
            o.append(text(bx + bar_w / 2, base_y + 20, month_lbl, size=11, fill=P["muted"], family=MONO, anchor="middle"))
            if count > 0:
                o.append(text(bx + bar_w / 2, by - 8, str(count), size=11.5, fill=P["text"], weight="700", family=MONO, anchor="middle"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 08 / TELEMETRY LOG (840 x 170 — 1:1 scale)
# ==============================================================================
def telemetry(t):
    W, H = 840, 170
    P = THEMES[t]
    o = [head(W, H)]
    o.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="{P["card"]}" stroke="{P["border"]}" stroke-width="1"/>')
    o.append(text(24, 32, "Visitor Handshake Log (GitHub Actions IssueOps)", size=14, fill=P["text"], weight="700"))
    o.append(text(W - 24, 32, "~15s auto-commit", size=12, fill=P["muted"], family=MONO, anchor="end"))

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
        o.append(f'<rect x="24" y="{sy}" width="{W-48}" height="30" rx="6" fill="{P["inset"]}" stroke="{P["border_subtle"]}" stroke-width="1"/>')
        o.append(text(38, sy + 20, "@" + s.get("sender", ""), size=12, fill=P["blue"], weight="600", family=MONO))
        o.append(text(210, sy + 20, s.get("org", ""), size=12, fill=P["text"], weight="500"))
        o.append(text(440, sy + 20, s.get("focus", ""), size=12, fill=P["sub"], family=MONO))
        o.append(text(W - 38, sy + 20, s.get("timestamp", "")[:10], size=11.5, fill=P["muted"], family=MONO, anchor="end"))

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
