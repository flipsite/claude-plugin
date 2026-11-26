"""Layout probe without Claude in Chrome: runs layout_probe.js in a headless Chromium.

Usage (from the skill's scripts folder or with full paths):

    uv run --with playwright python layout_probe.py ORIGINAL_URL [PREVIEW_URL] \
        [--out DIR] [--width 1400] [--section "Heading text"] [--styles "CSS selector"]

- Prints one line per section of each page (see layout_probe.js for what the line holds) and,
  with two URLs, the lines of both pages one under the other so they can be compared.
- Saves a full-page screenshot of each page to --out (default: current folder) as
  original.png / preview.png, and with --section also a screenshot of one section alone
  (original-section-camping-pitches.png, preview-section-…) – open them with the Read tool.
  --section takes a text in the section ("Camping Pitches", matched on both pages) or a number.
- --styles "selector" prints the computed font, colours, sizes, padding and border of the
  first element matching the selector on each page (e.g. ".et_pb_button_3", "#hero h1").

First run: Chromium is downloaded once (~150 MB) with `playwright install chromium`; the script
does it by itself when it is missing.
"""
import argparse
import pathlib
import subprocess
import sys

from playwright.sync_api import sync_playwright, Error as PlaywrightError

HERE = pathlib.Path(__file__).resolve().parent
PROBE = "\n".join(l for l in (HERE / "layout_probe.js").read_text().splitlines()
                  if not l.lstrip().startswith("//"))

STYLES_JS = """sel => { const e = document.querySelector(sel); if (!e) return 'no element ' + sel;
  const c = getComputedStyle(e), r = e.getBoundingClientRect();
  const keys = ['font-family','font-size','font-weight','line-height','text-transform','letter-spacing',
    'color','background-color','text-align','padding','margin','border','border-radius','box-shadow',
    'display','grid-template-columns','flex-direction','gap','max-width'];
  return `${Math.round(r.width)}x${Math.round(r.height)} ` + keys.map(k => `${k}: ${c.getPropertyValue(k)}`).join('; '); }"""


def launch(p):
    try:
        return p.chromium.launch()
    except PlaywrightError as e:
        if "Executable doesn't exist" not in str(e):
            raise
        print("Downloading Chromium for Playwright (once, ~150 MB)…", file=sys.stderr)
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        return p.chromium.launch()


def probe(page, url, name, out, width, section, styles):
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(url, wait_until="networkidle", timeout=60000)
    # Scroll through the page so lazy images, backgrounds and videos load.
    height = page.evaluate("document.body.scrollHeight")
    for y in range(0, height, 600):
        page.evaluate(f"window.scrollTo(0, {y})")
        page.wait_for_timeout(120)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(800)
    page.evaluate(PROBE)
    lines = page.evaluate("window.__layout")
    page.screenshot(path=str(out / f"{name}.png"), full_page=True)
    shots = [str(out / f"{name}.png")]
    if section is not None:
        # Crop the section out of a full-page shot taken at scroll 0: scrolling to the element would
        # turn sticky headers on (Divi does it with JavaScript) and cover the top of the section.
        box = page.evaluate(
            """n => { const all = [...document.querySelectorAll('.et_pb_section,.elementor-top-section,.e-con.e-parent,.vc_row:not(.vc_inner),main > section,body > section,.entry-content > .wp-block-group,.entry-content > .wp-block-cover,.entry-content > .wp-block-columns')]
                 .filter(e => { const r = e.getBoundingClientRect(); return r.width > 20 && r.height > 20; });
               const s = /^\\d+$/.test(n) ? all[+n]
                 : all.find(e => e.textContent.toLowerCase().includes(n.toLowerCase()));
               if (!s) return null;
               const r = s.getBoundingClientRect();
               return { x: r.left + scrollX, y: r.top + scrollY, width: r.width, height: r.height }; }""",
            section)
        slug = "".join(c if c.isalnum() else "-" for c in section.lower()).strip("-")[:30]
        p = out / f"{name}-section-{slug}.png"
        if box:
            page.screenshot(path=str(p), full_page=True, clip=box)
            shots.append(str(p))
        else:
            shots.append(f"(no section matching {section!r})")
    style = page.evaluate(STYLES_JS, styles) if styles else None
    return lines, shots, style


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("urls", nargs="+", help="original URL, and optionally the preview URL")
    ap.add_argument("--out", default=".", help="folder for the screenshots")
    ap.add_argument("--width", type=int, default=1400, help="viewport width (desktop 1400, mobile 390)")
    ap.add_argument("--section", help="also screenshot one section: its number in the probe output, or a text in it "
                    "(e.g. \"Camping Pitches\") to get the same section of both pages")
    ap.add_argument("--styles", help="CSS selector to print the computed styles of")
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    names = ["original", "preview"][: len(a.urls)]
    results = {}
    with sync_playwright() as p:
        browser = launch(p)
        page = browser.new_page()
        for name, url in zip(names, a.urls):
            results[name] = probe(page, url, name, out, a.width, a.section, a.styles)
        browser.close()
    for name in names:
        lines, shots, style = results[name]
        print(f"== {name}: {len(lines)} sections ({a.urls[names.index(name)]})")
        print("\n".join(lines))
        if style:
            print(f"-- styles of {a.styles}: {style}")
        print("-- screenshots: " + ", ".join(shots))


if __name__ == "__main__":
    main()
