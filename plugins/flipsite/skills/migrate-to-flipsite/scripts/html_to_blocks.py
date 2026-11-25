#!/usr/bin/env python3
"""Convert WordPress HTML (REST content.rendered or a page body) into Flipsite richtext blocks.

Usage: python3 html_to_blocks.py page.html > blocks.json   (or import blocks() from it)

Handles what WordPress content usually has: headings, paragraphs, ul/ol, <strong>/<em> as
Markdown, links as [text](url), images (also inside lightbox links and floated inside a
paragraph: they are moved after the paragraph instead of splitting it), YouTube iframes as
youtube blocks. Image URLs keep their original upload (the -WxH thumbnail suffix is removed);
map them to the imported asset ids before creating items. h1 becomes h2 (the page has its own h1).
"""
import json
import re
import sys
from html.parser import HTMLParser

BLOCK = {'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'div', 'td', 'th', 'blockquote'}


def _tidy(text):
    """Markdown that renders: no spaces inside **bold** or *italic* markers, no empty markers."""
    text = re.sub(r'\*\*\s*\*\*', '', text)
    text = re.sub(r'(?<!\*)\*\s+\*(?!\*)', ' ', text)
    text = re.sub(r'\*\*(\s*)(.+?)(\s*)\*\*', lambda m: m.group(1) + ('**' + m.group(2) + '**' if m.group(2).strip() else m.group(2)) + m.group(3), text)
    text = re.sub(r'(?<![*\w])\*(?!\*)(\s*)([^*]+?)(\s*)(?<!\*)\*(?![*\w])', lambda m: m.group(1) + '*' + m.group(2) + '*' + m.group(3), text)
    text = re.sub(r'\]\(([^)]+)\)(?=\w)', r'](\1) ', text)
    return re.sub(r'\s+', ' ', text).strip()


class _Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.buf, self.tag = [], '', None
        self.list, self.items, self.skip, self.href, self.imgs = None, None, 0, None, []

    def flush(self):
        text = re.sub(r'\s+', ' ', self.buf.replace('\xa0', ' ')).strip()
        text = _tidy(text)
        self.buf = ''
        imgs, self.imgs = self.imgs, []
        if text and text not in ('**', '*', '[', ']'):
            if self.items is not None:
                self.items.append(text)
            else:
                tag = self.tag if self.tag in ('h2', 'h3', 'h4', 'h5', 'h6') else ('h2' if self.tag == 'h1' else 'p')
                self.out.append({'type': tag, 'value': text})
        self.out.extend(imgs)

    def handle_starttag(self, t, a):
        a = dict(a)
        if t in ('script', 'style', 'form', 'noscript', 'head', 'title', 'nav', 'header', 'footer'):
            self.skip += 1
            return
        if self.skip:
            return
        if t in ('ul', 'ol'):
            self.flush()
            self.list, self.items = t, []
        elif t in BLOCK:
            self.flush()
            self.tag = t
        elif t == 'br':
            self.buf += ' '
        elif t in ('strong', 'b'):
            self.buf += '**'
        elif t in ('em', 'i') and not a.get('class'):
            self.buf += '*'
        elif t == 'a':
            self.href = a.get('href')
            self.buf += '['
        elif t == 'img':
            src = (a.get('data-src') or a.get('src') or '').split('?')[0]
            if 'uploads' in src:
                self.imgs.append({'type': 'img', 'value': re.sub(r'-\d+x\d+(?=\.\w+$)', '', src),
                                  **({'alt': a['alt']} if a.get('alt') else {})})
        elif t == 'iframe':
            y = re.search(r'youtube(?:-nocookie)?\.com/embed/([\w-]+)', a.get('src') or '')
            if y:
                self.flush()
                self.out.append({'type': 'youtube', 'value': y.group(1)})

    def handle_endtag(self, t):
        if t in ('script', 'style', 'form', 'noscript', 'head', 'title', 'nav', 'header', 'footer'):
            self.skip -= 1
            return
        if self.skip:
            return
        if t in ('strong', 'b'):
            self.buf += '**'
        elif t in ('em', 'i'):
            self.buf += '*' if self.buf.count('*') % 2 else ''
        elif t == 'a':
            i = self.buf.rfind('[')
            txt = self.buf[i + 1:].strip()
            link = f'[{txt}]({self.href})' if txt and self.href and not self.href.startswith('#') else txt
            self.buf = self.buf[:i] + link
        elif t in ('ul', 'ol'):
            self.flush()
            if self.items:
                self.out.append({'type': self.list, 'value': self.items})
            self.items = self.list = None
        elif t in BLOCK:
            self.flush()
            self.tag = None

    def handle_data(self, d):
        if not self.skip:
            self.buf += d


def blocks(html):
    p = _Parser()
    p.feed(html)
    p.flush()
    return p.out


if __name__ == '__main__':
    print(json.dumps(blocks(open(sys.argv[1], encoding='utf-8').read()), ensure_ascii=False, indent=1))
