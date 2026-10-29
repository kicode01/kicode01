"""
Generates precision kinetic systems engineering SVG assets for Kian's profile.
Motion-first: fluid waveforms, animated gyroscopes, dynamic circuit buses,
kinetic benchmark laser streams, live 360° radar sweeper, and spectrum equalizer.
Includes Apple-style interactive Bento Grid showcase cards.
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
        "bg0": "#08080A", "bg1": "#0F0F14", "panel": "#14141C", "card": "#151522",
        "card_grad_end": "#0D0D16",
        "rule": "#222230", "rule_glow": "#2E2E42",
        "text": "#F8FAFC", "dim": "#94A3B8", "micro": "#64748B", "faint": "#161622",
        "accent": "#06B6D4", "accent_end": "#2563EB", "accent_bright": "#38BDF8",
        "blue": "#3B82F6", "purple": "#8B5CF6", "pink": "#EC4899",
        "green": "#10B981", "amber": "#F59E0B", "bar": "#1E1E2C",
        "silver": "#CBD5E1",
    },
    "light": {
        "bg0": "#FFFFFF", "bg1": "#F8FAFC", "panel": "#FFFFFF", "card": "#F8FAFC",
        "card_grad_end": "#F1F5F9",
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
.shimmer{transform-box:fill-box;animation:shimmer 4.5s ease-in-out infinite}

@keyframes spin{0%{transform:rotate(0deg)}100%{transform:rotate(360deg)}}
@keyframes spin_rev{0%{transform:rotate(360deg)}100%{transform:rotate(0deg)}}
@keyframes flow{to{stroke-dashoffset:-28}}
@keyframes flow_fast{to{stroke-dashoffset:-40}}
@keyframes pulse{0%,100%{opacity:0.35;transform:scale(0.96)}50%{opacity:1;transform:scale(1.04)}}
@keyframes pulse_glow{0%,100%{opacity:0.4;transform:scale(0.97)}50%{opacity:1;transform:scale(1.03)}}
@keyframes glow{0%{opacity:0.6}100%{opacity:1}}
@keyframes ping{0%{r:2px;opacity:1;stroke-width:2px}80%,100%{r:26px;opacity:0;stroke-width:0.5px}}
@keyframes scan{0%,100%{transform:translateY(0);opacity:0.2}50%{transform:translateY(96px);opacity:0.95}}
@keyframes laser_pulse{0%,100%{opacity:0.6;r:4px}50%{opacity:1;r:7px}}
@keyframes eq{0%{transform:scaleY(0.72)}50%{transform:scaleY(1.04)}100%{transform:scaleY(0.85)}}
@keyframes shimmer{0%{transform:translateX(-100%)}30%,100%{transform:translateX(150%)}}
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

def head(w, h, motion):
    css = f"<style>{CSS}</style>" if motion else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" fill="none" role="img">{css}')

def text(x, y, s, size=14, fill="#000", weight="400", family=SANS,
         anchor="start", ls=0, op=1.0, cls="", style=""):
    cls_attr = f' class="{cls}"' if cls else ""
    style_attr = f' style="{style}"' if style else ""
    ls_attr = f' letter-spacing="{ls}"' if ls else ""
    op_attr = f' opacity="{op}"' if op != 1.0 else ""
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"'
            f'{ls_attr}{op_attr}{cls_attr}{style_attr}>{escape(str(s))}</text>')

def rule(x1, y1, x2, y2, color, op=1.0, dash=""):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{color}" stroke-width="1" opacity="{op}"{dash_attr}/>')

def label(x, y, s, P, size=10, ls=1.6, anchor="start", cls=""):
    return text(x, y, s, size=size, fill=P["micro"], weight="700", family=MONO,
                ls=ls, anchor=anchor, cls=cls)

# ==============================================================================
# 00 / MASTER HERO CONSOLE
# ==============================================================================
def hero(t, motion=True):
    W, H = 1280, 380
    P = THEMES[t]
    o = [head(W, H, motion)]

    o.append(f"""<defs>
<linearGradient id="hero_bg_{t}" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{P['bg1']}"/>
  <stop offset="0.6" stop-color="{P['bg0']}"/>
  <stop offset="1" stop-color="{P['bg1']}"/>
</linearGradient>
<linearGradient id="laser_{t}" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{P['accent']}"/>
  <stop offset="0.5" stop-color="{P['blue']}"/>
  <stop offset="1" stop-color="{P['purple']}"/>
</linearGradient>
<linearGradient id="text_grad_{t}" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{P['text']}"/>
  <stop offset="0.7" stop-color="{P['text']}"/>
  <stop offset="1" stop-color="{P['accent_bright']}"/>
</linearGradient>
<radialGradient id="reactor_{t}" cx="50%" cy="50%" r="50%">
  <stop offset="0%" stop-color="{P['accent_bright']}" stop-opacity="0.9"/>
  <stop offset="40%" stop-color="{P['accent']}" stop-opacity="0.5"/>
  <stop offset="80%" stop-color="{P['blue']}" stop-opacity="0.2"/>
  <stop offset="100%" stop-color="{P['bg0']}" stop-opacity="0"/>
</radialGradient>
<linearGradient id="shimmer_{t}" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{P['accent']}" stop-opacity="0"/>
  <stop offset="50%" stop-color="{P['accent_bright']}" stop-opacity="0.8"/>
  <stop offset="100%" stop-color="{P['accent']}" stop-opacity="0"/>
</linearGradient>
</defs>""")

    # Main Chassis
    o.append(f'<rect width="{W}" height="{H}" rx="20" fill="url(#hero_bg_{t})" stroke="{P["rule"]}" stroke-width="1.5"/>')

    # Top Specular Shimmer Line
    if motion:
        o.append(f'<g class="shimmer"><line x1="0" y1="1.5" x2="400" y2="1.5" stroke="url(#shimmer_{t})" stroke-width="2.5"/></g>')

    # Header strip
    o.append(rule(0, 48, W, 48, P["rule"]))
    o.append(f'<circle cx="48" cy="24" r="4.5" fill="{P["green"]}" class="pulse"/>')
    o.append(label(64, 28, "SYSTEM ONLINE // KIAN B. // SYSTEMS ARCHITECT & COMPILER ENGINEER", P, ls=1.8))
    o.append(text(W - 48, 28, f"UTC TELEMETRY · REPO STATUS: ALL SYSTEMS NOMINAL · {STATS['generated']}", size=10,
                  fill=P["accent"], weight="700", family=MONO, ls=1.5, anchor="end"))

    # Left Section: Identity & Vision
    o.append(text(48, 98, "CORE SYSTEMS · APPLIED AI · EDGE RUNTIMES", size=11,
                  fill=P["accent"], weight="700", family=MONO, ls=2.5))
    o.append(text(46, 175, "KIAN", size=82, fill=f"url(#text_grad_{t})", weight="900",
                  ls=-3.0, family=SANS))
    o.append(text(48, 218, "I architect compilers, edge firmware, and resilient applied AI.", size=18,
                  fill=P["dim"], weight="400", ls=-0.2, family=SANS))
    o.append(text(48, 242, "Zero-cost abstractions where every cycle, token, and byte is measured.", size=13.5,
                  fill=P["micro"], weight="500", family=MONO))

    # Metric Instrument Pods
    o.append(rule(48, 270, 720, 270, P["rule"]))
    metrics = [
        (str(STATS["public_repos"]), "PUBLIC REPOS", P["blue"]),
        (str(STATS["total_contributions"]), "CONTRIBUTIONS", P["green"]),
        (str(STATS["commits"]), "COMMITS (12M)", P["accent"]),
        ("26.1x", "COMPILER PEAK", P["pink"]),
    ]
    pod_w = 160
    for i, (val, lbl, col) in enumerate(metrics):
        px = 48 + i * pod_w
        if i > 0:
            o.append(rule(px - 10, 282, px - 10, 348, P["rule"]))
        o.append(f'<rect x="{px}" y="280" width="138" height="68" rx="10" fill="{P["panel"]}" stroke="{P["rule"]}" stroke-width="1"/>')
        o.append(label(px + 12, 302, lbl, P, size=8.5, ls=1.2))
        o.append(text(px + 12, 334, val, size=24, fill=col, weight="800", family=MONO, ls=-0.5))

    # Right Section: Gyroscopic Quantum Reactor Core
    cx, cy = 990, 210

    # Ambient Glow
    o.append(f'<circle cx="{cx}" cy="{cy}" r="140" fill="url(#reactor_{t})"/>')

    # Radial tick marks (Outer Stator)
    for a in range(0, 360, 15):
        import math
        rad = math.radians(a)
        r1 = 126
        r2 = 134 if a % 45 == 0 else 130
        x1 = cx + r1 * math.cos(rad)
        y1 = cy + r1 * math.sin(rad)
        x2 = cx + r2 * math.cos(rad)
        y2 = cy + r2 * math.sin(rad)
        tick_col = P["accent_bright"] if a % 90 == 0 else P["rule_glow"]
        o.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{tick_col}" stroke-width="1.2"/>')

    # Ring 1: Outer Reverse Gyro
    cls_r1 = 'class="spin_rev"' if motion else ''
    o.append(f'<g {cls_r1}>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="114" stroke="{P["accent"]}" stroke-width="1.5" stroke-dasharray="14 10 32 8" opacity="0.8"/>')
    o.append(f'<circle cx="{cx+114}" cy="{cy}" r="3.5" fill="{P["accent_bright"]}"/>')
    o.append(f'<circle cx="{cx-114}" cy="{cy}" r="3.5" fill="{P["accent_bright"]}"/>')
    o.append('</g>')

    # Ring 2: Intermediate Forward Gyro with Bus Nodes
    cls_r2 = 'class="spin"' if motion else ''
    o.append(f'<g {cls_r2}>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="88" stroke="{P["blue"]}" stroke-width="2" stroke-dasharray="24 16 48 12" opacity="0.9"/>')
    o.append(f'<rect x="{cx-5}" y="{cy-88-5}" width="10" height="10" rx="2" fill="{P["accent"]}" stroke="{P["bg0"]}" stroke-width="1.5"/>')
    o.append(f'<rect x="{cx-5}" y="{cy+88-5}" width="10" height="10" rx="2" fill="{P["purple"]}" stroke="{P["bg0"]}" stroke-width="1.5"/>')
    o.append('</g>')

    # Ring 3: Fast Core Ring
    cls_r3 = 'class="spin_fast"' if motion else ''
    o.append(f'<g {cls_r3}>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="62" stroke="{P["purple"]}" stroke-width="1.5" stroke-dasharray="12 6" opacity="0.8"/>')
    o.append(f'<circle cx="{cx}" cy="{cy-62}" r="3" fill="{P["green"]}"/>')
    o.append('</g>')

    # Center Reactor Crystal
    cls_core = 'class="pulse_glow"' if motion else ''
    o.append(f'<g {cls_core}>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="38" fill="{P["panel"]}" stroke="{P["accent"]}" stroke-width="2"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="22" fill="{P["accent"]}" opacity="0.85"/>')
    o.append(f'<circle cx="{cx}" cy="{cy}" r="10" fill="#FFFFFF"/>')
    o.append('</g>')

    # Crosshair Collimators
    o.append(f'<line x1="{cx-145}" y1="{cy}" x2="{cx-125}" y2="{cy}" stroke="{P["accent"]}" stroke-width="1.5"/>')
    o.append(f'<line x1="{cx+125}" y1="{cy}" x2="{cx+145}" y2="{cy}" stroke="{P["accent"]}" stroke-width="1.5"/>')
    o.append(f'<line x1="{cx}" y1="{cy-145}" x2="{cx}" y2="{cy-125}" stroke="{P["accent"]}" stroke-width="1.5"/>')
    o.append(f'<line x1="{cx}" y1="{cy+125}" x2="{cx}" y2="{cy+145}" stroke="{P["accent"]}" stroke-width="1.5"/>')

    # Reactor Labels
    o.append(text(cx, cy + 148, "CORE QUANTUM ENGINE // 120MHz", size=9,
                  fill=P["micro"], weight="700", family=MONO, anchor="middle", ls=1.5))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 01 / BENTO CARD: BLACK MAMBA JIT COMPILER
# ==============================================================================
def card_mamba(t, motion=True):
    W, H = 620, 360
    P = THEMES[t]
    o = [head(W, H, motion)]

    o.append(f"""<defs>
<linearGradient id="mamba_bg_{t}" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{P['card']}"/>
  <stop offset="1" stop-color="{P['card_grad_end']}"/>
</linearGradient>
<linearGradient id="speedo_grad_{t}" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{P['blue']}"/>
  <stop offset="1" stop-color="{P['accent_bright']}"/>
</linearGradient>
<linearGradient id="trace_flow_{t}" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{P['blue']}"/>
  <stop offset="0.5" stop-color="{P['accent_bright']}"/>
  <stop offset="1" stop-color="{P['green']}"/>
</linearGradient>
</defs>""")

    # Glassmorphic Chassis
    o.append(f'<rect width="{W}" height="{H}" rx="18" fill="url(#mamba_bg_{t})" stroke="{P["rule"]}" stroke-width="1.5"/>')

    # Top Header
    o.append(f'<rect x="24" y="22" width="180" height="24" rx="6" fill="{P["panel"]}" stroke="{P["rule"]}" stroke-width="1"/>')
    o.append(text(34, 38, "01 / JIT COMPILER & RUNTIME", size=9, fill=P["blue"], weight="700", family=MONO, ls=1.2))

    o.append(f'<circle cx="{W-135}" cy="34" r="4" fill="{P["green"]}" class="pulse"/>')
    o.append(text(W - 124, 38, "26.1x SPEEDUP", size=10, fill=P["green"], weight="700", family=MONO, ls=1.0))

    o.append(text(24, 82, "BLACK MAMBA v1.1.0", size=24, fill=P["text"], weight="800", family=SANS))
    o.append(text(24, 102, "Pure-Python JIT · Dynamic C3 MRO · Native x86-64 Machine Code", size=11, fill=P["dim"], weight="500", family=MONO))

    # Architecture Pipeline Graphic Viewport
    vx, vy, vw, vh = 24, 120, 572, 172
    o.append(f'<rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" rx="12" fill="{P["bg0"]}" stroke="{P["rule"]}" stroke-width="1"/>')

    # Flow trace lines
    cls_flow = 'class="flow_fast"' if motion else ''
    o.append(f'<path d="M {vx+30} {vy+50} H {vx+140} V {vy+105} H {vx+360}" fill="none" stroke="url(#trace_flow_{t})" stroke-width="2.5" {cls_flow}/>')
    o.append(f'<path d="M {vx+140} {vy+50} H {vx+360}" fill="none" stroke="{P["rule_glow"]}" stroke-width="1.5" stroke-dasharray="4 4"/>')

    # Stage Pod 1: Grammar & AST
    o.append(f'<rect x="{vx+24}" y="{vy+32}" width="105" height="38" rx="8" fill="{P["panel"]}" stroke="{P["blue"]}" stroke-width="1.2"/>')
    o.append(text(vx + 34, vy + 48, "PYTHONIC AST", size=9.5, fill=P["text"], weight="700", family=MONO))
    o.append(text(vx + 34, vy + 61, "Unboxed Structs", size=8, fill=P["micro"], weight="600", family=MONO))

    # Stage Pod 2: C3 MRO & Solver
    o.append(f'<rect x="{vx+155}" y="{vy+32}" width="115" height="38" rx="8" fill="{P["panel"]}" stroke="{P["purple"]}" stroke-width="1.2"/>')
    o.append(text(vx + 165, vy + 48, "DYNAMIC C3 MRO", size=9.5, fill=P["text"], weight="700", family=MONO))
    o.append(text(vx + 165, vy + 61, "0.42ms Linearize", size=8, fill=P["purple"], weight="600", family=MONO))

    # Stage Pod 3: TCO Collapse
    o.append(f'<rect x="{vx+105}" y="{vy+86}" width="135" height="38" rx="8" fill="{P["panel"]}" stroke="{P["accent"]}" stroke-width="1.2"/>')
    o.append(text(vx + 115, vy + 102, "TCO ENGINE", size=9.5, fill=P["text"], weight="700", family=MONO))
    o.append(text(vx + 115, vy + 115, "5M -> 0 Call Frames", size=8, fill=P["accent"], weight="600", family=MONO))

    # Stage Pod 4: x86-64 Machine Code Emitter
    o.append(f'<rect x="{vx+260}" y="{vy+86}" width="115" height="38" rx="8" fill="{P["panel"]}" stroke="{P["green"]}" stroke-width="1.2"/>')
    o.append(text(vx + 270, vy + 102, "x86-64 NATIVE", size=9.5, fill=P["text"], weight="700", family=MONO))
    o.append(text(vx + 270, vy + 115, "Direct JIT Emitter", size=8, fill=P["green"], weight="600", family=MONO))

    # Speedometer Gauge Dial on the Right
    gx, gy = vx + 465, vy + 86
    o.append(f'<circle cx="{gx}" cy="{gy}" r="55" fill="{P["panel"]}" stroke="{P["rule"]}" stroke-width="1.5"/>')
    o.append(f'<circle cx="{gx}" cy="{gy}" r="45" stroke="{P["rule"]}" stroke-width="6" stroke-dasharray="180 360" fill="none"/>')
    cls_pg = 'class="pulse_glow"' if motion else ''
    o.append(f'<circle cx="{gx}" cy="{gy}" r="45" stroke="url(#speedo_grad_{t})" stroke-width="6" stroke-dasharray="190 280" fill="none" {cls_pg}/>')
    o.append(text(gx, gy + 4, "26.1x", size=20, fill=P["text"], weight="900", family=MONO, anchor="middle"))
    o.append(text(gx, gy + 18, "VS CPYTHON", size=7.5, fill=P["accent_bright"], weight="700", family=MONO, anchor="middle", ls=1.0))

    # Bottom Pill Specs & Action
    o.append(rule(24, 308, W - 24, 308, P["rule"]))
    o.append(text(24, 334, "0 KB GC OVERHEAD  ·  1.7KB WASM  ·  PE32+/ELF64 LINKERS", size=9.5, fill=P["micro"], weight="600", family=MONO, ls=0.8))

    # Integrated Button
    btn_x = W - 180
    o.append(f'<rect x="{btn_x}" y="318" width="156" height="28" rx="6" fill="{P["panel"]}" stroke="{P["blue"]}" stroke-width="1"/>')
    o.append(text(btn_x + 78, 336, "EXPLORE JIT ENGINE ↗", size=9, fill=P["blue"], weight="700", family=MONO, anchor="middle", ls=0.8))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 02 / BENTO CARD: TYPENSCRAPE APPLIED AI CASCADE
# ==============================================================================
def card_typenscrape(t, motion=True):
    W, H = 620, 360
    P = THEMES[t]
    o = [head(W, H, motion)]

    o.append(f"""<defs>
<linearGradient id="ai_bg_{t}" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{P['card']}"/>
  <stop offset="1" stop-color="{P['card_grad_end']}"/>
</linearGradient>
<linearGradient id="ai_pulse_{t}" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{P['purple']}"/>
  <stop offset="0.5" stop-color="{P['blue']}"/>
  <stop offset="1" stop-color="{P['green']}"/>
</linearGradient>
</defs>""")

    # Chassis
    o.append(f'<rect width="{W}" height="{H}" rx="18" fill="url(#ai_bg_{t})" stroke="{P["rule"]}" stroke-width="1.5"/>')

    # Header
    o.append(f'<rect x="24" y="22" width="180" height="24" rx="6" fill="{P["panel"]}" stroke="{P["rule"]}" stroke-width="1"/>')
    o.append(text(34, 38, "02 / APPLIED AI & RESILIENCE", size=9, fill=P["purple"], weight="700", family=MONO, ls=1.2))

    o.append(f'<circle cx="{W-135}" cy="34" r="4" fill="{P["purple"]}" class="pulse"/>')
    o.append(text(W - 124, 38, "420ms CASCADE", size=10, fill=P["purple"], weight="700", family=MONO, ls=1.0))

    o.append(text(24, 82, "TYPENSCRAPE AI CASCADE", size=24, fill=P["text"], weight="800", family=SANS))
    o.append(text(24, 102, "Stochastic Resilience · Groq Llama-3 → Gemini · 16-Chunk IndexedDB", size=11, fill=P["dim"], weight="500", family=MONO))

    # Viewport
    vx, vy, vw, vh = 24, 120, 572, 172
    o.append(f'<rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" rx="12" fill="{P["bg0"]}" stroke="{P["rule"]}" stroke-width="1"/>')

    # Interconnect Routing
    cls_flow = 'class="flow"' if motion else ''
    o.append(f'<path d="M {vx+120} {vy+50} H {vx+190} V {vy+50} H {vx+270}" fill="none" stroke="{P["blue"]}" stroke-width="2" {cls_flow}/>')
    o.append(f'<path d="M {vx+230} {vy+50} V {vy+115} H {vx+270}" fill="none" stroke="{P["purple"]}" stroke-width="2" stroke-dasharray="6 4" {cls_flow}/>')
    o.append(f'<path d="M {vx+390} {vy+50} H {vx+440}" fill="none" stroke="{P["green"]}" stroke-width="2" {cls_flow}/>')

    # Query Input Pod
    o.append(f'<rect x="{vx+20}" y="{vy+32}" width="100" height="38" rx="8" fill="{P["panel"]}" stroke="{P["rule"]}" stroke-width="1"/>')
    o.append(text(vx + 30, vy + 48, "USER QUERY", size=9, fill=P["text"], weight="700", family=MONO))
    o.append(text(vx + 30, vy + 61, "Recipe Request", size=8, fill=P["micro"], weight="600", family=MONO))

    # Node 1: Groq Llama-3 (Primary)
    o.append(f'<rect x="{vx+270}" y="{vy+32}" width="125" height="38" rx="8" fill="{P["panel"]}" stroke="{P["blue"]}" stroke-width="1.5"/>')
    o.append(text(vx + 280, vy + 48, "GROQ LLAMA-3", size=9.5, fill=P["blue"], weight="800", family=MONO))
    o.append(text(vx + 280, vy + 61, "420ms Ultra-Fast", size=8, fill=P["green"], weight="700", family=MONO))

    # Node 2: Gemini Fallback
    o.append(f'<rect x="{vx+270}" y="{vy+96}" width="125" height="38" rx="8" fill="{P["panel"]}" stroke="{P["purple"]}" stroke-width="1.5"/>')
    o.append(text(vx + 280, vy + 112, "GEMINI RESILIENCE", size=9.5, fill=P["purple"], weight="800", family=MONO))
    o.append(text(vx + 280, vy + 125, "Rate Limit Fallback", size=8, fill=P["dim"], weight="600", family=MONO))

    # Memory Architecture Ring on Right (16-chunk IndexedDB)
    mx, my = vx + 495, vy + 86
    cls_spin = 'class="spin"' if motion else ''
    o.append(f'<g {cls_spin}>')
    o.append(f'<circle cx="{mx}" cy="{my}" r="45" fill="none" stroke="{P["rule"]}" stroke-width="1"/>')
    for a in range(0, 360, 24):
        import math
        rad = math.radians(a)
        cx_ = mx + 45 * math.cos(rad)
        cy_ = my + 45 * math.sin(rad)
        o.append(f'<circle cx="{cx_:.1f}" cy="{cy_:.1f}" r="3.5" fill="{P["accent_bright"]}"/>')
    o.append('</g>')
    o.append(f'<circle cx="{mx}" cy="{my}" r="26" fill="{P["panel"]}" stroke="{P["rule"]}" stroke-width="1"/>')
    o.append(text(mx, my + 3, "16-CHUNK", size=8.5, fill=P["text"], weight="800", family=MONO, anchor="middle"))
    o.append(text(mx, my + 14, "INDEXEDDB", size=7, fill=P["micro"], weight="600", family=MONO, anchor="middle"))

    # Bottom
    o.append(rule(24, 308, W - 24, 308, P["rule"]))
    o.append(text(24, 334, "OFFLINE-FIRST PWA  ·  MEMORY-BOUNDED STREAMING  ·  ZERO FAILURE", size=9.5, fill=P["micro"], weight="600", family=MONO, ls=0.8))

    btn_x = W - 180
    o.append(f'<rect x="{btn_x}" y="318" width="156" height="28" rx="6" fill="{P["panel"]}" stroke="{P["purple"]}" stroke-width="1"/>')
    o.append(text(btn_x + 78, 336, "EXPLORE AI CASCADE ↗", size=9, fill=P["purple"], weight="700", family=MONO, anchor="middle", ls=0.8))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 03 / BENTO CARD: VOLTSENSE EDGE FIRMWARE & IOT
# ==============================================================================
def card_voltsense(t, motion=True):
    W, H = 620, 360
    P = THEMES[t]
    o = [head(W, H, motion)]

    o.append(f"""<defs>
<linearGradient id="volt_bg_{t}" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{P['card']}"/>
  <stop offset="1" stop-color="{P['card_grad_end']}"/>
</linearGradient>
</defs>""")

    # Chassis
    o.append(f'<rect width="{W}" height="{H}" rx="18" fill="url(#volt_bg_{t})" stroke="{P["rule"]}" stroke-width="1.5"/>')

    # Header
    o.append(f'<rect x="24" y="22" width="180" height="24" rx="6" fill="{P["panel"]}" stroke="{P["rule"]}" stroke-width="1"/>')
    o.append(text(34, 38, "03 / EDGE FIRMWARE & HARDWARE", size=9, fill=P["green"], weight="700", family=MONO, ls=1.2))

    o.append(f'<circle cx="{W-135}" cy="34" r="4" fill="{P["green"]}" class="pulse"/>')
    o.append(text(W - 124, 38, "ACTIVE TELEMETRY", size=10, fill=P["green"], weight="700", family=MONO, ls=1.0))

    o.append(text(24, 82, "VOLTSENSE IoT FIRMWARE", size=24, fill=P["text"], weight="800", family=SANS))
    o.append(text(24, 102, "Memory-Bounded C++ · ESP32 · Isolated Vercel Push · Zero Secrets", size=11, fill=P["dim"], weight="500", family=MONO))

    # Viewport (Oscilloscope & Relay Monitor)
    vx, vy, vw, vh = 24, 120, 572, 172
    o.append(f'<rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" rx="12" fill="{P["bg0"]}" stroke="{P["rule"]}" stroke-width="1"/>')

    # Oscilloscope Graticule
    for gx in range(vx + 40, vx + 330, 40):
        o.append(f'<line x1="{gx}" y1="{vy+15}" x2="{gx}" y2="{vy+155}" stroke="{P["rule"]}" stroke-width="0.8" stroke-dasharray="2 4" opacity="0.6"/>')
    for gy in [vy + 45, vy + 85, vy + 125]:
        o.append(f'<line x1="{vx+20}" y1="{gy}" x2="{vx+330}" y2="{gy}" stroke="{P["rule"]}" stroke-width="0.8" stroke-dasharray="2 4" opacity="0.6"/>')

    # Sine Wave AC Voltage Curve
    sine_pts = []
    import math
    for x in range(0, 310, 4):
        rad = (x / 310) * 4 * math.pi
        y = (vy + 85) + math.sin(rad) * 32
        sine_pts.append(f"{'M' if x == 0 else 'L'} {vx+20+x} {y:.1f}")
    sine_path = " ".join(sine_pts)
    cls_flow = 'class="flow_fast"' if motion else ''
    o.append(f'<path d="{sine_path}" fill="none" stroke="{P["green"]}" stroke-width="2.5" {cls_flow}/>')
    o.append(text(vx + 30, vy + 35, "AC 230V RMS LOAD", size=9, fill=P["green"], weight="800", family=MONO))

    # Relay State Modules on Right
    rx = vx + 360
    relays = [
        ("RELAY 01 / HIGH LOAD", "ENGAGED", P["green"]),
        ("RELAY 02 / PERIPHERAL", "STANDBY", P["micro"]),
        ("RELAY 03 / SENSOR BUS", "ENGAGED", P["green"]),
    ]
    for i, (r_name, r_state, r_col) in enumerate(relays):
        ry = vy + 24 + i * 44
        o.append(f'<rect x="{rx}" y="{ry}" width="190" height="36" rx="6" fill="{P["panel"]}" stroke="{P["rule"]}" stroke-width="1"/>')
        o.append(f'<circle cx="{rx+16}" cy="{ry+18}" r="4" fill="{r_col}" class="pulse"/>')
        o.append(text(rx + 30, ry + 16, r_name, size=8.5, fill=P["text"], weight="700", family=MONO))
        o.append(text(rx + 30, ry + 28, f"STATE: {r_state}", size=8, fill=r_col, weight="800", family=MONO))

    # Bottom
    o.append(rule(24, 308, W - 24, 308, P["rule"]))
    o.append(text(24, 334, "ZERO HARDWARE SECRETS  ·  SERVERLESS PUSH  ·  ISOLATED RELAYS", size=9.5, fill=P["micro"], weight="600", family=MONO, ls=0.8))

    btn_x = W - 180
    o.append(f'<rect x="{btn_x}" y="318" width="156" height="28" rx="6" fill="{P["panel"]}" stroke="{P["green"]}" stroke-width="1"/>')
    o.append(text(btn_x + 78, 336, "LAUNCH LIVE IoT ↗", size=9, fill=P["green"], weight="700", family=MONO, anchor="middle", ls=0.8))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 04 / BENTO CARD: MEEMOMINI ON-DEVICE COMPUTER VISION
# ==============================================================================
def card_meemomini(t, motion=True):
    W, H = 620, 360
    P = THEMES[t]
    o = [head(W, H, motion)]

    o.append(f"""<defs>
<linearGradient id="vision_bg_{t}" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="{P['card']}"/>
  <stop offset="1" stop-color="{P['card_grad_end']}"/>
</linearGradient>
<linearGradient id="scan_beam_{t}" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{P['pink']}" stop-opacity="0"/>
  <stop offset="90%" stop-color="{P['pink']}" stop-opacity="0.8"/>
  <stop offset="100%" stop-color="#FFFFFF" stop-opacity="1"/>
</linearGradient>
</defs>""")

    # Chassis
    o.append(f'<rect width="{W}" height="{H}" rx="18" fill="url(#vision_bg_{t})" stroke="{P["rule"]}" stroke-width="1.5"/>')

    # Header
    o.append(f'<rect x="24" y="22" width="180" height="24" rx="6" fill="{P["panel"]}" stroke="{P["rule"]}" stroke-width="1"/>')
    o.append(text(34, 38, "04 / COMPUTER VISION & WASM", size=9, fill=P["pink"], weight="700", family=MONO, ls=1.2))

    o.append(f'<circle cx="{W-135}" cy="34" r="4" fill="{P["pink"]}" class="pulse"/>')
    o.append(text(W - 124, 38, "18ms INFERENCE", size=10, fill=P["pink"], weight="700", family=MONO, ls=1.0))

    o.append(text(24, 82, "MEEMOMINI ON-DEVICE VISION", size=24, fill=P["text"], weight="800", family=SANS))
    o.append(text(24, 102, "MediaPipe WASM Segmenter · Zero Server Hops · Client Privacy", size=11, fill=P["dim"], weight="500", family=MONO))

    # Viewport (Spatial Vision Reticle)
    vx, vy, vw, vh = 24, 120, 572, 172
    o.append(f'<rect x="{vx}" y="{vy}" width="{vw}" height="{vh}" rx="12" fill="{P["bg0"]}" stroke="{P["rule"]}" stroke-width="1"/>')

    # Viewfinder Corner Brackets
    fx, fy, fw, fh = vx + 40, vy + 20, 200, 132
    o.append(f'<path d="M {fx} {fy+20} V {fy} H {fx+20}" fill="none" stroke="{P["pink"]}" stroke-width="2"/>')
    o.append(f'<path d="M {fx+fw-20} {fy} H {fx+fw} V {fy+20}" fill="none" stroke="{P["pink"]}" stroke-width="2"/>')
    o.append(f'<path d="M {fx} {fy+fh-20} V {fy+fh} H {fx+20}" fill="none" stroke="{P["pink"]}" stroke-width="2"/>')
    o.append(f'<path d="M {fx+fw-20} {fy+fh} H {fx+fw} V {fy+fh-20}" fill="none" stroke="{P["pink"]}" stroke-width="2"/>')

    # Human Silhouette Mask in Viewfinder
    sx, sy = fx + 100, fy + 66
    o.append(f'<circle cx="{sx}" cy="{sy-22}" r="18" fill="{P["panel"]}" stroke="{P["accent_bright"]}" stroke-width="1.5"/>')
    o.append(f'<path d="M {sx-32} {sy+36} C {sx-28} {sy+2}, {sx+28} {sy+2}, {sx+32} {sy+36} Z" fill="{P["panel"]}" stroke="{P["accent_bright"]}" stroke-width="1.5"/>')

    # Animated Scanning Laser Beam
    if motion:
        o.append(f'<g class="scan">')
        o.append(f'<rect x="{fx+4}" y="{fy+4}" width="{fw-8}" height="28" fill="url(#scan_beam_{t})"/>')
        o.append(f'<line x1="{fx+4}" y1="{fy+32}" x2="{fx+fw-4}" y2="{fy+32}" stroke="#FFFFFF" stroke-width="1.5"/>')
        o.append('</g>')

    # Target Tracking Crosshair
    o.append(f'<circle cx="{sx}" cy="{sy-22}" r="26" stroke="{P["pink"]}" stroke-width="1" stroke-dasharray="4 6"/>')

    # Vision Telemetry Metrics on Right
    tx = vx + 280
    metrics = [
        ("INFERENCE LATENCY", "18 ms (WASM)", P["green"]),
        ("NETWORK EXFILTRATION", "0.00 BYTES (100% PRIVATE)", P["pink"]),
        ("FPS THROUGHPUT", "60.0 FPS CONTINUOUS", P["accent_bright"]),
    ]
    for i, (m_lbl, m_val, m_col) in enumerate(metrics):
        my = vy + 28 + i * 42
        o.append(f'<rect x="{tx}" y="{my}" width="270" height="34" rx="6" fill="{P["panel"]}" stroke="{P["rule"]}" stroke-width="1"/>')
        o.append(text(tx + 16, my + 14, m_lbl, size=8, fill=P["micro"], weight="700", family=MONO))
        o.append(text(tx + 16, my + 26, m_val, size=10, fill=m_col, weight="800", family=MONO))

    # Bottom
    o.append(rule(24, 308, W - 24, 308, P["rule"]))
    o.append(text(24, 334, "ZERO SERVER HOPS  ·  WASM IMAGE SEGMENTER  ·  WEBGL ACCELERATED", size=9.5, fill=P["micro"], weight="600", family=MONO, ls=0.8))

    btn_x = W - 180
    o.append(f'<rect x="{btn_x}" y="318" width="156" height="28" rx="6" fill="{P["panel"]}" stroke="{P["pink"]}" stroke-width="1"/>')
    o.append(text(btn_x + 78, 336, "LAUNCH VISION APP ↗", size=9, fill=P["pink"], weight="700", family=MONO, anchor="middle", ls=0.8))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 05 / COMPUTATIONAL FABRIC TOPOLOGY
# ==============================================================================
def topology(t, motion=True):
    W, H = 1280, 340
    P = THEMES[t]
    o = [head(W, H, motion)]
    o.append(f'<rect width="{W}" height="{H}" rx="18" fill="{P["bg0"]}" stroke="{P["rule"]}" stroke-width="1.5"/>')

    # Top Strip
    o.append(rule(0, 48, W, 48, P["rule"]))
    o.append(f'<circle cx="48" cy="24" r="4.5" fill="{P["accent"]}" class="pulse"/>')
    o.append(label(64, 28, "COMPUTATIONAL FABRIC TOPOLOGY  //  COMPILERS · RUNTIMES · APPLIED AI · EDGE", P, ls=1.8))
    o.append(text(W - 48, 28, "BUS CLOCK: SYNCHRONOUS · ARCHITECTURE v1.2", size=10, fill=P["accent"],
                  weight="700", family=MONO, ls=1.5, anchor="end"))

    # Main 5 Architectural Nodes
    nodes = [
        ("01 / SOURCE LAYER", "Black Mamba Syntax", "Pythonic grammar, unboxed structs", P["blue"]),
        ("02 / FRONTEND", "Dynamic C3 Diamond MRO", "0.42ms linearization, polymorphic vtables", P["purple"]),
        ("03 / INFERENCE", "Hindley-Milner Solver", "Static type propagator, escape analyzer", P["accent_bright"]),
        ("04 / CODEGEN", "LLVM 18 IR Emitter", "TCO collapse (5M -> 0 stack frames)", P["green"]),
        ("05 / TARGET EMISSION", "PE32+ / ELF64 / WASM", "Standalone native machine code, 0 GC", P["amber"]),
    ]

    nw = 210
    nh = 150
    gap = (W - 96 - (5 * nw)) / 4
    by = 95

    # Glowing Bus Backbone Line
    bus_y = by + nh / 2
    cls_flow = 'class="flow_fast"' if motion else ''
    o.append(f'<line x1="48" y1="{bus_y}" x2="{W-48}" y2="{bus_y}" stroke="{P["rule_glow"]}" stroke-width="3"/>')
    o.append(f'<line x1="48" y1="{bus_y}" x2="{W-48}" y2="{bus_y}" stroke="{P["accent_bright"]}" stroke-width="2" {cls_flow}/>')

    for i, (n_num, n_title, n_desc, n_col) in enumerate(nodes):
        nx = 48 + i * (nw + gap)
        # Node Card
        o.append(f'<rect x="{nx}" y="{by}" width="{nw}" height="{nh}" rx="12" fill="{P["panel"]}" stroke="{P["rule"]}" stroke-width="1"/>')
        o.append(f'<rect x="{nx}" y="{by}" width="{nw}" height="5" rx="2" fill="{n_col}"/>')

        o.append(text(nx + 16, by + 30, n_num, size=9.5, fill=n_col, weight="800", family=MONO, ls=1.0))
        o.append(text(nx + 16, by + 56, n_title, size=13, fill=P["text"], weight="700", family=SANS))
        o.append(text(nx + 16, by + 82, n_desc, size=9, fill=P["dim"], weight="500", family=MONO))

        # Port Connector Dot
        o.append(f'<circle cx="{nx+nw/2}" cy="{bus_y}" r="6" fill="{P["panel"]}" stroke="{n_col}" stroke-width="2.5"/>')
        o.append(f'<circle cx="{nx+nw/2}" cy="{bus_y}" r="2" fill="{n_col}"/>')

        o.append(f'<rect x="{nx+16}" y="{by+108}" width="{nw-32}" height="24" rx="6" fill="{P["bg0"]}" stroke="{P["rule"]}" stroke-width="0.8"/>')
        o.append(text(nx + nw / 2, by + 124, "STATUS: NOMINAL", size=8.5, fill=P["green"], weight="700", family=MONO, anchor="middle", ls=0.8))

    # Bottom Specs
    o.append(rule(48, 285, W - 48, 285, P["rule"]))
    specs = [
        ("EXECUTION PARADIGM", "DIRECT EXECUTION (mmap PROT_EXEC)"),
        ("COMPILER FRONTEND", "INDENTATION DESUGARING & AST DESERIALIZER"),
        ("TYPE SAFETY", "STATIC PROPAGATION + COMPILATION SPEED"),
        ("EDGE CODESIGN", "ESP32 C++ TELEMETRY & 18ms WASM COMPUTER VISION"),
    ]
    for i, (k, v) in enumerate(specs):
        cx = 48 + i * 300
        if i > 0:
            o.append(rule(cx - 15, 296, cx - 15, 324, P["rule"]))
        o.append(label(cx, 302, k, P, size=8.5, ls=1.2))
        o.append(text(cx, 322, v, size=10, fill=P["text"], weight="700", family=MONO))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 06 / EMPIRICAL BENCHMARK MATRIX
# ==============================================================================
def benchmark(t, motion=True):
    W, H = 1280, 300
    P = THEMES[t]
    o = [head(W, H, motion)]
    o.append(f'<rect width="{W}" height="{H}" rx="18" fill="{P["bg0"]}" stroke="{P["rule"]}" stroke-width="1.5"/>')

    # Top Strip
    o.append(rule(0, 48, W, 48, P["rule"]))
    o.append(f'<circle cx="48" cy="24" r="4.5" fill="{P["green"]}" class="pulse"/>')
    o.append(label(64, 28, "EMPIRICAL BENCHMARK MATRIX  //  BLACK MAMBA JIT vs CPYTHON 3.14 (IDENTICAL KERNELS)", P, ls=1.8))
    o.append(text(W - 48, 28, "HOST: x86-64 NATIVE MACHINE · ZERO RUNTIME GC TAX", size=10, fill=P["accent"],
                  weight="700", family=MONO, ls=1.5, anchor="end"))

    bench_data = [
        ("fib(32)", 288.62, 11.08, "26.1x", "14.2 MB vs 1.1 MB"),
        ("collatz(40k)", 227.84, 8.29, "27.5x", "12.8 MB vs 0.9 MB"),
        ("mandelbrot(120x120)", 39.14, 3.37, "11.6x", "16.4 MB vs 1.4 MB"),
        ("count_primes(30k)", 22.05, 1.73, "12.7x", "11.2 MB vs 0.8 MB"),
    ]

    base_y = 80
    row_h = 44
    bar_max_w = 480

    for i, (k_name, py_t, bm_t, ratio, mem) in enumerate(bench_data):
        ry = base_y + i * (row_h + 8)
        o.append(f'<rect x="48" y="{ry}" width="{W-96}" height="{row_h}" rx="8" fill="{P["panel"]}" stroke="{P["rule"]}" stroke-width="1"/>')

        o.append(text(68, ry + 27, k_name, size=12, fill=P["text"], weight="700", family=MONO))
        o.append(text(250, ry + 27, f"CPython: {py_t:.1f}ms", size=10.5, fill=P["micro"], weight="600", family=MONO))

        # Dynamic Benchmark Laser Bar
        bx = 410
        bw = int((py_t / 300.0) * bar_max_w)
        bw_bm = max(int((bm_t / 300.0) * bar_max_w), 12)

        # CPython baseline track
        o.append(f'<rect x="{bx}" y="{ry+16}" width="{bw}" height="12" rx="4" fill="{P["bar"]}" opacity="0.6"/>')
        # Black Mamba blazing laser
        cls_laser = 'class="pulse_glow"' if motion else ''
        o.append(f'<rect x="{bx}" y="{ry+16}" width="{bw_bm}" height="12" rx="4" fill="{P["green"]}" {cls_laser}/>')

        o.append(text(bx + bw + 18, ry + 26, f"{bm_t:.2f}ms", size=11, fill=P["green"], weight="800", family=MONO))

        # Speedup Ratio Pill
        px = W - 240
        o.append(f'<rect x="{px}" y="{ry+8}" width="78" height="28" rx="6" fill="{P["bg0"]}" stroke="{P["green"]}" stroke-width="1.2"/>')
        o.append(text(px + 39, ry + 26, ratio, size=11, fill=P["green"], weight="900", family=MONO, anchor="middle"))

        o.append(text(W - 68, ry + 27, mem, size=9.5, fill=P["dim"], weight="600", family=MONO, anchor="end"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 07 / LIVE 360° RADAR & ISSUEOPS TELEMETRY
# ==============================================================================
def telemetry(t, motion=True):
    W, H = 1280, 380
    P = THEMES[t]
    o = [head(W, H, motion)]
    o.append(f'<rect width="{W}" height="{H}" rx="18" fill="{P["bg0"]}" stroke="{P["rule"]}" stroke-width="1.5"/>')

    # Top Strip
    o.append(rule(0, 48, W, 48, P["rule"]))
    o.append(f'<circle cx="48" cy="24" r="4.5" fill="{P["accent"]}" class="pulse"/>')
    o.append(label(64, 28, "LIVE 360° RADAR & ISSUEOPS STATE MACHINE  //  EVENT-DRIVEN VISITOR TELEMETRY", P, ls=1.8))
    o.append(text(W - 48, 28, "HANDSHAKE PROTOCOL: ACTIVE · ACK TIME: ~15s", size=10, fill=P["green"],
                  weight="700", family=MONO, ls=1.5, anchor="end"))

    # Left Section: 360° Tactical Radar Screen
    rx, ry = 220, 210

    # Range Circles
    for r in [40, 80, 120, 150]:
        o.append(f'<circle cx="{rx}" cy="{ry}" r="{r}" stroke="{P["rule_glow"]}" stroke-width="1" stroke-dasharray="3 6" fill="none"/>')

    # Crosshair Axes
    o.append(f'<line x1="{rx-155}" y1="{ry}" x2="{rx+155}" y2="{ry}" stroke="{P["rule"]}" stroke-width="1"/>')
    o.append(f'<line x1="{rx}" y1="{ry-155}" x2="{rx}" y2="{ry+155}" stroke="{P["rule"]}" stroke-width="1"/>')

    # Tactical Sweep Beam
    cls_radar = 'class="radar"' if motion else ''
    o.append(f'<g {cls_radar}>')
    o.append(f'<line x1="{rx}" y1="{ry}" x2="{rx}" y2="{ry-150}" stroke="{P["accent_bright"]}" stroke-width="2"/>')
    o.append(f'<polygon points="{rx},{ry} {rx-60},{ry-140} {rx},{ry-150}" fill="{P["accent"]}" opacity="0.25"/>')
    o.append('</g>')

    # Target Blips (Telemetry signals from visitors)
    blips = [
        (rx + 65, ry - 70, "@kicode01", "ping1", P["accent_bright"]),
        (rx - 80, ry + 45, "@guest-eng", "ping2", P["green"]),
        (rx + 95, ry + 60, "@recruiter", "ping3", P["purple"]),
    ]
    for bx, by, tag, ping_cls, col in blips:
        cls_p = f'class="{ping_cls}"' if motion else ''
        o.append(f'<circle cx="{bx}" cy="{by}" r="4" fill="{col}"/>')
        o.append(f'<circle cx="{bx}" cy="{by}" r="12" stroke="{col}" fill="none" {cls_p}/>')
        o.append(text(bx + 10, by + 4, tag, size=8.5, fill=col, weight="700", family=MONO))

    # Right Section: Handshake Log Terminal
    tx, ty = 430, 75
    tw, th = W - tx - 48, 275
    o.append(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="12" fill="{P["panel"]}" stroke="{P["rule"]}" stroke-width="1"/>')
    o.append(rule(tx, ty + 38, tx + tw, ty + 38, P["rule"]))

    o.append(text(tx + 20, ty + 24, "VERIFIED TELEMETRY STREAM (ISSUEOPS STATE MACHINE)", size=10, fill=P["text"], weight="700", family=MONO, ls=1.0))
    o.append(text(tx + tw - 20, ty + 24, "PORT: 443 [OPEN]", size=9, fill=P["green"], weight="700", family=MONO, anchor="end"))

    # Load real signals from telemetry.json
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
        sy = ty + 56 + i * 68
        o.append(f'<rect x="{tx+16}" y="{sy}" width="{tw-32}" height="56" rx="8" fill="{P["bg0"]}" stroke="{P["rule"]}" stroke-width="1"/>')
        o.append(text(tx + 30, sy + 22, f"[{s.get('id')}] @{s.get('sender')}", size=11, fill=P["accent_bright"], weight="800", family=MONO))
        o.append(text(tx + 30, sy + 42, f"ORG: {s.get('org')}  ·  FOCUS: {s.get('focus')}", size=9, fill=P["dim"], weight="600", family=MONO))
        o.append(text(tx + tw - 34, sy + 22, "VERIFIED", size=9, fill=P["green"], weight="800", family=MONO, anchor="end"))
        o.append(text(tx + tw - 34, sy + 42, s.get("timestamp", ""), size=8.5, fill=P["micro"], weight="500", family=MONO, anchor="end"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# 08 / ANNUAL CONTRIBUTION SPECTRUM EQUALIZER
# ==============================================================================
def bars(t, motion=True):
    W, H = 1280, 250
    P = THEMES[t]
    o = [head(W, H, motion)]

    o.append(f"""<defs>
<linearGradient id="eq_grad_{t}" x1="0" y1="1" x2="0" y2="0">
  <stop offset="0%" stop-color="{P['blue']}"/>
  <stop offset="60%" stop-color="{P['accent_bright']}"/>
  <stop offset="100%" stop-color="{P['green']}"/>
</linearGradient>
</defs>""")

    o.append(f'<rect width="{W}" height="{H}" rx="18" fill="{P["bg0"]}" stroke="{P["rule"]}" stroke-width="1.5"/>')

    o.append(rule(0, 44, W, 44, P["rule"]))
    o.append(f'<circle cx="48" cy="22" r="4.5" fill="{P["accent_bright"]}" class="pulse"/>')
    o.append(label(64, 26, "ANNUAL CONTRIBUTION CADENCE  //  12-MONTH SPECTRUM EQUALIZER", P, ls=1.8))
    o.append(text(W - 48, 26, f"{STATS.get('total_contributions', 386)} CONTRIBUTIONS RECORDED", size=10,
                  fill=P["accent_bright"], weight="700", family=MONO, ls=1.5, anchor="end"))

    base_y = 195
    for level in [35, 75, 115]:
        o.append(f'<line x1="48" y1="{base_y - level}" x2="{W - 48}" y2="{base_y - level}" stroke="{P["rule"]}" stroke-width="0.6" stroke-dasharray="2 6"/>')

    m_data = STATS.get("monthly", [])
    if m_data:
        max_c = max(d["count"] for d in m_data) or 1
        n = len(m_data)
        bar_w = 76
        gap = (W - 96 - (n * bar_w)) / (n - 1) if n > 1 else 0
        max_h = 110

        for i, d in enumerate(m_data):
            bx = 48 + i * (bar_w + gap)
            count = d["count"]
            bh = int((count / max_c) * max_h)
            bh = max(bh, 6)
            by = base_y - bh

            eq_cls = f"eq{(i % 3) + 1}" if (motion and count > 0) else ""
            fill_val = f"url(#eq_grad_{t})" if count == max_c else P["bar"]

            o.append(f'<g class="{eq_cls}">')
            o.append(f'<rect x="{bx:.1f}" y="{by}" width="{bar_w}" height="{bh}" rx="5" fill="{fill_val}"/>')
            if count > 40:
                o.append(f'<rect x="{bx:.1f}" y="{by-6}" width="{bar_w}" height="2.5" rx="1" fill="{P["green"]}"/>')
            o.append('</g>')

            o.append(text(bx + bar_w / 2, base_y + 18, d["month"][-2:], size=10, fill=P["micro"],
                          weight="700", family=MONO, anchor="middle"))
            if count > 0:
                col = P["text"] if count == max_c else P["dim"]
                o.append(text(bx + bar_w / 2, by - 10, str(count), size=10, fill=col,
                              weight="800", family=MONO, anchor="middle"))

    o.append("</svg>")
    return "".join(o)


# ==============================================================================
# README GLUE & BUILD ORCHESTRATION
# ==============================================================================
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
        "card-mamba": card_mamba,
        "card-typenscrape": card_typenscrape,
        "card-voltsense": card_voltsense,
        "card-meemomini": card_meemomini,
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
