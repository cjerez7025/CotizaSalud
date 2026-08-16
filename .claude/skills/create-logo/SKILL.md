---
name: create-logo
description: Design and export a logo / brand mark / favicon for the CotizaSalud Chile site (index_13.html). Produces SVG-based vector marks matching the site's brand palette, then rasterizes them (favicon, apple-touch-icon, OG image) via a headless-Chrome screenshot since no image-generation tool is available. Use when asked to create, redesign, iterate on, or export the logo, brand mark, or favicon for this site.
---

No image-generation tool is available in this environment, so logos here
are built as **SVG vector art written by hand**, then rasterized locally
with headless Chrome when a PNG is actually needed (favicon fallback,
OG image, app icons). Treat the SVG as the source of truth; PNGs are a
build output, not something to hand-edit.

## Brand reference (pull from `index_13.html`, don't guess)

Colors are CSS custom properties in `:root` near the top of the
`<style>` block — read them fresh in case the palette has moved on:

```
--ink:#0A2A43        (primary dark navy — text, footer bg)
--ink-soft:#0F3B5C
--teal:#0079C8        (primary brand blue)
--teal-deep:#005A94
--teal-pale:#E3F1FA
--gold:#DE9F3A        (accent — used sparingly, e.g. modal accent bar)
--gold-deep:#B87E22
--slate:#4C6478
```

Typeface: **Montserrat** (weight 700–800 for wordmarks/headings).

Current placeholder mark: a rounded-square badge (`.logo .mark`, ~34px,
`border-radius:9px`, `linear-gradient(145deg, var(--teal), var(--teal-deep))`,
white bold "CS" initials centered). It appears in three places with
different surrounding treatments:

- Header logo — dark text "Cotiza" + teal "Salud" + " Chile" on light bg
  (search `<div class="logo">` near the `<header>` tag)
- Footer logo — same but "Salud" recolored to `#5FC4EF` for contrast on
  the dark `--ink` footer background
- Favicon — a minimal inline SVG data URI on the `<link rel="icon">` tag
  in `<head>` (rounded navy square + teal "CS" text)

Brand tone: health-insurance quote broker, official Bupa reseller,
Chilean market — should read as trustworthy/professional (navy + blue),
not playful. Gold is an accent only, never the dominant color.

## Workflow

1. **Design as SVG.** Write clean, hand-authored SVG (viewBox-based,
   no embedded raster). Reuse the exact hex values above — never
   invent new brand colors without asking.
2. **Preview by rendering it**, don't just eyeball the markup. Wrap the
   SVG in a minimal HTML file and screenshot it with the pattern below.
   Iterate on the SVG file, re-run, look at the PNG, adjust — same loop
   used earlier this session for reviewing the popup modal redesign.
3. **Get sign-off on the vector design** before wiring it into the
   site or generating export sizes — a logo is highly visible brand
   work, worth a quick confirmation.
4. **Wire it in**, replacing the placeholder `.mark` badge (header +
   footer) and the favicon data URI, keeping the two-tone wordmark
   treatment (light-bg vs dark-bg variants) unless asked to simplify
   it into a single lockup.
5. **Export raster sizes only as needed**: favicon (32x32 and 180x180
   `apple-touch-icon`), and optionally a proper square/OG version to
   replace the current `og:image`/`twitter:image` (which currently
   just points at a stock plan photo — swap it for a branded logo
   card once one exists, not before).

## Rendering an SVG to PNG (headless Chrome, no image-gen tool needed)

Playwright-core + the machine's installed Chrome does the job — no
browser download required:

```bash
npm install playwright-core --no-save   # in a scratch dir, not the repo
```

```javascript
// render_logo.js
const { chromium } = require('playwright-core');
const fs = require('fs');

async function main() {
  const svg = fs.readFileSync('logo.svg', 'utf8');
  const browser = await chromium.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: true,
    args: ['--no-sandbox', '--disable-gpu'],
  });
  const page = await browser.newPage({ viewport: { width: 512, height: 512 } });
  await page.setContent(`<body style="margin:0">${svg}</body>`);
  await page.screenshot({ path: 'logo-512.png', omitBackground: true });
  await browser.close();
}
main();
```

Adjust `viewport` per target size (32x32 for favicon fallback, 180x180
for apple-touch-icon, 1200x630 for an OG card with padding/background).
`omitBackground: true` keeps transparency for icon use; drop it for the
OG card (needs an opaque background — use `--ink` or `--paper`).

**Gotchas hit before, worth avoiding again:**
- Use `waitUntil: 'domcontentloaded'` (not `'load'`) if the page also
  pulls the Google Fonts `<link>` — this sandbox has no general
  outbound internet, so waiting on that request to finish hangs until
  timeout. `setContent()` sidesteps this entirely for a standalone SVG.
- Chrome launches here are occasionally flaky (intermittent
  navigation timeouts even against a local file/server) — retry once
  or twice before assuming something's actually broken.
- Kill the browser process (`await browser.close()`) every run; don't
  leave headless instances running.

## Where the final assets get wired in

- Favicon: `<link rel="icon" href="data:image/svg+xml,...">` in
  `<head>` — for a hand-authored icon, keep it inline as a data URI
  (matches the current pattern and avoids an extra HTTP request); only
  switch to a real file + `apple-touch-icon` link if adding iOS
  home-screen support.
- Header/footer marks: the `<span class="mark">CS</span>` element and
  its `.logo .mark` CSS rule — swap the CSS background/content, or
  replace the span with inline SVG if the new mark isn't a simple
  two-letter badge.
- OG/Twitter image: `og:image` / `twitter:image` meta tags in `<head>`
  — currently a placeholder plan photo (see the SEO work done earlier
  in `index_13.html`); replace once a proper branded card exists.
