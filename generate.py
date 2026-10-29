"""
Generates the animated SVG assets for Kian's Silicon Floorplan & Bento Grid profile.
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

TAGLINE = "I write compilers and firmware, then put models on top of them."

LANG_COLORS = {
    "Python": "#3572A5", "TypeScript": "#3178c6", "JavaScript": "#f1e05a",
    "HTML": "#e34c26", "CSS": "#663399", "Jupyter Notebook": "#DA5B0B",
    "C++": "#f34b7d", "C": "#555555", "PHP": "#4F5D95", "LLVM": "#185619",
    "WebAssembly": "#04133b", "Dockerfile": "#384d54", "OpenSCAD": "#e5cd45",
    "Batchfile": "#C1F12E", "MDX": "#fcb32c", "Shell": "#89e051",
}

THEMES = {
    "dark": {
        "bg0": "#08090B", "bg1": "#0B0E11", "panel": "#0F1317",
        "rule": "#1E242B", "text": "#F3F5F8", "dim": "#98A3AF",
        "micro": "#7E8A97", "faint": "#39414B", "accent": "#FFA028",
        "bar": "#2A323C", "green": "#22C55E", "cyan": "#38BDF8",
    },
    "light": {
        "bg0": "#FBFAF7", "bg1": "#F6F4EF", "panel": "#FFFFFF",
        "rule": "#E3DED4", "text": "#111418", "dim": "#4E5661",
        "micro": "#5A6270", "faint": "#A7ACB4", "accent": "#C2410C",
        "bar": "#C9C2B2", "green": "#16A34A", "cyan": "#0284C7",
    },
}

SANS = ("-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,"
        "'Noto Sans',sans-serif")
MONO = ("ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,"
        "'Liberation Mono',monospace")

CSS = """
.f{animation:fi .32s ease-out both}
.r{animation:ri .42s cubic-bezier(.22,.68,.2,1) both}
.gx{transform-box:fill-box;transform-origin:0 50%;animation:gx .7s cubic-bezier(.3,.8,.25,1) both}
.gy{transform-box:fill-box;transform-origin:50% 100%;animation:gy .55s cubic-bezier(.2,.8,.2,1) both}
.pulse{animation:pulse 2s ease-in-out infinite}
.flow{stroke-dasharray:6 4;animation:flow 1.2s linear infinite}
.trace{stroke-dasharray:1400;stroke-dashoffset:1400;animation:draw 1.6s cubic-bezier(.2,.8,.2,1) forwards}
.trace-fast{stroke-dasharray:1600;stroke-dashoffset:1600;animation:draw 1.2s cubic-bezier(.15,.85,.25,1) forwards}
@keyframes fi{from{opacity:0}to{opacity:1}}
@keyframes ri{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:translateY(0)}}
@keyframes gx{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes gy{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes bl{0%,45%{opacity:1}55%,100%{opacity:0}}
@keyframes pulse{0%,100%{opacity:0.35}50%{opacity:1}}
@keyframes flow{to{stroke-dashoffset:-20}}
@keyframes draw{to{stroke-dashoffset:0}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""

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
        out = json.loads(gh(["api", "repos/%s/%s/commits?per_page=%d"
                             % (LOGIN, LOGIN, n)]))
        return [(c["sha"][:7], c["commit"]["message"].split("\n")[0]) for c in out]
    except Exception:
        return []

# SVG Helpers
def head(w, h, motion):
    css = f"<style>{CSS}</style>" if motion else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" fill="none" role="img">{css}')

def A(motion, cls="", delay=None):
    if not motion:
        return ""
    out = f' class="{cls}"' if cls else ""
    if delay is not None:
        out += f' style="animation-delay:{delay:.2f}s"'
    return out

def text(x, y, s, size=14, fill="#000", weight="400", family=SANS,
         anchor="start", ls=0.0, op=1.0, motion=False, cls="", delay=None):
    anim = A(motion, cls, delay)
    ls_attr = f' letter-spacing="{ls}"' if ls else ""
    op_attr = f' opacity="{op}"' if op < 1.0 else ""
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"'
            f'{ls_attr}{op_attr}{anim}>{escape(str(s))}</text>')

def rule(x1, y1, x2, y2, color, op=1.0):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{color}" stroke-width="1" opacity="{op:.1f}"/>')

def label(x, y, s, P, size=10, ls=1.6, anchor="start", motion=False, delay=None):
    return text(x, y, s, size=size, fill=P["micro"], weight="700",
                family=MONO, anchor=anchor, ls=ls,
                motion=motion, cls="f", delay=delay)

# -------------------------------------------------------- status island ----
def status_island(t, motion=True):
    """1280x88. Dynamic Island & Systems Status Cockpit."""
    W, H = 1280, 88
    P = THEMES[t]
    o = [head(W, H, motion)]
    o.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="14" '
             f'fill="{P["panel"]}" stroke="{P["rule"]}" stroke-width="1.2"/>')

    # Left: Beacon & Identity
    o.append(f'<circle cx="36" cy="44" r="4.5" fill="{P["accent"]}" class="pulse"/>')
    o.append(text(52, 38, "SYS // ONLINE", size=10.5, fill=P["accent"], weight="800", family=MONO, ls=1.5))
    o.append(text(52, 54, "200 OK · LOW-LEVEL JIT", size=9.5, fill=P["micro"], weight="600", family=MONO))

    o.append(rule(196, 20, 196, 68, P["rule"]))

    # Identity
    o.append(text(216, 38, "KIAN B.", size=14, fill=P["text"], weight="800", family=MONO, ls=0.5))
    o.append(text(216, 54, "COMPUTER ENGINEERING  ·  SILICON TO MODEL", size=9.5, fill=P["dim"], weight="600", family=MONO, ls=1.0))

    o.append(rule(530, 20, 530, 68, P["rule"]))

    # Center: Tagline
    o.append(text(550, 47, TAGLINE, size=13.5, fill=P["text"], weight="500", family=SANS, ls=-0.1))

    o.append(rule(990, 20, 990, 68, P["rule"]))

    # Right: Recruiter Signal & Telemetry Sync
    o.append(text(W - 32, 38, "OPEN TO GLOBAL ROLES", size=10.5, fill=P["green"], weight="800", family=MONO, ls=1.2, anchor="end"))
    o.append(text(W - 32, 54, f"SYNC {STATS.get('generated', '2026-10-29')} · {STATS.get('public_repos', 19)} REPOSITORIES",
                  size=9.5, fill=P["micro"], weight="600", family=MONO, anchor="end"))

    o.append("</svg>")
    return "".join(o)

# ------------------------------------------------------------ floorplan ----
def floorplan(t, motion=True):
    """1280x440. Silicon Processor Die Floorplan (Heterogeneous Architecture)."""
    W, H = 1280, 440
    P = THEMES[t]
    o = [head(W, H, motion)]
    o.append(f'<rect width="{W}" height="{H}" rx="12" fill="{P["bg0"]}"/>')

    # Top strip
    o.append(rule(0, 44, W, 44, P["rule"]))
    o.append(f'<circle cx="36" cy="22" r="3.5" fill="{P["accent"]}" class="pulse"/>')
    o.append(label(48, 26, "SILICON PROCESSOR DIE FLOORPLAN  /  HETEROGENEOUS COMPUTATION ARCHITECTURE", P,
                   motion=motion, delay=0.08))
    o.append(text(W - 36, 26, "PROCESS: DIRECT x86-64 JIT / WASM / C++ · 4 HETEROGENEOUS CORES", size=10,
                  fill=P["accent"], weight="700", family=MONO, ls=1.2,
                  anchor="end", motion=motion, cls="f", delay=0.12))

    # Die outer frame
    o.append(f'<rect x="24" y="56" width="{W-48}" height="332" rx="8" '
             f'fill="{P["bg1"]}" stroke="{P["rule"]}" stroke-width="1.2"/>')

    # Core 0: JIT Compiler (Top Left)
    bx0, by0, bw, bh = 36, 68, 590, 134
    o.append(f'<rect x="{bx0}" y="{by0}" width="{bw}" height="{bh}" rx="6" '
             f'fill="{P["panel"]}" stroke="{P["rule"]}" stroke-width="1"/>')
    o.append(text(bx0 + 16, by0 + 22, "CORE 0 // NATIVE COMPILER & JIT RUNTIME [BLACK MAMBA]", size=11,
                  fill=P["text"], weight="700", family=MONO, ls=0.5))
    o.append(text(bx0 + bw - 16, by0 + 22, "26.1x FASTER vs CPYTHON", size=9.5, fill=P["accent"],
                  weight="700", family=MONO, anchor="end"))
    o.append(rule(bx0, by0 + 32, bx0 + bw, by0 + 32, P["rule"]))
    o.append(text(bx0 + 16, by0 + 52, "• Frontend: Indentation desugar · Dynamic C3 Diamond MRO (0.42ms)", size=10.5, fill=P["dim"], family=MONO))
    o.append(text(bx0 + 16, by0 + 72, "• Codegen: LLVM 18 IR · Direct x86-64 executable memory mapping (PROT_EXEC)", size=10.5, fill=P["dim"], family=MONO))
    o.append(text(bx0 + 16, by0 + 92, "• Target: Tail-Call recursion collapse (5M -> 0 frames) · Zero GC pause", size=10.5, fill=P["dim"], family=MONO))
    # Tag chips
    chips0 = ["x86-64 JIT", "C3 MRO", "LLVM 18", "1.7KB WASM", "TLS 1.3 / SQL"]
    cx = bx0 + 16
    for c in chips0:
        cw = len(c) * 6.5 + 14
        o.append(f'<rect x="{cx}" y="{by0 + 106}" width="{cw:.1f}" height="18" rx="4" fill="{P["bg0"]}" stroke="{P["rule"]}" stroke-width="0.8"/>')
        o.append(text(cx + cw/2, by0 + 118, c, size=8.5, fill=P["micro"], weight="600", family=MONO, anchor="middle"))
        cx += cw + 6

    # Core 1: Applied AI & Adaptive Inference (Top Right)
    bx1 = 654
    o.append(f'<rect x="{bx1}" y="{by0}" width="{bw}" height="{bh}" rx="6" '
             f'fill="{P["panel"]}" stroke="{P["rule"]}" stroke-width="1"/>')
    o.append(text(bx1 + 16, by0 + 22, "CORE 1 // APPLIED AI & ADAPTIVE INFERENCE [TYPEN置CRAPE / KLYPH]", size=11,
                  fill=P["text"], weight="700", family=MONO, ls=0.5))
    o.append(text(bx1 + bw - 16, by0 + 22, "ZERO-UNCHECKED LOOPS", size=9.5, fill=P["green"],
                  weight="700", family=MONO, anchor="end"))
    o.append(rule(bx1, by0 + 32, bx1 + bw, by0 + 32, P["rule"]))
    o.append(text(bx1 + 16, by0 + 52, "• Resilience: Groq (Llama 3 @ 420ms) -> Gemini fallback on 429 rate limit", size=10.5, fill=P["dim"], family=MONO))
    o.append(text(bx1 + 16, by0 + 72, "• Verification: Closed-loop beam search scoring over spaCy AST & 50k rules", size=10.5, fill=P["dim"], family=MONO))
    o.append(text(bx1 + 16, by0 + 92, "• Memory: 16-chunk IndexedDB paging to bound mobile peak memory limits", size=10.5, fill=P["dim"], family=MONO))
    chips1 = ["GROQ LLAMA-3", "GEMINI 2.0", "SPACY AST", "BEAM SCORING", "INDEXEDDB"]
    cx = bx1 + 16
    for c in chips1:
        cw = len(c) * 6.5 + 14
        o.append(f'<rect x="{cx}" y="{by0 + 106}" width="{cw:.1f}" height="18" rx="4" fill="{P["bg0"]}" stroke="{P["rule"]}" stroke-width="0.8"/>')
        o.append(text(cx + cw/2, by0 + 118, c, size=8.5, fill=P["micro"], weight="600", family=MONO, anchor="middle"))
        cx += cw + 6

    # Central High-Speed Data Bus (Interconnect)
    by_bus = 212
    o.append(rule(36, by_bus, W - 36, by_bus, P["rule"]))
    if motion:
        o.append(f'<line x1="36" y1="{by_bus}" x2="{W-36}" y2="{by_bus}" stroke="{P["accent"]}" stroke-width="1.8" class="flow"/>')
    o.append(f'<rect x="{W/2 - 240}" y="{by_bus - 10}" width="480" height="20" rx="4" fill="{P["bg1"]}" stroke="{P["rule"]}" stroke-width="1"/>')
    o.append(text(W / 2, by_bus + 3.5, "◄── ZERO-COST UNIFIED MEMORY BUS // MMAP · DIRECT MMIO · TELEMETRY ──►",
                  size=9.5, fill=P["accent"], weight="700", family=MONO, anchor="middle", ls=0.8))

    # Core 2: On-Device Vision Accelerator (Bottom Left)
    by2 = 242
    o.append(f'<rect x="{bx0}" y="{by2}" width="{bw}" height="{bh}" rx="6" '
             f'fill="{P["panel"]}" stroke="{P["rule"]}" stroke-width="1"/>')
    o.append(text(bx0 + 16, by2 + 22, "CORE 2 // ON-DEVICE COMPUTER VISION [MEEMOMINI]", size=11,
                  fill=P["text"], weight="700", family=MONO, ls=0.5))
    o.append(text(bx0 + bw - 16, by2 + 22, "18ms INFERENCE · 0 EGRESS", size=9.5, fill=P["green"],
                  weight="700", family=MONO, anchor="end"))
    o.append(rule(bx0, by2 + 32, bx0 + bw, by2 + 32, P["rule"]))
    o.append(text(bx0 + 16, by2 + 52, "• Vision: MediaPipe ImageSegmenter executing entirely in browser WASM", size=10.5, fill=P["dim"], family=MONO))
    o.append(text(bx0 + 16, by2 + 72, "• Privacy: Zero frames exfiltrated to cloud servers · True local execution", size=10.5, fill=P["dim"], family=MONO))
    o.append(text(bx0 + 16, by2 + 92, "• Export: Hardware-accelerated canvas filter pipeline · Still/GIF/MP4 PWA", size=10.5, fill=P["dim"], family=MONO))
    chips2 = ["MEDIAPIPE WASM", "ON-DEVICE", "WEBGL FILTERS", "OFFLINE PWA"]
    cx = bx0 + 16
    for c in chips2:
        cw = len(c) * 6.5 + 14
        o.append(f'<rect x="{cx}" y="{by2 + 106}" width="{cw:.1f}" height="18" rx="4" fill="{P["bg0"]}" stroke="{P["rule"]}" stroke-width="0.8"/>')
        o.append(text(cx + cw/2, by2 + 118, c, size=8.5, fill=P["micro"], weight="600", family=MONO, anchor="middle"))
        cx += cw + 6

    # Core 3: Embedded Firmware & Hardware (Bottom Right)
    o.append(f'<rect x="{bx1}" y="{by2}" width="{bw}" height="{bh}" rx="6" '
             f'fill="{P["panel"]}" stroke="{P["rule"]}" stroke-width="1"/>')
    o.append(text(bx1 + 16, by2 + 22, "CORE 3 // EDGE FIRMWARE & TELEMETRY [VOLTSENSE]", size=11,
                  fill=P["text"], weight="700", family=MONO, ls=0.5))
    o.append(text(bx1 + bw - 16, by2 + 22, "ZERO-SECRET CLIENT", size=9.5, fill=P["accent"],
                  weight="700", family=MONO, anchor="end"))
    o.append(rule(bx1, by2 + 32, bx1 + bw, by2 + 32, P["rule"]))
    o.append(text(bx1 + 16, by2 + 52, "• Firmware: Memory-bounded C++ on ESP32 sampling load & occupancy sensors", size=10.5, fill=P["dim"], family=MONO))
    o.append(text(bx1 + 16, by2 + 72, "• Security: Device -> Vercel -> FCM alerts (hardware holds zero secrets)", size=10.5, fill=P["dim"], family=MONO))
    o.append(text(bx1 + 16, by2 + 92, "• Control: Multi-relay electrical isolation & live Firebase RTDB sync", size=10.5, fill=P["dim"], family=MONO))
    chips3 = ["ESP32 C++", "FIREBASE RTDB", "FCM PUSH", "ADC SAMPLING", "OPTOCOUPLERS"]
    cx = bx1 + 16
    for c in chips3:
        cw = len(c) * 6.5 + 14
        o.append(f'<rect x="{cx}" y="{by2 + 106}" width="{cw:.1f}" height="18" rx="4" fill="{P["bg0"]}" stroke="{P["rule"]}" stroke-width="0.8"/>')
        o.append(text(cx + cw/2, by2 + 118, c, size=8.5, fill=P["micro"], weight="600", family=MONO, anchor="middle"))
        cx += cw + 6

    # Bottom Hardware Status
    o.append(rule(0, 400, W, 400, P["rule"]))
    statuses = [
        ("EXEC CORE 0", "ACTIVE · 0 KB GC OVERHEAD"),
        ("AI CORE 1", "RESILIENT CASCADE (GROQ -> GEMINI)"),
        ("VISION CORE 2", "18ms WASM ON-DEVICE INFERENCE"),
        ("EDGE CORE 3", "10Hz TELEMETRY SAMPLING · SECURE"),
    ]
    for i, (k, v) in enumerate(statuses):
        cx = 36 + i * 312
        if i:
            o.append(rule(cx - 24, 408, cx - 24, 432, P["rule"]))
        o.append(label(cx, 416, k, P, size=9.5, ls=1.2))
        o.append(text(cx, 430, v, size=10.5, fill=P["text"], weight="700", family=MONO))

    o.append("</svg>")
    return "".join(o)

# ---------------------------------------------------------- disassembly ----
def disassembly(t, motion=True):
    """1280x370. Side-by-Side Source vs Native Machine Disassembly & Benchmark."""
    W, H = 1280, 370
    P = THEMES[t]
    o = [head(W, H, motion)]
    o.append(f'<rect width="{W}" height="{H}" rx="12" fill="{P["bg0"]}"/>')

    # Top strip
    o.append(rule(0, 44, W, 44, P["rule"]))
    o.append(f'<circle cx="36" cy="22" r="3.5" fill="{P["accent"]}" class="pulse"/>')
    o.append(label(48, 26, "DISASSEMBLY & EXECUTION ENGINE  /  SOURCE (.BMB) -> DIRECT x86-64 JIT", P,
                   motion=motion, delay=0.08))
    o.append(text(W - 36, 26, "KERNEL: FIB(32) · COMPILATION: 0.42ms · 26.1x FASTER THAN CPYTHON", size=10,
                  fill=P["accent"], weight="700", family=MONO, ls=1.2,
                  anchor="end", motion=motion, cls="f", delay=0.12))

    # Left: Source .bmb
    pw = 570
    o.append(f'<rect x="36" y="58" width="{pw}" height="220" rx="6" fill="{P["panel"]}" stroke="{P["rule"]}" stroke-width="1"/>')
    o.append(text(52, 80, "SOURCE // fibonacci.bmb", size=11, fill=P["accent"], weight="700", family=MONO))
    o.append(text(36 + pw - 16, 80, "PYTHONIC SYNTAX · STATIC INFERENCE", size=9.5, fill=P["micro"], weight="600", family=MONO, anchor="end"))
    o.append(rule(36, 92, 36 + pw, 92, P["rule"]))

    src_lines = [
        ("def", P["accent"]), (" fib(n: int) -> int:", P["text"]),
        ("    if n <= 1:", P["text"]),
        ("        return n", P["cyan"]),
        ("    return fib(n - 1) + fib(n - 2)", P["cyan"]),
        ("", P["dim"]),
        ("# Compiled via Black Mamba v1.1.0 JIT", P["micro"]),
        ("# AST Parsing: 0.42ms | Type Prop: 0.31ms | Codegen: 1.84ms", P["micro"]),
    ]
    cur_y = 114
    for line in [
        [("def", P["accent"]), (" fib(n: int) -> int:", P["text"])],
        [("    if n <= 1:", P["dim"])],
        [("        return n", P["cyan"])],
        [("    return fib(n - 1) + fib(n - 2)", P["cyan"])],
        [("", P["text"])],
        [("# Compiled via Black Mamba v1.1.0 Native JIT", P["micro"])],
        [("# Frontend: 0.42ms | Inference: 0.31ms | JIT Alloc: 1.84ms", P["micro"])],
        [("# Zero Garbage Collector Overhead | Direct Machine Execution", P["green"])],
    ]:
        tx = 52
        for seg, color in line:
            o.append(text(tx, cur_y, seg, size=11.5, fill=color, weight="600", family=MONO))
            tx += len(seg) * 7.1
        cur_y += 18

    # Center: JIT arrow
    o.append(f'<polygon points="618,160 638,168 618,176" fill="{P["accent"]}"/>')
    o.append(text(628, 150, "JIT", size=9, fill=P["accent"], weight="800", family=MONO, anchor="middle"))

    # Right: Native Assembly
    bx1 = 650
    pw1 = W - bx1 - 36
    o.append(f'<rect x="{bx1}" y="58" width="{pw1}" height="220" rx="6" fill="{P["panel"]}" stroke="{P["rule"]}" stroke-width="1"/>')
    o.append(text(bx1 + 16, 80, "DISASSEMBLY // NATIVE x86-64 MACHINE CODE", size=11, fill=P["text"], weight="700", family=MONO))
    o.append(text(bx1 + pw1 - 16, 80, "PROT_READ | PROT_WRITE | PROT_EXEC", size=9.5, fill=P["micro"], weight="600", family=MONO, anchor="end"))
    o.append(rule(bx1, 92, bx1 + pw1, 92, P["rule"]))

    asm_lines = [
        "fib:",
        "    cmp    rdi, 1",
        "    jle    .L_base",
        "    push   rbx",
        "    mov    rbx, rdi",
        "    dec    rdi",
        "    call   fib",
        "    mov    rsi, rax",
        "    lea    rdi, [rbx - 2]",
        "    call   fib",
        "    add    rax, rsi",
        "    pop    rbx",
        "    ret",
        ".L_base:",
        "    mov    rax, rdi",
        "    ret",
    ]
    # Two columns of assembly
    for idx, l in enumerate(asm_lines[:8]):
        col_x = bx1 + 16
        col_y = 114 + idx * 18
        color = P["accent"] if l.endswith(":") else P["text"]
        o.append(text(col_x, col_y, l, size=11, fill=color, weight="600", family=MONO))
    for idx, l in enumerate(asm_lines[8:]):
        col_x = bx1 + 260
        col_y = 114 + idx * 18
        color = P["accent"] if l.endswith(":") else P["text"]
        o.append(text(col_x, col_y, l, size=11, fill=color, weight="600", family=MONO))

    # Bottom Benchmark Speedup Visualization
    o.append(rule(0, 292, W, 292, P["rule"]))
    o.append(label(36, 310, "EMPIRICAL SPEEDUP RATIO: FIB(32) ON IDENTICAL HOST HARDWARE", P, size=9.5, ls=1.2))

    # CPython bar
    by_c = 328
    o.append(text(36, by_c + 10, "CPython 3.14 (Interpreted)", size=10, fill=P["dim"], weight="600", family=MONO))
    o.append(f'<rect x="230" y="{by_c}" width="500" height="12" rx="3" fill="{P["bar"]}"/>')
    o.append(text(742, by_c + 10, "288.62 ms (14.2 MB RAM)", size=10, fill=P["dim"], weight="600", family=MONO))

    # Black Mamba bar
    by_m = 348
    o.append(text(36, by_m + 10, "Black Mamba (Native JIT)", size=10, fill=P["text"], weight="700", family=MONO))
    mb_w = max(19, int(500 * (11.078 / 288.62)))
    o.append(f'<rect x="230" y="{by_m}" width="{mb_w}" height="12" rx="3" fill="{P["accent"]}"/>')
    o.append(text(230 + mb_w + 12, by_m + 10, "11.08 ms (1.1 MB RAM)  ──  26.1x FASTER [TCO 5M -> 0 FRAMES]",
                  size=10, fill=P["accent"], weight="800", family=MONO))

    o.append("</svg>")
    return "".join(o)

# -------------------------------------------------------------- telemetry ----
def telemetry(t, motion=True):
    """1280x230. Live Event-Driven IssueOps Telemetry Radar."""
    W, H = 1280, 230
    P = THEMES[t]
    o = [head(W, H, motion)]
    o.append(f'<rect width="{W}" height="{H}" rx="12" fill="{P["bg0"]}"/>')

    # Top strip
    o.append(rule(0, 44, W, 44, P["rule"]))
    o.append(f'<circle cx="36" cy="22" r="3.5" fill="{P["accent"]}" class="pulse"/>')
    o.append(label(48, 26, "TELEMETRY RADAR  /  REAL-TIME ISSUEOPS SIGNAL LEDGER", P,
                   motion=motion, delay=0.08))
    o.append(text(W - 36, 26, "STATUS: ONLINE [200 OK] · EVENT DISPATCH ~15S", size=10,
                  fill=P["accent"], weight="700", family=MONO, ls=1.5,
                  anchor="end", motion=motion, cls="f", delay=0.12))

    p = os.path.join(ROOT, "telemetry.json")
    signals = []
    if os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                signals = json.load(f).get("signals", [])
        except Exception:
            pass

    if not signals:
        signals = [
            {"id": "SIG-001", "sender": "kicode01", "org": "Lead Architect",
             "focus": "Applied AI / Compilers", "note": "Genesis telemetry port online.",
             "timestamp": "2026-10-28 15:15 UTC"}
        ]

    y = 74
    o.append(text(48, y, "SIGNAL", size=9.5, fill=P["micro"], weight="700", family=MONO, ls=1.2))
    o.append(text(150, y, "TRANSMITTER", size=9.5, fill=P["micro"], weight="700", family=MONO, ls=1.2))
    o.append(text(330, y, "ORGANIZATION / AFFILIATION", size=9.5, fill=P["micro"], weight="700", family=MONO, ls=1.2))
    o.append(text(660, y, "DOMAIN FOCUS", size=9.5, fill=P["micro"], weight="700", family=MONO, ls=1.2))
    o.append(text(960, y, "TIMESTAMP", size=9.5, fill=P["micro"], weight="700", family=MONO, ls=1.2))
    o.append(text(W - 48, y, "STATUS", size=9.5, fill=P["micro"], weight="700", family=MONO, ls=1.2, anchor="end"))
    o.append(rule(48, y + 10, W - 48, y + 10, P["rule"]))

    for i, sig in enumerate(signals[:3]):
        ry = y + 36 + i * 28
        d = 0.2 + i * 0.1
        o.append(f'<circle cx="36" cy="{ry - 4}" r="2.5" fill="{P["accent"]}" {A(motion, "f", d)}/>')
        o.append(text(48, ry, sig.get("id", f"SIG-{i+1:03d}"), size=11, fill=P["accent"],
                      weight="700", family=MONO, motion=motion, cls="f", delay=d))
        o.append(text(150, ry, "@" + sig.get("sender", "anonymous")[:18], size=11, fill=P["text"],
                      weight="600", family=MONO, motion=motion, cls="f", delay=d + 0.05))
        o.append(text(330, ry, sig.get("org", "Verified Guest")[:32], size=11, fill=P["dim"],
                      weight="400", family=MONO, motion=motion, cls="f", delay=d + 0.1))
        o.append(text(660, ry, sig.get("focus", "Applied AI / Systems")[:32], size=11, fill=P["dim"],
                      weight="400", family=MONO, motion=motion, cls="f", delay=d + 0.15))
        o.append(text(960, ry, sig.get("timestamp", "RECENT")[:16], size=10.5, fill=P["micro"],
                      weight="400", family=MONO, motion=motion, cls="f", delay=d + 0.2))
        o.append(text(W - 48, ry, "[ACK // VERIFIED]", size=10.5, fill=P["accent"],
                      weight="700", family=MONO, ls=0.8, anchor="end", motion=motion, cls="f", delay=d + 0.25))

    o.append(rule(48, H - 32, W - 48, H - 32, P["rule"]))
    o.append(text(48, H - 14,
                  "trigger a live telemetry handshake: open an issue to execute GitHub Actions IssueOps and render signal in ~15s",
                  size=9.5, fill=P["micro"], weight="500", family=MONO, motion=motion, cls="f", delay=0.8))
    o.append(text(W - 48, H - 14, "EVENT-DRIVEN STATE MACHINE", size=9.5, fill=P["micro"],
                  weight="600", family=MONO, ls=1.0, anchor="end", motion=motion, cls="f", delay=0.8))

    o.append("</svg>")
    return "".join(o)

# ------------------------------------------------------------------- bars ----
def bars(t, motion=True):
    """1280x160. Monthly contribution volume across the last 12 months."""
    W, H = 1280, 160
    P = THEMES[t]
    o = [head(W, H, motion)]
    o.append(f'<rect width="{W}" height="{H}" rx="12" fill="{P["bg0"]}"/>')

    o.append(rule(0, 44, W, 44, P["rule"]))
    o.append(f'<circle cx="36" cy="22" r="3.5" fill="{P["accent"]}" class="pulse"/>')
    o.append(label(48, 26, "CONTRIBUTION PULSE  /  12-MONTH ACTIVITY SHAPE", P, motion=motion, delay=0.08))
    o.append(text(W - 36, 26, "%d CONTRIBUTIONS IN THE LAST YEAR" % STATS.get("total_contributions", 382),
                  size=10, fill=P["accent"], weight="700", family=MONO, ls=1.2,
                  anchor="end", motion=motion, cls="f", delay=0.12))

    m_data = STATS.get("monthly", [])
    if m_data:
        max_c = max(d["count"] for d in m_data) or 1
        n = len(m_data)
        bar_w = 76
        gap = (W - 96 - (n * bar_w)) / (n - 1) if n > 1 else 0
        max_h = 68
        base_y = 132

        for i, d in enumerate(m_data):
            bx = 48 + i * (bar_w + gap)
            count = d["count"]
            bh = int((count / max_c) * max_h)
            bh = max(bh, 4)
            by = base_y - bh
            color = P["accent"] if count == max_c else P["bar"]
            o.append(f'<rect x="{bx:.1f}" y="{by}" width="{bar_w}" height="{bh}" rx="3" fill="{color}"/>')
            o.append(text(bx + bar_w / 2, base_y + 16, d["month"][-2:], size=9.5, fill=P["micro"],
                          weight="600", family=MONO, anchor="middle"))
            if count > 0:
                o.append(text(bx + bar_w / 2, by - 6, str(count), size=9.5, fill=P["text"],
                              weight="700", family=MONO, anchor="middle"))

    o.append("</svg>")
    return "".join(o)

# --------------------------------------------------------------- readme glue --
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
            t_lines = ["| Signal | Transmitter | Organization | Domain Focus | Timestamp | Status |",
                       "| :--- | :--- | :--- | :--- | :--- | :--- |"]
            for s in tdata.get("signals", [])[:4]:
                t_lines.append(
                    f"| `{s.get('id')}` | **@{s.get('sender')}** | {s.get('org')} | "
                    f"`{s.get('focus')}` | {s.get('timestamp')} | `VERIFIED` |"
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
        "status-island": status_island,
        "floorplan": floorplan,
        "disassembly": disassembly,
        "telemetry": telemetry,
        "bars": bars,
    }
    for name, fn in jobs.items():
        for theme in ("dark", "light"):
            for mode in ("anim", "static"):
                svg = fn(theme, mode == "anim")
                path = os.path.join(ASSETS, f"{name}-{theme}-{mode}.svg")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(svg)
                print(f"  {name}-{theme}-{mode}.svg  {len(svg)/1024:.1f} KB")

    update_readme(STATS, recent_commits(), STATS.get("cross_repo_commits"))
    print(f"\n{STATS['public_repos']} repos · {STATS['total_contributions']} contributions "
          f"· {STATS['commits']} commits · {STATS['active_days']} active days")

if __name__ == "__main__":
    main()
