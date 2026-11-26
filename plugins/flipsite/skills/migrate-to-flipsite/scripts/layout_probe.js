// Layout probe: paste into Claude in Chrome's javascript_tool on the ORIGINAL page at desktop
// width, then on the Flipsite preview of the same page, and compare the two outputs line by line.
// It returns the first 4 lines; read the rest with window.__layout.slice(4, 8).join('\n') ...
// One line per top-level section with what decides whether the rebuild looks the same:
//   #i height | bg colour, background image, VIDEO, DIVIDER | H: first heading size/align/colour |
//   P: first paragraph size/align | B: first button bg/colour/radius/padding |
//   rows: items per row (5 = one row of five, 3+2 = wrapped) with the item look (border, fill, radius)
// Works for Divi, Elementor, WPBakery, Gutenberg and Flipsite pages.
(() => {
  const SEL = '.et_pb_section,.elementor-top-section,.e-con.e-parent,.vc_row:not(.vc_inner),' +
    'main > section,body > section,.entry-content > .wp-block-group,.entry-content > .wp-block-cover,' +
    '.entry-content > .wp-block-columns';
  const vis = e => { const r = e.getBoundingClientRect(); return r.width > 20 && r.height > 20; };
  const cs = e => getComputedStyle(e);
  const hex = c => { const m = c.match(/\d+(\.\d+)?/g); if (!m) return c; if (m[3] === '0') return 'none';
    return '#' + m.slice(0, 3).map(n => (+n).toString(16).padStart(2, '0')).join(''); };
  const t = e => e && `${parseInt(cs(e).fontSize)}px ${cs(e).fontWeight} ${cs(e).fontFamily.split(',')[0].replace(/"/g, '')} ` +
    `${cs(e).textAlign} ${hex(cs(e).color)}${cs(e).textTransform !== 'none' ? ' ' + cs(e).textTransform : ''} "${e.textContent.trim().slice(0, 18)}"`;
  const rows = sec => {
    const seen = new Set(), out = [];
    sec.querySelectorAll('*').forEach(el => {
      if (!/flex|grid/.test(cs(el).display) || !vis(el)) return;
      const kids = [...el.children].filter(vis); if (kids.length < 2) return;
      const tops = {}; kids.forEach(k => { const y = Math.round(k.getBoundingClientRect().top / 10); tops[y] = (tops[y] || 0) + 1; });
      const per = Object.values(tops); if (Math.max(...per) < 2) return;
      const k = cs(kids[0]);
      const look = [k.borderTopWidth !== '0px' ? `border ${k.borderTopWidth} ${hex(k.borderTopColor)}` : '',
        hex(k.backgroundColor) !== 'none' ? `fill ${hex(k.backgroundColor)}` : '',
        k.borderRadius !== '0px' ? `radius ${k.borderRadius}` : '', k.boxShadow !== 'none' ? 'shadow' : '',
        `align ${k.textAlign}`].filter(Boolean).join(' ');
      const key = `${per.join('+')} w${Math.round(kids[0].getBoundingClientRect().width)} ${look}`;
      if (!seen.has(key)) { seen.add(key); out.push(key); }
    });
    return out.slice(0, 3).join('; ');
  };
  const lines = [...document.querySelectorAll(SEL)].filter(vis).map((sec, i) => {
    const s = cs(sec);
    const img = [sec, ...sec.querySelectorAll(':scope > *')].map(e => cs(e).backgroundImage)
      .find(b => b && b !== 'none' && /url\(/.test(b));
    const name = img && (img.match(/url\("?([^")]+)/) || [])[1];
    const bgImg = name ? (name.startsWith('data:') ? 'svg-data' : name.split('/').pop().slice(0, 30)) : '';
    const video = sec.querySelector('video') ? ' VIDEO' : '';
    const div = ([...sec.querySelectorAll('[class*="divider"],[class*="shape"]')]
      .some(e => /svg/.test(cs(e).backgroundImage) || e.querySelector('svg')) ||
      [...sec.querySelectorAll('img')].some(e => cs(e).position === 'absolute' && /\.svg|svg\+xml/.test(e.currentSrc || e.src)))
      ? ' DIVIDER' : '';
    const b = sec.querySelector('a.et_pb_button,.elementor-button,.wp-block-button__link,a[class*="btn"],button,a[class*="button"]');
    return `#${i} ${Math.round(sec.getBoundingClientRect().height)}px | bg ${hex(s.backgroundColor)} ${bgImg}${video}${div}` +
      ` | H ${t(sec.querySelector('h1,h2,h3')) || '-'} | P ${t(sec.querySelector('p')) || '-'}` +
      (b ? ` | B ${hex(cs(b).backgroundColor)} ${t(b)} r${cs(b).borderRadius} p${cs(b).padding}` : '') +
      ` | rows ${rows(sec) || '-'}`;
  });
  // Tool output is cut at ~2000 characters: the lines stay in window.__layout, read them 4 at a
  // time with window.__layout.slice(0, 4).join('\n'), .slice(4, 8) ...
  window.__layout = lines;
  return `${lines.length} sections\n` + lines.slice(0, 4).join('\n');
})()
