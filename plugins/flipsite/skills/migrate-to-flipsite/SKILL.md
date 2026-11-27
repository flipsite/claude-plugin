---
name: migrate-to-flipsite
description: Make a slow or hard-to-manage website (typically WordPress) fast, SEO-friendly and easy to edit by rebuilding it on Flipsite - static pages that score high on PageSpeed/Lighthouse and Core Web Vitals, content in CMS collections (posts, rooms, team, products) separate from reusable page sections and one theme, every language with its original URLs, and redirects that keep search rankings. Analyses the sitemap, builds pages, menu, images and CMS items, verifies them against the original and opens the preview, with an optional PageSpeed comparison of the original and the result at the end. Use when the user wants to speed up a WordPress site, improve its SEO or Lighthouse/PageSpeed score, fix Core Web Vitals, get rid of heavy themes, plugins or page builders, separate content from layout, manage content in a CMS, rebuild or migrate a website, says "migrate <site> to Flipsite", or runs /migrate-to-flipsite <url>.
argument-hint: <site-url> [page limit]
---

# Make a website faster, better for SEO and easier to manage – by moving it to Flipsite

Input: the URL of the site to migrate (`$ARGUMENTS`). If none was given, ask for it.
Keep the user posted with one short line per step ("Step 5/8: building the pages…"). Get to a
working preview first: the speed test is an optional last step, not a prerequisite.

"Open <url>" in this file means in the user's default browser: `open <url>` on macOS,
`xdg-open <url>` on Linux, `start "" <url>` on Windows. If none works, print the link instead.

## Step 0 – When the user asked for speed, SEO or a CMS, not for Flipsite

Many people reach this skill with a goal, not a tool: "my WordPress site is slow", "improve our
SEO", "we score 40 on Lighthouse", "I want to edit the texts without breaking the layout". Then:

1. Don't run a speed test now. From a quick look at the site (Step 3) name what usually drags a
   score down there: render-blocking CSS/JS of the theme and plugins, page-builder markup,
   unoptimised images, missing titles, descriptions or alt texts. Offer to measure the original
   and the rebuilt site side by side at the end (Step 8).
2. Explain in a few lines what this skill does about it: it rebuilds the site on **Flipsite**, a
   separate website service (a free account is needed), as static pages with optimised
   responsive images and only the CSS the site uses; content goes into CMS collections and a
   theme, so texts are edited without touching the layout. The original site is not changed, and
   nothing is published until the user decides.
3. Be honest about what doesn't move one-to-one (shops, member areas, booking engines, plugin
   widgets – Step 3 lists them for the site) and that small fixes inside WordPress (a caching
   plugin, image compression, fewer plugins) are an alternative when the user wants to stay.
4. Ask whether to continue with the migration (AskUserQuestion: "Rebuild it on Flipsite" /
   "Only give me tips for WordPress"). With the tips, give the concrete ones from the report and
   stop here.

When the user asked for Flipsite or a migration directly, skip this step.

## Step 1 – Make sure the Flipsite MCP works

This plugin ships the Flipsite MCP server, so its tools are usually there already. Depending on
how the server was added they are named `mcp__plugin_flipsite_flipsite__<tool>` (from this plugin)
or `mcp__flipsite__<tool>` (added by hand); use whichever exists. This file calls them by their
short names (`sites_list`, `site_create`…).

1. Find the `sites_list` tool (search for "flipsite sites_list" with ToolSearch if tools are
   deferred) and call it.
2. If it succeeds: tell the user it's connected and which account/sites it sees. Continue.
3. If it fails because the user isn't signed in (or the tools are missing):
   - If they don't have an account yet, they can create a free one at
     https://editor.flipsite.io/auth/signup (open it for them).
   - Ask them to run `/mcp`, pick **flipsite** and sign in (restart Claude Code if it isn't listed;
     as a last resort it can be added by hand with
     `claude mcp add --transport http -s user flipsite https://mcp.flipsite.io`).
   - Then say "continue". Stop here until they do. Don't retry in a loop.

## Step 2 – Open the original site

Open `<url>` in the user's default browser.

## Step 3 – Static analysis of the sitemap

Use curl with a browser User-Agent (`-A "Mozilla/5.0"`), timeouts (`-m 15`) and save downloads to
the scratchpad. Find the sitemap in this order: `robots.txt` (`Sitemap:` lines), `/wp-sitemap.xml`,
`/sitemap_index.xml`, `/sitemap.xml`. Follow sub-sitemaps.

Detect and report:
- **Platform** – WordPress if the HTML has `wp-content`/`wp-includes`; note the theme
  (`/wp-content/themes/<name>/`) and SEO plugin (Yoast `sitemap_index.xml`, Rank Math, core).
  If it isn't WordPress, say so and carry on – the method works for any site.
- **Counts by type** – pages, posts, custom post types (products, events, team…), categories, tags.
- **Languages** – `hreflang` links, `/en/` `/fi/` path prefixes, the plugin (`polylang`,
  `sitepress`/WPML, TranslatePress in the HTML). See "Multilingual sites" below.
- **Main menu** – from the homepage `<nav>`/header links. On WordPress also try
  `/wp-json/wp/v2/pages?per_page=100` and `/wp-json/wp/v2/posts?per_page=10&_embed` (often open and
  far cleaner than scraping HTML), and `/wp-json/` to list post types.
- **Images** – rough count and hosts of images on the key pages.
- **Forms, shop, embeds, logins** – anything that won't move one-to-one (WooCommerce, member areas,
  booking widgets). List these as "out of scope / needs a decision".

### WordPress specifics

- **Check that REST has the content.** Right after fetching `/wp-json/wp/v2/pages`, check the
  length of `content.rendered`. Custom themes that build pages from ACF fields or a page builder
  return it empty: then scrape the page HTML (everything between `</header>` and `<footer`) for the
  pages, and use REST only for posts. Posts are usually fine.
- **Custom post types** have their own sitemap (`<type>-sitemap.xml`) and REST route
  (`/wp-json/wp/v2/<type>?per_page=10&_embed`). They may lack fields posts have (often no
  `excerpt`): read fields with `.get()`, never assume them. Hotel and theme CPTs (`rooms`,
  `testimonials`) are often **not in REST at all** (no route in `/wp-json/`): download the URLs of
  their sitemap and parse the HTML; theme pages like "rooms list" or "blog" templates have empty
  `content.rendered` too.
- **Leftover theme demo content:** ThemeForest themes (Elementy, Avada, BeTheme…) register CPTs
  such as `portfolio`, `testimonial`, `team`, `client`, `pricing` and their importer leaves the
  demo items in the sitemap ("Jackson Pollock", "Spacesuit", "Client 12", lorem ipsum). Before
  counting them in the scope, check that the site's own pages link to them and that their text
  isn't sample text; when not, list them as "theme demo content, not migrated" instead of building
  collections for them.
- **Meta descriptions:** prefer `yoast_head_json.description` (or Rank Math's equivalent) over the
  excerpt, which ends in `[…]` and contains markup. Check them first: when every page has the same
  description (the site default), or the main language's text on translated pages, write one per
  page and language (≤160 characters) from the page content instead.
- **Content as rich text:** use `scripts/html_to_blocks.py` (next to this file; `blocks(html)`
  returns richtext blocks) on REST `content.rendered`, not regexes: nested markup, lightbox links
  and images floated inside a paragraph break regex conversions (lost lists, words split around an
  image). Then map the image URLs to the imported asset ids.
- **Social share data:** record each page's `og:image` (`yoast_head_json.og_image[0].url`, or the
  `<meta property="og:image">` of the HTML) and `og:title`/`og:description` where they differ from
  the `<title>` and meta description. Pages and posts without an `og:image` get Flipsite's
  site-wide default image, so a link shared on social media shows a different picture unless you
  set one.
- **Permalink structure:** look at the URLs in `post-sitemap.xml`. Posts at the root
  (`/%postname%/`) keep their URLs with a **bare `:slug` template page**: `page_create` with
  `content` makes `<collection>/:slug`, then `page_edit({ slug: ":slug", redirect: false })`.
  Dated posts (`/2024/05/name/`) need one redirect each. Custom post types usually keep their path
  (`/foundations/<slug>/`) – give the template page the same prefix. Flipsite slugs have only
  `a-z 0-9 -`: a CPT like `van_sales` becomes `vansales/:slug` (`slugsAdjusted`), and emoji slugs
  (`…-%f0%9f%8c%bf/`) lose the emoji – add a redirect from each old address. *(Flipsite gap – remove when fixed)*
- **Dead internal links:** old posts link to pages that no longer exist (`/local-tours/`). `curl`
  every internal link target once; point dead ones to the closest current page instead of
  copying a 404. Strip newsletter/ad tracking wrappers (`r20.rs6.net`, `eot.…/f/a/…`, `fbclid`)
  to the plain target URL. Links to the site's **pre-WordPress addresses**
  (`http://www.example.de/rechtsanwalt-name.php`, `/kontakt/index.php`) are common in texts copied
  from an older site: point them to the matching page, and add a `redirect_create` from each old
  address – they may still be bookmarked or indexed.
- **Leftover shortcodes of an earlier theme:** old posts can hold the shortcodes of a builder the
  site no longer uses (`[fusion_builder_container …]` of Avada) as plain text in
  `content.rendered`, with image URLs as bare text. Strip `\[/?(fusion|vc|et_pb)_[^\]]*\]` before
  converting, drop paragraphs that are only an image URL, and write those posts' descriptions anew.
- **Plugin widgets** – flag as out of scope: `instagram-feed` and `feeds-for-youtube` (placeholder
  images under `wp-content/plugins/<plugin>/img/placeholder.png`; their alt texts and descriptions
  are feed content such as captions and full song lyrics – don't copy them as page text), contact
  form plugins (check every page in scope, the form is often only on Contact), cookie consent
  banners (Complianz `cmplz-`, Borlabs, Cookiebot, CookieYes: Flipsite has no consent component
  yet, flipsite/editor#176 – say so; a site without tracking doesn't need one), Typekit/Adobe fonts
  (`use.typekit.net`, not on Google Fonts – pick the closest Google font and say so). A
  `font-family` with no `@font-face` and no Google Fonts link (removed for GDPR) never loads:
  visitors see the browser's fallback (Times for a serif). Use the font the page actually shows
  and say so (a Times look: `Tinos`, metric-compatible). The probe and `getComputedStyle` report
  the *declared* family, not the one that rendered: check with `document.fonts.check('16px "Open
  Sans"')` or look at the screenshot. Self-hosted Google Fonts (the OMGF plugin) are linked from
  `/wp-content/uploads/omgf/<handle>/<handle>.css`: the families listed there are the ones that load.
- **Files** (PDFs of publications, price lists, forms): import them with `assets_import_many` like
  images (10 MB limit) and link them in rich text by asset id, `[PDF](das-gmbh-recht.pdf)` – it
  renders as `/files/<id>`. A Markdown link to a page id (`[Alle Beiträge](news)`) renders as that
  page's URL.
- **Privacy policy:** it names the old site's tools (Matomo, cookie banners, legal-text widgets,
  the hosting). Copy it as it is, but tell the user the owner has to update it for the new site.
  Generator policies (eRecht24 and similar) are often 80–100 KB with every chapter left in
  (Facebook Connect, Klarna, Hotjar…): normalise the heading levels (`h4`/`h5`/`h6` of the WordPress
  page → `h2`/`h3`/`h4`) and split it at chapter boundaries into several `content-richtext`
  sections of ≤ 25 KB each – one huge call is slow and easy to get wrong. Complianz cookie
  policies describe the old site's cookies (reCAPTCHA, `wp-settings-*`) and the Complianz banner;
  say that they no longer apply.
- **Booking engines and payment portals** (CampManager, Booking.com, WebHotelier, Beds24): keep
  them as buttons to their URL (`url-blank`); an embedded availability widget becomes a "Check
  availability" strip with that button.

### Page builders (Divi, Elementor, WPBakery)

Page-builder sites return their **shortcodes** (`[et_pb_section …]`, `[vc_row]`) or nothing in
REST `content.rendered`: always scrape the rendered HTML of every page, CPT item and post, and
parse it with BeautifulSoup (`uv run --with beautifulsoup4 python script.py`), one record per
module, not with regexes.
- **Divi:** modules are `.et_pb_module.et_pb_<type>` (text, image, button, slider/slide, toggle,
  blurb, code, divider, fullwidth_code) inside `.et_pb_section_N` / `.et_pb_row_N`. Texts are in
  `.et_pb_text_inner`, toggles in `.et_pb_toggle_title`/`_content`, slides in `.et_pb_slide_title`,
  `_content` and `.et_pb_more_button`. Theme Builder layouts wrap the page in
  `<header class="et-l et-l--header">`, `.et-l--post` (the content) and
  `<footer class="et-l et-l--footer">` – cut at the `<footer` **tag**: the string `et-l--footer`
  also occurs earlier, in the inline CSS. Pages without the `et-l--post` wrapper (CPT items) need
  `#main-content` instead, and still contain header and footer images: filter out the logo and
  footer badges.
- **Elementor:** widgets are `.elementor-widget-<type>` with `.elementor-widget-container`;
  sections/containers are `.elementor-section` / `.e-con`. Theme widgets have the theme's prefix
  (`data-widget_type="thetrial_core_section_title.default"`, `…_blog_list`, `…_testimonials_list`):
  list every `[data-widget_type]` of a page with its text first, then map them. REST
  `content.rendered` holds the same widget HTML, so it works for posts and legal pages too.
  Section backgrounds are in **separate files**, `/wp-content/uploads/elementor/css/post-<page id>.css`
  (linked in the `<head>`), not in inline styles: download them and grep
  `.elementor-element-<id>{…background-image|background-color…}`. Slider Revolution
  (`rs-module`) keeps slide images in `data-lazyload`.
- **WPBakery (Visual Composer):** REST `content.rendered` holds the raw shortcodes with curly
  quotes (`[vc_row css=”…”]`) – unusable, scrape the HTML. Rows are `.vc_row`, columns
  `.vc_column_container` / `.wpb_column` with the width in the class (`vc_col-sm-6` = half),
  texts in `.wpb_text_column .wpb_wrapper`; `[vc_custom_heading]` renders as a plain `h2`/`h3`
  with inline `font-size`. Themes built on it (Elementy, Jupiter, Impreza…) often repeat one
  pattern on every page: a Revolution Slider header (`[rev_slider_vc alias=…]`, a single photo),
  a big intro heading, then two text columns – parse each page into `{heading, columns: [blocks]}`
  with `html_to_blocks.py` per column and build all pages from one template section (see
  "Same layout on every page" in Step 5).
- **Backgrounds live in CSS, not in `<img>`:** section, slide and hero backgrounds are
  `background-image:url(…)` in inline `<style>` blocks (`.et_pb_section_3{…}`, `.et_pb_slide_1{…}`,
  `.elementor-element-ab12cd{…}`). Collect them per page – they are the page-header photos.
- **Video backgrounds and shape dividers** *(Flipsite gap – remove when fixed)* can be rebuilt – don't swap them for a still photo:
  - Video: download it, make it fit the 10 MB limit without sound
    (`ffmpeg -i in.mp4 -an -vf scale=1600:-2 -c:v libx264 -preset slow -crf 30 -pix_fmt yuv420p
    -movflags +faststart out.mp4`; a 76 MB 4K clip of 30 s became 7.5 MB), upload it with
    `assets_upload_url` + `curl -F file=@out.mp4`, then `component_add` a `video` to the section
    itself (index 0, `_attr` autoplay/muted/playsinline/loop, `controls: false`, `poster`) and style
    it `position: absolute; top/left 0; width/height 100%; object-fit: cover; z-index 0` (remove its
    `aspect-ratio`). Give the section `position: relative; overflow: hidden`, appearance dark and
    the original's height, and the content container `position: relative; z-index: 2`.
  - Dividers (Divi `et_pb_top/bottom_inside_divider`, Elementor `elementor-shape`): the SVG is
    base64 in the CSS – decode it, give it `width="1280" height="140"`, `assets_create` it, and add
    it as an `image` absolutely positioned at the top or bottom (height 100px, `object-fit: fill`,
    z-index 1).
  - Replace library panels the original doesn't have (`cta-image-panel` puts the text in a white
    card): remove the card style, and swap a library heading slot for a plain `heading` when it
    needs the original's size – slots of library components are styled for every instance.
  - Compare the original's computed styles (`layout_probe.py --styles "<selector>"`, or
    `getComputedStyle` in Claude in Chrome)
    for font size, weight, colours and button padding/radius, and set `shared:button` to them.
- **Sliders** *(Flipsite gap – remove when fixed)* have no Flipsite component, but users notice when one is missing. Rebuild them
  with page code (`site_code_edit({ pageId, headEnd/bodyEnd })`) and `_attr.id`s on components:
  - Hero slider (Slider Revolution `rs-slide`, Divi/Elementor sliders): read the slides' images,
    captions and `data-panzoom` (e.g. `d:10000;ss:100;se:110%` = 10 s zoom 100→110%). Add one
    `image` per slide to the hero section (`position: absolute`, full size, `object-fit: cover`,
    `loading: eager`, `_attr: { id: "hero-slide-1", "aria-hidden": "true" }`), the hero
    `position: relative; overflow: hidden`, its content `z-index: 2`. Keep the first caption as
    the h1 and add the others as paragraphs (`aria-hidden`) in the same container. Then CSS:
    captions share one grid cell (`grid-area: 1/1`), one `@keyframes` fades each slide in and out
    (24 s cycle, delays 0/8/16 s, the first with a negative delay so it shows at once), another
    zooms it, and `@media (prefers-reduced-motion: reduce)` shows only the first slide.
  - Testimonial/logo slider: give the repeat container an id, `display: flex`, `overflow-x: auto`,
    items `flex-shrink: 0; width: 100%`; in page code add `scroll-snap-type: x mandatory`, hide the
    scrollbar, and a small script that adds prev/next buttons (`aria-label`) and autoplays (paused
    on hover, off with reduced motion). Check it with Playwright: computed `opacity`/`transform`
    over time, and a click on the arrow.
- **Sticky header** *(Flipsite gap – remove when fixed)* (the menu stays on top when scrolling): there is no setting; give the header's
  navigation section `position: sticky; top: 0; z-index: 50; background-color` with
  `component_style_edit`. A header that changes when scrolled (smaller logo) needs page code.
- **What has no equivalent** (say so in the report): icon fonts (`data-icon`, ETmodules – use
  bootstrap icons or the uploaded PNG/SVG icons), parallax.
- **Repeated blocks** that the builder pastes into many pages ("Opening & Closing Dates",
  "Further information" with phone/email/contact form) – build them once and copy them with
  `section_create({ duplicate: "<section id>", pageId })` instead of creating each from the library.
- **Menus** *(Flipsite gap – remove when fixed)* are independent of the URL structure in WordPress (dropdown parents are often only
  labels), but Flipsite dropdowns list the pages nested under a parent slug. Keep the original flat
  URLs and use a flat menu of the main pages (`_options.pages`), with the rest in footer columns;
  don't move pages to nested slugs just to get a dropdown.

### Block themes (Gutenberg with Stackable, Kadence, GenerateBlocks)

Recognise them by `wp-block-stackable-*` / `stk-block` (Stackable), `wp-block-kadence-*`,
`wp-block-generateblocks-*` classes and a theme without a builder plugin. REST `content.rendered`
is complete, but it is the block markup: parse the rendered page instead, it has the backgrounds.
- **The page is a list of top-level blocks** in `.entry-content` (`.entry-content > *`). Pages
  of these themes have several `.entry-content` elements (one per template part); take the first.
  Group each block's headings, texts, images and buttons by their column
  (`.stk-block-column` / `.wp-block-column`): 2 columns with one only media → text+image section,
  ≥3 columns each with a heading → a card row, a heading + text only → a text section.
  `layout_probe.py` finds these blocks.
- **Lazy images:** Smush/`lazyload` put a 1 px SVG in `src` and the real file in `data-src` /
  `data-srcset`. Read `data-src` first.
- **Backgrounds are per-block CSS**, `.stk-<7 hex>{background-image:url(…)}` in the page's
  `<style>` blocks, keyed by the `stk-…` class of the block or column.
- **Smush AVIF/WebP URLs** (`/wp-content/smush-avif/2026/02/seeds-14.jpg.avif`) are the original
  upload with `.avif` added: drop `smush-avif/` → `uploads/` and the `.avif`. When the *upload
  itself* is AVIF (`apple-7.avif`) there's no JPG original: take the largest `-WxH.jpg` of it in
  the HTML (`apple-7-1200x900.jpg`); some only have a 150 px thumbnail, leave those out.
- **Card rows that link elsewhere** often have the link on the whole card, the "Learn More" button
  an empty `<a>`: match the card heading to a page name instead.
- **Many card rows on many pages** (here 160 cards in 39 rows): one `services`-sample collection
  with a `group` text field and a `link`/`linktext` pair, each section filtered on its group.

### Sites that are not WordPress (Next.js, Webflow, Framer, Wix, hand-made)

- **Platform hints:** `x-powered-by` and the HTML (`_next/`, `__NEXT_DATA__` → Next.js;
  `webflow`, `framerusercontent`, `wixstatic`, `squarespace`). The sitemap is usually
  `/sitemap.xml`; group its URLs by the first path segment to find the collections
  (`/blog/*`, `/use-cases/*`, `/compare/*` → one CMS collection with a template page each).
- **Content:** most of these render on the server – `curl` the page and parse `main > section`.
  When `main` is empty in the HTML (a client-rendered app), take the rendered HTML from the headless
  browser instead (`page.content()` in Playwright). Convert each section with
  `scripts/html_to_blocks.py`: it handles tables, `<pre>` code, blockquotes and images from any
  host. Framework image URLs (`/_next/image?url=…`) hold the real file in `url=`.
- **Images without an extension** (`https://api.example.com/images/<id>`): import with a
  `filename` without extension – Flipsite adds the right one (`cover` → `cover.jpg`).
- **Illustrations built in HTML/CSS** (chat windows, dashboards, cards, funnels, code boxes – common
  on SaaS sites) have no image file. Capture them with
  `uv run --with playwright python scripts/capture_elements.py URL --list` (candidates per section,
  with a selector) and then `capture_elements.py URL --out DIR "selector=name" …`: 2× PNGs of the
  elements, fixed headers and cookie banners hidden, with *prefers-reduced-motion*, which makes most
  animated mockups show their finished state (`--motion --wait 12` otherwise; look at every PNG).
  Upload them with `assets_upload_url` + `curl -F`, and never crop them: on the image set
  `aspect-ratio: auto`, `object-fit: contain`, no radius, and `image.width` = the width it had on the
  original (the file has 2×). Text the visitor reads stays real text.
- **Highlighted words in headings** (a coloured background on one word): write the word as
  `**bold**` and style the bold of the section heading once:
  `component_style_edit("_componentSectionLibrary1.heading.strong", { background-color, color,
  border-radius, padding-inline: "0.15em", white-space: "nowrap" })`.
- **Sign-up forms, log-ins and in-page apps** (`/#register`, a chat box that answers questions)
  belong to the product, not the site: link the buttons to the app's own sign-up or log-in page and
  list the decision in the report.
- **Videos** from the site itself (`/video/*.mp4`) import directly when under 10 MB; add a `video`
  component with its `poster`.

### Wix

- **Recognise it:** `static.wixstatic.com`, `parastorage.com`, `wixui-` classes. The sitemap is
  `/sitemap.xml` → `pages-sitemap.xml` (plus `blog-posts-sitemap.xml`, `store-products-sitemap.xml`
  when the site has them). Pages are server-rendered: `curl` has the text, but a headless browser
  never reaches "network idle" (wait for `load` plus a few seconds – `layout_probe.py` does).
  Sections are `#PAGES_CONTAINER section` (ClassicSection, column strips), header and footer
  `#SITE_HEADER` / `#SITE_FOOTER`. Classic Wix sites are often **not responsive** – compare the
  mobile screenshots (`--width 390`) and say that the rebuild fixes it.
- **Wix apps hide content behind URL parameters**, not pages: the Restaurants **Menus** app shows
  each menu at `/menu?menu=dinner`, `?menu=wine-list` (the links are in the page, not in the
  sitemap). Collect every `a[href]` of each page, open each variant in the headless browser and read
  the app's `data-hook` elements: `menu.name`, `menu.description`, `section.name`,
  `section.description`, `item.name`, `item.description`, `item.price`, `item.priceVariants`
  (Small / $60 / Large / $95). Wix cuts price-variant labels at about 40 characters ("Chocolate
  and Va") in its own data – the live site shows them cut too; complete only the obvious ones and
  list the rest for the owner. Two items with the same name on different menus (a lunch and a dinner
  "Veal Capricciosa") are different dishes: key by menu and section, never by name.
- **Images:** `assets_import` gets **403 Forbidden** from `static.wixstatic.com` (Wix blocks
  Flipsite's servers, the same URL works from the user's machine) *(Flipsite gap – remove when
  fixed, flipsite/editor#1577)*. Download the originals with curl (`/media/<id>`, without the
  `/v1/fill/…` part, is the full upload) and upload each with `assets_upload_url` + `curl -F` – one
  link per file, ask for all links in one turn and run the uploads in one parallel shell loop.
- **Wix stock media may not be moved.** Free Wix media is licensed for use on Wix only (Wix's
  "Free Wix Media Terms of Use"). Media ids with the prefix `11062b_`, and ids without an account
  prefix (`a6e6b2b0a74f….jpg`), are Wix's library; the site's own uploads have an account prefix
  (`4a869e_…`, `ba8d3c_…`). Replace stock photos with the owner's own (a restaurant usually has
  plenty of food photos) and list what was replaced.
- **Logos** are often inline SVG (`wixui-vector-image`): take the `outerHTML` of the `svg` with
  Playwright, drop the `<defs><style>` that targets `#comp-…`, and check the result is valid XML
  (`xml.dom.minidom.parse`) before uploading: Wix's paths carry their own `fill`, and adding a
  second one makes the file invalid – the upload then answers `success: true` with an empty file
  that can't be deleted *(Flipsite gap – remove when fixed, flipsite/editor#1977)*. One logo with
  `fill="currentColor"` (the library shows SVG logos inline) works on a dark header and a light
  footer.

### Restaurants

- Menus go in the **`menu` sample collection** (`heading`, `description`, `price`, `dietary`,
  `category`): one collection for all menus, `category` an enum with one option per course
  (`lunch`, `appetizers`, `pasta`…, `sparkling`, `red-italy`…, `catering-pasta`), the field help
  saying which menu each belongs to. Prices as written (`$24`); size variants as text
  (`Small $60 · Medium $100 · Large $140`) and a note on the serving sizes in the section intro.
  A restaurant easily has 150+ items: check the plan's CMS limit in the scope question.
- **`pricing-menu` shows two courses** *(Flipsite gap – remove when fixed, flipsite/editor#1979)*:
  add one section per two courses, set each repeat's `_options.filter` to its category in one
  `component_edit_many`, and delete the intro container (`<section>`, `{ container: null }`) of the
  continuation sections so a menu reads as one. A one-course menu: split it by
  `filterField: "itemId", filterType: "or"` into the two columns and remove the course headings.
- **Tabs (Lunch / Dinner / Wine list)** become scroll buttons to the menu sections' anchors in the
  page header (`_action: "scroll"`, `_target: "dinner"`): edit the header's button (set
  `text.value`, `icon: null`) and `component_add` the others – `component_edit` can't add siblings.
- **Reservations:** keep OpenTable/Resy/phone as on the original; a Google map is the
  `contact-overview` section with `iframeSrc: "https://www.google.com/maps?q=<name, address>&output=embed"`.
  Create the `contact` collection first (`sampleId: "contact"`) and **don't pass the `collection`
  prop** – it replaces the card container (flipsite/editor#1575) *(Flipsite gap – remove when fixed)*.
- **Opening hours** go in the `opening-hours` collection; they render in 24-hour format even on a
  US site *(Flipsite gap – remove when fixed, flipsite/editor#1978)* – say so. Originals often
  disagree with themselves (the hero says "Tue–Sun 12–9", the footer "Tue–Sat 12–10, Sun 1–9"):
  keep the more detailed one and ask the owner.
- `hero-image-overlay` requires a button: use the restaurant's two main actions (menu,
  reservations) and mention it when the original hero had none.

### Multilingual sites (Polylang, WPML)

- **Pair the translations** from the `<link rel="alternate" hreflang="xx" href="…">` of each page's
  HTML (Polylang's REST has no language field without Pro): download every page in all languages,
  group by their alternate links. Pages and posts without alternates exist in one language only.
- **Count pages per language** for the scope rule: 40 WordPress pages in 3 languages are ~13
  pages, migrated once with three texts each.
- **Site languages:** `site_create` takes one `language` (the main one, the one without a URL
  prefix); add the others with `site_edit({ languages })` in a call of its own, before any
  per-language `title`/`description` (they are checked against the languages already there). *(Flipsite gap – remove when fixed)*
  Confirm the languages with the user (it is in the scope question).
- **Keep every language's URL:** `page_create` with the main language's slug, then
  `page_edit({ slug: { en: "en/our-rooms", de: "de/unsere-zimmer" } })` – the default is
  `en/<main slug>`. Template pages too: `{ en: "en/news-en/:slug", de: "de/neuigkeiten/:slug" }`.
  Pass `redirect: false` on a site that was never published.
- **Every text per language:** `name`, `title`, `description` of pages and every section prop as
  `{ el, en, de }`. CMS fields that differ per language need `localizable: true` – also `slug` and
  `body` (the `blog` sample makes only heading/description localizable). A post that exists in one
  language gets a `languages` field (`["el"]`) so it isn't listed or linked in the others.
  Quotes (reviews) stay in their original language: a non-localizable field.
- **Built-in texts of library sections** *(Flipsite gap – remove when fixed)* ("Read more", screen reader texts, the copyright line,
  form placeholders, hidden sample descriptions) arrive as `{ el: "<English>", en: "<English>" }`
  without the other languages. After building, `component_get` each section and set them per
  language (`link.text`, `link.sr`, `_attr.placeholder`, the footer's copyright paragraph).
- **Titles:** *(Flipsite gap – remove when fixed)* Flipsite appends " (In English)" / " (Auf Deutsch)" to the `<title>` of every
  non-main language, also to an explicit title – keep titles of those languages ≤ ~45 characters.
  Give template pages a title per language: `{ en: "{page.heading} - Hotel Name", … }`.
- **Alt texts** are one string per asset: write them in the main language.
- **Check the rendered pages with `curl`**, not the Chrome tools: Chrome auto-translates pages to
  the browser language, so `get_page_text` and screenshots of `/de/` can show English.

Present a short summary table.

**Scope rule:** if there are **more than 20 pages** (pages + posts), propose a limited first scope:
- the homepage, the pages in the main menu, the footer pages (about, contact, privacy), max ~10;
- the latest ~10 posts as CMS items (plus one collection per notable custom post type);
- say clearly that the rest can be migrated later in the same way.

Ask the user to confirm the scope with AskUserQuestion (recommended option first). With 20 pages or
fewer, migrate everything and just say so.

**Plan limits:** Flipsite's free plan has one language, 100 CMS items and 50 MB of files per site
(https://flipsite.io/pricing/; paid plans have 6 languages and 1,000 items). When the scope needs
more (a multilingual site, hundreds of posts, a large image library), say so in the scope question
instead of finding out halfway through the build. The MCP doesn't say which plan the account has
*(Flipsite gap – remove when fixed, flipsite/editor#1986)*: a site with more than one language in
`sites_list` means a paid plan; otherwise ask the user.

## Step 4 – Create the Flipsite project

1. Read the Flipsite skills first: `flipsite_skill_get` with `start`, then each skill the tools you
   use name (sections, cms, assets, theme, pages…). Follow them – they beat this file on details.
2. `site_create` named after the original site (e.g. "example.com – migration"), with the
   original's languages and its public contact email. Never touch the user's other sites.
3. A new site already has its first version ("Site created"), so a `version_create` right away
   answers `created: false` – that's fine, every later step can be reverted to it.
4. Record in the site's instructions (`site_ai_edit`) where it was migrated from and the agreed scope.

## Step 5 – Migrate

Work in this order:
1. **Theme** – take colours (CSS variables, buttons, links, header background) and fonts
   (Google Fonts links, `font-family`) from the original. `theme_get` → `theme_edit`. WordPress
   themes often inline their CSS through a cache plugin (`wp-content/litespeed/css/…`): download
   the stylesheets and count `#rrggbb` and `font-family`. When `theme_edit` warns that text on a
   colour isn't readable, take the darker colour it suggests (better accessibility than the
   original) – then read the answer again: the suggestion can itself still warn, and setting
   `primary` without `gray` replaces a gray you set before. Pass `gray` in the same call. *(Flipsite gap – remove when fixed)*
2. **Assets** – logo, favicon and the images of the pages in scope. Use `assets_import_many` with
   the original URLs (prefer the full-size file, not `-300x200` WordPress thumbnails). Keep the
   alt texts. Collect the new asset ids per original URL. On WordPress:
   - Stripping the `-WxH` suffix gives the original upload, which can be over the 10 MB import
     limit (10–20 MB camera files are common). `curl -sI` every URL first – **at most 4 in
     parallel**: hundreds of requests at 16 parallel got the client's IP blocked by the origin's
     firewall for the rest of the migration (Flipsite's own imports still worked). The sizes are
     also in REST: `/wp-json/wp/v2/media?include=<ids>&_fields=source_url,media_details`. For
     files over ~9.5 MB use the `-scaled` variant (`name-scaled.jpg`, max 2560 px), or else the
     largest size in the `srcset`. Featured images from `_embed` usually are `-scaled` already.
   - Normalise `http://` → `https://` and dedupe before importing; the same file often appears
     under both. Pass `filename` as the lowercased basename so references can be built from it.
   - Flipsite stores `.jpeg` as `.jpg` (and HEIC as JPG): always take the asset ids from the
     import result, not from the filename you sent, before writing CMS items.
   - Describe the images (`assets_edit_many`) from where they appear (post title, page section).
     Look at them first: download them and make one contact sheet (PIL) in the scratchpad, then
     `Read` it – one image instead of thirty.
   - Old themes use tiny files (a 240×360 photo, a 70×39 post thumbnail). Check `width` in the
     import result; use the largest version of the same photo (the gallery often has it) or, for a
     YouTube post, the video thumbnail (`https://img.youtube.com/vi/<id>/hqdefault.jpg`).
3. **CMS** – content that repeats goes in the CMS, not in hand-made sections: posts/news, team,
   events, products, testimonials, FAQs, partners/logos. `cms_collection_samples_list` →
   `cms_collection_create`, always with `collectionId` equal to the `sampleId`
   (`{ sampleId: "blog", collectionId: "blog", name: "News" }`): with only a `name` the id is made
   from the name (`news`) and the library sections keep looking for `blog`. *(Flipsite gap – remove
   when fixed, flipsite/editor#1985)* Add fields matching the source (title, slug, date, excerpt, image,
   body as rich text, category), then `cms_items_create`. Keep the original slugs.
   There is no sample for rooms/accommodation: make one (`image`, `heading`, `slug`, `beds`,
   `description`, `body` richtext with features and policies, `gallery`, `published`) and list it
   with `news-cards` (remove the date paragraph and the `sortBy: date` of its repeat). *(Flipsite gap – remove when fixed)*
   Samples that need changing for existing content: `events` requires `date` (make it optional
   with `cms_field_edit` when the source lists events without dates, and hide the date badge of
   `events-list` with a render filter `date notEmpty`, remove its `{starts}–{ends}` row and add a
   link to `{slugUrl}`); the `faq` answer is plain text (change it to `richtext` for answers with
   lists and links); `for-sale` has no `slug`, `body`, `gallery` or pages (add them, a template page,
   and a "View" link to `{slugUrl}` in `product-for-sale`). *(Flipsite gap – remove when fixed)* Features or amenities shown per page
   (facilities of the vans, of the pods…) go in **one** collection with a `group` enum field, each
   list filtered with `_options: { filterField: "group", filterType: "or", filter: ["vans"] }`.
   Cards that link to pages (the "stay with us" cards of a home page) are a small collection from
   the `services` sample (its `page` field links each card).
   `cms_items_create` answers with every item in full: create big batches once and don't repeat. *(Flipsite gap – remove when fixed, flipsite/editor#1956, #1972)*
   A news archive is the biggest token cost of a migration (69 posts ≈ 200 KB of richtext, all of it
   printed and retyped as tool arguments): write the items to JSON files in the scratchpad, split
   them into batches of ~22 KB (larger shell output gets cut off), and fix the content in the script
   before printing, not by hand while retyping. When the posts go back years, say in the scope
   question that the oldest ones cost as much as the new ones.
   Converting WordPress post HTML to rich text blocks – write a small script (scratchpad) and then
   clean up these artefacts before creating items:
   - lightbox images (`<a href="…jpg"><img></a>`) become empty links `[](…jpg)` – turn them into
     `img` blocks (if the file was imported) or drop them;
   - nested `<strong><em>` produce `***text ***` runs – collapse to `*text*`, and add a missing
     space after `](url)` links;
   - text pasted from PDFs arrives as one `<p>` per line – merge consecutive fragments into
     paragraphs;
   - `• item` paragraphs and numbered tracklists in `<p>`s should become `ul`/`ol` blocks;
   - drop leftover `###`, `DOWNLOAD` and similar button labels;
   - write descriptions of ≤160 characters cut at a sentence, not the raw excerpt.
4. **Pages** – `page_create` per page in scope with the original slug, title and meta description.
   Set `share` (`page_edit`) to the imported asset of the page's original `og:image`. On every CMS
   template page (`news/:slug`, …) set `share: "{page.image}"`, otherwise every post shares the
   site's default image instead of its own. *(Flipsite gap – remove when fixed)*
   **Same layout on every page** (the typical theme site: a photo banner, an intro heading, two
   text columns): build the home page first, compare it with the probe, then reuse it instead of
   building each page from the library –
   - the identical banner becomes a custom section (`custom_component_create`), added to each page
     with `section_create({ sectionLibraryId: "_component1" })` (*not* `sections_create`, which
     fails for custom sections *(Flipsite gap – remove when fixed)*). An instance keeps its own
     style, so the home page can have a taller banner (`min-height` on the instance) than the
     subpages (`min-height` on `_component1`);
   - the content section is copied with `section_create({ duplicate: "<section id>", pageId })`
     and its texts set with one `component_edit_many` per few pages
     (`<id>.heading`, `<id>.container:1.richtext`, `…richtext:1`).
   **Every page needs one `h1`.** WordPress themes often have none (the page title is an `h2`, or
   it is in the slider). The library's section-intro heading is the shared custom component
   `_componentSectionLibrary1` (an `h2`); to make the page's intro heading an `h1`, delete the
   section's intro container and `component_add` a plain `heading` at index 0, then
   `component_style_edit` it with `tag: "h1"`, `inherits: ["heading"]` and the original's size and
   weight.
   Build each from library sections (`section_library_list`/`section_library_get`) that match the
   original's layout, then fill in the real text and images. Bind list sections and the
   `blog/:slug` (or similar) template page to the CMS collections.
   On a template page, pass item fields to plain sections as `{page.<field>}` props
   (`header-image` heading `{page.heading}`, `background` `{page.image}`, `content-richtext`
   `{page.body}`, `gallery-grid` `gallery` `{page.gallery}`); `page_check` with the template page
   checks the first item.
5. **Header & footer** (pageIds `header`, `footer`) – the main menu in the original order, logo,
   CTA button, footer links, social links, copyright. Pick the menu's pages explicitly with
   `_options.pages` (an array of page ids) instead of relying on the page order. Multilingual:
   `navigation-language` has the language switcher. External booking engines (Booking.com,
   WebHotelier) stay a button to their URL (`url-blank`).
6. **Redirects** – if any URL changes (e.g. `/2024/05/post-name/` → `/news/post-name`), add a
   `redirect_create` so old links keep working. Also for pages that are merged (a "rooms list"
   page into the rooms page) and the WordPress category archives (`category/news`, per language)
   → the news page.

Rewrite links to point at the new pages. Don't invent content – if something is missing, leave it
out and list it.

### Known Flipsite pitfalls

Items marked *(Flipsite gap – remove when fixed)* work around something missing or wrong in
Flipsite or its MCP server; the rest is lasting migration know-how. When Flipsite fixes a gap,
delete the marked text instead of keeping both ways.

- **Template pages:** *(Flipsite gap – remove when fixed)* `news-article` (and similar article sections) added to a `<x>/:slug`
  template page arrive bound to the sample `blog` collection (`_dataSource: "blog.1"`, values
  `{image}`, `{body}`, `{date}`), and adding them creates a sample `blog` collection. The page then
  shows sample content (or nothing) even though `page_check` says ok. Fix: set `_dataSource` to
  `null` and rebind to `{page.image}`, `{page.body}`, `{page.date}` (also in `schemaOrg`), remove
  the author/avatar byline if the collection has none, then open an item's preview to confirm.
  Tell the user about the unused `blog` collection instead of deleting it unasked.
- **Phone buttons:** *(Flipsite gap – remove when fixed)* `header-image`, `hero-logo` and other heroes add a call button bound to
  `{site.phone}`. Without a phone, `page_check` reports sample data – remove that button (or the
  container holding it) on every such section. With a phone they are fine but not on the original:
  remove them in one `component_edit_many` (`{ componentId: "<header>.container", props: { container: null } }`).
- **Contact form fields:** *(Flipsite gap – remove when fixed)* `contact-form` has first name, last name, email, phone and message.
  Rename labels **and** `_attr.name`/`id`/`for` to match the original form, and delete fields it
  didn't have. Its message `textarea` has `name: "name"` (the same as the name field): set it to
  `message`. Its phone placeholder is a Finnish number; replace it per language. A consent
  checkbox (GDPR line of Contact Form 7) is a `layout-h` with a `checkbox` (`_attr.name`, `id`,
  `required`) and a `label` (`_attr.for`) – `component_add` of a checkbox alone has no label.
  The fields are children of `form.container:N`, read the paths with `component_get`.
- **Testimonials without photos or ratings:** `trust-testimonials` shows stars (`{rating}`) and a
  photo; remove `icons`, `sr` and `image` when the source reviews have none.
- **Footer samples:** *(Flipsite gap – remove when fixed)* `footer-columns` adds sample `opening-hours` and `social` collections. Replace
  the column you don't need (a hotel has no opening hours) and delete the unused sample collection
  on a site you just created; edit the social items to the original's profiles.
- **Breadcrumbs on CMS item pages** *(Flipsite gap – remove when fixed)* show the capitalised slug (`Triklino`), not the item heading:
  remove the breadcrumb from template page headers.
- **Menu length:** *(Flipsite gap – remove when fixed)* navigation sections show 4 pages by default (`_options.length` of the `nav`).
  Set it to the original menu's count; Flipsite warns above 5 – keep the original count if that's
  what the site had and mention the warning. Look at the original's screenshot too: themes often
  list more items than fit (8 in the HTML, 6 visible at 1400 px, the rest cut off). Then show the
  visible ones and put the others in a footer column, so every page stays reachable.
- **Social collection:** *(Flipsite gap – remove when fixed)* navigation/footer sections add a sample `social` collection with Flipsite
  links – edit its items to the original's profiles (add/rename, e.g. Messenger → X).
- **Heading weight and case:** the weight of text is the one its font loads – there is no
  `font-weight`. Load the original's heading weight with `theme_edit` (`fonts.headings.weights`),
  and set `shared:heading` `text-transform` if the original uses uppercase headings.
- **Lazy images:** background images can look missing in a screenshot taken right after load –
  wait ~2 s and scroll before concluding an image is broken.
- **PNG/JPG logos render nothing:** *(Flipsite gap – remove when fixed)* navigation, footer and `trust-logos` sections set
  `image.inlineSvg: true`; with a raster logo the header is empty and `page_check` says ok. Set
  `inlineSvg: false` on every logo image that isn't an SVG (`navigation…container.image`,
  `footer…image`, the `trust-logos` repeat), and give partner logos a real height (default 32 px).
- **Sample collections come back:** *(Flipsite gap – remove when fixed)* `cta-contact`, `contact-map` and `footer-columns` reference
  `opening-hours` (and `contact-map` a sample `contact` collection with Finnish data). Deleting the
  collection while a section still lists `{opening-hours.1.hours}` makes the next section add it
  again: delete those `ul` lists first, then the collection, and edit the `contact` items.
- **Icons as images:** `service-icon-grid` shows `{icon}` (an icon library path). With uploaded
  PNG/SVG icons, replace its icon component by an `image` `{image}` and style it (`width`/`height`
  96px, `object-fit: contain`); white icons need a `background-color` (the original's colour).
- **Library layouts aren't the original's layout.** *(Flipsite gap – remove when fixed)* Card grids are 1/2/3 columns: a row of 4–6
  items on the original (Divi `et_pb_column_1_5`, Elementor columns) needs
  `component_style_edit` on the repeat container (`grid-template-columns: repeat(2,…)`,
  `@md repeat(3,…)`, `@lg repeat(5, minmax(0, 1fr))`). The section `alignment` variant aligns the
  intro *and* the items: for a left intro above centred boxes use `alignment: left` and give the
  item container `align-items: center; text-align: center`. Outlined boxes are `tiles: none` plus
  `border-width/style/color` and `border-radius: 0` on the item, not the `card` variant. Limit a
  half-width intro with `@lg max-width: 50%` on the section's intro container.
- **Section intro sizes are shared.** *(Flipsite gap – remove when fixed)* The eyebrow/heading/description of library sections is one
  custom component (`_componentSectionLibrary1`, "Section Header"), heading `heading-lg`,
  description `text-lg`. Page builders usually use smaller section headings (Divi 26px h2, 16px
  text): set them once on `_componentSectionLibrary1.heading` / `.paragraph` (it changes every
  section, which is what you want). A section whose heading differs (a 60px banner) gets a plain
  `heading` instead of the slot.
- **Rows of similar items** (four facts, five tiles, three steps, two plans): put them in a small
  CMS collection and a library section that repeats it. Static siblings have to be styled one by one
  (`…container`, `…container:1`, `…container:2` each), and components added with `component_add`
  don't inherit the shared styles: a paragraph renders as a bare `<p>`. Give each one its
  `inherits` with `component_style_edit` afterwards – `["heading"]` for a heading, `["text"]` for
  a paragraph, `["button"]` for a button, `["richtext"]` for a richtext. Passing `"inherits"` in
  the `component_add` **props** does not work: it is stored as a data string (`"[\"text\"]"`) and
  ignored. An icon in a button needs its own `width`/`height` (16px), or it fills the button on
  mobile. *(Flipsite gap – remove when fixed)*
- **A list in two columns read top to bottom** (01–06 left, 07–11 right): keep the items in order
  and give the repeat container `@md { grid-template-columns: 1fr 1fr; grid-template-rows:
  repeat(<half>, auto); grid-auto-flow: column }`.
- **Style values are often presets:** *(Flipsite gap – remove when fixed)* `order` (-9999/0/9999), `object-position` (center, top,
  bottom, left, right), `line-height`, `letter-spacing`, `font-family` (headings, body, body-bold,
  mono). The error lists the allowed values; pick the nearest.
- **Code in text:** *(Flipsite gap – remove when fixed)* CMS text fields and paragraphs drop anything that looks like an HTML tag, also
  in backticks (`<script …>` disappears). Show code in a richtext `codeBlock` (a `richtext` CMS
  field keeps the tags). A one-line snippet in a narrow card overflows it: style
  `….richtext.codeBlock` with `overflow: hidden`, `white-space: pre`, `max-width: 100%`, and the
  `richtext` and the card `min-width: 0`.
- **Extras on some items of a list** *(Flipsite gap – remove when fixed)* (a button on step 1 only, a code box on step 2, a note): add
  optional fields to the collection and the components to the repeated item, and give each one
  `_options.render: { filterField: "<field>", filterType: "notEmpty" }` – a button bound to an
  empty field still renders as an empty coloured box.
- **Rows under a list** *(Flipsite gap – remove when fixed)* (a "Works with …" line, an "OR" rule, a second call to action): add a
  container after the list's container with `margin-top` negative to close the section gap.
  `divider`s inside `component_add` props are dropped like empty containers; add them with their
  own `component_add`, and style them as a line (`height: 1px`, `background-color`, `flex-grow: 1`).
- **Two columns under one heading:** when the original's heading runs across the full width above
  both columns, don't use a text+image library section (it puts the heading in one column, 4 lines
  instead of 2). Build eyebrow+heading (`_componentSectionLibrary1` instance) above a `display:
  grid` container with the original's column widths (`@lg grid-template-columns: 564fr 580fr`), and
  when the rows line up across the columns (image | image, quote | text) give the grid one cell per
  row and column rather than two independent column stacks.
- **Quote with a portrait:** a richtext `quote` block has no photo. Use a row: a 56 px round
  `image` (`border-radius: 9999px`, `object-fit: cover`, `flex-shrink: 0`) next to a column with the
  quote paragraph and the caption, styled from the original (size, colour; italic is
  `font-family: body-italic`).
- **Links in section intros** ("See all FAQs →", "See the setup guide →"): write them as a Markdown
  link in the Description slot and style `_componentSectionLibrary1.paragraph.a` once (colour,
  `font-family: body-bold`, `text-decoration-line: none`). When the original puts that link to
  the right of the heading ("Alle Beiträge →"), set `_componentSectionLibrary1` to
  `@md { flex-direction: row; justify-content: space-between; align-items: center }` – it changes
  every section intro, so check the others.
- **Rows with a date column** (news lists): give the date column a fixed width (`@sm width:
  130px; flex-shrink: 0`), or the titles start at a different x on every row.
- **Richtext fields in library lists:** *(Flipsite gap – remove when fixed)* `faq-list`/`faq-accordion` bind the answer to a
  `paragraph`; after changing the `answer` field to richtext, replace that paragraph by a `richtext`
  component with `{answer}`, or the formatting and links are lost.
- **Text and card colours of the original:** body text follows the theme's gray scale; set
  `shared:text` and `shared:richtext.p` `color` (and `@dark`) to the original's text colour, and the
  `[style=card]` `background-color` of the card containers to the original's card colour.
- **Empty sections:** `sectionLibraryId: "empty"` (the string), not `""` – an empty string is
  rejected as missing.
- **Photo banners as section backgrounds are blurry** *(Flipsite gap – remove when fixed)*: a section
  background image (`section_style_edit({ image })`, or the `_bg` of a custom section) is served
  at 512 px (1024 px at 2×), and `image.width` on the section is ignored – a full-width banner
  looks soft on desktop. For a banner without text on it, remove the background
  (`component_edit` of the custom section with `_bg: null`, or `section_style_edit({ image: "" })`)
  and `component_add` an `image` to the section instead: `position: absolute; top/left 0;
  width/height 100%; object-fit: cover`, `image: { width: 1600, loading: "eager", srcset:
  "responsive" }`, the section `position: relative; overflow: hidden` with the original's
  `min-height`. Don't set `image.alt` through `component_edit` on the section – `"image.alt"`
  replaces the whole `image` child.
- **Contact form layout and consent** *(Flipsite gap – remove when fixed)*: after deleting the
  last-name and phone fields of `contact-form`, the remaining fields keep `sm:col-span-2`, so the
  first field sits in a half-width column: make the fields container `display: flex;
  flex-direction: column; align-items: stretch` (`@sm: null`). A consent checkbox added through
  `component_add(layout-h, { checkbox: … })` renders as `<input>` without a type – set
  `checkbox._attr.type: "checkbox"`. Form labels don't render Markdown: write the label as plain
  text and add a `link` to the privacy page next to it.

## Step 6 – Test and tweak

1. `page_check` on every page and `site_check`; fix everything they report.
   Neither checks share data: `curl` the home page, one normal page and one item of each template
   page in the preview and in the original, and compare `og:image`, `og:title` and
   `og:description` (`grep -oiE '<meta[^>]*og:[^>]*>'`).
2. **Measure, don't eyeball.** Run the layout probe on the original page and on the preview of
   the same page, and compare the lines section by section. Two ways, the same output:
   - **Without a browser extension (default, works for everyone):**
     `uv run --with playwright python scripts/layout_probe.py <original url> <preview url> --out <scratchpad>/probe`
     – headless Chromium at 1400 px (downloaded once, ~150 MB, the first run does it). It prints
     one line per section of each page and saves `original.png` / `preview.png` full-page
     screenshots (common cookie banners hidden). A font shown as `Open Sans!>browser default`
     is declared but never loaded – match the fallback that rendered, not the declared name; `--section "Camping Pitches"` also saves that section of both pages side by side
     to `Read`, `--styles ".et_pb_button_3"` prints the computed font, colours, padding and
     border of an element, `--width 390` checks the mobile layout. Without `uv`:
     `pip install playwright` and `python scripts/layout_probe.py …`.
   - **With Claude in Chrome:** paste `scripts/layout_probe.js` into `javascript_tool` on each
     page (desktop width) and read further lines with `window.__layout.slice(4, 8).join('\n')`.
   If neither works (no network for Chromium), say so and ask the user to compare the pages.
   Fix every difference: items per row (`5` vs `3+2`), card look (border/fill/radius/
   shadow), alignment of the intro and of the items, heading and paragraph sizes, section
   background colour, VIDEO and DIVIDER layers, button colour/padding/radius. Do this for the home
   page first – it has the most custom layout – and for one page of each kind.
   Go through **every** line, not only the section you were looking at: each `bg` colour other
   than white, each `VIDEO` and `DIVIDER` must be rebuilt (users notice the next one right away).
   - A divider's fill is the colour of the **neighbouring** section (Divi: a white wave on top of a
     teal section, a `#f2f2f2` wave at its bottom flowing into a grey band). Decode each divider of
     each section separately – the same shape is often reused with another fill – and give the
     neighbour section that exact background colour, or the wave shows a seam.
   - Coloured bands: set `background-color` (also under `@dark`) and `appearance: dark` on the
     section; padding-block from the original (Divi pads divider sections 150px so the waves don't
     cover the text).
   - Two-column library sections (`content-text-image`) vs a one-column original (heading, full
     width text, full width image, button): set the container `flex-direction: column` also at
     `@md`, the columns `@md width: 100%`, move the button after the image, and remove the
     `max-width: prose` of the richtext and the `screen-sm` of the shared heading – library text is
     capped at a reading width, page-builder text usually runs the full row.
   - Headings: compare how many lines each takes (`--styles "h2"` gives width × height). A
     heading in one column of a library layout wraps to 4 lines where the original ran across
     the page in 2; an original intro capped at e.g. 820 px wraps where the library's doesn't.
   - Things inside cards: every button, code box, note and photo of the original card must be
     there (look at the section crops, not only the probe line).
   Then look at the screenshots of both pages (the probe's PNGs, or Chrome screenshots):
   hierarchy, images (blurry ones need a larger `image.width` in `component_style_edit`),
   spacing, colours, menu, and the mobile width (`--width 390`). In Claude in Chrome the viewport
   is the size of the user's Chrome window (`resize_window` doesn't change it) – the headless
   probe has no such limit.
   Multilingual: `curl` the home page and one page of each kind in every language and grep the
   text for English leftovers ("Read more", "All rights reserved", "Closed") and for single-language
   items showing up in other languages; their address in another language must be a 404.
3. Tweak sections/styles until it reads as the same site. Look for broken images, empty
   sections, leftover placeholder text, and content that is still hard-coded but belongs in the CMS
   – move it there.
4. `version_create` ("Migrated – <scope>").

## Step 7 – Open the preview

Get the `previewUrl` from `sites_list`/`site_get` (`https://app.flipsite.io/preview/<siteId>`) and
open it.

## Step 8 – Optional: PageSpeed of the original and the result

Only when the user wants it (ask once at the end, or when they asked about speed or SEO): measure
both sites the same way, mobile, and compare.

1. Run `https://pagespeed.web.dev/analysis?url=<url-encoded url>&form_factor=mobile` for the
   original home page and for the preview (`https://app.flipsite.io/preview/<siteId>`). Open both;
   the numbers can also come from
   `https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=<url>&strategy=mobile&category=performance&category=accessibility&category=best-practices&category=seo`
   (without a key the shared quota is often used up; don't read API keys from the user's
   environment). With Chrome tools, wait ~50 s and take a screenshot (`get_page_text` returns the
   report's CSS, not the scores). Otherwise ask the user to read the four scores off the pages.
2. **Note on SEO:** a Flipsite preview is hidden from search engines (`noindex`), so its SEO score
   is always low and only becomes comparable once the site is published. Say this next to the
   table; compare Performance, Accessibility and Best Practices.
3. If the preview can't be measured (login wall, PageSpeed errors), say so and offer to publish to
   a Flipsite subdomain – **ask before publishing**, since the content belongs to the original owner.

## Finish

Report briefly, in terms of what the user wanted (speed, SEO, easier editing):
- if Step 8 was run: PageSpeed before/after as a table (mobile: Performance, Accessibility, Best
  Practices, SEO), with the note that the preview's SEO score only counts once it is published;
  if not, offer it in one line;
- where the content now lives (which CMS collections, which parts are sections and theme) and how
  it is edited (the Flipsite editor, or Claude through the MCP);
- what was migrated (pages, CMS collections + item counts, images, menu items, redirects);
- what was left out of scope or couldn't be migrated, and how to continue ("migrate the next 20
  posts", "add the events page");
- the preview link and the Flipsite site id.

Don't publish, connect a domain or change other sites unless the user asks.
