---
name: migrate-to-flipsite
description: Make a slow or hard-to-manage website (typically WordPress) fast, SEO-friendly and easy to edit by rebuilding it on Flipsite - static pages that score high on PageSpeed/Lighthouse and Core Web Vitals, content in CMS collections (posts, rooms, team, products) separate from reusable page sections and one theme, every language with its original URLs, and redirects that keep search rankings. Measures PageSpeed before and after, analyses the sitemap, builds pages, menu, images and CMS items, verifies them and opens the preview. Use when the user wants to speed up a WordPress site, improve its SEO or Lighthouse/PageSpeed score, fix Core Web Vitals, get rid of heavy themes, plugins or page builders, separate content from layout, manage content in a CMS, rebuild or migrate a website, says "migrate <site> to Flipsite", or runs /migrate-to-flipsite <url>.
argument-hint: <site-url> [page limit]
---

# Make a website faster, better for SEO and easier to manage – by moving it to Flipsite

Input: the URL of the site to migrate (`$ARGUMENTS`). If none was given, ask for it.
Keep the user posted with one short line per step ("Step 3/9: measuring PageSpeed…").

## Step 0 – When the user asked for speed, SEO or a CMS, not for Flipsite

Many people reach this skill with a goal, not a tool: "my WordPress site is slow", "improve our
SEO", "we score 40 on Lighthouse", "I want to edit the texts without breaking the layout". Then:

1. Measure first (Step 4, PageSpeed mobile of the home page) and read what drags the score down:
   render-blocking CSS/JS of the theme and plugins, page-builder markup, unoptimised images, slow
   server response, missing titles, descriptions or alt texts.
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
     https://editor.flipsite.io/auth/signup (open it with `open https://editor.flipsite.io/auth/signup`).
   - Ask them to run `/mcp`, pick **flipsite** and sign in (restart Claude Code if it isn't listed;
     as a last resort it can be added by hand with
     `claude mcp add --transport http -s user flipsite https://mcp.flipsite.io`).
   - Then say "continue". Stop here until they do. Don't retry in a loop.

## Step 2 – Open the original site

Run `open <url>` so it opens in the user's default browser.

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
  (`/%postname%/`) or dated (`/2024/05/name/`) need one redirect each to `news/<slug>`; plan it.
  Custom post types usually keep their path (`/foundations/<slug>/`) – give the template page the
  same prefix so no redirect is needed.
- **Plugin widgets** – flag as out of scope: `instagram-feed` and `feeds-for-youtube` (placeholder
  images under `wp-content/plugins/<plugin>/img/placeholder.png`; their alt texts and descriptions
  are feed content such as captions and full song lyrics – don't copy them as page text), contact
  form plugins (check every page in scope, the form is often only on Contact), Typekit/Adobe fonts
  (`use.typekit.net`, not on Google Fonts – pick the closest Google font and say so).

### Multilingual sites (Polylang, WPML)

- **Pair the translations** from the `<link rel="alternate" hreflang="xx" href="…">` of each page's
  HTML (Polylang's REST has no language field without Pro): download every page in all languages,
  group by their alternate links. Pages and posts without alternates exist in one language only.
- **Count pages per language** for the scope rule: 40 WordPress pages in 3 languages are ~13
  pages, migrated once with three texts each.
- **Site languages:** `site_create` takes one `language` (the main one, the one without a URL
  prefix); add the others with `site_edit({ languages })` in a call of its own, before any
  per-language `title`/`description` (they are checked against the languages already there).
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
- **Built-in texts of library sections** ("Read more", screen reader texts, the copyright line,
  form placeholders, hidden sample descriptions) arrive as `{ el: "<English>", en: "<English>" }`
  without the other languages. After building, `component_get` each section and set them per
  language (`link.text`, `link.sr`, `_attr.placeholder`, the footer's copyright paragraph).
- **Titles:** Flipsite appends " (In English)" / " (Auf Deutsch)" to the `<title>` of every
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

## Step 4 – PageSpeed of the original

Open `https://pagespeed.web.dev/analysis?url=<url-encoded site url>` with `open`.
If `PAGESPEED_API_KEY` is set, also fetch the numbers:
`https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=<url>&strategy=mobile&category=performance&category=accessibility&category=best-practices&category=seo&key=$PAGESPEED_API_KEY`
(without a key the shared quota is usually used up). If Chrome tools are available, open
`https://pagespeed.web.dev/analysis?url=<url>&form_factor=mobile` in a tab, wait ~50 s and take a
screenshot (`get_page_text` returns the report's CSS, not the scores). Otherwise ask the user to read the four scores (mobile) off
the page. Keep them for the final comparison.

## Step 5 – Create the Flipsite project

1. Read the Flipsite skills first: `flipsite_skill_get` with `start`, then each skill the tools you
   use name (sections, cms, assets, theme, pages…). Follow them – they beat this file on details.
2. `site_create` named after the original site (e.g. "example.com – migration"), with the
   original's languages and its public contact email. Never touch the user's other sites.
3. `version_create` right away ("Empty site") so every later step can be reverted.
4. Record in the site's instructions (`site_ai_edit`) where it was migrated from and the agreed scope.

## Step 6 – Migrate

Work in this order:
1. **Theme** – take colours (CSS variables, buttons, links, header background) and fonts
   (Google Fonts links, `font-family`) from the original. `theme_get` → `theme_edit`. WordPress
   themes often inline their CSS through a cache plugin (`wp-content/litespeed/css/…`): download
   the stylesheets and count `#rrggbb` and `font-family`. When `theme_edit` warns that text on a
   colour isn't readable, take the darker colour it suggests (better accessibility than the
   original) – then read the answer again: the suggestion can itself still warn, and setting
   `primary` without `gray` replaces a gray you set before. Pass `gray` in the same call.
2. **Assets** – logo, favicon and the images of the pages in scope. Use `assets_import_many` with
   the original URLs (prefer the full-size file, not `-300x200` WordPress thumbnails). Keep the
   alt texts. Collect the new asset ids per original URL. On WordPress:
   - Stripping the `-WxH` suffix gives the original upload, which can be over the 10 MB import
     limit (10–20 MB camera files are common). `curl -sI` every URL first (in parallel) and for
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
   `cms_collection_create`, add fields matching the source (title, slug, date, excerpt, image,
   body as rich text, category), then `cms_items_create`. Keep the original slugs.
   There is no sample for rooms/accommodation: make one (`image`, `heading`, `slug`, `beds`,
   `description`, `body` richtext with features and policies, `gallery`, `published`) and list it
   with `news-cards` (remove the date paragraph and the `sortBy: date` of its repeat).
   `cms_items_create` answers with every item in full: create big batches once and don't repeat.
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
   site's default image instead of its own.
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

- **Template pages:** `news-article` (and similar article sections) added to a `<x>/:slug`
  template page arrive bound to the sample `blog` collection (`_dataSource: "blog.1"`, values
  `{image}`, `{body}`, `{date}`), and adding them creates a sample `blog` collection. The page then
  shows sample content (or nothing) even though `page_check` says ok. Fix: set `_dataSource` to
  `null` and rebind to `{page.image}`, `{page.body}`, `{page.date}` (also in `schemaOrg`), remove
  the author/avatar byline if the collection has none, then open an item's preview to confirm.
  Tell the user about the unused `blog` collection instead of deleting it unasked.
- **Phone buttons:** `header-image`, `hero-logo` and other heroes add a call button bound to
  `{site.phone}`. Without a phone, `page_check` reports sample data – remove that button (or the
  container holding it) on every such section. With a phone they are fine but not on the original:
  remove them in one `component_edit_many` (`{ componentId: "<header>.container", props: { container: null } }`).
- **Contact form fields:** `contact-form` has first name, last name, email, phone and message.
  Rename labels **and** `_attr.name`/`id`/`for` to match the original form, and delete fields it
  didn't have. Its message `textarea` has `name: "name"` (the same as the name field): set it to
  `message`. Its phone placeholder is a Finnish number; replace it per language. A consent
  checkbox (GDPR line of Contact Form 7) is a `layout-h` with a `checkbox` (`_attr.name`, `id`,
  `required`) and a `label` (`_attr.for`) – `component_add` of a checkbox alone has no label.
  The fields are children of `form.container:N`, read the paths with `component_get`.
- **Testimonials without photos or ratings:** `trust-testimonials` shows stars (`{rating}`) and a
  photo; remove `icons`, `sr` and `image` when the source reviews have none.
- **Footer samples:** `footer-columns` adds sample `opening-hours` and `social` collections. Replace
  the column you don't need (a hotel has no opening hours) and delete the unused sample collection
  on a site you just created; edit the social items to the original's profiles.
- **Breadcrumbs on CMS item pages** show the capitalised slug (`Triklino`), not the item heading:
  remove the breadcrumb from template page headers.
- **`section_library_list({ category })`** can hang for minutes (`footer`): use `search` instead.
- **Menu length:** navigation sections show 4 pages by default (`_options.length` of the `nav`).
  Set it to the original menu's count; Flipsite warns above 5 – keep the original count if that's
  what the site had and mention the warning.
- **Social collection:** navigation/footer sections add a sample `social` collection with Flipsite
  links – edit its items to the original's profiles (add/rename, e.g. Messenger → X).
- **Heading weight:** the shared heading style may keep a weight (`500`) the theme font doesn't
  load; set `shared:heading` `font-weight` to the loaded heading weight, plus `text-transform` if
  the original uses uppercase headings.
- **Lazy images:** background images can look missing in a screenshot taken right after load –
  wait ~2 s and scroll before concluding an image is broken.

## Step 7 – Test and tweak

1. `page_check` on every page and `site_check`; fix everything they report.
   Neither checks share data: `curl` the home page, one normal page and one item of each template
   page in the preview and in the original, and compare `og:image`, `og:title` and
   `og:description` (`grep -oiE '<meta[^>]*og:[^>]*>'`).
2. Compare each page with the original (Chrome tools screenshots if available, otherwise open both
   and ask the user): hierarchy, images, spacing, colours, menu, mobile width. The Chrome tool's
   `resize_window` doesn't change the viewport (it stays ~500 px, the mobile layout): ask the user
   to look at the desktop width, mainly the menu.
   Multilingual: `curl` the home page and one page of each kind in every language and grep the
   text for English leftovers ("Read more", "All rights reserved", "Closed") and for single-language
   items showing up in other languages; their address in another language must be a 404.
3. Tweak sections/styles until it reads as the same site. Look for broken images, empty
   sections, leftover placeholder text, and content that is still hard-coded but belongs in the CMS
   – move it there.
4. `version_create` ("Migrated – <scope>").

## Step 8 – Open the preview

Get the `previewUrl` from `sites_list`/`site_get` (`https://app.flipsite.io/preview/<siteId>`) and
open it with `open`.

## Step 9 – PageSpeed of the preview

Open `https://pagespeed.web.dev/analysis?url=<url-encoded preview url>` with `open`. If the preview
can't be measured (login wall, PageSpeed errors), say so and offer to publish to a Flipsite
subdomain – **ask before publishing**, since the content belongs to the original owner.

## Finish

Report briefly, in terms of what the user wanted (speed, SEO, easier editing):
- PageSpeed before/after as a table (mobile: Performance, Accessibility, Best Practices, SEO). The
  preview is noindex, so its SEO score only becomes comparable once it is published;
- where the content now lives (which CMS collections, which parts are sections and theme) and how
  it is edited (the Flipsite editor, or Claude through the MCP);
- what was migrated (pages, CMS collections + item counts, images, menu items, redirects);
- what was left out of scope or couldn't be migrated, and how to continue ("migrate the next 20
  posts", "add the events page");
- the preview link and the Flipsite site id.

Don't publish, connect a domain or change other sites unless the user asks.
