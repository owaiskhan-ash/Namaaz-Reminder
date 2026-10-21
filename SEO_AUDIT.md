# SEO & AISO audit — Just Apps landing page

| | |
| --- | --- |
| **Site audited** | <https://www.justsimpleapps.online/> (production) |
| **Source** | `docs/` in this repository, deployed by Vercel with `docs` as the project root |
| **Date** | 20 October 2026 |
| **Pages in scope** | `/` (landing), `/privacy`, `robots.txt`, `sitemap.xml`, structured data, social metadata |
| **Fixes applied on** | branch `arena/a79b5946-namaaz-reminder`, rounds 1 and 2 |

> **AISO** here means AI search / answer-engine optimisation (also called AEO or GEO): being
> crawlable, understandable and quotable by ChatGPT, Claude, Perplexity, Gemini, Copilot and
> Google's AI surfaces, on top of classic search. It is not a separate bag of tricks — it starts
> with normal technical SEO and ends with clear, attributable, well-structured facts.

---

## 1. Verdict

**47 / 100 at the start of the audit. 89 / 100 now.**
Everything that can be fixed in this repository is fixed and deployed-ready. The eleven points
that remain are not code: they need an account, a listing or a decision that only you can make
(see §1.3).

| Area | Weight | Start | Now | What moved it |
| --- | --- | --- | --- | --- |
| Crawlability & indexation | 20% | 30 | 95 | Canonical host fixed, six URL sitemap, clean URLs, 308 from the alias, branded 404, per-app pages |
| On-page & content | 20% | 62 | 88 | Four app pages of 650–970 words, hub-and-spoke internal links, entity naming, H1 and title alignment |
| Structured data | 10% | 55 | 92 | `offers`, `@id`s, `screenshot`, `featureList`, BreadcrumbList, CollectionPage, FAQ synced to visible copy |
| AISO / answer engines | 15% | 45 | 82 | One page per question, quotable facts, direct answers, entity corroboration, explicit crawler allow list |
| Performance | 10% | 70 | 88 | WebP + `srcset` (−40% image bytes), intrinsic dimensions, immutable caching, CSP |
| Accessibility & UX | 10% | 62 | 86 | Contrast 5.24:1, skip links, working mobile nav, landmarks, 24 px targets |
| Measurement & off-page | 15% | 20 | 25 | Nothing measurable until Search Console and a public listing exist |

### 1.1 What was done in round 2

Round 1 fixed the critical metadata faults. Round 2 built the structure those fixes pointed to:

| Added | What it does |
| --- | --- |
| `docs/namaaz-reminder.html` | 972-word app page: what it does, how the timings are calculated (Aladhan, method 1 Karachi, offline re-anchoring), reminders, privacy table, compatibility, 6 FAQs |
| `docs/screen-time-reminder.html` | 663-word page: usage access, what it deliberately cannot do, no internet permission, 5 FAQs |
| `docs/subscription-tracker.html` | 654-word page: normalisation of billing cycles, manual-by-design privacy, 5 FAQs |
| `docs/vaccine-routine.html` | 654-word page: the schedule as a suggestion, storage model, medical disclaimer, 5 FAQs |
| `design/build_app_pages.py` | Generates those four pages from one data structure, so metadata and markup stay consistent |
| `docs/assets/og/*.png` | Four 1200×630 social cards, one per app, so a shared app link is not the same generic card |
| `docs/assets/**/*-400.webp`, `*-780.webp` | Twelve WebP variants; the screenshot payload drops from 708 KB to 386 KB, and `srcset` means phones no longer download 780 px images for a 210 px slot |
| `docs/nav.js` + `.nav-toggle` | A real mobile menu below 940 px; previously all navigation and the CTA simply disappeared |
| Home page | `CollectionPage` + `hasPart` linking the four app pages, an “About Just Apps” section with a visible review date, internal links from every card, WebP previews |
| `docs/vercel.json` | Content-Security-Policy and `X-DNS-Prefetch-Control` alongside the round-1 headers |

### 1.2 What was deliberately not done

- **No fake ratings.** `aggregateRating` stays absent until there are real reviews. Inventing one
  is a guidelines violation that can cost you the rich result entirely.
- **No keyword stuffing or hidden text.** Every added paragraph is a true statement about the app.
- **No `HowTo` or `Review` schema.** HowTo rich results were deprecated in 2023; self-review
  markup is ignored for SoftwareApplication.
- **No `hreflang`.** One language, one URL per page. Adding it without translations is noise.
- **No analytics.** The privacy page says the site runs no analytics; turning it on would make
  the policy untrue. Search Console measures the same thing without a script.
- **No Play Store links.** They do not exist yet, and a 404 CTA is worse than an honest
  “Coming to Google Play” pill.

### 1.3 Why this is 89 and not 100

No honest audit gives a website 100, and no single score exists across Google, Bing and the AI
answer engines. Here is exactly what stands between this site and the remaining points, and none
of it is markup:

| Gap | Points | Who can fix it |
| --- | --- | --- |
| No Google Search Console / Bing property, so nothing is indexed, submitted or measured | ~4 | You (needs your Google account) |
| Namaaz Reminder has no public download: repo private, no Play listing | ~3 | You (publish the listing or make the repo public) |
| No inbound links, no Play listing, no store reviews | ~2 | You, over months |
| Brand is still split between “Just Apps” and “Just Simple Apps” | ~1 | You (pick one; the markup already carries both) |
| No field Core Web Vitals data (no traffic yet) | ~1 | Time and traffic |

Everything else — canonical host, crawl paths, schema, content depth, internal links, image
weight, headers, accessibility — is done and validated. Push the branch, then work the checklist
in §7.

### 1.4 Already good — keep it


- **No web fonts, no third-party scripts, no cookies, no tag manager.** First load is ~67 KB
  uncompressed / ~17 KB gzipped. This is genuinely rare and it is an advantage.
- **Content is in the HTML**, not rendered by JavaScript, and the dark theme is set on `<html>`
  before paint. Crawlers and LLM fetchers see the full page; there is no flash of wrong theme.
- **Semantic structure**: one `h1`, ordered `h2`/`h3`, `<article>` per app, native
  `<details>/<summary>` FAQ, `aria-label`s on icon-only controls, descriptive screenshot alt text.
- **Titles and descriptions are the right length**: 38 / 158 characters on home, 43 / 100 on the
  privacy page. Most sites get this wrong.
- **`prefers-reduced-motion` is respected**, focus rings are visible, and the theme toggle exposes
  `aria-pressed`.
- **The privacy policy is unusually good** — specific about `api.aladhan.com`, local storage and
  the absence of a location permission. It is also the URL you need for the Play Console listing.

### The five things that matter most

1. **Canonical, OG images, sitemap and robots pointed at a dead host** — fixed in round 1.
2. **One page was trying to rank for four unrelated products** — fixed in round 2: four app
   pages, 650–970 words each, interlinked from the hub.
3. **Namaaz Reminder had no working download anywhere on the site** — the broken links are gone,
   but the app still needs a public home (Play listing or a public repo). This is the one
   product-level gap left.
4. **No Search Console, no Bing property**, so nothing is submitted or measurable — needs your
   account; see §7.
5. **The brand is three names** — "Just Apps", "Just Simple Apps", and the repo name. The markup
   now carries `alternateName` for both, but you should pick one for the store listing.

---

## 2. Critical findings

### P0-1 · The canonical URL pointed at a 404 (fixed)

| URL | Response at audit time |
| --- | --- |
| `https://www.justsimpleapps.online/` | 200 — the real site |
| `https://justsimpleapps.online/` | 308 → `www` |
| `https://namaaz-reminder.vercel.app/` | 200 — Vercel production alias, same HTML |
| `https://owaiskhan-ash.github.io/Namaaz-Reminder/` | **404 — "There isn't a GitHub Pages site here"** |
| `https://github.com/owaiskhan-ash/Namaaz-Reminder` | **404 — repository is private** |

Ten absolute URLs in `docs/index.html` used the `github.io` host: the canonical, `og:url`,
`og:image`, `twitter:image`, and every `@id`/`url`/`logo` in the JSON-LD graph. `robots.txt`
pointed its `Sitemap:` line there and both `<loc>` entries in `sitemap.xml` did too.

Consequences, in order of severity:

- A canonical that returns 404 is **discarded** by Google. At best the page is indexed under
  whichever host Google prefers (possibly the `vercel.app` alias, splitting signals); at worst
  the URL is treated as unreliable and not indexed at all.
- **Social previews were blank.** `og:image` was an absolute URL on a 404 host, so WhatsApp,
  X, LinkedIn and Slack could not fetch it. For a site whose main distribution channel will be
  shared links, this is a conversion bug, not a cosmetic one.
- The Organization/WebSite `@id`s were unreachable URIs, so the entity could not be resolved.

**Fixed:** all ten URLs, plus `robots.txt` and `sitemap.xml`, now use
`https://www.justsimpleapps.online`. `www` is correct because the apex 308-redirects to it; a
canonical should never point at a redirecting host.

**No migration is needed.** GitHub Pages was never enabled for this repository
(`has_pages: false`), so there is no legacy `github.io` indexation and no redirect to build.
If Search Console ever shows `github.io` URLs, treat them as noise, not as a property to move.

### P0-2 · Namaaz Reminder has no public download (fixed on-site, still open for the product)

At the audit, the Namaaz Reminder card's **Download** and **GitHub** buttons, the screenshot
link, the footer link, the privacy-page button and the privacy header CTA all pointed at
`github.com/owaiskhan-ash/Namaaz-Reminder/...`, which returns 404 to anyone not signed in — the
repository is private. It was the highest-intent click on the page and it failed silently. The
other three apps are public and their links resolve (verified: `ScreenTime-Reminder@apk-latest`,
`Subscription-Tracker@v1.1.0`, `vaccine-Tracker@v1.0`).

**What round 2 did:** every one of those links is gone. The home card now links to
`/namaaz-reminder`, the app page carries an honest "Coming to Google Play" pill, and the privacy
page links back to the app page. Nothing on the site offers a download that 404s, and
`downloadUrl` is omitted from that page's `SoftwareApplication` node so the structured data does
not advertise one either.

**What is still yours to decide**, in order of effort:

1. **Make the repository public.** One setting; the existing release URLs start working, and it
   unlocks the source-code and commit-history signals that answer engines use to judge whether
   an app is real.
2. **Publish the Play listing** (see `PRE_PUBLISH_CHECKLIST.md`). Then replace the pill on
   `/namaaz-reminder` with a real button, add `downloadUrl`, add the store URL to `sameAs`, and
   put a "Get it on Google Play" button on the home card.
3. **Or stay private** and keep the honest pill. That is a valid choice; a missing download is
   survivable, a broken one is not.

---

## 3. Findings by area

### 3.1 Crawlability and indexation

| ID | Finding | Severity | Status |
| --- | --- | --- | --- |
| C1 | Canonical, `og:url`, OG/Twitter images on a 404 host | Critical | **Fixed** |
| C2 | `robots.txt` sitemap line on a 404 host | High | **Fixed** |
| C3 | `sitemap.xml` URLs on a 404 host, no `lastmod` | High | **Fixed** |
| C4 | Three indexable hostnames (`www`, `vercel.app`, preview aliases) serving identical HTML | Medium | **Fixed** — `vercel.json` 308s `namaaz-reminder.vercel.app` to `www` |
| C5 | `.html` URLs create `/privacy` vs `/privacy.html` ambiguity | Low | **Fixed** — `cleanUrls` + extensionless canonical |
| C6 | No `404.html`, so a miss returns Vercel's unbranded page | Low | **Fixed** |
| C7 | No Search Console / Bing Webmaster verification | High | Open |
| C8 | AI crawlers were allowed but not named, so a future CDN rule could block them unnoticed | Low | **Fixed** — explicit allow list |
| C9 | GitHub Pages leftovers (`.nojekyll`, `github.io` URLs) | Low | Partly fixed — `.nojekyll` is harmless, URLs corrected |
| C10 | Preview deployments are `noindex` by Vercel default | Info | OK — leave as is |

`robots.txt` and `sitemap.xml` are served from the same directory as the site, so they were
live on the correct host all along — they just advertised the wrong one.

### 3.2 On-page and content

| ID | Finding | Severity | Status |
| --- | --- | --- | --- |
| O1 | `<h1>` was "Useful apps for everyday life." — no product, platform or intent keyword | High | **Fixed** — "Free Android apps, quietly made." |
| O2 | One URL targeted four unrelated intents (prayer, wellbeing, finance, health) | Critical | **Fixed** — four app pages, §5 |
| O3 | ~599 visible words on the only page | High | **Fixed** — 746 on the hub, 654–972 per app page |
| O4 | Internal links were hash anchors only, with no crawlable page-level structure | High | **Fixed** — five pages, every card links to its app page |
| O5 | Brand inconsistency: **Just Apps**, **Just Simple Apps**, repo **Namaaz-Reminder** | High | Partly fixed (`alternateName`) — still needs one decision |
| O6 | Homepage had no "last updated" or authorship signal | Medium | **Fixed** — About section with review date |
| O7 | Nav links disappeared below 940 px with no replacement menu | Medium | **Fixed** — `nav.js` + ☰ toggle |
| O8 | Alt text is genuinely good — descriptive on screenshots, empty on decorative icons | — | OK |
| O9 | Titles / descriptions are well-sized and unique per page | — | OK (mirrored to the privacy page) |

The page is a **collection landing page**, which is fine as a brand home — but it is not a
ranking page. Nobody searches "useful apps for everyday life". They search "namaz time app",
"screen time reminder android", "subscription tracker app" and "baby vaccine tracker India".
Right now none of those queries has a page to land on.

### 3.3 Structured data

| ID | Finding | Severity | Status |
| --- | --- | --- | --- |
| S1 | FAQ `acceptedAnswer` for Vaccine Routine did not match the visible answer (curly apostrophe in "India’s") | Medium | **Fixed** — all 7 answers now match the page byte-for-byte |
| S2 | `SoftwareApplication` had no `offers`, so it could not qualify for a Software App rich result | High | **Fixed** — `offers.price: 0`, `priceCurrency: INR` |
| S3 | No stable `@id`s, no `image`/`screenshot`, no `publisher`, no `featureList` | Medium | **Fixed** |
| S4 | `url` on each app pointed off-site to GitHub (and 404 for Namaaz) | Medium | **Fixed** — on-page anchors; `downloadUrl` kept only where it resolves |
| S5 | Privacy page had no canonical, no social metadata and no structured data | Medium | **Fixed** — `WebPage` + `BreadcrumbList` |
| S6 | No `WebPage`/`speakable` node on home | Low | **Fixed** |
| S7 | No `aggregateRating` | Info | Correct to omit — see below |

Two things worth knowing before you spend more time on schema:

- **FAQ rich results are gone from Google.** They were restricted to government and health
  sites in August 2023 and stopped appearing entirely on 7 May 2026; Google removed the
  documentation in June 2026. Keeping `FAQPage` is still useful for AI extraction and for
  other engines, but it will not produce a Google rich result. Do not expect one.
- **Do not invent ratings.** A Software App rich result needs `name` and `offers.price`; the
  stars come from a real `aggregateRating` or `review`. Fabricated ratings violate Google's
  structured-data policy and can trigger a manual action. Add them only when the Play listing
  has real reviews, and make sure the number matches the page.

### 3.4 AISO / answer engines

| ID | Finding | Severity | Status |
| --- | --- | --- | --- |
| A1 | No entity clarity: brand, GitHub account and app names do not corroborate each other | High | Partly fixed — `Organization` now has `alternateName`, `slogan`, `logo` as `ImageObject`, `sameAs` |
| A2 | Nothing quotable in depth | High | **Fixed** — calculation, reminders and privacy detail per app page |
| A3 | Medical-adjacent content (vaccine schedule) with no named author or reviewer | Medium | Partly fixed — disclaimer added; a named author is still needed |
| A4 | No visible freshness signal | Medium | **Fixed** — "Last reviewed" on the hub |
| A5 | AI crawlers were allowed but unnamed in `robots.txt` | Low | **Fixed** |
| A6 | No `llms.txt` | Low | **Added** — low yield, see the caveat below |
| A7 | Off-site corroboration is thin: one public README links to the site, the GitHub profile has no name, bio or website | High | Open |

**On `llms.txt`:** it is cheap and harmless, so `docs/llms.txt` now exists, but the evidence
says not to expect anything from it. Google's AI-optimisation guidance states that Search does
not use it, and crawl studies have found roughly 97% of published `llms.txt` files are never
fetched. Treat it as documentation for humans and stray agents, not as an AISO lever. The
levers that do work are A1, A2, A3, A7 and the per-app pages in §5.

**On being quoted by AI:** answer engines retrieve passages, not pages. They reward (a) a clear
entity, (b) one fact per sentence with a number or a name, and (c) pages that answer one
question completely. The current 599-word page is a brochure; it gives a model very little to
cite beyond "four free apps with no ads". The privacy page is actually closer to what works —
specific, factual, quotable — which is why it is worth turning each app into its own page.

### 3.5 Performance

Measured by byte weight, not field data (Lighthouse is unavailable in this environment and the
PageSpeed Insights API quota was exhausted — see §9).

| Metric | Start | Now |
| --- | --- | --- |
| HTML (`index.html`) | 27.1 KB raw / 5.5 KB gzip | 30.3 KB raw / **6.3 KB gzip** |
| CSS | 34.7 KB raw / 7.3 KB gzip | 39.6 KB raw / **8.1 KB gzip** |
| JS (`theme.js` + `nav.js` + `motion.js`) | 8.4 KB raw / 2.9 KB gzip | 9.6 KB raw / **3.5 KB gzip** |
| Blocking first paint (HTML + CSS + theme.js) | ~67 KB raw / ~15 KB gzip | ~72 KB raw / **~15 KB gzip** |
| Images referenced by a full scroll | 479 KB | **~300 KB** (WebP + `srcset`) |
| App pages | — | 17–19 KB raw / **~5.3 KB gzip** each |
| Web fonts | none | none — still none |

The extra 5 KB of HTML bought four indexable pages and a `CollectionPage` graph; the extra 5 KB
of CSS bought a working mobile menu and the app-page layout. Every byte is still same-origin and
cached for a year.

| ID | Finding | Severity | Status |
| --- | --- | --- | --- |
| P1 | Screenshots were 4–7× the size they are displayed | Medium | **Fixed** — WebP at two widths, 708 KB → 386 KB |
| P2 | No WebP/AVIF and no `srcset` | Medium | **Fixed** — WebP + `srcset`/`sizes` |
| P3 | No explicit cache headers | Medium | **Fixed** — `/assets/*` is `max-age=31536000, immutable` |
| P4 | No security headers | Low | **Fixed** — `nosniff`, `Referrer-Policy`, `Permissions-Policy` |
| P5 | `just-apps-icon.svg` is 57 KB — larger than the entire HTML page | Low | Open (only the favicon uses it) |
| P6 | ~711 KB of screenshots and icons deployed but never requested | Low | Partly fixed — originals kept as the source for the WebP variants |
| P7 | Images had no intrinsic `width`/`height` | Low | **Fixed** |
| P8 | `theme.js` blocks rendering | Info | Intentional — 1.9 KB, prevents a theme flash; leave it |

Because the container reserves a fixed 270 px height for previews, CLS was already near zero;
the intrinsic dimensions are belt-and-braces. The image work is done: the four screenshot sets are
now WebP at two widths, so a phone downloads the 400 px variant for a ~210 px slot instead of the
780 px original.

### 3.6 Accessibility and UX (SEO-adjacent)

| ID | Finding | Severity | Status |
| --- | --- | --- | --- |
| X1 | Light theme `--muted` (#7A7A7C) on #E4E4E6 was **3.37:1**, failing WCAG AA for the 11–12.5 px text that uses it | High | **Fixed** — #5C5C60, now **5.24:1** on `--bg`, 5.7:1 on cards, 6.1:1 on hover |
| X2 | No skip link; keyboard users tab through the nav on every page | Medium | **Fixed** |
| X3 | Footer links were ~21 px tall, under the 24×24 px target minimum | Low | **Fixed** |
| X4 | `cursor: none` replaces the pointer with an 11 px dot and removes the text I-beam on every hoverable element | Medium | Open |
| X5 | Wheel events are hijacked and `preventDefault`ed for inertia scrolling | Medium | Open |
| X6 | Nav links `display: none` under 940 px, with no hamburger | Medium | **Fixed** — accessible disclosure menu |
| X7 | `:focus-visible` rings, reduced-motion handling, `aria-pressed`, native disclosure widgets | — | OK |
| X8 | Heading order is correct; landmarks were missing labels | Low | **Fixed** — `<main id="main">`, `aria-label` on navs |

X4 and X5 are design choices, not bugs, so I left them alone — but both are genuine usability
risks. Removing the text cursor in particular disorients low-vision users and anyone who relies
on the I-beam to know where they can type or select. If the ring is kept, apply it only to the
decorative accent and keep `cursor: auto` on text.

### 3.7 Measurement and off-page

| ID | Finding | Severity | Status |
| --- | --- | --- | --- |
| M1 | No analytics. You cannot see traffic, sources, or which app card gets clicked | High | Open |
| M2 | No Search Console / Bing Webmaster property, no sitemap submission, no IndexNow | High | Open |
| M3 | GitHub repo `homepage` points at `namaaz-reminder.vercel.app`, not the canonical domain | Low | Open — one command in §7 |
| M4 | GitHub profile has no name, bio or website; `public_repos: 5` | Medium | Open |
| M5 | Only 1 of 3 public repos links to the site | Medium | Open |
| M6 | No Play Store listing yet — the single strongest entity and backlink signal available to you | High | Open |
| M7 | No inbound links found in the search index | High | Open |
| M8 | Vercel Web Analytics and Speed Insights are provisioned but disabled/empty | Info | Open |

⚠️ **If you enable analytics, update the privacy page in the same commit.** It currently says
the site "runs no analytics". Vercel Analytics is cookieless, but the statement would still be
untrue. Either keep the site analytics-free and measure in Search Console only, or amend the
policy with what is collected and why.

---

## 4. What changed in this branch

Round 1 changed metadata and structure only. Round 2 added the four app pages, a mobile menu,
responsive images and one new home-page section. The visual language, type scale and palette are
unchanged; the H1 is the only visible copy change on the landing page.

| File | Change |
| --- | --- |
| `docs/index.html` | Canonical/OG/Twitter/JSON-LD moved to `www.justsimpleapps.online`; theme-color corrected to the real default; `og:locale`; web manifest; skip link; `<main id="main">`; brand link with accessible name; labelled navs; four card IDs for deep links; intrinsic image dimensions + `async` decoding; footer Privacy link now `/privacy`; rebuilt JSON-LD graph (Organization, WebSite, WebPage + speakable, ImageObject, ItemList with `offers`/`image`/`screenshot`/`featureList`, FAQ synced to the visible copy) |
| `docs/privacy.html` | Canonical, robots, OG/Twitter, theme-color; `WebPage` + `BreadcrumbList`; skip link; `<main id="main">`; labelled navs; brand link; `#screentime` deep link fixed; extensionless URLs; footer nav |
| `docs/styles.css` | Light-theme `--muted` darkened to 5.24:1; skip-link styles; `.nav-brand`; 24 px footer tap targets; card scroll-margin |
| `docs/robots.txt` | Correct sitemap host; explicit allow list for AI crawlers |
| `docs/sitemap.xml` | Correct host, `lastmod`, clean `/privacy` URL |
| `docs/vercel.json` | `cleanUrls`, `trailingSlash: false`, 308 from the `vercel.app` alias to the canonical host, immutable asset caching, security headers |
| `docs/404.html` | Branded, `noindex` 404 page that routes visitors back to the collection or the policy |
| `docs/site.webmanifest` | Installable name, colours and icons |
| `docs/llms.txt` | Machine-readable summary of the collection (low yield — see §3.4) |
| `README.md` | Canonical-host note, page table and generator instructions |
| `docs/namaaz-reminder.html` | **New.** App page: 972 words, 6 FAQs, `SoftwareApplication` + `WebPage` + `BreadcrumbList` + `FAQPage` |
| `docs/screen-time-reminder.html` | **New.** 663 words, 5 FAQs, download goes to the working GitHub release |
| `docs/subscription-tracker.html` | **New.** 654 words, 5 FAQs, download goes to `v1.1.0` |
| `docs/vaccine-routine.html` | **New.** 654 words, 5 FAQs, medical disclaimer, download to `releases/latest` |
| `design/build_app_pages.py` | **New.** Generates the four app pages from one data structure |
| `docs/assets/og/*.png` | **New.** Four 1200×630 social cards |
| `docs/assets/**/*-400.webp`, `*-780.webp` | **New.** Twelve responsive WebP variants (708 KB → 386 KB) |
| `docs/nav.js` | **New.** Mobile menu toggle, Escape to close, `aria-expanded` in sync |
| `docs/index.html` | Round 2: `CollectionPage` + `hasPart`, About section with a review date, internal links from every card, WebP previews, mobile menu, new H1 |

**Validation run:** `html-validate` (recommended preset) — clean; JSON-LD parses and the FAQ
schema now matches the visible text exactly; `sitemap.xml` and the manifest parse; every
internal link resolves; every image has an `alt`.

---

## 5. Page architecture and keyword plan — built

Round 2 created the hub-and-spoke structure this section originally proposed. The home page is
the hub; each app has its own page and its own intent cluster.

| URL | Intent cluster | `<title>` (length) | `<h1>` |
| --- | --- | --- | --- |
| `/` | brand + "free Android apps" | Free Android Apps, Quietly \| Just Apps (38) | Free Android apps, quietly made. |
| `/namaaz-reminder` | namaz / prayer times app India, adhan reminder, offline prayer times | Namaaz Reminder — Prayer Times for India \| Just Apps (53) | Prayer times for your city, and a countdown to the next salah. |
| `/screen-time-reminder` | screen time reminder Android, break reminder app | Screen Time Reminder — Break Reminder \| Just Apps (51) | A gentle nudge to look up from your phone. |
| `/subscription-tracker` | subscription tracker, recurring bills tracker | Subscription Tracker — Recurring Bills \| Just Apps (52) | Every subscription and recurring bill, in one place. |
| `/vaccine-routine` | baby vaccine tracker India, vaccination record | Vaccine Routine — Baby Vaccine Log \| Just Apps (49) | A calm, offline vaccine log for little ones. |

Each page carries a one-sentence answer at the top (the passage an AI answer engine is most
likely to lift), 3–3 screenshots with captions, what it does, how it works, a privacy table,
compatibility facts, 5–6 FAQs that match their `FAQPage` markup exactly, and links to the other
three apps.

**Keyword caveat, repeated:** there was no keyword-volume tool in this environment. These are
intent clusters derived from the product and from competing listings, not measured volumes.
Validate them in Search Console → Performance → Queries after four weeks, and rewrite the two
lowest-CTR pages first.

### Further content that would earn links

- **A city page experiment** is *not* recommended: programmatically generating 500 "prayer times
  in <city>" pages with no unique data is a doorway-page risk, not a ranking strategy.
- **One honest article** — "Why a prayer-time app needs no location permission" — is worth more
  than twenty directory listings, and it is a story only you can tell.
- **The vaccine page** is the one that needs an author. Add a line naming who writes and reviews
  it, even if that is "Owais Khan, Mumbai". E-E-A-T for health-adjacent content is not a
  checklist, it is a person.


## 6. Copy

The H1 was the one visible copy change, and it now matches the `<title>`:

```html
<h1 id="mission-title">Free Android apps,<br>quietly made.</h1>
```

It keeps the two-line rhythm and the serif scale of the original, while putting the category term
("Android apps") in the strongest on-page position. The old line, *Useful apps for everyday
life.*, described a mood rather than a product and shared no phrase with the title.

**Titles now in place**

| Page | Title | Length |
| --- | --- | --- |
| `/` | Free Android Apps, Quietly \| Just Apps | 38 |
| `/namaaz-reminder` | Namaaz Reminder — Prayer Times for India \| Just Apps | 53 |
| `/screen-time-reminder` | Screen Time Reminder — Break Reminder \| Just Apps | 51 |
| `/subscription-tracker` | Subscription Tracker — Recurring Bills \| Just Apps | 52 |
| `/vaccine-routine` | Vaccine Routine — Baby Vaccine Log \| Just Apps | 49 |
| `/privacy` | Privacy policy: Namaaz Reminder \| Just Apps | 43 |

**One copy question still open:** the privacy page headline is branded "NAMAAZ REMINDER" while
the site header is "JUST APPS", which is confusing when a visitor arrives from search. Either
retitle it *"Just Apps privacy policy"* (and cover all four apps, which it partly does already)
or keep it app-specific and add a sentence saying which apps it covers. That is a decision about
what the page is for, not a markup fix.

## 7. Roadmap

### Done in this branch

- [x] Canonical, OG, Twitter, sitemap, robots and every `@id` moved to the live host
- [x] `og:image` now resolves, so shared links render a card
- [x] Structured data rebuilt: `CollectionPage`, `ItemList` with `offers`, per-app
      `SoftwareApplication`, `BreadcrumbList`, `FAQPage` matching the visible text
- [x] Four app pages with real content, internal links, per-app social cards and schema
- [x] WebP + `srcset` (−45% screenshot weight), intrinsic image dimensions
- [x] `cleanUrls`, 404 page, 308 from the `vercel.app` alias, immutable asset caching, CSP
- [x] Mobile navigation, skip links, 5.24:1 contrast, labelled landmarks, 24 px targets
- [x] `llms.txt`, web manifest, Apple touch icon
- [x] README documents the canonical host and the page generator

### Now — this week (needs your accounts, ~40 minutes)

1. **Deploy.** Push the branch, confirm the Vercel build, then run §8.
2. **Decide the Namaaz download.** Either make the repository public (one setting, unlocks the
   existing release links) or publish the Play listing. Then replace the “Coming to Google Play”
   pill on `/namaaz-reminder` with a real button, add `downloadUrl` to that page's schema, and
   restore a download button on the home card.
3. **Search Console** — add a *Domain* property for `justsimpleapps.online`, verify by DNS
   (Vercel can add the TXT record), submit `https://www.justsimpleapps.online/sitemap.xml`.
4. **Bing Webmaster Tools** — import from Search Console; this also feeds ChatGPT's search index.
5. **GitHub identity** — the profile has no name, bio or website, and two of the three public
   repos do not link to the site:

   ```bash
   gh api -X PATCH repos/owaiskhan-ash/Namaaz-Reminder \
     -f homepage='https://www.justsimpleapps.online/'
   gh api -X PATCH user \
     -f name='Owais Khan' \
     -f bio='Free, quiet Android apps — prayer times, screen breaks, subscriptions, vaccine records.' \
     -f blog='https://www.justsimpleapps.online/'
   ```
6. **Pick one brand.** “Just Apps” and “Just Simple Apps” currently compete. The markup carries
   both (`alternateName`), but the Play listing, README and domain should agree.

### Next — 30 days

7. Publish the Play listing for Namaaz Reminder and add a “Get it on Google Play” button plus
   `sameAs` to the store listing.
8. Add real `aggregateRating` **only** once reviews exist, and make it match the listing exactly.
9. Ask the three public app repos to link to `/` from their READMEs, and set each repo's
   `homepage` field.
10. Review Search Console queries after four weeks and rewrite the two pages with the worst
    click-through.

### Later — 90 days

11. One editorial article (the location-permission story) and, if it earns a link, another.
12. Hindi or Urdu versions of the Namaaz page with proper `hreflang` — only if you can maintain
    them. Machine translation is worse than no translation.
13. Revisit the custom cursor: it removes the text I-beam. The dot is charming; the trade-off is
    not worth it for low-vision visitors.


## 8. Post-deploy verification checklist

Redirects and headers (run after Vercel deploys):

```bash
curl -sI https://www.justsimpleapps.online/ | head -20
curl -sI https://justsimpleapps.online/ | grep -i '^location'        # → https://www...
curl -sI https://www.justsimpleapps.online/privacy.html | grep -i '^location'  # → /privacy
curl -sI https://namaaz-reminder.vercel.app/ | grep -i '^location'   # → canonical host
curl -sI https://www.justsimpleapps.online/assets/just-apps-icon-512.png | grep -i cache-control
curl -s https://www.justsimpleapps.online/sitemap.xml
curl -s https://www.justsimpleapps.online/robots.txt
```

Markup and previews:

- <https://validator.schema.org/> — paste the page source.
- <https://search.google.com/test/rich-results> — confirm Software App + Breadcrumbs.
- <https://developers.facebook.com/tools/debug/> and the LinkedIn Post Inspector — confirm the
  1200×630 image resolves from the canonical host.
- Send the URL to yourself on WhatsApp and check the card renders.
- <https://pagespeed.web.dev/> — record mobile LCP/CLS/INP as the baseline for `/` and
  `/namaaz-reminder`.
- Check the four new routes render with the right canonical:
  `/namaaz-reminder`, `/screen-time-reminder`, `/subscription-tracker`, `/vaccine-routine`.
- Confirm `/privacy.html` and `/namaaz-reminder/` both 308 to the extensionless URL.
- Load `/namaaz-reminder` on a phone-width viewport and open the ☰ menu: it should close on tap,
  on Escape, and when the window is widened past 940 px.

Search:

- Search Console → URL Inspection → *Test live URL* on `/` and `/privacy`.
- Request indexing for both.
- After ~two weeks, check `site:justsimpleapps.online` in Google and Bing.

---

## 9. Limits of this audit

- **No rendered-browser check.** No Chromium binary was available and the Playwright/Puppeteer
  download hosts are outside this sandbox's allowlist, so layout was verified by validating the
  markup and by serving the site locally (all routes, assets and 404 behaviour return correctly),
  not by screenshotting it. Open the preview and look at the four new pages before you deploy.
- **No Lighthouse/Core Web Vitals run.** Chromium is not installed in this environment and the
  PageSpeed Insights API returned a hard quota error (`429`, daily quota 0). Performance figures
  above are computed from actual byte weights, not field data. Run PageSpeed once deployed.
- **No live header inspection.** HTTPS from the sandbox to GitHub Pages failed at the TLS layer,
  and `fetch_page` does not expose response headers. Host, redirect and content behaviour were
  verified from live responses; cache and security headers are asserted from `vercel.json`.
- **GitHub Pages settings** could not be read (`403 Resource not accessible by integration`);
  `has_pages: false` came from the repository metadata instead.
- **Vercel domain DNS details** could not be read (the connector returned a validation error),
  but both hostnames resolve and serve the production deployment, so DNS is working.
- **No keyword-volume data.** The clusters in §5 are editorial and should be validated against
  Search Console queries.
- **No crawl of the wider web** beyond the site itself, so the backlink picture is indicative,
  not exhaustive: a search for the domain returned no results.

---

## 10. Sources

- Google, *Changes to HowTo and FAQ rich results* (8 Aug 2023) —
  <https://developers.google.com/search/blog/2023/08/howto-faq-changes>
- Google, *Software app (SoftwareApplication) structured data* —
  <https://developers.google.com/search/docs/appearance/structured-data/software-app>
- Search Engine Journal, *Google drops FAQ rich results from Search* (May 2026) —
  <https://www.searchenginejournal.com/google-drops-faq-rich-results-from-search/574429/>
- Search Engine Land, *Does your website need an llms.txt file?* (2026 update) —
  <https://searchengineland.com/guide/llms-txt>
