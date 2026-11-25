# Make your WordPress site faster, better for SEO and easier to manage

A Claude Code plugin that rebuilds an existing website, usually WordPress, on
[Flipsite](https://flipsite.io), and shows you the PageSpeed (Lighthouse) score before and after.

Ask Claude in your own words:

- *"Our WordPress site is slow, can you make it faster?"*
- *"Improve the SEO and the Lighthouse score of example.com."*
- *"We fail Core Web Vitals. What can we do?"*
- *"I want to edit our news and team members without breaking the layout."*
- *"Move example.com to Flipsite."* or `/migrate-to-flipsite example.com`

## What you get

- **Speed.** Static pages with responsive, optimised images and only the CSS the site uses. No
  theme, plugin or page-builder code is left on the page. On average, the mobile PageSpeed score
  of the sites moved so far went from **60+ to 90+**.
- **SEO kept and improved.** The original URLs in every language, redirects for the addresses
  that change, a title and meta description per page and language, alt texts for every image,
  share images for social media, `hreflang` links and a sitemap.
- **Content separate from layout.** Everything that repeats (blog posts, rooms, team, products,
  reviews, FAQs) goes into **CMS collections**. Pages are built from reusable **sections**, and
  colours and fonts live in one **theme**. Editors change texts in the Flipsite editor, or ask
  Claude.
- **All languages.** Polylang and WPML sites are moved with every translation and its URL.
- **A report.** What was moved, what wasn't (shops, member areas, booking engines, plugin widgets)
  and the PageSpeed comparison, with the preview open next to the original.

The original site is never changed, and nothing is published or connected to a domain until you
say so.

## Works with

WordPress sites made with the block editor or the classic editor, page builders such as Elementor,
Divi and WPBakery (read from the rendered pages), custom post types, Yoast SEO and Rank Math titles
and descriptions, and Polylang or WPML translations. Sites that aren't WordPress work too: the
plugin reads the sitemap and the pages.

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

1. **Measure:** the PageSpeed (Lighthouse) score of the current site, and what slows it down. If
   you asked about speed or SEO without mentioning Flipsite, Claude explains the option first and
   asks before rebuilding anything. It can also just give you tips for WordPress.
2. **Analyse:** sitemap, pages, posts, custom post types, languages, menu, images, forms and
   plugins. For a large site Claude proposes a first scope (main menu + latest posts) and asks.
3. **Build:** a new Flipsite site with the theme, images, CMS collections, pages from library
   sections, header and footer, and redirects.
4. **Check:** every page and every language, links, images, titles and descriptions, share data.
5. **Compare:** opens the preview and its PageSpeed report next to the original's.

The plugin also connects the Flipsite MCP server (`https://mcp.flipsite.io`), so after the move you
can keep asking Claude to edit pages, add CMS items or change the theme.

## Questions

**Will I lose my Google rankings?** The pages keep their addresses in every language. Addresses
that have to change (dated post URLs, merged pages, category archives) get a redirect, and titles,
descriptions, `hreflang` and the sitemap are carried over. Search engines find the same URLs, with
faster pages behind them.

**What does it cost?** The plugin is free. Flipsite's free plan covers a site in one language with
up to 100 CMS items and 50 MB of files, published to GitHub Pages, Netlify or as a ZIP. A site in
several languages, or a bigger one, needs a paid plan: https://flipsite.io/pricing/

**Does it change my WordPress site?** No. It only reads the public pages, and the new site stays a
separate preview until you publish it and point your domain at it.

**What doesn't move?** Web shops (WooCommerce), member areas, booking engines and plugin widgets
such as Instagram or YouTube feeds. Claude lists them for your site and keeps them as links where
it can.

**Can I keep editing the site with Claude afterwards?** Yes. The Flipsite MCP server works in
Claude Code, Claude, ChatGPT, Cursor and other MCP clients: https://flipsite.io/mcp/

## Good to know

- Works best for content sites: companies, hotels and B&Bs, restaurants, associations, portfolios,
  blogs.
- Made for Claude Code: the skill fetches the site with `curl` and opens pages in your browser.
- A preview is hidden from search engines, so its SEO score is only comparable after publishing.

## What gets sent where

The skill fetches the public pages, sitemaps and (for WordPress) the public REST API of the site
you name, and imports its public images into your Flipsite account through the Flipsite MCP
server. It opens Google PageSpeed Insights (pagespeed.web.dev) for the original site and the
preview, which sends those two addresses to Google. Nothing else is sent anywhere.
Flipsite's privacy policy: https://flipsite.io/privacy/

## Support

Questions and bug reports: [GitHub issues](https://github.com/flipsite/claude-plugin/issues) or
https://flipsite.io/contact/

## License

MIT, see [LICENSE](LICENSE).
