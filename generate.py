"""
Generates precision kinetic systems engineering SVG assets for Kian's profile.
Motion-first: fluid waveforms, animated gyroscopes, dynamic circuit buses,
kinetic benchmark laser streams, live 360° radar sweeper, and spectrum equalizer.
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

LANG_COLORS = {
    "Python": "#3B82F6", "TypeScript": "#06B6D4", "JavaScript": "#EAB308",
    "HTML": "#EF4444", "CSS": "#8B5CF6", "Jupyter Notebook": "#F97316",
    "C++": "#EC4899", "C": "#64748B", "LLVM": "#10B981", "WebAssembly": "#0284C7",
    "OpenSCAD": "#F59E0B", "Shell": "#10B981",
}

# Precision Systems Architecture Theme (Obsidian & Laser Cobalt / Cyan)
THEMES = {
    "dark": {
        "bg0": "#08080A", "bg1": "#0F0F14", "panel": "#14141C", "card": "#181824",
        "rule": "#222230", "rule_glow": "#2E2E42",
        "text": "#F8FAFC", "dim": "#94A3B8", "micro": "#64748B", "faint": "#161622",
        "accent": "#06B6D4", "accent_end": "#2563EB", "accent_bright": "#38BDF8",
        "blue": "#3B82F6", "purple": "#8B5CF6", "pink": "#EC4899",
        "green": "#10B981", "amber": "#F59E0B", "bar": "#1E1E2C",
        "silver": "#CBD5E1",
    },
    "light": {
        "bg0": "#FFFFFF", "bg1": "#F8FAFC", "panel": "#FFFFFF", "card": "#F1F5F9",
        "rule": "#E2E8F0", "rule_glow": "#CBD5E1",
        "text": "#0F172A", "dim": "#64748B", "micro": "#94A3B8", "faint": "#F8FAFC",
        "accent": "#0284C7", "accent_end": "#1D4ED8", "accent_bright": "#0369A1",
        "blue": "#2563EB", "purple": "#7C3AED", "pink": "#DB2777",
        "green": "#059669", "amber": "#D97706", "bar": "#E2E8F0",
        "silver": "#475569",
    },
}

SANS = ("-apple-system,BlinkMacSystemFont,'Inter','SF Pro Display','SF Pro Text','Segoe UI',Roboto,Helvetica,Arial,sans-serif")
MONO = ("ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace")

CSS = """
.spin{transform-box:fill-box;transform-origin:center;animation:spin 14s linear infinite}
.spin_rev{transform-box:fill-box;transform-origin:center;animation:spin_rev 9s linear infinite}
.spin_fast{transform-box:fill-box;transform-origin:center;animation:spin 4s linear infinite}
.pulse{animation:pulse 2.2s ease-in-out infinite}
.pulse_glow{transform-box:fill-box;transform-origin:center;animation:pulse_glow 2.5s ease-in-out infinite}
.glow{animation:glow 3s ease-in-out infinite alternate}
.flow{stroke-dasharray:8 6;animation:flow 1.4s linear infinite}
.flow_fast{stroke-dasharray:12 8;animation:flow_fast 0.9s linear infinite}
.flow_slow{stroke-dasharray:16 12;animation:flow 2.8s linear infinite}
.radar{transform-box:fill-box;transform-origin:center;animation:spin 3.6s linear infinite}
.ping1{animation:ping 3.6s cubic-bezier(0,0,.2,1) infinite}
.ping2{animation:ping 3.6s cubic-bezier(0,0,.2,1) infinite 1.2s}
.ping3{animation:ping 3.6s cubic-bezier(0,0,.2,1) infinite 2.4s}
.scan{animation:scan 3.2s ease-in-out infinite}
.laser_head{animation:laser_pulse 1.4s ease-in-out infinite alternate}
.eq1{transform-box:fill-box;transform-origin:bottom;animation:eq 1.8s ease-in-out infinite alternate}
.eq2{transform-box:fill-box;transform-origin:bottom;animation:eq 2.2s ease-in-out infinite alternate .4s}
.eq3{transform-box:fill-box;transform-origin:bottom;animation:eq 1.5s ease-in-out infinite alternate .8s}

@keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}
@keyframes spin_rev{0%{transform:rotate(360deg)}100%{transform:rotate(0deg)}}
@keyframes flow{to{stroke-dashoffset:-28}}
@keyframes flow_fast{to{stroke-dashoffset:-40}}
@keyframes pulse{0%,100%{opacity:0.35;transform:scale(0.96)}50%{opacity:1;transform:scale(1.04)}}
@keyframes pulse_glow{0%,100%{opacity:0.4;transform:scale(0.97)}50%{opacity:1;transform:scale(1.03)}}
@keyframes glow{0%{opacity:0.6}100%{opacity:1}}
@keyframes ping{0%{r:2px;opacity:1;stroke-width:2px}80%,100%{r:26px;opacity:0;stroke-width:0.5px}}
@keyframes scan{0%,100%{transform:translateY(0);opacity:0.2}50%{transform:translateY(84px);opacity:0.9}}
@keyframes laser_pulse{0%,100%{opacity:0.6;r:4px}50%{opacity:1;r:7px}}
@keyframes eq{0%{transform:scaleY(0.72)}50%{transform:scaleY(1.04)}100%{transform:scaleY(0.85)}}
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

# ------------------------------------------------ KINETIC HERO ----
def hero(t, motion=True):
    """1280x320. Motion-First Kinetic Waveform & Gyroscope Hero."""
    W, H = 1280, 320
    P = THEMES[t]

    defs = f"""<defs>
<linearGradient id="sys_gradient" x1="0%" y1="0%" x2="100%" y2="0%">
  <stop offset="0%" stop-color="{P['accent_end']}"/>
  <stop offset="60%" stop-color="{P['accent']}"/>
  <stop offset="100%" stop-color="{P['accent_bright']}"/>
</linearGradient>
<radialGradient id="gyro_glow" cx="50%" cy="50%" r="50%">
  <stop offset="0%" stop-color="{P['accent']}" stop-opacity="0.25"/>
  <stop offset="100%" stop-color="{P['bg0']}" stop-opacity="0"/>
</radialGradient>
<radialGradient id="vignette" cx="50%" cy="50%" r="80%">
  <stop offset="0%" stop-color="{P['panel']}" stop-opacity="0.4"/>
  <stop offset="100%" stop-color="{P['bg0']}" stop-opacity="1"/>
</radialGradient>
</defs>"""

    o = [head(W, H, motion, defs)]
    o.append(f'<rect width="{W}" height="{H}" rx="16" fill="{P["bg0"]}"/>')
    o.append(f'<rect width="{W}" height="{H}" rx="16" fill="url(#vignette)"/>')
    o.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{P["rule"]}" stroke-width="1"/>')

    # Background Coordinate Crosshairs
    for cx in (160, 320, 960, 1120):
        for cy in (70, 150, 230):
            o.append(f'<path d="M{cx-4} {cy}h8M{cx} {cy-4}v8" stroke="{P["rule_glow"]}" stroke-width="0.8" opacity="0.4"/>')

    # Hypnotic Kinetic Oscilloscope Waveforms (undulating through center)
    w_y = 150
    # Wave 1: Fast Cyan Carrier Wave
    d1 = "M0 150 Q160 110, 320 150 T640 150 T960 150 T1280 150"
    o.append(f'<path d="{d1}" stroke="{P["accent"]}" stroke-width="2" fill="none" opacity="0.85" class="flow_fast"/>')
    # Wave 2: Cobalt Harmonic Wave
    d2 = "M0 150 Q160 190, 320 150 T640 150 T960 150 T1280 150"
    o.append(f'<path d="{d2}" stroke="{P["accent_end"]}" stroke-width="1.6" fill="none" opacity="0.65" class="flow"/>')
    # Wave 3: Ambient Violet Envelope
    d3 = "M0 150 Q320 80, 640 150 T1280 150"
    o.append(f'<path d="{d3}" stroke="{P["purple"]}" stroke-width="1.2" fill="none" opacity="0.45" class="flow_slow"/>')

    # Central Kinetic Gyroscope Reticle with [ K ] Monogram Emblem
    gx, gy = W / 2, 88
    o.append(f'<circle cx="{gx}" cy="{gy}" r="45" fill="url(#gyro_glow)"/>')
    # Outer Rotating Ticks Ring
    o.append(f'<circle cx="{gx}" cy="{gy}" r="42" stroke="{P["rule_glow"]}" stroke-width="1.2" stroke-dasharray="3 6" fill="none" class="spin"/>')
    # Counter-Rotating Ring with Orbital Photons
    o.append(f'<g class="spin_rev">')
    o.append(f'<circle cx="{gx}" cy="{gy}" r="32" stroke="{P["accent"]}" stroke-width="1" stroke-dasharray="14 8 4 8" fill="none" opacity="0.7"/>')
    o.append(f'<circle cx="{gx+32}" cy="{gy}" r="2.5" fill="{P["accent"]}"/>')
    o.append(f'<circle cx="{gx-32}" cy="{gy}" r="2.5" fill="{P["accent_bright"]}"/>')
    o.append(f'</g>')
    # Center Illuminated Monogram Badge
    o.append(f'<circle cx="{gx}" cy="{gy}" r="16" fill="{P["card"]}" stroke="{P["accent"]}" stroke-width="1.4" class="pulse"/>')
    o.append(text(gx, gy + 5, "K", size=13, fill=P["accent_bright"], weight="900", family=MONO, anchor="middle"))

    # Top Status Pill
    pill_w = 400
    o.append(f'<rect x="{W/2 - pill_w/2}" y="18" width="{pill_w}" height="24" rx="12" fill="{P["card"]}" stroke="{P["rule_glow"]}" stroke-width="1"/>')
    o.append(f'<circle cx="{W/2 - pill_w/2 + 16}" cy="30" r="3.5" fill="{P["green"]}" class="pulse"/>')
    o.append(text(W/2 - pill_w/2 + 28, 34, "KIAN B. // SYSTEMS & COMPILERS ARCHITECTURE", size=9, fill=P["text"], weight="700", family=MONO, ls=1.1))
    o.append(text(W/2 + pill_w/2 - 16, 34, "ACTIVE", size=9, fill=P["green"], weight="800", family=MONO, anchor="end"))

    # Display Typography
    o.append(text(W/2, 146, "KIAN B.", size=38, fill=P["text"], weight="900", family=SANS, anchor="middle", ls=6.0))
    # Glowing Laser Underline with Sweeping Comet Head
    o.append(f'<line x1="{W/2 - 180}" y1="158" x2="{W/2 + 180}" y2="158" stroke="{P["rule_glow"]}" stroke-width="1"/>')
    o.append(f'<line x1="{W/2 - 160}" y1="158" x2="{W/2 + 160}" y2="158" stroke="{P["accent"]}" stroke-width="2" class="flow_fast"/>')
    o.append(f'<circle cx="{W/2}" cy="158" r="4" fill="{P["accent_bright"]}" class="laser_head"/>')

    # Subtitle
    o.append(text(W/2, 184, "PRECISION COMPILERS · EMBEDDED SILICON · ZERO-ALLOC APPLIED AI",
                  size=10.5, fill=P["dim"], weight="700", family=MONO, anchor="middle", ls=1.6))
    o.append(text(W/2, 204, "Where abstraction has a measurable cost: know what the layer below actually costs.",
                  size=12.5, fill=P["micro"], weight="400", family=SANS, anchor="middle", ls=-0.1))

    # Bottom 4 Kinetic Graphic Gauges
    o.append(rule(48, 230, W - 48, 230, P["rule"]))
    pillars = [
        ("26.1x", "NATIVE JIT SPEEDUP", "led"),
        ("0 KB", "ZERO GC PAUSES", "scope"),
        ("18 ms", "ON-DEVICE WASM VISION", "wave"),
        ("0 secrets", "ISOLATED FIRMWARE PUSH", "shield"),
    ]

    for idx, (stat, label, gtype) in enumerate(pillars):
        px = 48 + idx * 296
        # Graphical Meter Icon
        if gtype == "led":
            # 8-segment LED meter bar
            for s in range(8):
                sx = px + s * 11
                s_op = "1.0" if s < 6 else "0.35"
                s_cls = ' class="pulse"' if s >= 5 else ""
                o.append(f'<rect x="{sx}" y="250" width="8" height="6" rx="1.5" fill="{P["accent"]}" opacity="{s_op}"{s_cls}/>')
        elif gtype == "scope":
            # Flatline oscilloscope line with locked zero badge
            o.append(f'<line x1="{px}" y1="253" x2="{px+80}" y2="253" stroke="{P["green"]}" stroke-width="2"/>')
            o.append(f'<circle cx="{px}" cy="253" r="2.5" fill="{P["green"]}"/>')
            o.append(f'<circle cx="{px+80}" cy="253" r="2.5" fill="{P["green"]}"/>')
            o.append(f'<rect x="{px+26}" y="247" width="28" height="12" rx="3" fill="{P["panel"]}" stroke="{P["green"]}" stroke-width="1"/>')
            o.append(text(px+40, 256, "0.00", size=7.5, fill=P["green"], weight="800", family=MONO, anchor="middle"))
        elif gtype == "wave":
            # Heartbeat / high-frequency pulse spike
            w_path = f"M{px} 253 h16 l6 -10 l8 18 l6 -12 l6 4 h38"
            o.append(f'<path d="{w_path}" stroke="{P["accent_bright"]}" stroke-width="1.8" fill="none" class="flow"/>')
        elif gtype == "shield":
            # Cryptographic shield vector with pulse
            o.append(f'<path d="M{px+10} 247 h20 l10 8 v10 c0 10 -15 16 -20 18 c-5 -2 -20 -8 -20 -18 v-10 z" stroke="{P["purple"]}" stroke-width="1.2" fill="none" class="pulse"/>')
            o.append(f'<circle cx="{px+20}" cy="258" r="3" fill="{P["accent"]}"/>')

        o.append(text(px, 286, stat, size=18, fill=P["text"], weight="900", family=SANS, ls=-0.5))
        o.append(text(px, 304, label, size=9.5, fill=P["dim"], weight="700", family=MONO, ls=0.8))

    o.append("</svg>")
    return "".join(o)

# ------------------------------------------------ KINETIC TOPOLOGY ----
def topology(t, motion=True):
    """1280x420. Kinetic Microarchitecture Silicon Die & Active Bus Topology."""
    W, H = 1280, 420
    P = THEMES[t]

    defs = f"""<defs>
<linearGradient id="bus_glow" x1="0%" y1="0%" x2="100%" y2="0%">
  <stop offset="0%" stop-color="{P['accent_end']}"/>
  <stop offset="50%" stop-color="{P['accent']}"/>
  <stop offset="100%" stop-color="{P['accent_bright']}"/>
</linearGradient>
<radialGradient id="die_center_glow" cx="50%" cy="50%" r="50%">
  <stop offset="0%" stop-color="{P['accent']}" stop-opacity="0.35"/>
  <stop offset="100%" stop-color="{P['bg0']}" stop-opacity="0"/>
</radialGradient>
<linearGradient id="node_surface" x1="0%" y1="0%" x2="100%" y2="100%">
  <stop offset="0%" stop-color="{P['panel']}"/>
  <stop offset="100%" stop-color="{P['card']}"/>
</linearGradient>
</defs>"""

    o = [head(W, H, motion, defs)]
    o.append(f'<rect width="{W}" height="{H}" rx="16" fill="{P["bg0"]}"/>')
    o.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{P["rule"]}" stroke-width="1"/>')

    # Header Strip
    o.append(rule(0, 44, W, 44, P["rule"]))
    o.append(text(48, 26, "HETEROGENEOUS COMPUTATIONAL FABRIC  /  SUBSYSTEM TOPOLOGY", size=10, fill=P["text"], weight="700", family=MONO, ls=1.5))
    o.append(text(W - 48, 26, "LIVE INTERCONNECT TRAFFIC · ZERO GC · ZERO ALLOCATION OVERHEAD", size=10, fill=P["accent"], weight="700", family=MONO, ls=1.0, anchor="end"))

    # Silicon Die Frame
    dx, dy, dw, dh = 48, 62, W - 96, 332
    o.append(f'<rect x="{dx}" y="{dy}" width="{dw}" height="{dh}" rx="14" fill="{P["bg1"]}" stroke="{P["rule_glow"]}" stroke-width="1.2"/>')

    # Active Bus Interconnect Lines (Connecting center hub to 4 quadrants)
    cx, cy = W / 2, dy + dh / 2
    cw = 560
    ch = 136
    y1 = dy + 18
    y2 = dy + 178

    # Bus Traces with traveling photon packets
    q1_cx, q1_cy = dx + 16 + cw / 2, y1 + ch / 2
    q2_cx, q2_cy = dx + dw - cw - 16 + cw / 2, y1 + ch / 2
    q3_cx, q3_cy = dx + 16 + cw / 2, y2 + ch / 2
    q4_cx, q4_cy = dx + dw - cw - 16 + cw / 2, y2 + ch / 2

    for qx, qy in ((q1_cx, q1_cy), (q2_cx, q2_cy), (q3_cx, q3_cy), (q4_cx, q4_cy)):
        o.append(f'<line x1="{cx}" y1="{cy}" x2="{qx}" y2="{qy}" stroke="{P["rule_glow"]}" stroke-width="1.2"/>')
        o.append(f'<line x1="{cx}" y1="{cy}" x2="{qx}" y2="{qy}" stroke="{P["accent"]}" stroke-width="2" class="flow"/>')

    # Central Master Interconnect Die Hub
    o.append(f'<circle cx="{cx}" cy="{cy}" r="45" fill="url(#die_center_glow)"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="34" stroke="{P["accent_end"]}" stroke-width="1.5" stroke-dasharray="6 6" fill="{P["panel"]}" class="spin"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="22" stroke="{P["accent"]}" stroke-width="1.8" fill="{P["card"]}" class="spin_rev"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="8" fill="{P["accent_bright"]}" class="pulse_glow"/>')

    # Central Fabric Pill
    badge_w = 340
    o.append(f'<rect x="{cx - badge_w/2}" y="{cy + 42}" width="{badge_w}" height="20" rx="10" fill="{P["panel"]}" stroke="{P["rule_glow"]}" stroke-width="1"/>')
    o.append(text(cx, cy + 55, "UNIFIED MEMORY FABRIC // ZERO-ALLOC BUS", size=8.5, fill=P["accent"], weight="800", family=MONO, anchor="middle", ls=1.0))

    # --- QUADRANT 1: JIT Compiler Pipeline (Top Left) ---
    o.append(f'<rect x="{dx+16}" y="{y1}" width="{cw}" height="{ch}" rx="10" fill="url(#node_surface)" stroke="{P["rule_glow"]}" stroke-width="1"/>')
    o.append(text(dx + 32, y1 + 24, "NATIVE JIT COMPILER PIPELINE", size=11, fill=P["text"], weight="800", family=SANS))
    o.append(text(dx + cw - 16, y1 + 24, "BLACK MAMBA v1.1.0", size=9.5, fill=P["accent"], weight="700", family=MONO, anchor="end"))
    o.append(rule(dx + 32, y1 + 34, dx + cw - 16, y1 + 34, P["rule"]))

    # Graphical 4-Stage Execution Pipeline
    p_stages = [("AST DESUGAR", 100), ("C3 MRO", 90), ("TCO O(1)", 85), ("x86-64 NATIVE", 110)]
    sx = dx + 32
    sy = y1 + 46
    for i, (stage, sw) in enumerate(p_stages):
        o.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="26" rx="5" fill="{P["panel"]}" stroke="{P["rule_glow"]}" stroke-width="1"/>')
        o.append(text(sx + sw / 2, sy + 17, stage, size=8.5, fill=P["text"], weight="700", family=MONO, anchor="middle"))
        if i < 3:
            arrow_x = sx + sw
            o.append(f'<line x1="{arrow_x}" y1="{sy+13}" x2="{arrow_x+16}" y2="{sy+13}" stroke="{P["accent"]}" stroke-width="1.8" class="flow_fast"/>')
            sx += sw + 16
        else:
            sx += sw

    # Micro Specs
    o.append(text(dx + 32, y1 + 94, "• Direct JIT Execution: mmap(PROT_EXEC) maps native machine code with zero pauses", size=10, fill=P["dim"], family=SANS))
    o.append(text(dx + 32, y1 + 112, "• C3 Diamond Resolution in 0.42ms · Collapses 5,000,000 recursive call frames to O(1)", size=10, fill=P["dim"], family=SANS))

    # --- QUADRANT 2: Stochastic Resilience Cascade (Top Right) ---
    x2 = dx + dw - cw - 16
    o.append(f'<rect x="{x2}" y="{y1}" width="{cw}" height="{ch}" rx="10" fill="url(#node_surface)" stroke="{P["rule_glow"]}" stroke-width="1"/>')
    o.append(text(x2 + 20, y1 + 24, "STOCHASTIC RESILIENCE CASCADE", size=11, fill=P["text"], weight="800", family=SANS))
    o.append(text(x2 + cw - 20, y1 + 24, "TYPENSCRAPE", size=9.5, fill=P["purple"], weight="700", family=MONO, anchor="end"))
    o.append(rule(x2 + 20, y1 + 34, x2 + cw - 20, y1 + 34, P["rule"]))

    # Graphical Routing Cluster & Memory Buffer Grid
    # Primary Node: Groq Llama-3
    o.append(f'<rect x="{x2+20}" y="{y1+46}" width="150" height="26" rx="5" fill="{P["panel"]}" stroke="{P["green"]}" stroke-width="1"/>')
    o.append(f'<circle cx="{x2+32}" cy="{y1+59}" r="3" fill="{P["green"]}" class="pulse"/>')
    o.append(text(x2 + 42, y1 + 63, "Groq Llama-3 @ 420ms", size=8.5, fill=P["text"], weight="700", family=MONO))
    # Failover Bus Line
    o.append(f'<path d="M{x2+170} {y1+59} h24 l8 12 h18" stroke="{P["purple"]}" stroke-width="1.5" fill="none" class="flow"/>')
    # Fallback Node: Gemini
    o.append(f'<rect x="{x2+220}" y="{y1+58}" width="110" height="26" rx="5" fill="{P["panel"]}" stroke="{P["purple"]}" stroke-width="1"/>')
    o.append(text(x2 + 275, y1 + 75, "Gemini Fallback", size=8.5, fill=P["purple"], weight="700", family=MONO, anchor="middle"))

    # 16-Chunk IndexedDB Paging Grid (4x4)
    gx_start = x2 + 355
    gy_start = y1 + 46
    for row in range(2):
        for col in range(8):
            cell_x = gx_start + col * 12
            cell_y = gy_start + row * 12
            c_fill = P["accent"] if (col + row) % 2 == 0 else P["panel"]
            o.append(f'<rect x="{cell_x}" y="{cell_y}" width="9" height="9" rx="1.5" fill="{c_fill}" stroke="{P["rule_glow"]}" stroke-width="0.6"/>')

    o.append(text(x2 + 20, y1 + 102, "• Multi-Tier Stochastic Routing: Groq cascades smoothly to Gemini on 429 rate limit", size=10, fill=P["dim"], family=SANS))
    o.append(text(x2 + 20, y1 + 120, "• Memory Bounding: 16-chunk IndexedDB paging prevents mobile browser OOM", size=10, fill=P["dim"], family=SANS))

    # --- QUADRANT 3: On-Device Vision Accelerator (Bottom Left) ---
    o.append(f'<rect x="{dx+16}" y="{y2}" width="{cw}" height="{ch}" rx="10" fill="url(#node_surface)" stroke="{P["rule_glow"]}" stroke-width="1"/>')
    o.append(text(dx + 32, y2 + 24, "ON-DEVICE VISION ACCELERATOR", size=11, fill=P["text"], weight="800", family=SANS))
    o.append(text(dx + cw - 16, y2 + 24, "MEEMOMINI", size=9.5, fill=P["pink"], weight="700", family=MONO, anchor="end"))
    o.append(rule(dx + 32, y2 + 34, dx + cw - 16, y2 + 34, P["rule"]))

    # Graphical Computer Vision Viewfinder & Scanning Laser Line
    vx = dx + 32
    vy = y2 + 46
    vw = 120
    vh = 64
    o.append(f'<rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" rx="4" fill="{P["panel"]}" stroke="{P["rule_glow"]}" stroke-width="0.8"/>')
    # Viewfinder Corner Brackets
    o.append(f'<path d="M{vx+2} {vy+8}v-6h6 M{vx+vw-8} {vy+2}h6v6 M{vx+2} {vy+vh-8}v6h6 M{vx+vw-8} {vy+vh-2}h6v-6" stroke="{P["pink"]}" stroke-width="1.4" fill="none"/>')
    # 8x4 Feature Matrix
    for r in range(4):
        for c in range(8):
            o.append(f'<circle cx="{vx+16+c*12}" cy="{vy+12+r*13}" r="1.5" fill="{P["rule_glow"]}"/>')
    # Rotating Tracking Reticle in Center
    o.append(f'<circle cx="{vx+vw/2}" cy="{vy+vh/2}" r="14" stroke="{P["pink"]}" stroke-width="1" stroke-dasharray="6 4" fill="none" class="spin_fast"/>')
    # Scanning Horizontal Laser Line
    o.append(f'<line x1="{vx+4}" y1="{vy+vh/2}" x2="{vx+vw-4}" y2="{vy+vh/2}" stroke="{P["pink"]}" stroke-width="1.8" class="scan"/>')

    # Vision Specs
    o.append(text(dx + 168, y2 + 62, "MediaPipe WASM Segmenter", size=11, fill=P["text"], weight="700", family=SANS))
    o.append(text(dx + 168, y2 + 80, "18ms Latency · Zero Exfiltration", size=10, fill=P["pink"], weight="700", family=MONO))
    o.append(text(dx + 168, y2 + 98, "Client-side WebGL canvas filters & local GIF/MP4 export", size=9.5, fill=P["dim"], family=SANS))

    # --- QUADRANT 4: Edge Firmware Transceiver (Bottom Right) ---
    o.append(f'<rect x="{x2}" y="{y2}" width="{cw}" height="{ch}" rx="10" fill="url(#node_surface)" stroke="{P["rule_glow"]}" stroke-width="1"/>')
    o.append(text(x2 + 20, y2 + 24, "EDGE FIRMWARE TRANSCEIVER", size=11, fill=P["text"], weight="800", family=SANS))
    o.append(text(x2 + cw - 20, y2 + 24, "VOLTSENSE IoT", size=9.5, fill=P["green"], weight="700", family=MONO, anchor="end"))
    o.append(rule(x2 + 20, y2 + 34, x2 + cw - 20, y2 + 34, P["rule"]))

    # Graphical ESP32 Microcontroller & Animated Radio Broadcast
    ex = x2 + 20
    ey = y2 + 48
    # Silicon Chip Package
    o.append(f'<rect x="{ex}" y="{ey}" width="70" height="60" rx="4" fill="{P["panel"]}" stroke="{P["green"]}" stroke-width="1"/>')
    o.append(text(ex + 35, ey + 34, "ESP32", size=10, fill=P["green"], weight="800", family=MONO, anchor="middle"))
    # Chip Pins
    for p in range(4):
        o.append(f'<line x1="{ex-6}" y1="{ey+12+p*12}" x2="{ex}" y2="{ey+12+p*12}" stroke="{P["rule_glow"]}" stroke-width="1.5"/>')
        o.append(f'<line x1="{ex+70}" y1="{ey+12+p*12}" x2="{ex+76}" y2="{ey+12+p*12}" stroke="{P["rule_glow"]}" stroke-width="1.5"/>')

    # Animated Radio Broadcast Waves
    rx_center = ex + 76
    ry_center = ey + 30
    o.append(f'<path d="M{rx_center+8} {ry_center-12} a16 16 0 0 1 0 24" stroke="{P["green"]}" stroke-width="1.4" fill="none" class="ping1"/>')
    o.append(f'<path d="M{rx_center+18} {ry_center-20} a26 26 0 0 1 0 40" stroke="{P["green"]}" stroke-width="1.4" fill="none" class="ping2"/>')
    o.append(f'<path d="M{rx_center+28} {ry_center-28} a36 36 0 0 1 0 56" stroke="{P["green"]}" stroke-width="1.2" fill="none" class="ping3"/>')

    # Firmware Specs
    o.append(text(x2 + 160, y2 + 62, "Memory-Bounded C++ on ESP32", size=11, fill=P["text"], weight="700", family=SANS))
    o.append(text(x2 + 160, y2 + 80, "Zero-Secret Serverless Bridge", size=10, fill=P["green"], weight="700", family=MONO))
    o.append(text(x2 + 160, y2 + 98, "Optocoupler relay isolation & direct FCM edge dispatch", size=9.5, fill=P["dim"], family=SANS))

    o.append("</svg>")
    return "".join(o)

# ------------------------------------------------ KINETIC BENCHMARK ----
def benchmark(t, motion=True):
    """1280x280. Kinetic Benchmark Velocity Streams."""
    W, H = 1280, 280
    P = THEMES[t]

    defs = f"""<defs>
<linearGradient id="bench_stream" x1="0%" y1="0%" x2="100%" y2="0%">
  <stop offset="0%" stop-color="{P['accent_end']}"/>
  <stop offset="60%" stop-color="{P['accent']}"/>
  <stop offset="100%" stop-color="{P['accent_bright']}"/>
</linearGradient>
<radialGradient id="laser_glow" cx="50%" cy="50%" r="50%">
  <stop offset="0%" stop-color="{P['accent_bright']}" stop-opacity="0.8"/>
  <stop offset="100%" stop-color="{P['accent']}" stop-opacity="0"/>
</radialGradient>
</defs>"""

    o = [head(W, H, motion, defs)]
    o.append(f'<rect width="{W}" height="{H}" rx="16" fill="{P["bg0"]}"/>')
    o.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{P["rule"]}" stroke-width="1"/>')

    # Top strip
    o.append(rule(0, 44, W, 44, P["rule"]))
    o.append(text(48, 26, "EMPIRICAL BENCHMARK MATRIX  /  BLACK MAMBA JIT vs CPYTHON 3.14", size=10, fill=P["text"], weight="700", family=MONO, ls=1.5))
    o.append(text(W - 48, 26, "DETERMINISTIC LATENCY REDUCTION · IDENTICAL HOST HARDWARE", size=10, fill=P["accent"], weight="700", family=MONO, anchor="end"))

    kernels = [
        ("fib(32) — Recursive Branching", "288.62ms", "11.08ms", 26.1, "26.1x FASTER"),
        ("collatz(40k) — Control Flow", "227.84ms", "8.29ms", 27.5, "27.5x FASTER"),
        ("count_primes(30k) — Memory Scanning", "22.05ms", "1.73ms", 12.7, "12.7x FASTER"),
        ("mandelbrot(120x120) — Floating-Point", "39.14ms", "3.37ms", 11.6, "11.6x FASTER"),
    ]

    base_y = 66
    for idx, (name, c_ms, m_ms, ratio, badge) in enumerate(kernels):
        ky = base_y + idx * 48

        # Kernel Name
        o.append(text(48, ky + 14, name, size=11, fill=P["text"], weight="700", family=SANS))
        o.append(text(340, ky + 14, f"CPython: {c_ms}", size=10, fill=P["dim"], weight="500", family=MONO))
        o.append(text(470, ky + 14, f"JIT: {m_ms}", size=10, fill=P["accent"], weight="700", family=MONO))

        # Precision Track
        bx = 580
        max_track_w = 460
        bar_w = int(max_track_w * (ratio / 30.0))

        # Background Track with micro ruler ticks
        o.append(f'<rect x="{bx}" y="{ky + 4}" width="{max_track_w}" height="14" rx="7" fill="{P["bar"]}"/>')
        for tick in range(1, 9):
            tx = bx + tick * (max_track_w / 9)
            o.append(f'<line x1="{tx}" y1="{ky+4}" x2="{tx}" y2="{ky+18}" stroke="{P["rule"]}" stroke-width="0.8"/>')

        # Vibrant Kinetic Laser Stream
        o.append(f'<rect x="{bx}" y="{ky + 4}" width="{bar_w}" height="14" rx="7" fill="url(#bench_stream)"/>')
        o.append(f'<line x1="{bx+4}" y1="{ky+11}" x2="{bx+bar_w-4}" y2="{ky+11}" stroke="#FFFFFF" stroke-width="1.2" opacity="0.6" class="flow_fast"/>')

        # Glowing Comet Head Node at the tip
        comet_x = bx + bar_w
        o.append(f'<circle cx="{comet_x}" cy="{ky+11}" r="9" fill="url(#laser_glow)"/>')
        o.append(f'<circle cx="{comet_x}" cy="{ky+11}" r="4" fill="{P["accent_bright"]}" class="laser_head"/>')

        # Glowing Speedup Pill
        o.append(f'<rect x="{bx + max_track_w + 16}" y="{ky + 2}" width="114" height="18" rx="9" fill="{P["card"]}" stroke="{P["accent"]}" stroke-width="1"/>')
        o.append(text(bx + max_track_w + 73, ky + 14, badge, size=9.5, fill=P["accent"], weight="800", family=MONO, anchor="middle"))

    o.append(rule(48, H - 28, W - 48, H - 28, P["rule"]))
    o.append(text(W/2, H - 12, "Deep recursive call kernel collapses 5,000,000 frames to 0 stack bytes via Tail-Call Optimization.",
                  size=9.5, fill=P["dim"], weight="500", family=SANS, anchor="middle"))

    o.append("</svg>")
    return "".join(o)

# ------------------------------------------------ KINETIC SIGNAL RADAR ----
def telemetry(t, motion=True):
    """1280x230. Live 360° Radar Sweeper & Oscilloscope Mesh."""
    W, H = 1280, 230
    P = THEMES[t]

    defs = f"""<defs>
<radialGradient id="radar_cone" cx="50%" cy="50%" r="50%">
  <stop offset="0%" stop-color="{P['accent']}" stop-opacity="0.3"/>
  <stop offset="100%" stop-color="{P['bg0']}" stop-opacity="0"/>
</radialGradient>
</defs>"""

    o = [head(W, H, motion, defs)]
    o.append(f'<rect width="{W}" height="{H}" rx="16" fill="{P["bg0"]}"/>')
    o.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{P["rule"]}" stroke-width="1"/>')

    # Top strip
    o.append(rule(0, 44, W, 44, P["rule"]))
    o.append(f'<circle cx="48" cy="22" r="3.5" fill="{P["green"]}" class="pulse"/>')
    o.append(text(62, 26, "SIGNAL MESH  /  AUTONOMOUS EVENT-DRIVEN ISSUEOPS RADAR", size=10, fill=P["text"], weight="700", family=MONO, ls=1.5))
    o.append(text(W - 48, 26, "AUTONOMOUS GITHUB ACTIONS DISPATCH IN ~15 SECONDS", size=10, fill=P["accent"], weight="700", family=MONO, ls=1.0, anchor="end"))

    # Tactical Circular Radar Screen (Left side)
    rx, ry, rad = 130, 134, 72
    # Background Glow & Outer Ring
    o.append(f'<circle cx="{rx}" cy="{ry}" r="{rad}" fill="{P["panel"]}" stroke="{P["rule_glow"]}" stroke-width="1.2"/>')
    o.append(f'<circle cx="{rx}" cy="{ry}" r="{rad*0.66:.1f}" stroke="{P["rule"]}" stroke-width="0.8" fill="none"/>')
    o.append(f'<circle cx="{rx}" cy="{ry}" r="{rad*0.33:.1f}" stroke="{P["rule"]}" stroke-width="0.8" fill="none"/>')
    # Cardinal Crosshairs
    o.append(f'<line x1="{rx-rad}" y1="{ry}" x2="{rx+rad}" y2="{ry}" stroke="{P["rule_glow"]}" stroke-width="0.8"/>')
    o.append(f'<line x1="{rx}" y1="{ry-rad}" x2="{rx}" y2="{ry+rad}" stroke="{P["rule_glow"]}" stroke-width="0.8"/>')

    # 360° Rotating Radar Sweep Cone
    o.append(f'<g class="radar">')
    o.append(f'<path d="M{rx} {ry} L{rx+rad} {ry} A{rad} {rad} 0 0 0 {rx} {ry-rad} Z" fill="url(#radar_cone)"/>')
    o.append(f'<line x1="{rx}" y1="{ry}" x2="{rx+rad}" y2="{ry}" stroke="{P["accent_bright"]}" stroke-width="1.8"/>')
    o.append(f'</g>')

    # 3 Radar Blip Targets with Ping Ripple Waves
    blips = [(rx - 28, ry - 32, "ping1", P["accent"]),
             (rx + 36, ry + 22, "ping2", P["blue"]),
             (rx - 14, ry + 40, "ping3", P["green"])]
    for bx, by, ping_cls, b_col in blips:
        o.append(f'<circle cx="{bx}" cy="{by}" r="3" fill="{b_col}"/>')
        o.append(f'<circle cx="{bx}" cy="{by}" r="2" stroke="{b_col}" fill="none" class="{ping_cls}"/>')

    # Center Screen Divider
    o.append(rule(230, 60, 230, H - 36, P["rule"]))

    # Digital Oscilloscope Waveform Display (Middle)
    ox, oy, ow, oh = 250, 68, 300, 114
    o.append(f'<rect x="{ox}" y="{oy}" width="{ow}" height="{oh}" rx="6" fill="{P["panel"]}" stroke="{P["rule_glow"]}" stroke-width="0.8"/>')
    o.append(text(ox + 12, oy + 20, "TELEMETRY CARRIER OSCILLOSCOPE", size=8.5, fill=P["dim"], weight="700", family=MONO, ls=1.0))

    # Animated Square Clock Signal & Sine Waveform
    sq_path = f"M{ox+12} {oy+50} h16 v-16 h16 v16 h16 v-16 h16 v16 h16 v-16 h16 v16 h16 v-16 h16 v16 h16 v-16 h16 v16 h16 v-16 h16 v16 h16 v-16 h16 v16 h16 v-16 h16 v16 h16 v-16"
    o.append(f'<path d="{sq_path}" stroke="{P["purple"]}" stroke-width="1.4" fill="none" class="flow_fast"/>')
    sin_path = f"M{ox+12} {oy+88} q20 -20, 40 0 t40 0 t40 0 t40 0 t40 0 t40 0"
    o.append(f'<path d="{sin_path}" stroke="{P["accent"]}" stroke-width="1.6" fill="none" class="flow"/>')

    # Live Signal Slots (Right side)
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

    tx_start = 574
    for i, sig in enumerate(signals[:3]):
        sy = 68 + i * 40
        o.append(f'<rect x="{tx_start}" y="{sy}" width="{W - tx_start - 48}" height="32" rx="6" fill="{P["panel"]}" stroke="{P["rule_glow"]}" stroke-width="1"/>')
        o.append(f'<circle cx="{tx_start + 18}" cy="{sy + 16}" r="3" fill="{P["accent"]}"/>')
        o.append(text(tx_start + 30, sy + 20, sig.get("id", f"SIG-{i+1:03d}"), size=10, fill=P["accent"], weight="800", family=MONO))
        o.append(text(tx_start + 110, sy + 20, "@" + sig.get("sender", "anonymous")[:16], size=10.5, fill=P["text"], weight="700", family=MONO))
        o.append(text(tx_start + 270, sy + 20, sig.get("focus", "Applied AI / Systems")[:26], size=9.5, fill=P["dim"], weight="500", family=MONO))
        o.append(text(W - 68, sy + 20, "VERIFIED", size=9.5, fill=P["green"], weight="800", family=MONO, anchor="end"))

    o.append(rule(48, H - 28, W - 48, H - 28, P["rule"]))
    o.append(text(W/2, H - 12, "CLICK BELOW TO TRANSMIT LIVE HANDSHAKE // GITHUB ACTIONS AUTO-DISPATCH IN ~15 SECONDS",
                  size=9, fill=P["dim"], weight="700", family=MONO, anchor="middle", ls=0.8))

    o.append("</svg>")
    return "".join(o)

# ------------------------------------------------ KINETIC SPECTRUM EQUALIZER ----
def bars(t, motion=True):
    """1280x160. Kinetic Spectrum Equalizer Contribution Volume."""
    W, H = 1280, 160
    P = THEMES[t]

    defs = f"""<defs>
<linearGradient id="eq_grad" x1="0%" y1="0%" x2="0%" y2="100%">
  <stop offset="0%" stop-color="{P['accent_bright']}"/>
  <stop offset="50%" stop-color="{P['accent']}"/>
  <stop offset="100%" stop-color="{P['panel']}"/>
</linearGradient>
</defs>"""

    o = [head(W, H, motion, defs)]
    o.append(f'<rect width="{W}" height="{H}" rx="16" fill="{P["bg0"]}"/>')
    o.append(f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{P["rule"]}" stroke-width="1"/>')

    # Top Strip
    o.append(rule(0, 44, W, 44, P["rule"]))
    o.append(text(48, 26, "ANNUAL CONTRIBUTION CADENCE  /  SPECTRUM EQUALIZER", size=10, fill=P["text"], weight="700", family=MONO, ls=1.5))
    o.append(text(W - 48, 26, f"{STATS.get('total_contributions', 386)} CONTRIBUTIONS IN 12 MONTHS",
                  size=10, fill=P["accent"], weight="700", family=MONO, ls=1.2, anchor="end"))

    # Faint Oscilloscope Reference Lines
    base_y = 130
    for level, l_val in ((90, "100"), (60, "200"), (30, "300")):
        o.append(f'<line x1="48" y1="{base_y - level}" x2="{W-48}" y2="{base_y - level}" stroke="{P["rule"]}" stroke-width="0.6" stroke-dasharray="2 6"/>')

    m_data = STATS.get("monthly", [])
    if m_data:
        max_c = max(d["count"] for d in m_data) or 1
        n = len(m_data)
        bar_w = 76
        gap = (W - 96 - (n * bar_w)) / (n - 1) if n > 1 else 0
        max_h = 72

        for i, d in enumerate(m_data):
            bx = 48 + i * (bar_w + gap)
            count = d["count"]
            bh = int((count / max_c) * max_h)
            bh = max(bh, 4)
            by = base_y - bh

            # Kinetic Multi-Tier Equalizer Segments
            eq_cls = f"eq{(i % 3) + 1}" if (motion and count > 0) else ""
            fill_val = "url(#eq_grad)" if count == max_c else P["bar"]

            o.append(f'<g class="{eq_cls}">')
            # The Main Equalizer Column
            o.append(f'<rect x="{bx:.1f}" y="{by}" width="{bar_w}" height="{bh}" rx="4" fill="{fill_val}"/>')

            # Glowing Floating Peak Needle for high bars
            if count > 50:
                o.append(f'<rect x="{bx:.1f}" y="{by-5}" width="{bar_w}" height="2" rx="1" fill="{P["accent_bright"]}"/>')
            o.append(f'</g>')

            o.append(text(bx + bar_w / 2, base_y + 16, d["month"][-2:], size=9.5, fill=P["micro"],
                          weight="600", family=MONO, anchor="middle"))
            if count > 0:
                col = P["text"] if count == max_c else P["dim"]
                o.append(text(bx + bar_w / 2, by - 8, str(count), size=9.5, fill=col,
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
        "sys-hero": hero,
        "sys-topology": topology,
        "sys-benchmark": benchmark,
        "sys-signal": telemetry,
        "sys-pulse": bars,
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
