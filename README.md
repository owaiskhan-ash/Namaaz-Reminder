# Namaaz Reminder

A clean, minimal, monochrome **prayer times & reminder app for India**.

- Live countdown to the next prayer, with a card per prayer (Fajr, Dhuhr, Asr, Maghrib, Isr).
- City picker and calculation method selection, backed by the [Aladhan](https://aladhan.com) API.
- Offline cache: the last successful schedule is stored locally and re-anchored to the current day.
- Notifications for upcoming prayer times, with exact alarms (Android 12+) and a boot receiver that
  re-arms the schedule after a restart.
- Light / dark / system theme, and a settings sheet for muted prayers, reminder timing and
  calculation method. Reminders fire **at or shortly after** the prayer time (5 minutes after by
  default), which is when the adhan ends and the salah begins.

Current version: **1.7.3** (`versionCode` 14).

## The website

`docs/` is the static site for the whole collection, published at
<https://www.justsimpleapps.online/> from the `docs` directory. Every canonical, Open Graph,
sitemap and JSON-LD URL must use that host: `owaiskhan-ash.github.io` does not serve this site
(GitHub Pages is off), so a `github.io` URL in the markup is a dead link.

| Page | File | URL |
| --- | --- | --- |
| Collection landing page | `docs/index.html` | `/` |
| Namaaz Reminder | `docs/namaaz-reminder.html` | `/namaaz-reminder` |
| Screen Time Reminder | `docs/screen-time-reminder.html` | `/screen-time-reminder` |
| Subscription Tracker | `docs/subscription-tracker.html` | `/subscription-tracker` |
| Vaccine Routine | `docs/vaccine-routine.html` | `/vaccine-routine` |
| Water Reminder | `docs/water-reminder.html` | `/water-reminder` |
| Step Reminder | `docs/steps-reminder.html` | `/steps-reminder` |
| RemindME | `docs/remindme.html` | `/remindme` |
| Arabic Clock | `docs/arabic-clock.html` | `/arabic-clock` |
| Privacy policy | `docs/privacy.html` | `/privacy` |

The extensions are stripped by `cleanUrls` in `docs/vercel.json`, which also sets the asset
cache headers, the security headers and the 308 from the `vercel.app` alias to the custom
domain. `docs/404.html` is the branded not-found page.

Every page declares the same Just Apps search icon at the stable URL
`/favicon-96x96.png`, with `/favicon.ico` containing 16, 32 and 48px fallbacks.
The square 96px PNG meets Google's size guidance. Keep these URLs
stable and crawlable; an SVG alone is not a Google Search favicon format.
After deployment, use Search Console's URL Inspection tool to request indexing
of the **home page**. Google can take days or weeks to refresh its search icon;
a globe in a recent result does not necessarily mean the browser favicon is
missing. See [Google's favicon guidelines](https://developers.google.com/search/docs/appearance/favicon-in-search).

All eight app pages are **generated**; edit `design/build_app_pages.py` (copy, screenshots,
facts and FAQ live in its `APPS` list) and rebuild rather than editing the HTML by hand:

```bash
python3 design/build_app_pages.py
```

Every app therefore owns a page of its own (`/namaaz-reminder`, `/water-reminder` and so on)
rather than a card on the home page: one URL per search intent, with its own title, meta
description, canonical, 1200x630 social card, `SoftwareApplication` + `FAQPage` +
`BreadcrumbList` graph, a one-line answer paragraph, a visible FAQ mirrored in schema, and
links to all seven sibling apps. The landing page keeps the `ItemList` of all eight, so the
collection and the individual apps reinforce each other instead of competing for one title.

After changing anything under `docs/`, run the SEO/AISO validator. It checks canonical host,
title/description lengths and uniqueness, `og:url`/canonical agreement, social-image existence,
JSON-LD parsing, FAQ schema ≡ visible `<details>`, internal links and anchors, sitemap ↔ pages,
`robots.txt`, `llms.txt` URLs, that every page resolves the same `Organization` node, that the
home `ItemList` matches each app page's `SoftwareApplication` node, that every app page is linked
from the hub and from all seven siblings and carries an author, a publication date and
`speakable` passages, that no page has stray or unclosed block tags, that the 404 page has a real
description and social image, that no FAQ question is asked on two pages, and that no em dash or
en dash has crept into the copy. It tokenizes robots directives (so `noindex` can never be
mistaken for `index`) and checks each sitemap `lastmod` against the page's JSON-LD `dateModified`.
Run the SEO check and its indexability regression tests with:

```bash
python3 design/seo_check.py
python3 -m unittest discover -s design -p 'test_*.py'
```

CI runs both checks on any push or PR that touches the site
(`.github/workflows/seo-check.yml`), so a metadata regression fails the build instead of
reaching production. `SEO_AUDIT.md` records the full audit history.

Screenshots come from the other apps' repositories. Each one is also written as two WebP
variants (400 px and 780 px wide) that the pages reference through `srcset`; regenerate them
with Pillow (`pip install pillow`) whenever a screenshot changes:

```bash
python3 - <<'EOF'
from PIL import Image
src = 'docs/assets/vaccine/today.jpg'
im = Image.open(src).convert('RGB')
for width in (400, 585):
    height = round(im.height * width / im.width)
    im.resize((width, height), Image.LANCZOS).save(
        src.rsplit('.', 1)[0] + f'-{width}.webp', 'WEBP', quality=82, method=6)
EOF
```

`docs/assets/og/` holds the 1200×630 social cards, one per app. The four newer cards are
rendered by one shared script, which carries a single copy of the layout:

```bash
python3 design/build_app_og_cards.py
``` The `-400.webp` and `-780.webp`
files next to each screenshot are the responsive variants referenced from the pages; the
original PNG/JPG files next to them are kept as the source for regenerating those variants.

Adding an app means one more entry in `APPS`, its screenshots and social card under
`docs/assets/`, a card on the landing page (linking to the new page), a URL in
`docs/sitemap.xml`, an app entry in `docs/llms.txt`, a matching `ItemList` item in the
`index.html` JSON-LD, and the new filename in `INDEXABLE` in `design/seo_check.py`; then bump
`DATE_MODIFIED` in the generator and `<lastmod>` in the sitemap and run
`python3 design/seo_check.py`. Page copy uses plain punctuation; the check rejects
em dashes and their HTML entities in the site files and generator.

## The other apps

All public apps in the collection share the same promise: free to use, no ads, no clutter, no accounts.

| # | App | Source |
| --- | --- | --- |
| 02 | **Screen Time Reminder** | <https://github.com/owaiskhan-ash/ScreenTime-Reminder> |
| 03 | **Subscription Tracker** | <https://github.com/owaiskhan-ash/Subscription-Tracker> |
| 04 | **Vaccine Routine** | <https://github.com/owaiskhan-ash/vaccine-Tracker> |
| 05 | **Water Reminder** | <https://github.com/owaiskhan-ash/Water-Reminder> |
| 06 | **Step Reminder** | <https://github.com/owaiskhan-ash/Steps-Reminder> |
| 07 | **RemindME** | <https://github.com/owaiskhan-ash/RemindME> |
| 08 | **Arabic Clock** | <https://github.com/owaiskhan-ash/Arabic-Clock-For-Android-> |

## Getting the APKs

Every push to `main` or an `arena/**` branch runs the **Android CI** workflow, which produces two
signed APKs:

| Build | What it is | Notes |
| --- | --- | --- |
| `NamaazReminder-<version>-debug.apk` | Debug build | Includes Compose tooling; signed with the standard Android debug key. |
| `NamaazReminder-<version>-release.apk` | Release build | Release variant, minification off, signed with the same certificate, so it upgrades the debug build in place. |
| `NamaazReminder-<version>-release.aab` | Play bundle | Upload this to the Play Console; Play does not accept new APK uploads. |

They are available in three places:

1. **Actions artifacts**: every run of *Android CI* uploads an `NamaazReminder-apks` artifact.
2. **The rolling `apk-latest` release**: <https://github.com/owaiskhan-ash/Namaaz-Reminder/releases/tag/apk-latest>
   always holds the newest pair of APKs.
3. **The `apk-builds` branch**: the same APKs are mirrored into `apk-builds/` on that branch, so
   they can be downloaded straight from the branch page.

Install over ADB with:

```bash
adb install -r NamaazReminder-1.7.3-release.apk
```

Pushing a `v*` tag additionally publishes a versioned GitHub Release containing both APKs.

## Building locally

Requires JDK 21 and the Android SDK (compileSdk 36, minSdk 24).

```bash
./gradlew testDebugUnitTest   # unit tests
./gradlew assembleDebug       # -> app/build/outputs/apk/debug/app-debug.apk
./gradlew assembleRelease     # -> app/build/outputs/apk/release/app-release.apk
```

The `release` build type signs with the `upload` key alias, configured in
`app/build.gradle.kts`.

CI uses the Play upload key from repository secrets: `KEYSTORE_BASE64`
(base64 of the PKCS12 keystore), `STORE_PASSWORD` and `KEY_PASSWORD`. When
those secrets are present it also builds `NamaazReminder-<version>-release.aab`
for the Play Console; without them it builds only the APKs, signed with the
debug key, so a build can never silently publish a bundle signed by the wrong
key.

For a local build, provide the key through the environment:

| Variable | Meaning |
| --- | --- |
| `KEYSTORE_PATH` | Path to the keystore containing the `upload` alias. Defaults to `./my-upload-key.jks`. |
| `STORE_PASSWORD` | Keystore password. |
| `KEY_PASSWORD` | Key password. |

CI derives the `upload` alias from the committed, publicly known `debug.keystore`, so the release
APK keeps a stable signature across builds. For a Play Store upload, point `KEYSTORE_PATH` at your
own upload key instead.

## Brand

The app icon is the approved **NR** artwork, a rounded block monogram in vivid
coral and pink, set inside a matching neon frame on charcoal (`design/source/NR-icon.png`).

`design/build_icons.py` derives every icon from that one file, so the launcher
icon, the themed icon and the in-app header can never drift apart:

| Asset | How it is made |
| --- | --- |
| `mipmap-*/ic_launcher.png` | the artwork, tightly cropped to the plate |
| `mipmap-*/ic_launcher_round.png` | circular crop of the artwork |
| `drawable/ic_app_icon.png` | the header badge |
| `drawable/ic_launcher_foreground_mark.png` | the artwork full-bleed for the adaptive icon: the monogram's furthest corner sits at ~47% of the tile, inside every launcher mask |
| `drawable/ic_launcher_background.xml` | the plate edge tone, for the margin a wide mask exposes |
| `drawable/ic_launcher_monochrome.xml` | a flat NR silhouette for themed icons; the launcher tints this layer, so the artwork's 3D shading cannot be used |

Regenerate after replacing the source artwork:

```bash
pip install pillow numpy
python3 design/build_icons.py     # rewrites the res/ assets + design/preview/
```

The source artwork can be refreshed from its public URL with the *Fetch brand
asset* workflow (GitHub runners can reach hosts that some sandboxes cannot).

## Project layout

```
app/src/main/java/com/example/
├── MainActivity.kt                  # Compose entry point, notification channel setup
├── data/
│   ├── local/PreferencesManager.kt   # SharedPreferences-backed settings + cached schedule
│   ├── model/PrayerModels.kt        # Prayer types, schedule data, UI state models
│   └── repository/
│       ├── PrayerRepository.kt       # Aladhan API + offline cache fallback
│       └── PrayerScheduleCustomizer.kt # Applies the per-prayer custom times
├── notification/
│   ├── AlarmRescheduler.kt          # Re-arms exact alarms
│   ├── AzaanSoundStore.kt           # Stores the azaan sound on the device
│   └── PrayerNotificationManager.kt # Channels, reminders, permission prompts
├── receiver/                        # Boot + prayer alarm broadcast receivers
└── ui/                              # Screen, view model, components, theme
```

## Notifications

Each prayer reminder stays a separate notification; the app never groups or bundles them:

- every prayer gets its own notification id, so a Fajr reminder never disappears into a
  "5 notifications" stack,
- the reminder names the prayer and the time in the title and body, with the city in the text,
- posting the same prayer again on a later day updates its existing notification instead of
  adding a duplicate,
- turning **Enable Reminders** off cancels the pending alarms *and* clears reminders already in
  the shade,
- exact alarms are used when Android allows them (Android 12+); otherwise the app falls back to
  inexact alarms rather than dropping the reminder,
- sound and vibration live in separate channels (`Prayer Reminders (Silent)` and
  `Prayer Reminders: <sound name>`), because from Android 8.0 the system reads both from the
  channel rather than the individual notification. Changing the sound or vibration creates the
  new channel and deletes the superseded ones.

## Azaan (reminder sound)

The reminder can play a full azaan instead of the short system sound:

- the audio is **not** shipped inside the APK; it is fetched from the public asset bucket the
  first time it is used and then **saved on the device** (media library on Android 10+, the
  app's external files folder on older versions), so it also plays when the phone is offline,
- **Settings → Notifications & reminders → Azaan** lists the available azaans with a
  *play* and a *download* button, the default system sound stays selectable as well,
- the picked azaan is stored per device, the reminder plays it through a silent channel and
  the sound is set on the notification itself, so the sound / vibration toggles keep working,
- **Send Test Reminder Notification** plays the same azaan, so it can be checked right away.

## Custom prayer times

Every prayer card can be **long pressed** to set its time by hand:

- the custom time is shown next to the calculated one, the calculated time stays visible but
  is dimmed, the card is marked with a `CUSTOM` badge,
- the custom time is the one the countdown, the next-prayer line and the reminder alarm use,
- the times survive a restart and can be removed again: long press the card and choose
  **Reset to calculated**.

## Permissions

`INTERNET`, `ACCESS_NETWORK_STATE` (schedule fetch), `POST_NOTIFICATIONS` (Android 13+ reminders),
`VIBRATE`, `RECEIVE_BOOT_COMPLETED` (re-arm alarms after reboot) and `SCHEDULE_EXACT_ALARM`
(Android 12+ precise prayer alarms, granted in-app on first launch).
