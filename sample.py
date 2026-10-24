"""Render an SVG at a specific point in its animation timeline.

`--virtual-time-budget` is unreliable here (the frames come back frozen), so
instead we inline the SVG into a page and seek every CSS animation to an exact
time with the Web Animations API, then screenshot. This is the only way to know
what a viewer actually sees at t seconds.
"""
import subprocess
import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
PREV = os.path.join(ROOT, ".preview")
CHROME = r"C:\Users\PC\AppData\Local\ms-playwright\chromium-1228\chrome-win64\chrome.exe"

TMPL = """<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;padding:0;background:{bg}}}
</style></head><body>
<div id="host">{svg}</div>
<script>
window.addEventListener('load', () => {{
  const t = {t_ms};
  document.getAnimations().forEach(a => {{
    try {{ a.pause(); a.currentTime = t; }} catch (e) {{}}
  }});
  document.title = 'sought ' + t;
}});
</script></body></html>"""


def sample(name, t, bg="#000000", out=None):
    path = os.path.join(ROOT, "assets", f"{name}.svg")
    with open(path, encoding="utf-8") as f:
        svg = f.read()
    html = TMPL.format(svg=svg, t_ms=int(t * 1000), bg=bg)
    tmp = os.path.join(ROOT, "_sample.html")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(html)

    out = out or os.path.join(PREV, f"{name}-t{t}.png")
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu",
                    "--hide-scrollbars", "--force-device-scale-factor=2",
                    "--window-size=1280,348",
                    f"--screenshot={out}", "file:///" + tmp.replace("\\", "/")],
                   capture_output=True)
    print(f"{out}  (t={t}s)")
    return out


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "hero-dark"
    for t in [float(x) for x in sys.argv[2:]] or [0.7, 1.5, 4.0]:
        sample(name, t)
