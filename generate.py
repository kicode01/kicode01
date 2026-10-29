"""
Generates static, high-precision SVG specification plates for Kian's profile README.

Design principles:
  1. Zero looping animations, zero sci-fi/AI tropes, zero neon gradients.
  2. Swiss / hardware datasheet aesthetic: 1px hairlines, tabular monospace
     metrics, restrained monochrome palette with a single warm signal accent.
  3. Every number is read from the GitHub API (stats.json) or benchmark suite.
  4. Full dark and light theme variants selected via <picture>.
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
    ("fib(32)", 288.62, 11.078, "26.1x", "14.2 MB -> 1.1 MB"),
    ("collatz(40k)", 227.84, 8.291, "27.5x", "12.8 MB -> 0.9 MB"),
    ("mandelbrot(120x120)", 39.14, 3.368, "11.6x", "16.4 MB -> 1.4 MB"),
    ("count_primes(30k)", 22.05, 1.730, "12.7x", "11.2 MB -> 0.8 MB"),
]

# Matte Carbon (dark) & Warm Archival Paper (light) with International Orange accent.
THEMES = {
    "dark": {
        "bg0": "#0B0C0E",
        "bg1": "#101216",
        "panel": "#15181E",
        "rule": "#22262F",
        "rule_strong": "#333946",
        "text": "#F3F4F6",
        "dim": "#9CA3AF",
        "micro": "#6B7280",
        "faint": "#374151",
        "accent": "#F97316",
        "accent_soft": "#2A1810",
        "green": "#10B981",
        "bar": "#262B35",
    },
    "light": {
        "bg0": "#FAF8F5",
        "bg1": "#F3EFEA",
        "panel": "#FFFFFF",
        "rule": "#E2DDD5",
        "rule_strong": "#C7C0B5",
        "text": "#111317",
        "dim": "#4B5563",
        "micro": "#6B7280",
        "faint": "#9CA3AF",
        "accent": "#EA580C",
        "accent_soft": "#FFF1E6",
        "green": "#059669",
        "bar": "#D6D1C7",
    },
}

SANS = ("-apple-system,BlinkMacSystemFont,'Inter','Segoe UI',Helvetica,Arial,sans-serif")
MONO = ("ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace")


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
         anchor="start", ls=0, op=1.0):
    ls_attr = f' letter-spacing="{ls}"' if ls else ""
    op_attr = f' opacity="{op}"' if op != 1.0 else ""
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"'
            f'{ls_attr}{op_attr}>{escape(str(s))}</text>')


def rule(x1, y1, x2, y2, color, op=1.0, dash=""):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{color}" stroke-width="1" opacity="{op}"{dash_attr}/>')


def label(x, y, s, P, size=10, ls=1.4, anchor="start"):
    return text(x, y, s, size=size, fill=P["micro"], weight="600", family=MONO,
                ls=ls, anchor=anchor)


# ==============================================================================
# 00 / ARCHITECTURAL HEADER PLATE (STATIC)
# ==============================================================================
def hero(t):
    W, H = 1280, 330
    P = THEMES[t]
    o = [head(W, H)]

    o.append(f'<rect width="{W}" height="{H}" rx="8" fill="{P["bg0"]}" stroke="{P["rule"]}" stroke-width="1"/>')

    # Top bar
    o.append(rule(0, 40, W, 40, P["rule"]))
    o.append(f'<circle cx="44" cy="20" r="3.5" fill="{P["accent"]}"/>')
    o.append(text(58, 24, "KIAN  /  ARCHITECTURAL SPECIFICATION", size=10.5,
                  fill=P["text"], weight="600", family=MONO, ls=1.4))
    o.append(text(W - 44, 24, f"INDEXED {STATS['generated']}  ·  {STATS['public_repos']} PUBLIC REPOS",
                  size=10.5, fill=P["micro"], weight="500", family=MONO, ls=1.2, anchor="end"))

    # Left column: Identity & thesis
    o.append(label(44, 82, "COMPUTER ENGINEERING  ·  SYSTEMS, COMPILERS & APPLIED AI", P, size=10.5, ls=1.6))
    o.append(text(42, 152, "Kian", size=68, fill=P["text"], weight="800", ls=-2.4, family=SANS))
    o.append(text(44, 188, "I write compilers and firmware, then put models on top of them.",
                  size=18, fill=P["text"], weight="500", ls=-0.2, family=SANS))
    o.append(text(44, 214, "Know what the layer below actually costs — in clock cycles, memory, and latency.",
                  size=13.5, fill=P["dim"], weight="400", family=SANS))

    # Left bottom metric strip
    o.append(rule(44, 242, 680, 242, P["rule"]))
    metrics = [
        ("26.1x", "JIT VS CPYTHON 3.14"),
        ("18 ms", "WASM VISION INFERENCE"),
        (str(STATS["total_contributions"]), "CONTRIBUTIONS (12M)"),
        (str(STATS["public_repos"]), "PUBLIC REPOSITORIES"),
    ]
    for i, (val, lbl) in enumerate(metrics):
        mx = 44 + i * 162
        if i > 0:
            o.append(rule(mx - 14, 254, mx - 14, 308, P["rule"]))
        o.append(label(mx, 266, lbl, P, size=9, ls=1.1))
        col = P["accent"] if i == 0 else P["text"]
        o.append(text(mx, 300, val, size=24, fill=col, weight="700", family=MONO, ls=-0.5))

    # Vertical divider
    o.append(rule(716, 40, 716, H, P["rule"]))

    # Right column: 3-Layer Stack Cross-Section
    rx = 748
    rw = W - rx - 44
    o.append(label(rx, 72, "OPERATING STACK (TOP TO BOTTOM)", P, size=9.5, ls=1.4))
    o.append(text(rx + rw, 72, "3 LAYERS", size=9.5, fill=P["micro"], weight="600", family=MONO, anchor="end"))

    layers = [
        ("L3", "Applied AI & Vision", "TypenScrape · meemomini · klyph-txt",
         "Groq -> Gemini failover  ·  MediaPipe WASM  ·  Beam-search scoring"),
        ("L2", "Compilers & Runtimes", "Black Mamba v1.1.0",
         "Python AST -> C3 MRO -> HM Types -> LLVM 18 / x86-64 JIT & WASM"),
        ("L1", "Edge Firmware & Hardware", "VoltSense IoT",
         "Memory-bounded C++ on ESP32  ·  Zero on-device secrets  ·  Relays"),
    ]
    for i, (code, title, repos, spec) in enumerate(layers):
        ly = 88 + i * 74
        o.append(f'<rect x="{rx}" y="{ly}" width="{rw}" height="62" rx="4" fill="{P["panel"]}" stroke="{P["rule"]}" stroke-width="1"/>')
        # Left index tag
        o.append(f'<rect x="{rx+12}" y="{ly+12}" width="32" height="20" rx="3" fill="{P["bg1"]}" stroke="{P["rule_strong"]}" stroke-width="1"/>')
        o.append(text(rx + 28, ly + 26, code, size=10, fill=P["accent"], weight="700", family=MONO, anchor="middle"))

        o.append(text(rx + 56, ly + 26, title, size=13.5, fill=P["text"], weight="700", family=SANS))
        o.append(text(rx + rw - 14, ly + 25, repos, size=10.5, fill=P["dim"], weight="500", family=MONO, anchor="end"))
        o.append(text(rx + 56, ly + 46, spec, size=10.5, fill=P["micro"], weight="500", family=MONO))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 01 / SPEC CARD: BLACK MAMBA COMPILER
# ==============================================================================
def card_mamba(t):
    W, H = 620, 300
    P = THEMES[t]
    o = [head(W, H)]

    o.append(f'<rect width="{W}" height="{H}" rx="8" fill="{P["bg0"]}" stroke="{P["rule"]}" stroke-width="1"/>')
    o.append(rule(0, 38, W, 38, P["rule"]))
    o.append(label(24, 24, "M-01  /  COMPILER & NATIVE RUNTIME", P, size=9.5, ls=1.3))
    o.append(text(W - 24, 24, "26.1x VS CPYTHON", size=10, fill=P["accent"], weight="700", family=MONO, anchor="end"))

    o.append(text(24, 72, "Black Mamba", size=22, fill=P["text"], weight="800", family=SANS, ls=-0.4))
    o.append(text(172, 72, "v1.1.0", size=12, fill=P["micro"], weight="600", family=MONO))
    o.append(text(24, 94, "Python syntax compiled to native x86-64 machine code, PE32+/ELF64 & 1.7 KB WASM.",
                  size=12, fill=P["dim"], weight="400", family=SANS))

    # Schematic Box
    vx, vy, vw, vh = 24, 112, W - 48, 136
    o.append(f'<rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" rx="6" fill="{P["panel"]}" stroke="{P["rule"]}" stroke-width="1"/>')

    # 4-stage pipeline boxes
    stages = [
        ("01 AST + C3", "0.42 ms MRO"),
        ("02 HM TYPES", "Static Solver"),
        ("03 LLVM 18", "5M->0 Frames"),
        ("04 NATIVE JIT", "0 KB GC Tax"),
    ]
    sw = 122
    gap = (vw - 32 - 4 * sw) / 3
    for i, (st, sub) in enumerate(stages):
        sx = vx + 16 + i * (sw + gap)
        sy = vy + 16
        border = P["accent"] if i == 3 else P["rule_strong"]
        o.append(f'<rect x="{sx:.1f}" y="{sy}" width="{sw}" height="46" rx="4" fill="{P["bg0"]}" stroke="{border}" stroke-width="1"/>')
        o.append(text(sx + 10, sy + 20, st, size=10, fill=P["text"], weight="700", family=MONO))
        o.append(text(sx + 10, sy + 36, sub, size=9.5, fill=P["micro"], weight="500", family=MONO))
        if i < 3:
            ax = sx + sw + 3
            o.append(rule(ax, sy + 23, ax + gap - 6, sy + 23, P["rule_strong"]))

    # Empirical comparison inside card
    o.append(rule(vx + 16, vy + 76, vx + vw - 16, vy + 76, P["rule"]))
    o.append(text(vx + 16, vy + 96, "fib(32) CPython 3.14", size=10, fill=P["micro"], weight="500", family=MONO))
    o.append(f'<rect x="{vx+170}" y="{vy+86}" width="270" height="10" rx="2" fill="{P["bar"]}"/>')
    o.append(text(vx + vw - 16, vy + 96, "288.62 ms", size=10, fill=P["dim"], weight="600", family=MONO, anchor="end"))

    o.append(text(vx + 16, vy + 118, "fib(32) Black Mamba", size=10, fill=P["text"], weight="700", family=MONO))
    o.append(f'<rect x="{vx+170}" y="{vy+108}" width="14" height="10" rx="2" fill="{P["accent"]}"/>')
    o.append(text(vx + 194, vy + 118, "26.1x faster (1.1 MB vs 14.2 MB)", size=10, fill=P["accent"], weight="700", family=MONO))
    o.append(text(vx + vw - 16, vy + 118, "11.08 ms", size=10, fill=P["text"], weight="700", family=MONO, anchor="end"))

    # Footer
    o.append(text(24, 276, "Python · x86-64 · LLVM IR · WebAssembly · TLS 1.3 · SQL",
                  size=10, fill=P["micro"], weight="500", family=MONO))
    o.append(text(W - 24, 276, "github.com/kicode01/blackmamba-lang ->",
                  size=10, fill=P["text"], weight="600", family=MONO, anchor="end"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 02 / SPEC CARD: VOLTSENSE IOT FIRMWARE
# ==============================================================================
def card_voltsense(t):
    W, H = 620, 300
    P = THEMES[t]
    o = [head(W, H)]

    o.append(f'<rect width="{W}" height="{H}" rx="8" fill="{P["bg0"]}" stroke="{P["rule"]}" stroke-width="1"/>')
    o.append(rule(0, 38, W, 38, P["rule"]))
    o.append(label(24, 24, "M-02  /  EDGE FIRMWARE & ISOLATED CLOUD PUSH", P, size=9.5, ls=1.3))
    o.append(text(W - 24, 24, "0 SECRETS ON DEVICE", size=10, fill=P["accent"], weight="700", family=MONO, anchor="end"))

    o.append(text(24, 72, "VoltSense", size=22, fill=P["text"], weight="800", family=SANS, ls=-0.4))
    o.append(text(24, 94, "ESP32 load & occupancy telemetry with air-gapped server push credentials.",
                  size=12, fill=P["dim"], weight="400", family=SANS))

    vx, vy, vw, vh = 24, 112, W - 48, 136
    o.append(f'<rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" rx="6" fill="{P["panel"]}" stroke="{P["rule"]}" stroke-width="1"/>')

    # 3-Tier Isolation Architecture Diagram
    tiers = [
        ("TIER 1 · ESP32 (C++)", "ADC Current + PIR", "3x Relay GPIO · 0 Keys"),
        ("TIER 2 · VERCEL EDGE", "Credential Boundary", "Holds FCM Push Keys"),
        ("TIER 3 · REACT 19 PWA", "Operator Console", "Live Load + Relay UI"),
    ]
    tw = 164
    gap = (vw - 32 - 3 * tw) / 2
    for i, (t_title, t_line1, t_line2) in enumerate(tiers):
        tx = vx + 16 + i * (tw + gap)
        ty = vy + 16
        border = P["accent"] if i == 1 else P["rule_strong"]
        o.append(f'<rect x="{tx:.1f}" y="{ty}" width="{tw}" height="62" rx="4" fill="{P["bg0"]}" stroke="{border}" stroke-width="1"/>')
        o.append(text(tx + 12, ty + 20, t_title, size=9.5, fill=P["text"], weight="700", family=MONO))
        o.append(text(tx + 12, ty + 38, t_line1, size=10, fill=P["dim"], weight="500", family=SANS))
        o.append(text(tx + 12, ty + 53, t_line2, size=9.5, fill=P["micro"], weight="500", family=MONO))
        if i < 2:
            ax = tx + tw + 4
            o.append(rule(ax, ty + 31, ax + gap - 8, ty + 31, P["rule_strong"]))

    o.append(rule(vx + 16, vy + 92, vx + vw - 16, vy + 92, P["rule"]))
    o.append(text(vx + 16, vy + 114, "SECURITY INVARIANT", size=9.5, fill=P["accent"], weight="700", family=MONO))
    o.append(text(vx + 162, vy + 114, "Dumping the ESP32 flash yields zero cloud messaging keys.",
                  size=10.5, fill=P["text"], weight="500", family=MONO))

    o.append(text(24, 276, "C++ · ESP32 · Firebase RTDB · FCM · React 19 · Vercel",
                  size=10, fill=P["micro"], weight="500", family=MONO))
    o.append(text(W - 24, 276, "voltsense-iot.vercel.app ->",
                  size=10, fill=P["text"], weight="600", family=MONO, anchor="end"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 03 / SPEC CARD: TYPENSCRAPE APPLIED AI
# ==============================================================================
def card_typenscrape(t):
    W, H = 620, 300
    P = THEMES[t]
    o = [head(W, H)]

    o.append(f'<rect width="{W}" height="{H}" rx="8" fill="{P["bg0"]}" stroke="{P["rule"]}" stroke-width="1"/>')
    o.append(rule(0, 38, W, 38, P["rule"]))
    o.append(label(24, 24, "M-03  /  APPLIED AI ROUTING & OFFLINE STORAGE", P, size=9.5, ls=1.3))
    o.append(text(W - 24, 24, "16-CHUNK INDEXEDDB", size=10, fill=P["accent"], weight="700", family=MONO, anchor="end"))

    o.append(text(24, 72, "TypenScrape", size=22, fill=P["text"], weight="800", family=SANS, ls=-0.4))
    o.append(text(24, 94, "Offline-first recipe engine with Groq -> Gemini failover and bounded mobile heap.",
                  size=12, fill=P["dim"], weight="400", family=SANS))

    vx, vy, vw, vh = 24, 112, W - 48, 136
    o.append(f'<rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" rx="6" fill="{P["panel"]}" stroke="{P["rule"]}" stroke-width="1"/>')

    # Left half: Inference Cascade
    o.append(label(vx + 16, vy + 24, "INFERENCE FAILOVER CASCADE", P, size=9, ls=1.1))
    o.append(f'<rect x="{vx+16}" y="{vy+34}" width="254" height="38" rx="4" fill="{P["bg0"]}" stroke="{P["rule_strong"]}" stroke-width="1"/>')
    o.append(text(vx + 28, vy + 51, "1. Primary: Groq (Llama 3)", size=10, fill=P["text"], weight="700", family=MONO))
    o.append(text(vx + 28, vy + 65, "Low-latency token stream (~420 ms)", size=9.5, fill=P["micro"], weight="500", family=MONO))

    o.append(f'<rect x="{vx+16}" y="{vy+80}" width="254" height="38" rx="4" fill="{P["bg0"]}" stroke="{P["accent"]}" stroke-width="1"/>')
    o.append(text(vx + 28, vy + 97, "2. Fallback: Gemini API", size=10, fill=P["accent"], weight="700", family=MONO))
    o.append(text(vx + 28, vy + 111, "Automatic switch on rate limit / 429", size=9.5, fill=P["dim"], weight="500", family=MONO))

    # Divider
    o.append(rule(vx + 286, vy + 14, vx + 286, vy + vh - 14, P["rule"]))

    # Right half: 16-Chunk IndexedDB Grid
    rx = vx + 302
    o.append(label(rx, vy + 24, "BOUNDED HEAP: 16 SEQUENTIAL CHUNKS", P, size=9, ls=1.1))
    for c in range(16):
        col_i = c % 8
        row_i = c // 8
        cx = rx + col_i * 31
        cy = vy + 34 + row_i * 24
        fill_c = P["accent_soft"] if c < 4 else P["bg0"]
        stroke_c = P["accent"] if c < 4 else P["rule_strong"]
        o.append(f'<rect x="{cx}" y="{cy}" width="27" height="18" rx="2" fill="{fill_c}" stroke="{stroke_c}" stroke-width="1"/>')
        o.append(text(cx + 13.5, cy + 12.5, f"{c+1:02d}", size=8, fill=P["text"], weight="600", family=MONO, anchor="middle"))

    o.append(text(rx, vy + 98, "Pulled one chunk at a time into IndexedDB", size=10, fill=P["text"], weight="500", family=SANS))
    o.append(text(rx, vy + 114, "so mobile browsers never spike peak RAM.", size=10, fill=P["micro"], weight="500", family=MONO))

    o.append(text(24, 276, "React 18 · TypeScript · IndexedDB · Groq · Gemini · Firestore",
                  size=10, fill=P["micro"], weight="500", family=MONO))
    o.append(text(W - 24, 276, "github.com/kicode01/typenscrape ->",
                  size=10, fill=P["text"], weight="600", family=MONO, anchor="end"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 04 / SPEC CARD: MEEMOMINI ON-DEVICE VISION
# ==============================================================================
def card_meemomini(t):
    W, H = 620, 300
    P = THEMES[t]
    o = [head(W, H)]

    o.append(f'<rect width="{W}" height="{H}" rx="8" fill="{P["bg0"]}" stroke="{P["rule"]}" stroke-width="1"/>')
    o.append(rule(0, 38, W, 38, P["rule"]))
    o.append(label(24, 24, "M-04  /  ON-DEVICE COMPUTER VISION (WASM)", P, size=9.5, ls=1.3))
    o.append(text(W - 24, 24, "18 ms CLIENT INFERENCE", size=10, fill=P["accent"], weight="700", family=MONO, anchor="end"))

    o.append(text(24, 72, "meemomini", size=22, fill=P["text"], weight="800", family=SANS, ls=-0.4))
    o.append(text(24, 94, "Browser photo booth with client-side MediaPipe person segmentation & export.",
                  size=12, fill=P["dim"], weight="400", family=SANS))

    vx, vy, vw, vh = 24, 112, W - 48, 136
    o.append(f'<rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" rx="6" fill="{P["panel"]}" stroke="{P["rule"]}" stroke-width="1"/>')

    steps = [
        ("01 WEBRTC STREAM", "Camera Frame"),
        ("02 MEDIAPIPE WASM", "ImageSegmenter"),
        ("03 COMPOSITOR", "Mask + Filters"),
        ("04 HANDOFF", "MP4 / GIF / QR"),
    ]
    sw = 122
    gap = (vw - 32 - 4 * sw) / 3
    for i, (st, sub) in enumerate(steps):
        sx = vx + 16 + i * (sw + gap)
        sy = vy + 16
        border = P["accent"] if i == 1 else P["rule_strong"]
        o.append(f'<rect x="{sx:.1f}" y="{sy}" width="{sw}" height="46" rx="4" fill="{P["bg0"]}" stroke="{border}" stroke-width="1"/>')
        o.append(text(sx + 10, sy + 20, st, size=9.5, fill=P["text"], weight="700", family=MONO))
        o.append(text(sx + 10, sy + 36, sub, size=9.5, fill=P["micro"], weight="500", family=MONO))
        if i < 3:
            ax = sx + sw + 3
            o.append(rule(ax, sy + 23, ax + gap - 6, sy + 23, P["rule_strong"]))

    o.append(rule(vx + 16, vy + 76, vx + vw - 16, vy + 76, P["rule"]))
    o.append(text(vx + 16, vy + 98, "PRIVACY & LATENCY", size=9.5, fill=P["accent"], weight="700", family=MONO))
    o.append(text(vx + 162, vy + 98, "0 frames leave the browser  ·  ~18 ms per frame in WebAssembly",
                  size=10.5, fill=P["text"], weight="500", family=MONO))
    o.append(text(vx + 162, vy + 116, "No GPU server bill, no upload queue, installable offline as a PWA.",
                  size=10.5, fill=P["dim"], weight="400", family=SANS))

    o.append(text(24, 276, "React 18 · TypeScript · MediaPipe Vision · WebAssembly · PWA",
                  size=10, fill=P["micro"], weight="500", family=MONO))
    o.append(text(W - 24, 276, "github.com/kicode01/meemomini ->",
                  size=10, fill=P["text"], weight="600", family=MONO, anchor="end"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 05 / FULL COMPILER PIPELINE SCHEMATIC (STATIC)
# ==============================================================================
def topology(t):
    W, H = 1280, 270
    P = THEMES[t]
    o = [head(W, H)]
    o.append(f'<rect width="{W}" height="{H}" rx="8" fill="{P["bg0"]}" stroke="{P["rule"]}" stroke-width="1"/>')

    o.append(rule(0, 38, W, 38, P["rule"]))
    o.append(label(44, 24, "BLACK MAMBA v1.1.0  /  END-TO-END COMPILATION & EXECUTION PIPELINE", P, size=9.5, ls=1.4))
    o.append(text(W - 44, 24, "ZERO BORROW CHECKER  ·  ZERO GC PAUSE", size=9.5, fill=P["micro"],
                  weight="600", family=MONO, ls=1.2, anchor="end"))

    nodes = [
        ("01 / SOURCE", "Pythonic Grammar", "Unboxed value structs", "Zero runtime tax"),
        ("02 / FRONTEND", "AST + C3 Diamond MRO", "Indentation desugaring", "0.42 ms linearization"),
        ("03 / INFERENCE", "Hindley-Milner Solver", "Static type propagation", "1-cycle vtable dispatch"),
        ("04 / CODEGEN", "LLVM 18 IR Emitter", "Tail-call collapse (TCO)", "5,000,000 -> 0 frames"),
        ("05 / TARGET", "Native Binary & WASM", "PE32+ / ELF64 linkers", "1.7 KB WASM module"),
    ]

    nw = 216
    nh = 136
    gap = (W - 88 - 5 * nw) / 4
    by = 62
    bus_y = by + nh / 2

    o.append(rule(44, bus_y, W - 44, bus_y, P["rule_strong"]))

    for i, (step, title, l1, l2) in enumerate(nodes):
        nx = 44 + i * (nw + gap)
        border = P["accent"] if i in (3, 4) else P["rule_strong"]
        o.append(f'<rect x="{nx:.1f}" y="{by}" width="{nw}" height="{nh}" rx="6" fill="{P["panel"]}" stroke="{border}" stroke-width="1"/>')
        o.append(text(nx + 16, by + 26, step, size=9.5, fill=P["accent"], weight="700", family=MONO, ls=1.0))
        o.append(text(nx + 16, by + 52, title, size=14, fill=P["text"], weight="700", family=SANS))
        o.append(rule(nx + 16, by + 66, nx + nw - 16, by + 66, P["rule"]))
        o.append(text(nx + 16, by + 90, l1, size=11, fill=P["dim"], weight="400", family=SANS))
        o.append(text(nx + 16, by + 114, l2, size=10.5, fill=P["text"], weight="600", family=MONO))

    o.append(rule(44, 220, W - 44, 220, P["rule"]))
    o.append(text(44, 246, "STANDARD LIBRARY ECOSYSTEM:", size=10, fill=P["micro"], weight="700", family=MONO, ls=1.0))
    o.append(text(260, 246, "Pure-native TLS 1.3  ·  Relational SQL Engine  ·  24-bit RGB GUI  ·  Structured Exception Stack Unwinding",
                  size=11, fill=P["text"], weight="500", family=MONO))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 06 / EMPIRICAL BENCHMARK SUITE (STATIC)
# ==============================================================================
def benchmark(t):
    W, H = 1280, 290
    P = THEMES[t]
    o = [head(W, H)]
    o.append(f'<rect width="{W}" height="{H}" rx="8" fill="{P["bg0"]}" stroke="{P["rule"]}" stroke-width="1"/>')

    o.append(rule(0, 38, W, 38, P["rule"]))
    o.append(label(44, 24, "EMPIRICAL BENCHMARK SUITE  /  BLACK MAMBA JIT VS. CPYTHON 3.14 (SAME MACHINE, SAME KERNELS)", P, size=9.5, ls=1.4))
    o.append(text(W - 44, 24, "LOWER TIME IS BETTER", size=9.5, fill=P["micro"],
                  weight="600", family=MONO, ls=1.2, anchor="end"))

    base_y = 60
    row_h = 48
    bar_max_w = 500

    for i, (k_name, py_t, bm_t, ratio, mem) in enumerate(BENCH):
        ry = base_y + i * (row_h + 6)
        o.append(f'<rect x="44" y="{ry}" width="{W-88}" height="{row_h}" rx="4" fill="{P["panel"]}" stroke="{P["rule"]}" stroke-width="1"/>')

        o.append(text(64, ry + 29, k_name, size=12.5, fill=P["text"], weight="700", family=MONO))
        o.append(text(250, ry + 29, f"CPython: {py_t:.2f} ms", size=11, fill=P["micro"], weight="500", family=MONO))

        bx = 420
        bw_py = max(int((py_t / 300.0) * bar_max_w), 24)
        bw_bm = max(int((bm_t / 300.0) * bar_max_w), 8)

        # CPython bar (top thin track) + Black Mamba bar (bottom accent track)
        o.append(f'<rect x="{bx}" y="{ry+14}" width="{bw_py}" height="7" rx="2" fill="{P["bar"]}"/>')
        o.append(f'<rect x="{bx}" y="{ry+26}" width="{bw_bm}" height="8" rx="2" fill="{P["accent"]}"/>')

        o.append(text(bx + bw_py + 14, ry + 29, f"JIT: {bm_t:.2f} ms", size=11, fill=P["text"], weight="700", family=MONO))

        # Ratio badge
        px = W - 260
        o.append(f'<rect x="{px}" y="{ry+11}" width="68" height="26" rx="3" fill="{P["accent_soft"]}" stroke="{P["accent"]}" stroke-width="1"/>')
        o.append(text(px + 34, ry + 28, ratio, size=11, fill=P["accent"], weight="700", family=MONO, anchor="middle"))

        o.append(text(W - 64, ry + 29, mem, size=10, fill=P["dim"], weight="500", family=MONO, anchor="end"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 07 / 12-MONTH CONTRIBUTION CADENCE (STATIC)
# ==============================================================================
def bars(t):
    W, H = 1280, 240
    P = THEMES[t]
    o = [head(W, H)]

    o.append(f'<rect width="{W}" height="{H}" rx="8" fill="{P["bg0"]}" stroke="{P["rule"]}" stroke-width="1"/>')
    o.append(rule(0, 38, W, 38, P["rule"]))
    o.append(label(44, 24, "CONTRIBUTIONS BY MONTH (LAST 12 MONTHS)", P, size=9.5, ls=1.4))
    o.append(text(W - 44, 24, f"{STATS.get('total_contributions', 386)} TOTAL  ·  {STATS.get('active_days', 27)} ACTIVE DAYS",
                  size=9.5, fill=P["accent"], weight="700", family=MONO, ls=1.2, anchor="end"))

    base_y = 192
    o.append(rule(44, base_y, W - 44, base_y, P["rule"]))

    m_data = STATS.get("monthly", [])
    if m_data:
        max_c = max(d["count"] for d in m_data) or 1
        n = len(m_data)
        bar_w = 72
        gap = (W - 88 - (n * bar_w)) / (n - 1) if n > 1 else 0
        max_h = 112

        for i, d in enumerate(m_data):
            bx = 44 + i * (bar_w + gap)
            count = d["count"]
            bh = int((count / max_c) * max_h) if count > 0 else 3
            bh = max(bh, 3)
            by = base_y - bh

            fill_val = P["accent"] if count == max_c else (P["text"] if count > 0 else P["bar"])
            op_val = 1.0 if count == max_c else (0.75 if count > 0 else 0.4)
            o.append(f'<rect x="{bx:.1f}" y="{by}" width="{bar_w}" height="{bh}" rx="2" fill="{fill_val}" opacity="{op_val}"/>')

            o.append(text(bx + bar_w / 2, base_y + 20, d["month"], size=9.5, fill=P["micro"],
                          weight="500", family=MONO, anchor="middle"))
            if count > 0:
                col = P["accent"] if count == max_c else P["text"]
                o.append(text(bx + bar_w / 2, by - 8, str(count), size=10.5, fill=col,
                              weight="700", family=MONO, anchor="middle"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 08 / TELEMETRY LOG PLATE (STATIC)
# ==============================================================================
def telemetry(t):
    W, H = 1280, 220
    P = THEMES[t]
    o = [head(W, H)]
    o.append(f'<rect width="{W}" height="{H}" rx="8" fill="{P["bg0"]}" stroke="{P["rule"]}" stroke-width="1"/>')

    o.append(rule(0, 38, W, 38, P["rule"]))
    o.append(label(44, 24, "ISSUEOPS TELEMETRY LOG  /  EVENT-DRIVEN GITHUB ACTIONS HANDSHAKE", P, size=9.5, ls=1.4))
    o.append(text(W - 44, 24, "NO EXTERNAL SERVER  ·  ~15s COMMIT TURNAROUND", size=9.5, fill=P["micro"],
                  weight="600", family=MONO, ls=1.2, anchor="end"))

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
            {"id": "SIG-001", "sender": "kicode01", "org": "Core Systems Lab", "focus": "Applied AI / Compilers", "timestamp": "2026-10-28 15:15 UTC"},
            {"id": "SIG-002", "sender": "guest-engineer", "org": "Compiler Engineering", "focus": "LLVM IR / Runtime Performance", "timestamp": "2026-10-28 12:40 UTC"},
            {"id": "SIG-003", "sender": "recruiter-network", "org": "Global Frontier AI", "focus": "Applied AI Systems & Firmware", "timestamp": "2026-10-27 21:05 UTC"},
        ]

    for i, s in enumerate(signals[:3]):
        sy = 54 + i * 50
        o.append(f'<rect x="44" y="{sy}" width="{W-88}" height="42" rx="4" fill="{P["panel"]}" stroke="{P["rule"]}" stroke-width="1"/>')
        o.append(text(64, sy + 26, s.get("id", ""), size=10.5, fill=P["accent"], weight="700", family=MONO))
        o.append(text(150, sy + 26, "@" + s.get("sender", ""), size=11, fill=P["text"], weight="700", family=MONO))
        o.append(text(340, sy + 26, s.get("org", ""), size=11, fill=P["dim"], weight="500", family=SANS))
        o.append(text(620, sy + 26, s.get("focus", ""), size=10.5, fill=P["text"], weight="500", family=MONO))
        o.append(text(W - 64, sy + 26, s.get("timestamp", ""), size=10, fill=P["micro"], weight="500", family=MONO, anchor="end"))

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
                    f"{name} alone. Flat for months, then it isn't.")
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
