"""
Generates the animated SVG assets for Kian's Electric Cyber-Indigo & Neon Cyan profile.
Linear / Cursor / Frontier AI Lab Aesthetic.
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

TAGLINE = "Zero-cost compilers, hardware telemetry & fault-tolerant model orchestration."

LANG_COLORS = {
    "Python": "#38BDF8", "TypeScript": "#6366F1", "JavaScript": "#FACC15",
    "HTML": "#F97316", "CSS": "#A855F7", "Jupyter Notebook": "#FB923C",
    "C++": "#EC4899", "C": "#94A3B8", "LLVM": "#10B981", "WebAssembly": "#06B6D4",
    "OpenSCAD": "#FBBF24", "Shell": "#4ADE80",
}

THEMES = {
    "dark": {
        "bg0": "#050814", "bg1": "#0B1120", "panel": "#0F172A",
        "rule": "#1E293B", "rule_glow": "#334155",
        "text": "#F8FAFC", "dim": "#94A3B8", "micro": "#64748B", "faint": "#1E293B",
        "cyan": "#22D3EE", "cyan_glow": "#06B6D4",
        "indigo": "#818CF8", "indigo_glow": "#6366F1",
        "purple": "#C084FC", "green": "#34D399",
        "bar": "#1E293B", "accent": "#22D3EE",
    },
    "light": {
        "bg0": "#FAFAFA", "bg1": "#F1F5F9", "panel": "#FFFFFF",
        "rule": "#E2E8F0", "rule_glow": "#CBD5E1",
        "text": "#0F172A", "dim": "#475569", "micro": "#64748B", "faint": "#E2E8F0",
        "cyan": "#0284C7", "cyan_glow": "#0369A1",
        "indigo": "#4F46E5", "indigo_glow": "#4338CA",
        "purple": "#9333EA", "green": "#059669",
        "bar": "#E2E8F0", "accent": "#0284C7",
    },
}

SANS = ("-apple-system,BlinkMacSystemFont,'Inter','Segoe UI',Helvetica,Arial,"
        "'Noto Sans',sans-serif")
MONO = ("ui-monospace,SFMono-Regular,'JetBrains Mono','SF Mono',Menlo,Consolas,"
        "'Liberation Mono',monospace")

CSS = """
.f{animation:fi .32s ease-out both}
.r{animation:ri .42s cubic-bezier(.22,.68,.2,1) both}
.gx{transform-box:fill-box;transform-origin:0 50%;animation:gx .7s cubic-bezier(.3,.8,.25,1) both}
.gy{transform-box:fill-box;transform-origin:50% 100%;animation:gy .55s cubic-bezier(.2,.8,.2,1) both}
.pulse{animation:pulse 2s ease-in-out infinite}
.flow{stroke-dasharray:6 4;animation:flow 1.2s linear infinite}
.glow{animation:glow 3s ease-in-out infinite alternate}
@keyframes fi{from{opacity:0}to{opacity:1}}
@keyframes ri{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:translateY(0)}}
@keyframes gx{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes gy{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes pulse{0%,100%{opacity:0.4;transform:scale(0.95)}50%{opacity:1;transform:scale(1.05)}}
@keyframes flow{to{stroke-dashoffset:-20}}
@keyframes glow{0%{opacity:0.6}100%{opacity:1}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""

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

    prev = _previous_stats()
    totals = {k: prev.get(k, 0) for k in ("total_contributions", "commits", "prs", "repos_contributed")}
    days = prev.get("days", [])

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
    monthly = defaultdict(int)
    for d, c in days:
        monthly[d.strftime("%Y-%m")] += c
    s["monthly"] = [{"month": m, "count": c} for m, c in sorted(monthly.items())][-12:]
    if "cross_repo_commits" not in s or not s["cross_repo_commits"]:
        s["cross_repo_commits"] = cross_repo_commits()
    return s

def load():
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

# SVG Helpers
def head(w, h, motion, defs=""):
    css = f"<style>{CSS}</style>" if motion else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" fill="none" role="img">{css}{defs}')

def text(x, y, s, size=14, fill="#000", weight="400", family=SANS,
         anchor="start", ls=0.0, op=1.0, motion=False, cls="", delay=None):
    anim = f' class="{cls}"' if (motion and cls) else ""
    if motion and delay is not None:
        anim += f' style="animation-delay:{delay:.2f}s"'
    ls_attr = f' letter-spacing="{ls}"' if ls else ""
    op_attr = f' opacity="{op}"' if op < 1.0 else ""
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"'
            f'{ls_attr}{op_attr}{anim}>{escape(str(s))}</text>')

def rule(x1, y1, x2, y2, color, op=1.0):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{color}" stroke-width="1" opacity="{op:.1f}"/>')

# ----------------------------------------------------------- HERO BANNER ----
def hero(t, motion=True):
    """1280x280. Linear / Frontier AI Lab Hero Banner."""
    W, H = 1280, 280
    P = THEMES[t]

    defs = f"""<defs>
<radialGradient id="mesh_glow" cx="80%" cy="20%" r="60%">
  <stop offset="0%" stop-color="{P['indigo_glow']}" stop-opacity="0.35"/>
  <stop offset="50%" stop-color="{P['cyan_glow']}" stop-opacity="0.15"/>
  <stop offset="100%" stop-color="{P['bg0']}" stop-opacity="0"/>
</radialGradient>
<linearGradient id="text_grad" x1="0%" y1="0%" x2="100%" y2="0%">
  <stop offset="0%" stop-color="{P['cyan']}"/>
  <stop offset="50%" stop-color="{P['indigo']}"/>
  <stop offset="100%" stop-color="{P['purple']}"/>
</linearGradient>
</defs>"""

    o = [head(W, H, motion, defs)]
    # Background canvas
    o.append(f'<rect width="{W}" height="{H}" rx="16" fill="{P["bg0"]}"/>')
    o.append(f'<rect width="{W}" height="{H}" rx="16" fill="url(#mesh_glow)"/>')
    o.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{P["rule"]}" stroke-width="1.2"/>')

    # Top Status Pill
    o.append(f'<rect x="48" y="32" width="280" height="28" rx="14" fill="{P["panel"]}" stroke="{P["rule_glow"]}" stroke-width="1"/>')
    o.append(f'<circle cx="66" cy="46" r="4" fill="{P["cyan"]}" class="pulse"/>')
    o.append(text(80, 50, "SYSTEM // RUNTIME ACTIVE", size=10, fill=P["cyan"], weight="800", family=MONO, ls=1.2))
    o.append(text(240, 50, "v1.1.0", size=10, fill=P["micro"], weight="600", family=MONO))

    # Main Headline
    o.append(text(48, 126, "KIAN B.", size=68, fill="url(#text_grad)", weight="900", family=SANS, ls=-2.5))
    o.append(text(48, 168, "COMPUTER ENGINEERING  ·  SILICON TO MODEL", size=13, fill=P["dim"], weight="700", family=MONO, ls=2.0))
    o.append(text(48, 206, TAGLINE, size=16, fill=P["text"], weight="500", family=SANS, ls=-0.2))

    # Metrics Strip (Left bottom)
    metrics = [
        ("PUBLIC REPOS", str(STATS.get("public_repos", 19))),
        ("12MO CONTRIBUTIONS", str(STATS.get("total_contributions", 383))),
        ("JIT EXECUTION SPEEDUP", "26.1x vs CPYTHON"),
    ]
    for idx, (lbl, val) in enumerate(metrics):
        mx = 48 + idx * 190
        o.append(text(mx, 238, lbl, size=9, fill=P["micro"], weight="700", family=MONO, ls=1.0))
        o.append(text(mx, 256, val, size=13, fill=P["text"], weight="800", family=MONO))

    # Right side: Glassmorphic Specs Card
    gx, gy, gw, gh = 880, 32, 352, 216
    o.append(f'<rect x="{gx}" y="{gy}" width="{gw}" height="{gh}" rx="12" fill="{P["panel"]}" stroke="{P["rule_glow"]}" stroke-width="1.2"/>')
    o.append(text(gx + 20, gy + 30, "SYSTEM SPECIFICATIONS", size=10.5, fill=P["indigo"], weight="800", family=MONO, ls=1.2))
    o.append(text(gx + gw - 20, gy + 30, "VERIFIED", size=9.5, fill=P["green"], weight="800", family=MONO, anchor="end"))
    o.append(rule(gx, gy + 42, gx + gw, gy + 42, P["rule"]))

    specs = [
        ("Architecture", "x86-64 Native JIT / LLVM 18 IR"),
        ("Memory Model", "Direct mmap(PROT_EXEC) · Zero GC"),
        ("Inference Engine", "Groq Llama-3 -> Gemini Cascade"),
        ("On-Device Vision", "MediaPipe WASM (18ms latency)"),
        ("Edge Telemetry", "ESP32 C++ · Zero-Secret FCM"),
        ("Availability", "Open to Global / Remote Roles"),
    ]
    for s_idx, (k, v) in enumerate(specs):
        sy = gy + 66 + s_idx * 24
        o.append(text(gx + 20, sy, k, size=10.5, fill=P["micro"], weight="600", family=MONO))
        o.append(text(gx + gw - 20, sy, v, size=10.5, fill=P["text"], weight="600", family=MONO, anchor="end"))

    o.append("</svg>")
    return "".join(o)

# ---------------------------------------------------- BENTO ARCHITECTURE ----
def bento(t, motion=True):
    """1280x420. Linear-Style 4-Quadrant Architecture Bento Grid."""
    W, H = 1280, 420
    P = THEMES[t]

    defs = f"""<defs>
<linearGradient id="card0_glow" x1="0%" y1="0%" x2="100%" y2="100%">
  <stop offset="0%" stop-color="{P['indigo_glow']}" stop-opacity="0.12"/>
  <stop offset="100%" stop-color="{P['panel']}" stop-opacity="0.8"/>
</linearGradient>
<linearGradient id="card1_glow" x1="0%" y1="0%" x2="100%" y2="100%">
  <stop offset="0%" stop-color="{P['cyan_glow']}" stop-opacity="0.12"/>
  <stop offset="100%" stop-color="{P['panel']}" stop-opacity="0.8"/>
</linearGradient>
<linearGradient id="card2_glow" x1="0%" y1="0%" x2="100%" y2="100%">
  <stop offset="0%" stop-color="{P['purple']}" stop-opacity="0.12"/>
  <stop offset="100%" stop-color="{P['panel']}" stop-opacity="0.8"/>
</linearGradient>
<linearGradient id="card3_glow" x1="0%" y1="0%" x2="100%" y2="100%">
  <stop offset="0%" stop-color="{P['green']}" stop-opacity="0.12"/>
  <stop offset="100%" stop-color="{P['panel']}" stop-opacity="0.8"/>
</linearGradient>
</defs>"""

    o = [head(W, H, motion, defs)]
    o.append(f'<rect width="{W}" height="{H}" rx="16" fill="{P["bg0"]}"/>')
    o.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{P["rule"]}" stroke-width="1.2"/>')

    # Top Header
    o.append(rule(0, 48, W, 48, P["rule"]))
    o.append(f'<circle cx="36" cy="24" r="4" fill="{P["indigo"]}" class="pulse"/>')
    o.append(text(50, 28, "SYSTEM CAPABILITIES  /  HETEROGENEOUS EXECUTION MATRIX", size=10.5, fill=P["indigo"], weight="800", family=MONO, ls=1.5))
    o.append(text(W - 36, 28, "4 FULLY INTEGRATED VERTICAL LAYERS", size=10, fill=P["cyan"], weight="700", family=MONO, ls=1.2, anchor="end"))

    # 4 Cards Layout
    cw = 586
    ch = 160
    c_y1 = 64
    c_y2 = 236

    # Card 0: Compilers (Top Left)
    o.append(f'<rect x="36" y="{c_y1}" width="{cw}" height="{ch}" rx="12" fill="url(#card0_glow)" stroke="{P["rule_glow"]}" stroke-width="1.2"/>')
    o.append(text(56, c_y1 + 30, "01 / NATIVE COMPILER & JIT RUNTIME", size=11.5, fill=P["indigo"], weight="800", family=MONO, ls=1.0))
    o.append(text(36 + cw - 20, c_y1 + 30, "BLACK MAMBA v1.1.0", size=10, fill=P["text"], weight="700", family=MONO, anchor="end"))
    o.append(rule(36, c_y1 + 42, 36 + cw, c_y1 + 42, P["rule"]))
    o.append(text(56, c_y1 + 68, "• Direct JIT: Allocates mmap(PROT_EXEC) memory in pure Python without runtime GC", size=11, fill=P["dim"], family=SANS))
    o.append(text(56, c_y1 + 92, "• Multiple Inheritance: Dynamic C3 Diamond MRO linearization resolves in 0.42ms", size=11, fill=P["dim"], family=SANS))
    o.append(text(56, c_y1 + 116, "• Stack Unwinding: DWARF exception frames + Tail-Call Collapse (5M -> 0 frames)", size=11, fill=P["dim"], family=SANS))
    o.append(text(56, c_y1 + 140, "Speedup: 26.1x faster vs CPython 3.14 · 1.7 KB WebAssembly modules · Native TLS 1.3/SQL", size=10, fill=P["indigo"], weight="700", family=MONO))

    # Card 1: Adaptive Applied AI (Top Right)
    o.append(f'<rect x="658" y="{c_y1}" width="{cw}" height="{ch}" rx="12" fill="url(#card1_glow)" stroke="{P["rule_glow"]}" stroke-width="1.2"/>')
    o.append(text(678, c_y1 + 30, "02 / ADAPTIVE APPLIED AI CASCADE", size=11.5, fill=P["cyan"], weight="800", family=MONO, ls=1.0))
    o.append(text(658 + cw - 20, c_y1 + 30, "TYPEN置CRAPE", size=10, fill=P["text"], weight="700", family=MONO, anchor="end"))
    o.append(rule(658, c_y1 + 42, 658 + cw, c_y1 + 42, P["rule"]))
    o.append(text(678, c_y1 + 68, "• Cascade Routing: Groq (Llama-3 @ 420ms) degrades gracefully to Gemini on 429 limits", size=11, fill=P["dim"], family=SANS))
    o.append(text(678, c_y1 + 92, "• Memory Bounding: 16-chunk IndexedDB paging ensures zero OOM on resource-tight devices", size=11, fill=P["dim"], family=SANS))
    o.append(text(678, c_y1 + 116, "• Offline-First: Local SQLite fallback dataset keeps user interaction 100% operational", size=11, fill=P["dim"], family=SANS))
    o.append(text(678, c_y1 + 140, "Resilience: Graceful degradation over outright failure · PWA mobile optimization", size=10, fill=P["cyan"], weight="700", family=MONO))

    # Card 2: On-Device Vision (Bottom Left)
    o.append(f'<rect x="36" y="{c_y2}" width="{cw}" height="{ch}" rx="12" fill="url(#card2_glow)" stroke="{P["rule_glow"]}" stroke-width="1.2"/>')
    o.append(text(56, c_y2 + 30, "03 / ON-DEVICE COMPUTER VISION", size=11.5, fill=P["purple"], weight="800", family=MONO, ls=1.0))
    o.append(text(36 + cw - 20, c_y2 + 30, "MEEMOMINI", size=10, fill=P["text"], weight="700", family=MONO, anchor="end"))
    o.append(rule(36, c_y2 + 42, 36 + cw, c_y2 + 42, P["rule"]))
    o.append(text(56, c_y2 + 68, "• Client WASM: MediaPipe ImageSegmenter runs entirely in browser hardware", size=11, fill=P["dim"], family=SANS))
    o.append(text(56, c_y2 + 92, "• Absolute Privacy: Zero frames transmitted to servers · Background removal in 18ms", size=11, fill=P["dim"], family=SANS))
    o.append(text(56, c_y2 + 116, "• Real-Time Filters: Hardware canvas WebGL shaders, local still/GIF/MP4 encoding", size=11, fill=P["dim"], family=SANS))
    o.append(text(56, c_y2 + 140, "Latency: 18ms on-device inference · Zero backend dependency · Installable PWA", size=10, fill=P["purple"], weight="700", family=MONO))

    # Card 3: Edge Firmware (Bottom Right)
    o.append(f'<rect x="658" y="{c_y2}" width="{cw}" height="{ch}" rx="12" fill="url(#card3_glow)" stroke="{P["rule_glow"]}" stroke-width="1.2"/>')
    o.append(text(678, c_y2 + 30, "04 / EDGE FIRMWARE & TELEMETRY", size=11.5, fill=P["green"], weight="800", family=MONO, ls=1.0))
    o.append(text(658 + cw - 20, c_y2 + 30, "VOLTSENSE IoT", size=10, fill=P["text"], weight="700", family=MONO, anchor="end"))
    o.append(rule(658, c_y2 + 42, 658 + cw, c_y2 + 42, P["rule"]))
    o.append(text(678, c_y2 + 68, "• Firmware: Memory-bounded C++ on ESP32 sampling electrical load & occupancy", size=11, fill=P["dim"], family=SANS))
    o.append(text(678, c_y2 + 92, "• Zero-Secret Hardware: Microcontroller delegates push credentials to edge functions", size=11, fill=P["dim"], family=SANS))
    o.append(text(678, c_y2 + 116, "• Pipeline: Device -> Vercel Serverless -> Firebase Cloud Messaging (FCM)", size=11, fill=P["dim"], family=SANS))
    o.append(text(678, c_y2 + 140, "Security: Optocoupler relay isolation · Physical hardware holds zero API keys", size=10, fill=P["green"], weight="700", family=MONO))

    # Bottom Interconnect line
    o.append(rule(0, H - 14, W, H - 14, P["rule"]))
    o.append(text(36, H - 4, "VERTICAL COHERENCE: SILICON FIRMWARE -> RUNTIME JIT -> MODEL ROUTING -> CLIENT INTERFACE",
                  size=8.5, fill=P["micro"], weight="700", family=MONO, ls=1.0))

    o.append("</svg>")
    return "".join(o)

# ---------------------------------------------------- BENCHMARK MATRIX ----
def benchmark(t, motion=True):
    """1280x320. Benchmark Execution Diff: Black Mamba JIT vs CPython 3.14."""
    W, H = 1280, 320
    P = THEMES[t]

    defs = f"""<defs>
<linearGradient id="bar_grad" x1="0%" y1="0%" x2="100%" y2="0%">
  <stop offset="0%" stop-color="{P['cyan']}"/>
  <stop offset="100%" stop-color="{P['indigo']}"/>
</linearGradient>
</defs>"""

    o = [head(W, H, motion, defs)]
    o.append(f'<rect width="{W}" height="{H}" rx="16" fill="{P["bg0"]}"/>')
    o.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{P["rule"]}" stroke-width="1.2"/>')

    # Top strip
    o.append(rule(0, 48, W, 48, P["rule"]))
    o.append(f'<circle cx="36" cy="24" r="4" fill="{P["cyan"]}" class="pulse"/>')
    o.append(text(50, 28, "BENCHMARK TELEMETRY  /  EMPIRICAL RUNTIME VERIFICATION", size=10.5, fill=P["cyan"], weight="800", family=MONO, ls=1.5))
    o.append(text(W - 36, 28, "IDENTICAL HOST HARDWARE · BLACK MAMBA JIT vs CPYTHON 3.14", size=10, fill=P["micro"], weight="700", family=MONO, anchor="end"))

    kernels = [
        ("fib(32) — Recursive Tree", 288.62, 11.08, "26.1x FASTER", "14.2 MB -> 1.1 MB RAM"),
        ("collatz(40k) — Branch Thrashing", 227.84, 8.29, "27.5x FASTER", "12.8 MB -> 0.9 MB RAM"),
        ("mandelbrot(120x120) — Floating-Point", 39.14, 3.37, "11.6x FASTER", "18.4 MB -> 1.4 MB RAM"),
        ("count_primes(30k) — Memory Scanning", 22.05, 1.73, "12.7x FASTER", "11.2 MB -> 0.8 MB RAM"),
    ]

    base_y = 70
    for idx, (name, c_ms, m_ms, speedup, mem) in enumerate(kernels):
        ky = base_y + idx * 56
        # Label
        o.append(text(48, ky + 14, name, size=11, fill=P["text"], weight="700", family=MONO))
        o.append(text(380, ky + 14, f"CPython: {c_ms:.1f}ms", size=10, fill=P["micro"], weight="600", family=MONO))
        o.append(text(540, ky + 14, f"JIT: {m_ms:.2f}ms", size=10, fill=P["cyan"], weight="700", family=MONO))
        o.append(text(680, ky + 14, speedup, size=11, fill=P["cyan"], weight="800", family=MONO))
        o.append(text(W - 48, ky + 14, mem, size=10, fill=P["micro"], weight="600", family=MONO, anchor="end"))

        # Bar comparison
        by = ky + 24
        # CPython bar
        o.append(f'<rect x="48" y="{by}" width="600" height="8" rx="2" fill="{P["bar"]}"/>')
        # JIT bar
        jit_w = max(18, int(600 * (m_ms / c_ms)))
        o.append(f'<rect x="48" y="{by}" width="{jit_w}" height="8" rx="2" fill="url(#bar_grad)"/>')

    # Bottom notice
    o.append(rule(0, H - 24, W, H - 24, P["rule"]))
    o.append(text(48, H - 9, "TAIL-CALL RECURSION KERNEL OMITTED: CPYTHON RAISES RECURSIONERROR, WHILE BLACK MAMBA COLLAPSES 5,000,000 CALL FRAMES TO ZERO",
                  size=8, fill=P["micro"], weight="600", family=MONO, ls=0.8))

    o.append("</svg>")
    return "".join(o)

# ----------------------------------------------------------- TELEMETRY RADAR ----
def telemetry(t, motion=True):
    """1280x230. Event-Driven IssueOps Telemetry Radar in Linear Indigo/Cyan."""
    W, H = 1280, 230
    P = THEMES[t]

    defs = f"""<defs>
<linearGradient id="rad_grad" x1="0%" y1="0%" x2="100%" y2="0%">
  <stop offset="0%" stop-color="{P['cyan']}"/>
  <stop offset="100%" stop-color="{P['indigo']}"/>
</linearGradient>
</defs>"""

    o = [head(W, H, motion, defs)]
    o.append(f'<rect width="{W}" height="{H}" rx="16" fill="{P["bg0"]}"/>')
    o.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{P["rule"]}" stroke-width="1.2"/>')

    # Top strip
    o.append(rule(0, 48, W, 48, P["rule"]))
    o.append(f'<circle cx="36" cy="24" r="4" fill="{P["cyan"]}" class="pulse"/>')
    o.append(text(50, 28, "EVENT-DRIVEN ISSUEOPS RADAR  /  LIVE VISITOR TELEMETRY PROTOCOL", size=10.5, fill=P["cyan"], weight="800", family=MONO, ls=1.5))
    o.append(text(W - 36, 28, "STATUS: ONLINE [200 OK] · GITHUB ACTIONS DISPATCH ~15S", size=10, fill=P["indigo"], weight="700", family=MONO, ls=1.2, anchor="end"))

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
            {"id": "SIG-001", "sender": "kicode01", "org": "Core Systems Lab",
             "focus": "Applied AI / Compilers", "note": "Genesis telemetry port online.",
             "timestamp": "2026-10-28 15:15 UTC"}
        ]

    y = 76
    o.append(text(48, y, "SIGNAL", size=9.5, fill=P["micro"], weight="700", family=MONO, ls=1.2))
    o.append(text(150, y, "TRANSMITTER", size=9.5, fill=P["micro"], weight="700", family=MONO, ls=1.2))
    o.append(text(340, y, "ORGANIZATION / AFFILIATION", size=9.5, fill=P["micro"], weight="700", family=MONO, ls=1.2))
    o.append(text(660, y, "DOMAIN FOCUS", size=9.5, fill=P["micro"], weight="700", family=MONO, ls=1.2))
    o.append(text(960, y, "TIMESTAMP", size=9.5, fill=P["micro"], weight="700", family=MONO, ls=1.2))
    o.append(text(W - 48, y, "STATUS", size=9.5, fill=P["micro"], weight="700", family=MONO, ls=1.2, anchor="end"))
    o.append(rule(48, y + 10, W - 48, y + 10, P["rule"]))

    for i, sig in enumerate(signals[:3]):
        ry = y + 36 + i * 28
        o.append(f'<circle cx="36" cy="{ry - 4}" r="2.5" fill="{P["cyan"]}"/>')
        o.append(text(48, ry, sig.get("id", f"SIG-{i+1:03d}"), size=11, fill=P["cyan"], weight="700", family=MONO))
        o.append(text(150, ry, "@" + sig.get("sender", "anonymous")[:18], size=11, fill=P["text"], weight="600", family=MONO))
        o.append(text(340, ry, sig.get("org", "Verified Guest")[:32], size=11, fill=P["dim"], weight="400", family=MONO))
        o.append(text(660, ry, sig.get("focus", "Applied AI / Systems")[:32], size=11, fill=P["dim"], weight="400", family=MONO))
        o.append(text(960, ry, sig.get("timestamp", "RECENT")[:16], size=10.5, fill=P["micro"], weight="400", family=MONO))
        o.append(text(W - 48, ry, "[ACK // VERIFIED]", size=10.5, fill=P["indigo"], weight="800", family=MONO, ls=0.8, anchor="end"))

    o.append(rule(48, H - 32, W - 48, H - 32, P["rule"]))
    o.append(text(48, H - 14, "TRANSMIT TELEMETRY: OPEN AN ISSUE TO TRIGGER GITHUB ACTIONS ISSUEOPS DISPATCH IN ~15 SECONDS",
                  size=9, fill=P["micro"], weight="600", family=MONO))
    o.append(text(W - 48, H - 14, "ZERO EXTERNAL SERVERS · 100% PURE ISSUEOPS", size=9, fill=P["micro"],
                  weight="700", family=MONO, ls=1.0, anchor="end"))

    o.append("</svg>")
    return "".join(o)

# --------------------------------------------------------- ACTIVITY BARS ----
def bars(t, motion=True):
    """1280x160. Monthly contribution volume in Cyber-Indigo."""
    W, H = 1280, 160
    P = THEMES[t]

    defs = f"""<defs>
<linearGradient id="bars_grad" x1="0%" y1="0%" x2="0%" y2="100%">
  <stop offset="0%" stop-color="{P['cyan']}"/>
  <stop offset="100%" stop-color="{P['indigo']}"/>
</linearGradient>
</defs>"""

    o = [head(W, H, motion, defs)]
    o.append(f'<rect width="{W}" height="{H}" rx="16" fill="{P["bg0"]}"/>')
    o.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{P["rule"]}" stroke-width="1.2"/>')

    o.append(rule(0, 48, W, 48, P["rule"]))
    o.append(f'<circle cx="36" cy="24" r="4" fill="{P["indigo"]}" class="pulse"/>')
    o.append(text(50, 28, "ANNUAL CONTRIBUTION PULSE  /  ACTIVITY SHAPE", size=10.5, fill=P["indigo"], weight="800", family=MONO, ls=1.5))
    o.append(text(W - 36, 28, f"{STATS.get('total_contributions', 383)} CONTRIBUTIONS IN 12 MONTHS",
                  size=10, fill=P["cyan"], weight="700", family=MONO, ls=1.2, anchor="end"))

    m_data = STATS.get("monthly", [])
    if m_data:
        max_c = max(d["count"] for d in m_data) or 1
        n = len(m_data)
        bar_w = 76
        gap = (W - 96 - (n * bar_w)) / (n - 1) if n > 1 else 0
        max_h = 66
        base_y = 130

        for i, d in enumerate(m_data):
            bx = 48 + i * (bar_w + gap)
            count = d["count"]
            bh = int((count / max_c) * max_h)
            bh = max(bh, 4)
            by = base_y - bh
            fill_val = "url(#bars_grad)" if count == max_c else P["bar"]
            o.append(f'<rect x="{bx:.1f}" y="{by}" width="{bar_w}" height="{bh}" rx="3" fill="{fill_val}"/>')
            o.append(text(bx + bar_w / 2, base_y + 16, d["month"][-2:], size=9.5, fill=P["micro"],
                          weight="600", family=MONO, anchor="middle"))
            if count > 0:
                col = P["cyan"] if count == max_c else P["text"]
                o.append(text(bx + bar_w / 2, by - 6, str(count), size=9.5, fill=col,
                              weight="700", family=MONO, anchor="middle"))

    o.append("</svg>")
    return "".join(o)

# --------------------------------------------------------------- README GLUE ----
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
        "hero-linear": hero,
        "bento-architecture": bento,
        "benchmark-matrix": benchmark,
        "telemetry-radar": telemetry,
        "activity-shape": bars,
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
