"""Builds a local preview of the profile README using GitHub's own renderer.

Renders README.md through the GitHub markdown API, strips the `themed-picture`
wrapper GitHub adds (a plain <picture> works in a normal browser), and wraps the
result in CSS that approximates github.com so layout and contrast can be judged
before anything is pushed.
"""
import os
import re
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
PREV = os.path.join(ROOT, ".preview")

CSS = """
*{box-sizing:border-box}
body{margin:0;background:var(--page);font-family:-apple-system,BlinkMacSystemFont,
'Segoe UI',Helvetica,Arial,sans-serif;color:var(--fg);-webkit-font-smoothing:antialiased}
.shell{max-width:1012px;margin:0 auto;padding:40px 32px 80px}
.markdown-body{font-size:16px;line-height:1.5;word-wrap:break-word}
.markdown-body h2{font-size:1.5em;font-weight:600;margin:32px 0 16px;padding-bottom:.3em;
border-bottom:1px solid var(--border)}
.markdown-body h3{font-size:1.15em;font-weight:600;margin:28px 0 10px;line-height:1.3}
.markdown-body p{margin:0 0 16px}
.markdown-body a{color:var(--link);text-decoration:none}
.markdown-body a:hover{text-decoration:underline}
.markdown-body code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;
font-size:85%;background:var(--code-bg);padding:.2em .4em;border-radius:6px}
.markdown-body blockquote{margin:0 0 16px;padding:0 1em;color:var(--muted);
border-left:.25em solid var(--border)}
.markdown-body blockquote p{margin:6px 0}
.markdown-body hr{height:.25em;padding:0;margin:28px 0;background:var(--border);
border:0;border-radius:2px}
.markdown-body table{border-collapse:collapse;width:100%;margin:0 0 16px;
display:table;overflow:auto;font-size:14.5px}
.markdown-body th,.markdown-body td{border:1px solid var(--border);padding:8px 12px}
.markdown-body th{font-weight:600;background:var(--th)}
.markdown-body tr:nth-child(2n) td{background:var(--tr)}
.markdown-body img{max-width:100%;border:0}
.markdown-body p[align="center"]{margin:0 0 16px}
.markdown-body p[align="center"] img{display:inline-block}
.markdown-body sub{font-size:12px;color:var(--muted)}
.markdown-body strong{font-weight:600}
"""


def build(theme):
    with open(os.path.join(PREV, "body.html"), encoding="utf-8") as f:
        body = f.read()

    body = (body.replace('<themed-picture data-catalyst-inline="true">', "")
                .replace("</themed-picture>", ""))

    # <picture> picks its <source> by prefers-color-scheme, which headless Chrome
    # reports as dark regardless of the page. Strip the sources and pin the <img>
    # to the variant we actually want to inspect, so both files are deterministic.
    body = re.sub(r"<source\b[^>]*>", "", body)
    if theme == "dark":
        for name in ("hero", "activity", "langs"):
            body = body.replace(f"assets/{name}-light.svg", f"assets/{name}-dark.svg")

    vars_ = {
        "light": ("#ffffff", "#1f2328", "#d1d9e0", "#0969da", "#f6f8fa", "#f6f8fa",
                  "#656d76"),
        "dark": ("#0d1117", "#e6edf3", "#30363d", "#4493f8", "#161b22", "#161b22",
                 "#9198a1"),
    }[theme]
    page, fg, border, link, code_bg, th, muted = vars_

    html = f"""<!doctype html>
<html><head><meta charset="utf-8">
<title>README preview — {theme}</title>
<style>:root{{--page:{page};--fg:{fg};--border:{border};--link:{link};
--code-bg:{code_bg};--th:{th};--tr:{th};--muted:{muted}}}
{CSS}</style></head>
<body><div class="shell"><article class="markdown-body">
{body}
</article></div></body></html>"""

    path = os.path.join(ROOT, f"preview-{theme}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path


if __name__ == "__main__":
    os.makedirs(PREV, exist_ok=True)
    with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as f:
        md = f.read()
    out = subprocess.run(["gh", "api", "-X", "POST", "markdown", "-F",
                          "text=" + md, "-f", "mode=gfm"],
                         capture_output=True, text=True, encoding="utf-8")
    if out.returncode != 0:
        raise SystemExit("markdown render failed: " + out.stderr)
    with open(os.path.join(PREV, "body.html"), "w", encoding="utf-8") as f:
        f.write(out.stdout)
    for t in ("light", "dark"):
        print("wrote", build(t))
