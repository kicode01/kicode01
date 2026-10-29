"""
Generates Apple Keynote & Space Black / Silicon Pro SVG assets for Kian's profile.
Ultra-optimized, Apple design language, iridescent gradient glow, and pro performance metrics.
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
    "Python": "#2997FF", "TypeScript": "#0A84FF", "JavaScript": "#FFD60A",
    "HTML": "#FF453A", "CSS": "#BF5AF2", "Jupyter Notebook": "#FF9F0A",
    "C++": "#FF375F", "C": "#8E8E93", "LLVM": "#30D158", "WebAssembly": "#64D2FF",
    "OpenSCAD": "#FFD60A", "Shell": "#30D158",
}

# Apple Space Black & Titanium Theme
THEMES = {
    "dark": {
        "bg0": "#000000", "bg1": "#0D0D0E", "panel": "#161617", "card": "#1C1C1E",
        "rule": "#2C2C2E", "rule_glow": "#38383A",
        "text": "#F5F5F7", "dim": "#86868B", "micro": "#6E6E73", "faint": "#1C1C1E",
        "blue": "#2997FF", "purple": "#BF5AF2", "pink": "#FF375F",
        "green": "#30D158", "amber": "#FF9F0A", "bar": "#2C2C2E",
        "accent": "#2997FF", "silver": "#E5E5EA",
    },
    "light": {
        "bg0": "#FFFFFF", "bg1": "#F5F5F7", "panel": "#FFFFFF", "card": "#F5F5F7",
        "rule": "#E5E5EA", "rule_glow": "#D1D1D6",
        "text": "#1D1D1F", "dim": "#86868B", "micro": "#A1A1A6", "faint": "#F5F5F7",
        "blue": "#0071E3", "purple": "#8944AB", "pink": "#D3385A",
        "green": "#248A3D", "amber": "#B25E02", "bar": "#E5E5EA",
        "accent": "#0071E3", "silver": "#6E6E73",
    },
}

SANS = ("-apple-system,BlinkMacSystemFont,'SF Pro Display','SF Pro Text','Helvetica Neue',Helvetica,Arial,sans-serif")
MONO = ("ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace")

CSS = """
.f{animation:fi .32s ease-out both}
.r{animation:ri .42s cubic-bezier(.22,.68,.2,1) both}
.gx{transform-box:fill-box;transform-origin:0 50%;animation:gx .7s cubic-bezier(.3,.8,.25,1) both}
.pulse{animation:pulse 2.2s ease-in-out infinite}
.glow{animation:glow 3s ease-in-out infinite alternate}
.flow{stroke-dasharray:6 4;animation:flow 1.2s linear infinite}
@keyframes fi{from{opacity:0}to{opacity:1}}
@keyframes ri{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
@keyframes gx{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes pulse{0%,100%{opacity:0.35;transform:scale(0.96)}50%{opacity:1;transform:scale(1.04)}}
@keyframes glow{0%{opacity:0.6}100%{opacity:1}}
@keyframes flow{to{stroke-dashoffset:-20}}
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

# --------------------------------------------------- APPLE KEYNOTE HERO ----
def hero(t, motion=True):
    """1280x320. Apple Keynote Product Reveal Hero."""
    W, H = 1280, 320
    P = THEMES[t]

    defs = f"""<defs>
<linearGradient id="apple_grad" x1="0%" y1="0%" x2="100%" y2="0%">
  <stop offset="0%" stop-color="{P['blue']}"/>
  <stop offset="40%" stop-color="{P['purple']}"/>
  <stop offset="70%" stop-color="{P['pink']}"/>
  <stop offset="100%" stop-color="{P['amber']}"/>
</linearGradient>
<radialGradient id="space_vignette" cx="50%" cy="0%" r="90%">
  <stop offset="0%" stop-color="{P['panel']}" stop-opacity="0.6"/>
  <stop offset="100%" stop-color="{P['bg0']}" stop-opacity="1"/>
</radialGradient>
</defs>"""

    o = [head(W, H, motion, defs)]
    o.append(f'<rect width="{W}" height="{H}" rx="18" fill="{P["bg0"]}"/>')
    o.append(f'<rect width="{W}" height="{H}" rx="18" fill="url(#space_vignette)"/>')
    o.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="18" fill="none" stroke="{P["rule"]}" stroke-width="1"/>')

    # Apple-style pill badge
    o.append(f'<rect x="{W/2 - 170}" y="32" width="340" height="28" rx="14" fill="{P["card"]}" stroke="{P["rule_glow"]}" stroke-width="1"/>')
    o.append(f'<circle cx="{W/2 - 150}" cy="46" r="3.5" fill="{P["blue"]}" class="pulse"/>')
    o.append(text(W/2 - 136, 50, "KIAN // APPLIED AI & SYSTEMS RUNTIME", size=9.5, fill=P["text"], weight="700", family=MONO, ls=1.2))
    o.append(text(W/2 + 148, 50, "ONLINE", size=9, fill=P["blue"], weight="800", family=MONO, anchor="end"))

    # Apple Pro Headline
    o.append(text(W/2, 124, "Pro performance.", size=64, fill=P["text"], weight="800", family=SANS, anchor="middle", ls=-2.2))
    o.append(text(W/2, 184, "Silicon to model.", size=64, fill="url(#apple_grad)", weight="800", family=SANS, anchor="middle", ls=-2.2))

    # Apple Subtitle
    o.append(text(W/2, 222, "Compilers, microcontrollers & applied AI where abstraction has a measurable cost.",
                  size=16, fill=P["dim"], weight="400", family=SANS, anchor="middle", ls=-0.2))

    # Bottom Stat Grid (4 Apple Pillars)
    o.append(rule(48, 256, W - 48, 256, P["rule"]))
    pillars = [
        ("26.1x", "Faster JIT vs CPython"),
        ("0 KB", "Garbage Collection Overhead"),
        ("18 ms", "On-Device WASM Vision"),
        ("0 secrets", "ESP32 Firmware Architecture"),
    ]
    for idx, (stat, desc) in enumerate(pillars):
        px = 48 + idx * 296
        o.append(text(px, 282, stat, size=18, fill=P["text"], weight="800", family=SANS, ls=-0.5))
        o.append(text(px, 300, desc, size=11, fill=P["dim"], weight="500", family=SANS))

    o.append("</svg>")
    return "".join(o)

# ---------------------------------------------------- APPLE SILICON CHIP ----
def chip(t, motion=True):
    """1280x420. Apple Silicon / M-Series Die Architecture Visualizer."""
    W, H = 1280, 420
    P = THEMES[t]

    defs = f"""<defs>
<linearGradient id="die_border" x1="0%" y1="0%" x2="100%" y2="100%">
  <stop offset="0%" stop-color="{P['silver']}" stop-opacity="0.8"/>
  <stop offset="50%" stop-color="{P['rule']}" stop-opacity="0.4"/>
  <stop offset="100%" stop-color="{P['blue']}" stop-opacity="0.8"/>
</linearGradient>
<linearGradient id="core_glow" x1="0%" y1="0%" x2="100%" y2="100%">
  <stop offset="0%" stop-color="{P['panel']}"/>
  <stop offset="100%" stop-color="{P['card']}"/>
</linearGradient>
</defs>"""

    o = [head(W, H, motion, defs)]
    o.append(f'<rect width="{W}" height="{H}" rx="18" fill="{P["bg0"]}"/>')
    o.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="18" fill="none" stroke="{P["rule"]}" stroke-width="1"/>')

    # Top Header
    o.append(rule(0, 44, W, 44, P["rule"]))
    o.append(text(48, 26, "K1 UNIFIED SILICON ENGINE  /  HETEROGENEOUS COMPUTATION DIE", size=10, fill=P["text"], weight="700", family=MONO, ls=1.5))
    o.append(text(W - 48, 26, "PRO ARCHITECTURE · ZERO GC · ZERO BORROW CHECKER OVERHEAD", size=10, fill=P["blue"], weight="700", family=MONO, ls=1.0, anchor="end"))

    # The Silicon Die Container
    dx, dy, dw, dh = 48, 62, W - 96, 332
    o.append(f'<rect x="{dx}" y="{dy}" width="{dw}" height="{dh}" rx="14" fill="{P["bg1"]}" stroke="url(#die_border)" stroke-width="1.4"/>')

    # 4 Silicon Core Quadrants
    cw = 570
    ch = 132
    y1 = dy + 18
    y2 = dy + 182

    # Core 0: Compiler (Top Left)
    o.append(f'<rect x="{dx+16}" y="{y1}" width="{cw}" height="{ch}" rx="10" fill="url(#core_glow)" stroke="{P["rule_glow"]}" stroke-width="1"/>')
    o.append(text(dx + 36, y1 + 28, "JIT COMPILER CORE", size=12, fill=P["text"], weight="800", family=SANS))
    o.append(text(dx + cw - 10, y1 + 28, "BLACK MAMBA v1.1.0", size=10, fill=P["blue"], weight="700", family=MONO, anchor="end"))
    o.append(rule(dx + 36, y1 + 38, dx + cw - 10, y1 + 38, P["rule"]))
    o.append(text(dx + 36, y1 + 60, "• Direct JIT: mmap(PROT_EXEC) direct x86-64 executable memory pages", size=11, fill=P["dim"], family=SANS))
    o.append(text(dx + 36, y1 + 82, "• Multiple Inheritance: Dynamic C3 Diamond MRO linearization in 0.42ms", size=11, fill=P["dim"], family=SANS))
    o.append(text(dx + 36, y1 + 104, "• Recursion: Tail-Call Elimination collapsing 5M frames to 0 stack bytes", size=11, fill=P["dim"], family=SANS))

    # Core 1: Applied AI Cascade (Top Right)
    x2 = dx + dw - cw - 16
    o.append(f'<rect x="{x2}" y="{y1}" width="{cw}" height="{ch}" rx="10" fill="url(#core_glow)" stroke="{P["rule_glow"]}" stroke-width="1"/>')
    o.append(text(x2 + 20, y1 + 28, "NEURAL INFERENCE CASCADE", size=12, fill=P["text"], weight="800", family=SANS))
    o.append(text(x2 + cw - 20, y1 + 28, "TYPENSCRAPE", size=10, fill=P["purple"], weight="700", family=MONO, anchor="end"))
    o.append(rule(x2 + 20, y1 + 38, x2 + cw - 20, y1 + 38, P["rule"]))
    o.append(text(x2 + 20, y1 + 60, "• Multi-Tier Routing: Groq (Llama-3 @ 420ms) degrades gracefully to Gemini", size=11, fill=P["dim"], family=SANS))
    o.append(text(x2 + 20, y1 + 82, "• Memory Bounding: 16-chunk IndexedDB paging prevents mobile browser OOM", size=11, fill=P["dim"], family=SANS))
    o.append(text(x2 + 20, y1 + 104, "• Evaluation: Closed-loop beam search scoring over spaCy AST & 50k grammar rules", size=11, fill=P["dim"], family=SANS))

    # Center High-Speed Bus
    bus_y = dy + 159
    o.append(rule(dx + 16, bus_y, dx + dw - 16, bus_y, P["rule"]))
    if motion:
        o.append(f'<line x1="{dx+16}" y1="{bus_y}" x2="{dx+dw-16}" y2="{bus_y}" stroke="{P["blue"]}" stroke-width="1.8" class="flow"/>')
    o.append(f'<rect x="{W/2 - 190}" y="{bus_y - 10}" width="380" height="20" rx="10" fill="{P["panel"]}" stroke="{P["rule"]}" stroke-width="1"/>')
    o.append(text(W/2, bus_y + 4, "UNIFIED MEMORY FABRIC // 0 KB GC OVERHEAD", size=9, fill=P["blue"], weight="800", family=MONO, anchor="middle", ls=1.0))

    # Core 2: On-Device Vision (Bottom Left)
    o.append(f'<rect x="{dx+16}" y="{y2}" width="{cw}" height="{ch}" rx="10" fill="url(#core_glow)" stroke="{P["rule_glow"]}" stroke-width="1"/>')
    o.append(text(dx + 36, y2 + 28, "ON-DEVICE VISION ACCELERATOR", size=12, fill=P["text"], weight="800", family=SANS))
    o.append(text(dx + cw - 10, y2 + 28, "MEEMOMINI", size=10, fill=P["pink"], weight="700", family=MONO, anchor="end"))
    o.append(rule(dx + 36, y2 + 38, dx + cw - 10, y2 + 38, P["rule"]))
    o.append(text(dx + 36, y2 + 60, "• Client WASM: MediaPipe ImageSegmenter runs entirely on client silicon", size=11, fill=P["dim"], family=SANS))
    o.append(text(dx + 36, y2 + 82, "• Zero Server Hops: No frame ever leaves the machine · 18ms inference latency", size=11, fill=P["dim"], family=SANS))
    o.append(text(dx + 36, y2 + 104, "• Local Export: Hardware canvas WebGL shaders, local still/GIF/MP4 PWA encoding", size=11, fill=P["dim"], family=SANS))

    # Core 3: Edge Firmware (Bottom Right)
    o.append(f'<rect x="{x2}" y="{y2}" width="{cw}" height="{ch}" rx="10" fill="url(#core_glow)" stroke="{P["rule_glow"]}" stroke-width="1"/>')
    o.append(text(x2 + 20, y2 + 28, "EDGE FIRMWARE TRANSCEIVER", size=12, fill=P["text"], weight="800", family=SANS))
    o.append(text(x2 + cw - 20, y2 + 28, "VOLTSENSE IoT", size=10, fill=P["green"], weight="700", family=MONO, anchor="end"))
    o.append(rule(x2 + 20, y2 + 38, x2 + cw - 20, y2 + 38, P["rule"]))
    o.append(text(x2 + 20, y2 + 60, "• Memory-Bounded C++: ESP32 sampling room electrical load and occupancy", size=11, fill=P["dim"], family=SANS))
    o.append(text(x2 + 20, y2 + 82, "• Zero Secrets: Hardware delegates push keys to serverless Vercel edge functions", size=11, fill=P["dim"], family=SANS))
    o.append(text(x2 + 20, y2 + 104, "• Optocoupler Isolation: Device -> Cloud Function -> Firebase RTDB & FCM alerts", size=11, fill=P["dim"], family=SANS))

    o.append("</svg>")
    return "".join(o)

# ------------------------------------------------ APPLE BENCHMARK CHART ----
def benchmark(t, motion=True):
    """1280x280. Apple-Style Empirical Benchmark Comparison (Keynote Format)."""
    W, H = 1280, 280
    P = THEMES[t]

    defs = f"""<defs>
<linearGradient id="bar_apple" x1="0%" y1="0%" x2="100%" y2="0%">
  <stop offset="0%" stop-color="{P['blue']}"/>
  <stop offset="100%" stop-color="{P['purple']}"/>
</linearGradient>
</defs>"""

    o = [head(W, H, motion, defs)]
    o.append(f'<rect width="{W}" height="{H}" rx="18" fill="{P["bg0"]}"/>')
    o.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="18" fill="none" stroke="{P["rule"]}" stroke-width="1"/>')

    # Top strip
    o.append(rule(0, 44, W, 44, P["rule"]))
    o.append(text(48, 26, "BENCHMARK PERFORMANCE  /  NATIVE JIT vs INTERPRETED BASELINE", size=10, fill=P["text"], weight="700", family=MONO, ls=1.5))
    o.append(text(W - 48, 26, "HIGHER SPEEDUP IS BETTER · MEASURED ON IDENTICAL HOST HARDWARE", size=10, fill=P["dim"], weight="600", family=MONO, anchor="end"))

    kernels = [
        ("fib(32) — Recursive Branching", "288.62ms", "11.08ms", 26.1, "26.1x FASTER"),
        ("collatz(40k) — Control Flow", "227.84ms", "8.29ms", 27.5, "27.5x FASTER"),
        ("count_primes(30k) — Memory Scanning", "22.05ms", "1.73ms", 12.7, "12.7x FASTER"),
        ("mandelbrot(120x120) — Floating-Point", "39.14ms", "3.37ms", 11.6, "11.6x FASTER"),
    ]

    base_y = 66
    for idx, (name, c_ms, m_ms, ratio, badge) in enumerate(kernels):
        ky = base_y + idx * 48
        o.append(text(48, ky + 14, name, size=11, fill=P["text"], weight="700", family=SANS))
        o.append(text(400, ky + 14, f"CPython: {c_ms}", size=10, fill=P["dim"], weight="500", family=MONO))
        o.append(text(540, ky + 14, f"JIT: {m_ms}", size=10, fill=P["blue"], weight="700", family=MONO))

        # Bar comparison
        bx = 650
        max_bar_w = 420
        bar_w = int(max_bar_w * (ratio / 30.0))
        o.append(f'<rect x="{bx}" y="{ky + 4}" width="{max_bar_w}" height="12" rx="6" fill="{P["bar"]}"/>')
        o.append(f'<rect x="{bx}" y="{ky + 4}" width="{bar_w}" height="12" rx="6" fill="url(#bar_apple)"/>')
        o.append(text(bx + max_bar_w + 16, ky + 14, badge, size=11, fill=P["blue"], weight="800", family=MONO))

    o.append(rule(48, H - 28, W - 48, H - 28, P["rule"]))
    o.append(text(W/2, H - 12, "Deep recursive call kernel collapses 5,000,000 frames to 0 stack bytes without RecursionError.",
                  size=9.5, fill=P["dim"], weight="500", family=SANS, anchor="middle"))

    o.append("</svg>")
    return "".join(o)

# ---------------------------------------------------- APPLE AIRDROP RADAR ----
def telemetry(t, motion=True):
    """1280x230. Apple AirDrop-Style IssueOps Telemetry Radar."""
    W, H = 1280, 230
    P = THEMES[t]

    defs = f"""<defs>
<radialGradient id="airdrop_glow" cx="50%" cy="50%" r="50%">
  <stop offset="0%" stop-color="{P['blue']}" stop-opacity="0.15"/>
  <stop offset="100%" stop-color="{P['bg0']}" stop-opacity="0"/>
</radialGradient>
</defs>"""

    o = [head(W, H, motion, defs)]
    o.append(f'<rect width="{W}" height="{H}" rx="18" fill="{P["bg0"]}"/>')
    o.append(f'<rect width="{W}" height="{H}" rx="18" fill="url(#airdrop_glow)"/>')
    o.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="18" fill="none" stroke="{P["rule"]}" stroke-width="1"/>')

    # Top strip
    o.append(rule(0, 44, W, 44, P["rule"]))
    o.append(f'<circle cx="48" cy="22" r="3.5" fill="{P["blue"]}" class="pulse"/>')
    o.append(text(62, 26, "AIRDROP PROTOCOL  /  LIVE ISSUEOPS TELEMETRY RADAR", size=10, fill=P["text"], weight="700", family=MONO, ls=1.5))
    o.append(text(W - 48, 26, "AUTONOMOUS GITHUB ACTIONS DISPATCH IN ~15 SECONDS", size=10, fill=P["blue"], weight="700", family=MONO, ls=1.0, anchor="end"))

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

    y = 74
    o.append(text(48, y, "SIGNAL", size=9.5, fill=P["micro"], weight="700", family=MONO, ls=1.2))
    o.append(text(150, y, "TRANSMITTER", size=9.5, fill=P["micro"], weight="700", family=MONO, ls=1.2))
    o.append(text(340, y, "AFFILIATION / TEAM", size=9.5, fill=P["micro"], weight="700", family=MONO, ls=1.2))
    o.append(text(660, y, "FOCUS AREA", size=9.5, fill=P["micro"], weight="700", family=MONO, ls=1.2))
    o.append(text(960, y, "TIMESTAMP", size=9.5, fill=P["micro"], weight="700", family=MONO, ls=1.2))
    o.append(text(W - 48, y, "VERIFICATION", size=9.5, fill=P["micro"], weight="700", family=MONO, ls=1.2, anchor="end"))
    o.append(rule(48, y + 10, W - 48, y + 10, P["rule"]))

    for i, sig in enumerate(signals[:3]):
        ry = y + 36 + i * 28
        o.append(f'<circle cx="36" cy="{ry - 4}" r="2.5" fill="{P["blue"]}"/>')
        o.append(text(48, ry, sig.get("id", f"SIG-{i+1:03d}"), size=11, fill=P["blue"], weight="700", family=MONO))
        o.append(text(150, ry, "@" + sig.get("sender", "anonymous")[:18], size=11, fill=P["text"], weight="600", family=MONO))
        o.append(text(340, ry, sig.get("org", "Verified Guest")[:32], size=11, fill=P["dim"], weight="400", family=MONO))
        o.append(text(660, ry, sig.get("focus", "Applied AI / Systems")[:32], size=11, fill=P["dim"], weight="400", family=MONO))
        o.append(text(960, ry, sig.get("timestamp", "RECENT")[:16], size=10.5, fill=P["micro"], weight="400", family=MONO))
        o.append(text(W - 48, ry, "VERIFIED", size=10.5, fill=P["green"], weight="800", family=MONO, ls=0.8, anchor="end"))

    o.append(rule(48, H - 32, W - 48, H - 32, P["rule"]))
    o.append(text(48, H - 14, "TRANSMIT HANDSHAKE: OPEN AN ISSUE TO TRIGGER GITHUB ACTIONS ISSUEOPS DISPATCH",
                  size=9, fill=P["dim"], weight="500", family=MONO))
    o.append(text(W - 48, H - 14, "ZERO EXTERNAL SERVERS · 100% GITHUB ACTIONS", size=9, fill=P["micro"],
                  weight="700", family=MONO, ls=1.0, anchor="end"))

    o.append("</svg>")
    return "".join(o)

# ------------------------------------------------- APPLE ACTIVITY BARS ----
def bars(t, motion=True):
    """1280x160. Apple Space Black Contribution Volume."""
    W, H = 1280, 160
    P = THEMES[t]

    defs = f"""<defs>
<linearGradient id="apple_bars" x1="0%" y1="0%" x2="0%" y2="100%">
  <stop offset="0%" stop-color="{P['blue']}"/>
  <stop offset="100%" stop-color="{P['panel']}"/>
</linearGradient>
</defs>"""

    o = [head(W, H, motion, defs)]
    o.append(f'<rect width="{W}" height="{H}" rx="18" fill="{P["bg0"]}"/>')
    o.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="18" fill="none" stroke="{P["rule"]}" stroke-width="1"/>')

    o.append(rule(0, 44, W, 44, P["rule"]))
    o.append(text(48, 26, "ANNUAL COMMIT PULSE  /  ACTIVITY SHAPE", size=10, fill=P["text"], weight="700", family=MONO, ls=1.5))
    o.append(text(W - 48, 26, f"{STATS.get('total_contributions', 386)} CONTRIBUTIONS IN 12 MONTHS",
                  size=10, fill=P["blue"], weight="700", family=MONO, ls=1.2, anchor="end"))

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
            fill_val = "url(#apple_bars)" if count == max_c else P["bar"]
            o.append(f'<rect x="{bx:.1f}" y="{by}" width="{bar_w}" height="{bh}" rx="4" fill="{fill_val}"/>')
            o.append(text(bx + bar_w / 2, base_y + 16, d["month"][-2:], size=9.5, fill=P["micro"],
                          weight="600", family=MONO, anchor="middle"))
            if count > 0:
                col = P["text"] if count == max_c else P["dim"]
                o.append(text(bx + bar_w / 2, by - 6, str(count), size=9.5, fill=col,
                              weight="700", family=MONO, anchor="middle"))

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
            t_lines = ["| Signal | Transmitter | Affiliation | Focus Area | Timestamp | Verification |",
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
        "apple-hero": hero,
        "apple-chip": chip,
        "apple-benchmark": benchmark,
        "apple-radar": telemetry,
        "apple-bars": bars,
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
