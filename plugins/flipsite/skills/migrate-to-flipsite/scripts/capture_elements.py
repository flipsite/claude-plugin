"""Capture parts of a page as images, for illustrations that are built in HTML/CSS.

Modern sites draw their "screenshots" (chat windows, dashboards, cards, funnels, code boxes) as
HTML and CSS, not as image files, so there is nothing to import. A Flipsite page can't rebuild
them faithfully from library sections; a sharp PNG of the original element is the closest match.
Only use this for illustrations: text the visitor reads (headings, paragraphs, prices, lists)
stays real text in Flipsite.

    # 1. list the candidates: blocks without headings next to text, per section
    uv run --with playwright python capture_elements.py URL --list

    # 2. capture the ones to keep, each "css selector=filename"
    uv run --with playwright python capture_elements.py URL --out DIR \
        "figure.hero_figure=hero-mockup" "section:nth-of-type(4) .digest=weekly-digest"

Options: --width 1400 (viewport), --scale 2 (pixel density of the PNGs), --wait 12 (seconds
for an animated mockup to finish before capturing; look at the PNG), --index N (with a
selector that matches several elements, the Nth, 0-based). Fixed and sticky elements (cookie
banners, chat buttons, headers) are hidden before capturing, and the page is scrolled through
first so lazy content and animations have run. Videos are captured as their current frame:
import the video file itself instead when it is a real video.
Then import the PNGs with assets_upload_url (+ curl -F file=@…) and use them as images.
"""
import argparse
import pathlib
import subprocess
import sys

from playwright.sync_api import sync_playwright, Error as PlaywrightError

LIST_JS = r"""() => {
  const out = [];
  const secs = [...document.querySelectorAll('main > section, main > div > section, body > section, .et_pb_section, .elementor-top-section, .e-con.e-parent')];
  const path = e => { // a short, unique enough selector
    if (e.id) return '#' + e.id;
    const cls = (e.className || '').toString().split(/\s+/).filter(c => c && !/[:\[\]\/]/.test(c)).slice(0, 2);
    let sel = e.tagName.toLowerCase() + cls.map(c => '.' + CSS.escape(c)).join('');
    if (document.querySelectorAll(sel).length > 1) {
      const sec = e.closest('section'); const idx = secs.indexOf(sec);
      if (idx >= 0) sel = `section:nth-of-type(${[...sec.parentElement.children].filter(c => c.tagName === 'SECTION').indexOf(sec) + 1}) ${sel}`;
    }
    return sel;
  };
  secs.forEach((sec, i) => {
    const cands = [...sec.querySelectorAll('div,figure,aside,picture')].filter(e => {
      const r = e.getBoundingClientRect(); if (r.width < 160 || r.height < 120) return false;
      if (e.querySelector('h1,h2,h3')) return false;
      const p = e.parentElement; if (!p || !sec.contains(p)) return false;
      return p.getBoundingClientRect().width > r.width + 40 || p.querySelector('h1,h2,h3');
    });
    cands.filter(c => !cands.some(o => o !== c && o.contains(c))).forEach(e => {
      const r = e.getBoundingClientRect();
      const kind = e.querySelector('video') ? 'video' : (e.querySelectorAll('img').length && e.innerText.trim().length < 20 ? 'image file(s)' : 'html');
      out.push(`#${i} ${Math.round(r.width)}x${Math.round(r.height)} [${kind}] ${path(e)}  "${e.innerText.trim().replace(/\s+/g, ' ').slice(0, 50)}"`);
    });
  });
  return out.join('\n');
}"""

HIDE_JS = """() => document.querySelectorAll('body *').forEach(e => {
  const pos = getComputedStyle(e).position;
  if (pos === 'fixed' || pos === 'sticky') e.style.setProperty('visibility', 'hidden', 'important'); })"""


def launch(p):
    try:
        return p.chromium.launch()
    except PlaywrightError as e:
        if "Executable doesn't exist" not in str(e):
            raise
        print("Downloading Chromium for Playwright (once, ~150 MB)…", file=sys.stderr)
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        return p.chromium.launch()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument("items", nargs="*", help='"css selector=filename" (without extension)')
    ap.add_argument("--list", action="store_true", help="list candidate illustrations per section")
    ap.add_argument("--out", default=".")
    ap.add_argument("--width", type=int, default=1400)
    ap.add_argument("--scale", type=float, default=2)
    ap.add_argument("--index", type=int, default=0)
    ap.add_argument("--motion", action="store_true",
                    help="let animations run (default: prefers-reduced-motion, which makes most sites "
                         "show the finished state of animated mockups at once)")
    ap.add_argument("--wait", type=float, default=0,
                    help="seconds to wait after scrolling an element into view, for animated mockups "
                         "(a chat that types its answers) to reach their final state")
    a = ap.parse_intermixed_args()
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = launch(p)
        page = browser.new_page(viewport={"width": a.width, "height": 900}, device_scale_factor=a.scale,
                                reduced_motion="no-preference" if a.motion else "reduce")
        page.goto(a.url, wait_until="networkidle", timeout=60000)
        h = page.evaluate("document.body.scrollHeight")
        for y in range(0, h, 500):
            page.evaluate(f"window.scrollTo(0, {y})")
            page.wait_for_timeout(150)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(1000)
        if a.list:
            print(page.evaluate(LIST_JS))
        page.evaluate(HIDE_JS)
        for item in a.items:
            sel, _, name = item.rpartition("=")
            loc = page.locator(sel)
            n = loc.count()
            if not n:
                print(f"!! no element for {sel}")
                continue
            el = loc.nth(min(a.index, n - 1))
            el.scroll_into_view_if_needed()
            page.wait_for_timeout(400 + int(a.wait * 1000))
            path = out / f"{name}.png"
            el.screenshot(path=str(path))
            box = el.bounding_box()
            print(f"{path}  {int(box['width'])}x{int(box['height'])} css px ({n} match{'es' if n > 1 else ''})")
        browser.close()


if __name__ == "__main__":
    main()
