"""
Generates the animated SVG assets behind the profile README.

What makes this more than a poster:

  1. GitHub strips <script>, <style> and inline <svg> from a README, but it
     happily serves an .svg *file* as an <img> — and CSS animations inside that
     image still run. So the page can move with no JavaScript at all.
  2. Every animated asset has a static twin, selected by a
     `prefers-reduced-motion` media query in <picture>. Almost nobody wires
     that up; it is the difference between a gimmick and something that
     respects its reader.
  3. Every number is read from the API. Nothing on the page is typed by hand.

Two invariants keep the animation honest:
  * The base state of each element is its FINAL state. Animation only adds
    motion; if a renderer ignores CSS the page still reads correctly.
  * Wipes use <mask> with an animated rect width. `clip-path: inset()` resolves
    against the SVG viewport rather than the element box, so it is unusable
    here.

Usage:
    python generate.py            # uses stats.json if present, else fetches
    python generate.py --fetch    # force a fresh pull from the GitHub API
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

TICKER = [
    "PYTHON", "C", "C++", "X86-64", "LLVM IR", "WEBASSEMBLY", "TYPESCRIPT",
    "REACT", "NEXT.JS", "VITE", "TAILWIND", "LLM", "FIREBASE", "ESP32", "OPENSCAD",
    "SPACY", "SHOPIFY API", "NODE", "GIT",
]

# Transcribed from blackmamba-lang's own benchmark table. Re-run that suite in
# the repo before trusting these after a compiler change.
BENCH = [
    ("fib(32)", 288.62, 11.078, "26.1x"),
    ("collatz(40k)", 227.84, 8.291, "27.5x"),
    ("mandelbrot(120x120)", 39.14, 3.368, "11.6x"),
    ("count_primes(30k)", 22.05, 1.730, "12.7x"),
]

# --------------------------------------------------------------- palettes ----
# Amber on near-black. Flat by design: hairlines and spacing carry the structure,
# so the page reads like an instrument panel rather than a poster.
THEMES = {
    "dark": {
        "bg0": "#08090B", "bg1": "#0B0E11", "panel": "#0F1317",
        "rule": "#1E242B", "text": "#F3F5F8", "dim": "#98A3AF",
        # `micro` is for 9-11px caps. `faint` is structure only (rules, dot
        # leaders) and must never carry text — at that size it disappears.
        "micro": "#7E8A97", "faint": "#39414B", "accent": "#FFA028",
        "bar": "#2A323C",
    },
    "light": {
        "bg0": "#FBFAF7", "bg1": "#F6F4EF", "panel": "#FFFFFF",
        "rule": "#E3DED4", "text": "#111418", "dim": "#4E5661",
        "micro": "#5A6270", "faint": "#A7ACB4", "accent": "#C2410C",
        "bar": "#C9C2B2",
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
@keyframes fi{from{opacity:0}to{opacity:1}}
@keyframes ri{from{opacity:0;transform:translateY(5px)}to{opacity:1;transform:translateY(0)}}
@keyframes gx{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes gy{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes bl{0%,45%{opacity:1}55%,100%{opacity:0}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


# ------------------------------------------------------------------- data ----
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


def fetch():
    # users/{login}, not /user: the default Actions token is an installation
    # token with no user context, so /user 403s in CI.
    user = json.loads(gh(["api", "users/" + LOGIN]))
    repos = json.loads(gh(["api", "users/%s/repos?per_page=100&sort=pushed" % LOGIN]))

    contrib, prev = None, {}
    try:
        q = " ".join(QL.split())
        gql = json.loads(gh(["api", "graphql", "-f", "query=" + q]))["data"]["user"]
        contrib = gql["contributionsCollection"]
    except Exception as exc:  # noqa: BLE001 — losing this must not break a build
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
        days = prev["days"]
        totals = {k: prev[k] for k in
                  ("total_contributions", "commits", "prs", "repos_contributed")}

    by_lang = defaultdict(int)
    for r in repos:
        # The profile repo is tooling for this page, not a project.
        if r["language"] and r["name"] != LOGIN:
            by_lang[r["language"]] += 1

    stats = {
        "login": user["login"], "name": user["name"], "bio": user["bio"],
        "created_at": user["created_at"], "public_repos": user["public_repos"],
        "followers": user["followers"],
        "total_stars": sum(r["stargazers_count"] for r in repos),
        "days": days, "lang_counts": dict(by_lang), "lang_colors": LANG_COLORS,
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
    days = [(dt.date.fromisoformat(d), c) for d, c in s["days"]]
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
    """The terminal prints this repo's real git log, so it cannot go stale."""
    try:
        out = json.loads(gh(["api", "repos/%s/%s/commits?per_page=%d"
                             % (LOGIN, LOGIN, n)]))
        return [(c["sha"][:7], c["commit"]["message"].split("\n")[0]) for c in out]
    except Exception:  # noqa: BLE001
        return []


# ------------------------------------------------------------ svg helpers ----
def head(w, h, motion):
    css = f"<style>{CSS}</style>" if motion else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
            f'viewBox="0 0 {w} {h}" fill="none" role="img">{css}')


def A(motion, cls="", delay=None):
    """Class + inline delay, or empty for the static twin."""
    if not motion:
        return ""
    out = f' class="{cls}"' if cls else ""
    if delay is not None:
        out += f' style="animation-delay:{delay:.2f}s"'
    return out


def text(x, y, s, size=14, fill="#000", weight="400", family=SANS,
         anchor="start", ls=0, op=1.0, motion=False, cls="", delay=None,
         tlen=None, style=""):
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}"'
            + (f' letter-spacing="{ls}"' if ls else "")
            + (f' opacity="{op}"' if op != 1.0 else "")
            + (f' style="{style}"' if style else "")
            + A(motion, cls, delay)
            + (f' textLength="{tlen}" lengthAdjust="spacingAndGlyphs"' if tlen else "")
            + f'>{escape(str(s))}</text>')


def rule(x1, y1, x2, y2, color, op=1.0):
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{color}" stroke-width="1" opacity="{op}"/>')


def label(x, y, s, P, size=10, ls=1.6, anchor="start", motion=False, delay=None):
    return text(x, y, s, size=size, fill=P["micro"], weight="700", family=MONO,
                ls=ls, anchor=anchor, motion=motion, cls="f", delay=delay)


# ------------------------------------------------------------------- hero ----
def boot(t, motion=True):
    """1280x400. Identity on the left, a boot log that types itself on the right."""
    W, H = 1280, 400
    P = THEMES[t]
    o = [head(W, H, motion)]

    o.append(f"""<defs><linearGradient id="wash" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="{P['bg1']}"/><stop offset="0.6" stop-color="{P['bg0']}"/>
</linearGradient></defs>""")
    o.append(f'<rect width="{W}" height="{H}" fill="url(#wash)"/>')

    # ---- top strip
    o.append(rule(0, 44, W, 44, P["rule"]))
    o.append(f'<circle cx="58" cy="22" r="3.5" fill="{P["accent"]}" {A(motion, "f", 0.05)}/>')
    o.append(text(70, 26, "ONLINE", size=10.5, fill=P["accent"], weight="700",
                  family=MONO, ls=1.8, motion=motion, cls="f", delay=0.08))
    o.append(text(150, 26, "/ PROFILE", size=10.5, fill=P["micro"], weight="600",
                  family=MONO, ls=1.8, motion=motion, cls="f", delay=0.12))
    o.append(text(W - 56, 26, "SYNC " + STATS["generated"], size=10.5,
                  fill=P["micro"], weight="600", family=MONO, ls=1.6,
                  anchor="end", motion=motion, cls="f", delay=0.16))

    # ---- left: identity
    o.append(text(56, 114, "COMPUTER ENGINEERING  /  SYSTEMS & WEB", size=11,
                  fill=P["dim"], weight="600", family=MONO, ls=2.0,
                  motion=motion, cls="f", delay=0.22))
    o.append(text(52, 198, "KIAN", size=88, fill=P["text"], weight="800",
                  ls=-3.0, motion=motion, cls="r", delay=0.30))
    o.append(text(56, 240, TAGLINE, size=20, fill=P["dim"], weight="400",
                  ls=-0.2, motion=motion, cls="r", delay=0.46))

    # ---- right: boot log
    px, py, pw, ph = 676, 68, 548, 228
    o.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" '
             f'fill="{P["panel"]}" stroke="{P["rule"]}" stroke-width="1" '
             f'{A(motion, "f", 0.20)}/>')
    o.append(text(px + 18, py + 22, "boot.log", size=10.5, fill=P["micro"],
                  weight="600", family=MONO, ls=0.8, motion=motion, cls="f", delay=0.30))
    o.append(text(px + pw - 18, py + 22, "tty0", size=10.5, fill=P["micro"],
                  weight="600", family=MONO, ls=0.8, anchor="end",
                  motion=motion, cls="f", delay=0.30))
    o.append(rule(px, py + 34, px + pw, py + 34, P["rule"]))

    rows = [
        ("init", "kian@" + STATS["login"]),
        ("role", "computer engineering"),
        ("focus", "applied ai / llm systems"),
        ("target", "x86-64 / wasm / llvm ir"),
        ("indexed", "%d repositories" % STATS["public_repos"]),
        ("status", "open to applied ai roles"),
    ]
    CW = 7.9  # mono advance at 13px, close enough to align the dot leaders
    # len(key) + 1 + len(dots) + 1 is constant, so every value lands in the same
    # column regardless of how long the key is.
    LEAD = 10
    for i, (k, v) in enumerate(rows):
        d = 0.42 + i * 0.13
        y = py + 56 + i * 20
        dots = "." * (LEAD - len(k))
        o.append(text(px + 18, y, k, size=13, fill=P["micro"], weight="600",
                      family=MONO, motion=motion, cls="f", delay=d))
        o.append(text(px + 18 + CW * (len(k) + 1), y, dots, size=13,
                      fill=P["faint"], weight="400", family=MONO, op=0.5,
                      motion=motion, cls="f", delay=d))
        o.append(text(px + 18 + CW * (LEAD + 2), y, v,
                      size=13, fill=P["dim"], weight="400", family=MONO,
                      motion=motion, cls="f", delay=d))

    ry = py + 56 + (len(rows) - 1) * 20 + 24
    o.append(text(px + 18, ry, ">", size=12.5, fill=P["accent"], weight="700",
                  family=MONO, motion=motion, cls="f", delay=1.30))
    o.append(text(px + 32, ry, "ready", size=12.5, fill=P["accent"], weight="700",
                  family=MONO, motion=motion, cls="f", delay=1.30))
    cur = ('style="opacity:0;animation:fi .18s ease-out 1.45s both,'
           'bl 1.05s steps(1) 1.60s infinite"' if motion else 'style="opacity:.9"')
    o.append(f'<rect x="{px+75}" y="{ry-10}" width="7" height="12" '
             f'fill="{P["accent"]}" {cur}/>')

    # ---- progress bar
    bx, by, bw = px + 18, py + 210, pw - 36
    o.append(text(bx, by - 8, "init complete", size=9, fill=P["micro"],
                  weight="700", family=MONO, ls=1.2, motion=motion, cls="f", delay=1.1))
    o.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="2" fill="{P["rule"]}"/>')
    o.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="2" fill="{P["accent"]}" '
             f'{A(motion, "gx", 1.05)}/>')

    # ---- metrics strip
    o.append(rule(0, 320, W, 320, P["rule"]))
    metrics = [
        (str(STATS["public_repos"]), "REPOSITORIES"),
        (str(STATS["total_contributions"]), "CONTRIBUTIONS / 12MO"),
        (str(STATS["commits"]), "COMMITS / 12MO"),
        (str(STATS["active_days"]), "ACTIVE DAYS"),
    ]
    for i, (v, k) in enumerate(metrics):
        cx = 56 + i * 292
        d = 0.9 + i * 0.07
        if i:
            o.append(rule(cx - 24, 338, cx - 24, 386, P["rule"]))
        o.append(label(cx, 350, k, P, motion=motion, delay=d))
        o.append(text(cx, 384, v, size=28, fill=P["text"], weight="700",
                      family=MONO, ls=-0.5, motion=motion, cls="r", delay=d + 0.04))

    o.append("</svg>")
    return "".join(o)


# ----------------------------------------------------------------- ticker ----
def ticker(t, motion=True):
    """1280x56 strip of technologies. The motion is the entire point."""
    W, H = 1280, 56
    P = THEMES[t]
    o = [head(W, H, motion)]

    o.append(f'<rect width="{W}" height="{H}" fill="{P["bg0"]}"/>')
    o.append(rule(0, 0.5, W, 0.5, P["rule"]))
    o.append(rule(0, H - 0.5, W, H - 0.5, P["rule"]))
    o.append(f"""<defs>
<linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="#fff" stop-opacity="0"/>
  <stop offset="0.06" stop-color="#fff" stop-opacity="1"/>
  <stop offset="0.94" stop-color="#fff" stop-opacity="1"/>
  <stop offset="1" stop-color="#fff" stop-opacity="0"/>
</linearGradient>
<mask id="edge"><rect width="{W}" height="{H}" fill="url(#fade)"/></mask>
</defs>""")

    o.append('<g mask="url(#edge)">')
    if motion:
        # Two identical copies 1400 apart; sliding exactly -1400 loops seamlessly.
        o.append("<style>@keyframes sl{from{transform:translateX(0)}"
                 "to{transform:translateX(-1400px)}}"
                 "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
                 "</style>")
        o.append('<g style="animation:sl 44s linear infinite">')
        line = "  ·  ".join(TICKER) + "  ·  "
        for x in (0, 1400):
            o.append(f'<text x="{x}" y="35" font-family="{MONO}" font-size="12" '
                     f'font-weight="600" fill="{P["dim"]}" letter-spacing="1.4" '
                     f'textLength="1400" lengthAdjust="spacing">'
                     f'{escape(line)}</text>')
        o.append("</g>")
    else:
        o.append(f'<text x="{W/2}" y="35" font-family="{MONO}" font-size="12" '
                 f'font-weight="600" fill="{P["dim"]}" letter-spacing="1.6" '
                 f'text-anchor="middle">'
                 f'{escape("  ·  ".join(TICKER[:14]))}</text>')
    o.append("</g>")

    o.append("</svg>")
    return "".join(o)


# ------------------------------------------------------------------- bars ----
def bars(t, motion=True):
    """1280x250. Monthly contributions, bars growing from the baseline."""
    W, H = 1280, 250
    P = THEMES[t]
    data = STATS["monthly"]
    o = [head(W, H, motion)]
    o.append(f'<rect width="{W}" height="{H}" fill="{P["bg0"]}"/>')

    o.append(label(56, 34, "CONTRIBUTIONS / MONTH", P, size=10, ls=1.8,
                   motion=motion, delay=0.05))
    o.append(text(W - 56, 34, "%d IN THE LAST 12 MONTHS" % STATS["total_contributions"],
                  size=10, fill=P["accent"], weight="700", family=MONO, ls=1.6,
                  anchor="end", motion=motion, cls="f", delay=0.05))

    base_y, top_y = 186, 66
    x0, x1 = 56, W - 56
    slot = (x1 - x0) / max(len(data), 1)
    bw = slot * 0.5
    mx = max([d["count"] for d in data] or [1])

    o.append(rule(x0, base_y, x1, base_y, P["rule"]))
    for frac in (0.5, 1.0):
        gy = base_y - (base_y - top_y) * frac
        o.append(rule(x0, gy, x1, gy, P["rule"], 0.4))

    for i, d in enumerate(data):
        cx = x0 + slot * i + slot / 2
        h = max((base_y - top_y) * d["count"] / mx, 2.5)
        last = i == len(data) - 1
        fill = P["accent"] if last else P["bar"]
        o.append(f'<rect x="{cx - bw/2:.1f}" y="{base_y - h:.1f}" width="{bw:.1f}" '
                 f'height="{h:.1f}" fill="{fill}" {A(motion, "gy", 0.1 + i * 0.045)}/>')
        mon = dt.date.fromisoformat(d["month"] + "-01").strftime("%b").upper()
        o.append(text(cx, base_y + 20, mon, size=9.5,
                      fill=P["accent"] if last else P["micro"], weight="700",
                      family=MONO, ls=0.8, anchor="middle",
                      motion=motion, cls="f", delay=0.3 + i * 0.045))
        if d["count"]:
            o.append(text(cx, base_y - h - 8, str(d["count"]), size=10,
                          fill=P["accent"] if last else P["dim"], weight="700",
                          family=MONO, anchor="middle",
                          motion=motion, cls="f", delay=0.45 + i * 0.045))

    o.append("</svg>")
    return "".join(o)


# ------------------------------------------------------------------ bench ----
def bench(t, motion=True):
    """1280x340. Black Mamba vs CPython on the repo's own kernels."""
    W, H = 1280, 340
    P = THEMES[t]
    o = [head(W, H, motion)]
    o.append(f'<rect width="{W}" height="{H}" fill="{P["bg0"]}"/>')

    o.append(label(56, 34, "BENCHMARK  /  BLACK MAMBA vs CPYTHON 3.14", P,
                   size=10, ls=1.8, motion=motion, delay=0.05))
    o.append(text(W - 56, 34, "LOWER IS BETTER  ·  MS PER KERNEL", size=10,
                  fill=P["faint"], weight="700", family=MONO, ls=1.5,
                  anchor="end", motion=motion, cls="f", delay=0.05))

    # legend
    o.append(f'<rect x="56" y="52" width="16" height="8" fill="{P["faint"]}" '
             f'opacity="0.55" {A(motion, "f", 0.15)}/>')
    o.append(text(78, 60, "CPYTHON", size=9.5, fill=P["dim"], weight="700",
                  family=MONO, ls=1.2, motion=motion, cls="f", delay=0.15))
    o.append(f'<rect x="168" y="52" width="16" height="8" fill="{P["accent"]}" '
             f'{A(motion, "f", 0.18)}/>')
    o.append(text(190, 60, "BLACK MAMBA", size=9.5, fill=P["dim"], weight="700",
                  family=MONO, ls=1.2, motion=motion, cls="f", delay=0.18))

    bar_x, bar_max = 300, 560
    scale = bar_max / 300.0
    y = 96
    for i, (name, cpy, bmb, sp) in enumerate(BENCH):
        d = 0.25 + i * 0.13
        o.append(text(56, y + 12, name, size=12, fill=P["text"], weight="600",
                      family=MONO, motion=motion, cls="f", delay=d))
        w1 = max(6.0, cpy * scale)
        w2 = max(6.0, bmb * scale)
        o.append(f'<rect x="{bar_x}" y="{y}" width="{w1:.1f}" height="12" '
                 f'fill="{P["faint"]}" opacity="0.55" {A(motion, "gx", d)}/>')
        o.append(f'<rect x="{bar_x}" y="{y+18}" width="{w2:.1f}" height="12" '
                 f'fill="{P["accent"]}" {A(motion, "gx", d + 0.05)}/>')
        o.append(text(bar_x + w1 + 10, y + 10, f"{cpy:g} ms", size=10,
                      fill=P["micro"], weight="500", family=MONO,
                      motion=motion, cls="f", delay=d + 0.3))
        o.append(text(bar_x + w2 + 10, y + 28, f"{bmb:g} ms", size=10,
                      fill=P["accent"], weight="600", family=MONO,
                      motion=motion, cls="f", delay=d + 0.34))
        o.append(text(W - 56, y + 22, sp, size=22, fill=P["accent"],
                      weight="700", family=MONO, ls=-0.5, anchor="end",
                      motion=motion, cls="r", delay=d + 0.28))
        y += 56

    o.append(rule(56, H - 30, W - 56, H - 30, P["rule"]))
    o.append(text(56, H - 12,
                  "measured with the repo's own suite  ·  tail-call kernel omitted (CPython recurses out)",
                  size=9.5, fill=P["micro"], weight="500", family=MONO,
                  motion=motion, cls="f", delay=0.9))
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


def update_readme(S, commits):
    p = os.path.join(ROOT, "README.md")
    if not os.path.exists(p):
        return
    with open(p, encoding="utf-8") as f:
        md = f.read()

    monthly = S["monthly"]
    if monthly:
        peak = max(monthly, key=lambda d: d["count"])
        total = S["total_contributions"] or 1
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

    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(md)
    print("  README.md refreshed")


def main():
    global STATS
    STATS = load()
    os.makedirs(ASSETS, exist_ok=True)

    jobs = {"boot": boot, "ticker": ticker, "bars": bars, "bench": bench}
    for name, fn in jobs.items():
        for theme in ("dark", "light"):
            for mode in ("anim", "static"):
                svg = fn(theme, mode == "anim")
                path = os.path.join(ASSETS, f"{name}-{theme}-{mode}.svg")
                with open(path, "w", encoding="utf-8") as f:
                    f.write(svg)
                print(f"  {name}-{theme}-{mode}.svg  {len(svg)/1024:.1f} KB")

    update_readme(STATS, recent_commits())
    print(f"\n{STATS['public_repos']} repos · {STATS['total_contributions']} contributions "
          f"· {STATS['commits']} commits · {STATS['active_days']} active days")


if __name__ == "__main__":
    main()
