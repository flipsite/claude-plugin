# Make your WordPress site faster, better for SEO and easier to manage

A Claude Code plugin that rebuilds an existing website – usually WordPress – on
[Flipsite](https://flipsite.io), and shows you the PageSpeed (Lighthouse) score before and after.

Ask Claude in your own words:

- *"Our WordPress site is slow, can you make it faster?"*
- *"Improve the SEO and the Lighthouse score of example.com."*
- *"I want to edit our news and team members without breaking the layout."*
- *"Move example.com to Flipsite."* or `/migrate-to-flipsite example.com`

## What you get

- **Speed.** Static pages with responsive, optimised images and only the CSS the site uses – no
  theme, plugin or page-builder overhead. On a real three-language hotel site the mobile
  PageSpeed score went from **64 to 89** (Accessibility 78 → 96, Best Practices 92 → 100).
- **SEO kept and improved.** The original URLs in every language, redirects for the addresses
  that change, a title and meta description per page and language, alt texts for every image,
  share images for social media, `hreflang` links and a sitemap.
- **Content separate from layout.** Everything that repeats – blog posts, rooms, team, products,
  reviews, FAQs – goes into **CMS collections**; pages are built from reusable **sections**; colours
  and fonts live in one **theme**. Editors change texts in the Flipsite editor, or ask Claude.
- **All languages.** Polylang and WPML sites are moved with every translation and its URL.
- **A report.** What was moved, what wasn't (shops, member areas, booking engines, plugin widgets)
  and the PageSpeed comparison, with the preview open next to the original.

The original site is never changed, and nothing is published or connected to a domain until you
say so.

## Install

In Claude Code:

```
/plugin marketplace add flipsite/claude-plugin
/plugin install flipsite@flipsite
```

Then run `/mcp`, pick **flipsite** and sign in with your Flipsite account (create a free one at
https://editor.flipsite.io/auth/signup).

If you already added the Flipsite MCP server by hand (`claude mcp add … flipsite`), remove it with
`claude mcp remove flipsite` to avoid having the tools twice.

## How it works

1. **Measure** – the PageSpeed (Lighthouse) score of the current site, and what slows it down. If
   you asked about speed or SEO without mentioning Flipsite, Claude explains the option first and
   asks before rebuilding anything; it can also just give you tips for WordPress.
2. **Analyse** – sitemap, pages, posts, custom post types, languages, menu, images, forms and
   plugins. For a large site Claude proposes a first scope (main menu + latest posts) and asks.
3. **Build** – a new Flipsite site: theme, images, CMS collections, pages from library sections,
   header and footer, redirects.
4. **Check** – every page and every language, links, images, titles and descriptions, share data.
5. **Compare** – opens the preview and its PageSpeed report next to the original's.

The plugin also connects the Flipsite MCP server (`https://mcp.flipsite.io`), so after the move you
can keep asking Claude to edit pages, add CMS items or change the theme.

## Good to know

- Works best for content sites: companies, hotels and B&Bs, restaurants, associations, portfolios,
  blogs. Web shops (WooCommerce), member areas and booking engines are listed as out of scope
  and kept as links where possible.
- A preview is hidden from search engines, so its SEO score is only comparable after publishing.

## What gets sent where

The skill fetches the public pages, sitemaps and (for WordPress) the public REST API of the site
you name, and imports its public images into your Flipsite account. Nothing else is sent anywhere.
Flipsite's privacy policy: https://flipsite.io/privacy/

## License

MIT, see [LICENSE](LICENSE).
