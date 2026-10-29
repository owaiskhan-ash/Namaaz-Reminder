#!/usr/bin/env python3
"""Generate the per-app landing pages from the data in this file.

Each page is written to docs/<slug>/index.html and is served as
https://www.justsimpleapps.online/<slug> (Vercel `cleanUrls`). The pages share
the markup in TEMPLATE, so a link or metadata change is made once here instead
of four times by hand.

    python3 design/build_app_pages.py
"""

import html
import json
import os
from datetime import date

BASE = "https://www.justsimpleapps.online"
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs")
STAGES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_stages.json")

# Bump whenever any copy in this file changes; it feeds WebPage.dateModified
# and should agree with the <lastmod> for the same URL in docs/sitemap.xml.
DATE_MODIFIED = "2026-10-29"

# First publication date of the app pages. The original four went live
# together; the four newer pages were added later, so a page-level
# datePublished is honest about which is which.
DATE_PUBLISHED = "2026-10-20"

# The publisher entity, defined here so every app page resolves it on its own.
# The same @ids and field values are used on docs/index.html; keep them equal.
ORGANIZATION = {
    "@type": "Organization",
    "@id": BASE + "/#organization",
    "name": "Just Apps",
    "alternateName": "Just Simple Apps",
    "url": BASE + "/",
    "description": "A small studio making free, quiet Android apps for everyday life: prayer times, screen breaks, step goals, water reminders, conversational reminders, subscriptions, childhood vaccine records and a transparent Arabic-Indic clock widget.",
    "slogan": "Free apps for everyday life, quietly.",
    "foundingLocation": {"@type": "Place", "name": "Mumbai, India"},
    "logo": {
        "@type": "ImageObject",
        "@id": BASE + "/#logo",
        "url": BASE + "/assets/just-apps-icon-512.png",
        "contentUrl": BASE + "/assets/just-apps-icon-512.png",
        "width": 512,
        "height": 512,
        "caption": "Just Apps",
    },
    "image": {"@id": BASE + "/#logo"},
    "founder": {
        "@type": "Person",
        "name": "Owais Khan",
        "url": "https://github.com/owaiskhan-ash",
    },
    "sameAs": [
        "https://github.com/owaiskhan-ash",
        "https://github.com/owaiskhan-ash/Namaaz-Reminder",
        "https://github.com/owaiskhan-ash/ScreenTime-Reminder",
        "https://github.com/owaiskhan-ash/Subscription-Tracker",
        "https://github.com/owaiskhan-ash/vaccine-Tracker",
        "https://github.com/owaiskhan-ash/Steps-Reminder",
        "https://github.com/owaiskhan-ash/Water-Reminder",
        "https://github.com/owaiskhan-ash/RemindME",
        "https://github.com/owaiskhan-ash/Arabic-Clock-For-Android-",
    ],
}
WEBSITE = {
    "@type": "WebSite",
    "@id": BASE + "/#website",
    "url": BASE + "/",
    "name": "Just Apps",
    "alternateName": "Just Simple Apps",
    "description": "Free, ad-free apps for prayer times, screen breaks, step goals, water reminders, conversational reminders, subscriptions, vaccine records and an Arabic-Indic clock widget.",
    "publisher": {"@id": BASE + "/#organization"},
    "inLanguage": "en",
}
AUTHOR = {
    "@type": "Person",
    "name": "Owais Khan",
    "url": "https://github.com/owaiskhan-ash",
}


def long_date(iso):
    """2026-10-28 -> 28 October 2026, the form used in the visible copy."""
    d = date.fromisoformat(iso)
    return f"{d.day} {d.strftime('%B %Y')}"


def shot(src, alt, caption, width, height, srcset=None, sizes=None):
    ss = f' srcset="{srcset}" sizes="{sizes}"' if srcset else ""
    return (
        f'<figure><img src="{src}"{ss} alt="{html.escape(alt)}" '
        f'width="{width}" height="{height}" loading="lazy" decoding="async">'
        f"<figcaption>{caption}</figcaption></figure>"
    )


APPS = [
    {
        "slug": "namaaz-reminder",
        "name": "Namaaz Reminder",
        "kicker": "01 · Prayer",
        "nav_cta": "See the app",
        "title": "Namaaz Reminder: Prayer Times for India | Just Apps",
        "description": "Free Android prayer-times app for India: daily salah times for your city, a live countdown, optional adhan reminders. No ads, no account, no location permission.",
        "og": "og-namaaz-reminder.png",
        "h1": "Namaaz Reminder: prayer times and a countdown to the next salah.",
        "lede": "Namaaz Reminder shows today’s Fajr, Dhuhr, Asr, Maghrib and Isha times for your city in India, counts down to the next prayer, and can remind you at adhan. It is free, has no ads, and asks for no account.",
        "answer": "<p><strong>In one line:</strong> Namaaz Reminder is a free Android prayer-times app for India that shows daily salah times, a live countdown and optional adhan reminders, with no ads, accounts or location permission.</p>",
        "cta": """          <a class="btn btn-primary" href="https://github.com/owaiskhan-ash/Namaaz-Reminder/releases/download/v1.7.3/NamaazReminder-1.7.3-release.apk">Download the APK</a>
          <a class="btn btn-ghost" href="/privacy">Privacy policy</a>""",
        "cta_note": "Version 1.7.3 for Android 7.0 and later. Free, signed APK from the project’s GitHub releases; Google Play listing in preparation.",
        "shots": [
            shot("/assets/namaaz/today-400.webp",
                 "Namaaz Reminder showing the next prayer countdown and today's five prayer times on black leather",
                 "Today: live countdown to the next salah and all five prayer times.",
                 400, 866,
                 "/assets/namaaz/today-400.webp 400w, /assets/namaaz/today-780.webp 780w",
                 "(max-width: 620px) 42vw, 210px"),
            shot("/assets/namaaz/cities-400.webp",
                 "City picker for India with offline schedule caching and no GPS permission",
                 "Any city in India, chosen by name, with no GPS permission needed.",
                 400, 866,
                 "/assets/namaaz/cities-400.webp 400w, /assets/namaaz/cities-780.webp 780w",
                 "(max-width: 620px) 42vw, 210px"),
            shot("/assets/namaaz/settings-400.webp",
                 "Settings showing calculation method, reminder offset, and bundled Madinah Azaan audio",
                 "Settings: calculation method, reminder offset and Madinah adhan.",
                 400, 866,
                 "/assets/namaaz/settings-400.webp 400w, /assets/namaaz/settings-780.webp 780w",
                 "(max-width: 620px) 42vw, 210px"),
        ],
        "body": """
        <h2>What it does</h2>
        <ul>
          <li><strong>Today’s five prayers</strong>: Fajr, Dhuhr, Asr, Maghrib and Isha for the city you pick, in 12- or 24-hour format.</li>
          <li><strong>A live countdown</strong> to the next salah, so you can see at a glance how long is left.</li>
          <li><strong>Reminders at the adhan</strong>, or a set number of minutes after it, for any or all prayers.</li>
          <li><strong>A city picker</strong> that works by name: Delhi by default, or any Indian city you type.</li>
          <li><strong>A choice of calculation method</strong>, with the method used across India selected by default.</li>
          <li><strong>An offline copy</strong> of the last schedule that was fetched, so the screen still opens without a connection.</li>
        </ul>

        <h2>How the prayer times are calculated</h2>
        <p>Timings are not bundled with the app. When you open it, Namaaz Reminder asks the
        <a href="https://aladhan.com/">Aladhan prayer-times API</a> for today’s schedule, sending only three
        things: the city name, the country (India) and the number of the calculation method you chose.
        The API returns the five timings and the city’s time zone, and the app draws the countdown from
        the device clock.</p>
        <p>Different schools and organisations use slightly different solar angles for Fajr and Isha, which is
        why the method is a setting rather than a fixed decision. The default is method 1, the University of
        Islamic Sciences, Karachi convention that is common across India. If your mosque follows a different
        convention, pick the matching method in Settings and the times will move to match it. Individual
        prayers can also be corrected by hand for a given day; long-pressing a corrected time restores the
        calculated one.</p>
        <p>Because the last successful response is kept on the phone, the schedule is re-anchored to the
        current date when the app is offline. If the cached copy is several days old, a timing can be off by a
        minute or two, and the screen says so rather than pretending the data is live.</p>

        <h2>Reminders that behave</h2>
        <p>Prayer reminders are scheduled on the device with Android’s alarm manager, not sent from a server.
        That has three consequences worth knowing: they work with no connection, they survive a reboot
        (the app re-arms them at startup), and no notification content ever leaves your phone.</p>
        <p>By default a reminder fires <strong>five minutes after</strong> the prayer time (the point at which the
        adhan has finished and the salah begins), and the offset is adjustable from zero upwards. Sound and
        vibration are separate switches, individual prayers can be muted, and the Madinah adhan can be
        replaced with an audio file of your own.</p>

        <h2>What stays on your phone</h2>
        <p>There is no account and no sync. Everything the app knows lives in its own private storage on the
        device.</p>
        <dl class="facts">
          <dt>Location permission</dt><dd>Not requested. The app never reads GPS, Wi-Fi or cell-tower position.</dd>
          <dt>Sent over the network</dt><dd>The city name, the country and the calculation method, to api.aladhan.com over HTTPS. Nothing else is attached.</dd>
          <dt>Stored on the device</dt><dd>Your settings and today’s schedule, in the app’s private storage. Removed when you uninstall.</dd>
          <dt>Analytics and ads</dt><dd>None. No advertising SDK, no crash-reporting SDK, no tracking.</dd>
        </dl>
        <p>The full detail, including the adhan audio download and Android’s own backup behaviour, is on the
        <a href="/privacy">privacy policy page</a>.</p>

        <h2>Compatibility and version</h2>
        <dl class="facts">
          <dt>Platform</dt><dd>Android 7.0 (API 24) and later, targeting Android 16.</dd>
          <dt>Version</dt><dd>1.7.3 (versionCode 14).</dd>
          <dt>Price</dt><dd>Free, with no in-app purchases.</dd>
          <dt>Account</dt><dd>Not required, and not possible; there is no sign-in.</dd>
          <dt>Source</dt><dd><a href="https://github.com/owaiskhan-ash/Namaaz-Reminder">Namaaz-Reminder repository on GitHub</a></dd>
          <dt>Made by</dt><dd>Owais Khan (Just Apps), an independent studio in Mumbai, India. <a href="https://github.com/owaiskhan-ash">github.com/owaiskhan-ash</a>.</dd>
        </dl>
        """,
        "faq": [
            ("Does Namaaz Reminder need an internet connection?",
             "Only to fetch the timings. Once a schedule has been downloaded it is cached on the phone, so the main screen and the countdown keep working offline. Reminders are scheduled on the device and need no connection at all."),
            ("Does Namaaz Reminder use my GPS location?",
             "No. The app does not request Android’s location permission and never reads GPS, Wi-Fi or cell-tower position. You choose a city by name, and that name is the only location information involved."),
            ("When do the Namaaz Reminder notifications fire?",
             "By default five minutes after the prayer time, which is when the adhan has ended and the salah begins. The offset is adjustable in Settings down to zero, and individual prayers can be muted."),
            ("Which prayer-time calculation method does Namaaz Reminder use?",
             "Method 1, the University of Islamic Sciences, Karachi convention, is the default because it is the most common choice in India. Other methods can be selected in Settings, and any single prayer time can be corrected by hand for the day."),
            ("Is Namaaz Reminder free?",
             "Yes. Namaaz Reminder is free, has no ads, no subscriptions and no in-app purchases, and it does not ask you to create an account."),
            ("Which Indian cities does Namaaz Reminder support?",
             "Any city you can name, with Delhi as the default. The request is made against India as the country and the API returns the city’s own time zone."),
            ("Is Namaaz Reminder on Google Play?",
             "Not yet. While the Play Store listing is being prepared, you can download the free signed APK directly from the project’s GitHub releases."),
        ],
        "software": {
            "name": "Namaaz Reminder",
            "applicationCategory": "LifestyleApplication",
            "operatingSystem": "Android 7.0 and later",
            "softwareVersion": "1.7.3",
            "description": "Daily prayer times for cities in India, a live countdown to the next salah, optional adhan reminders and an offline copy of the last schedule. Free, no ads, no account, no location permission.",
            "image": BASE + "/assets/nr-mark-512.png",
            "screenshot": [
                BASE + "/assets/namaaz/today-780.webp",
                BASE + "/assets/namaaz/cities-780.webp",
                BASE + "/assets/namaaz/settings-780.webp",
            ],
            "featureList": [
                "Prayer times for any city in India",
                "Live countdown to the next salah",
                "Adhan reminders, at or after the prayer time",
                "Exact alarms re-armed after a reboot",
                "Offline copy of the last fetched schedule",
                "Choice of calculation method and 12/24-hour format",
                "Light, dark and system themes",
                "No ads, accounts, analytics or location permission",
            ],
            "downloadUrl": "https://github.com/owaiskhan-ash/Namaaz-Reminder/releases/download/v1.7.3/NamaazReminder-1.7.3-release.apk",
            "sameAs": ["https://github.com/owaiskhan-ash/Namaaz-Reminder"],
        },
        "cta_primary": "https://github.com/owaiskhan-ash/Namaaz-Reminder/releases/download/v1.7.3/NamaazReminder-1.7.3-release.apk",
    },
    {
        "slug": "screen-time-reminder",
        "name": "Screen Time Reminder",
        "kicker": "02 · Wellbeing",
        "nav_cta": "Get the app",
        "title": "Screen Time Reminder: Break Reminder | Just Apps",
        "description": "Free Android app that counts continuous phone use and sends one gentle break reminder. Seven-day history, no streaks, no ads, no internet permission.",
        "og": "og-screen-time-reminder.png",
        "h1": "Screen Time Reminder: a gentle nudge to look up from your phone.",
        "lede": "Screen Time Reminder counts how long you have been using your phone in one stretch, and sends a single calm reminder when a session runs long. There are no streaks, no scores and no guilt, just one honest number and a reason to put the phone down for a minute.",
        "answer": "<p><strong>In one line:</strong> Screen Time Reminder is a free Android app that tracks continuous phone use and sends one gentle break reminder when a session runs long, keeping a seven-day history and asking for no account, no ads and no internet access.</p>",
        "cta": """          <a class="btn btn-primary" href="https://github.com/owaiskhan-ash/ScreenTime-Reminder/releases/download/v1.2.7/ScreenTimeReminder.apk">Download the APK</a>
          <a class="btn btn-ghost" href="https://github.com/owaiskhan-ash/ScreenTime-Reminder">Source on GitHub</a>""",
        "cta_note": "Version 1.2.7 for Android 8.0 and later. Free, signed APK from the project’s GitHub releases.",
        "shots": [
            shot("/assets/screentime/today-400.webp",
                 "Screen Time Reminder today view with stitched cyan leather card and live screen-time count",
                 "Today: one running count of continuous use.",
                 400, 866,
                 "/assets/screentime/today-400.webp 400w, /assets/screentime/today-780.webp 780w",
                 "(max-width: 620px) 42vw, 210px"),
            shot("/assets/screentime/break-400.webp",
                 "Screen Time Reminder calm five-minute break screen with 20-20-20 eye rest note",
                 "The break nudge: one message, no streak to lose.",
                 400, 866,
                 "/assets/screentime/break-400.webp 400w, /assets/screentime/break-780.webp 780w",
                 "(max-width: 620px) 42vw, 210px"),
            shot("/assets/screentime/week-400.webp",
                 "Screen Time Reminder seven-day history and daily average chart",
                 "Seven days, so you can see the pattern.",
                 400, 866,
                 "/assets/screentime/week-400.webp 400w, /assets/screentime/week-780.webp 780w",
                 "(max-width: 620px) 42vw, 210px"),
        ],
        "body": """
        <h2>What it does</h2>
        <ul>
          <li><strong>One live number</strong>: how long the current stretch of phone use has lasted.</li>
          <li><strong>One calm reminder</strong> when a session runs long, instead of a stream of notifications.</li>
          <li><strong>A seven-day history</strong>, so a bad afternoon is visible as a pattern rather than a verdict.</li>
          <li><strong>Nothing to keep up.</strong> No streaks, no scores, no daily target to miss.</li>
        </ul>

        <h2>How it works</h2>
        <p>Android exposes app-usage information to apps that are granted <em>usage access</em>. Screen Time
        Reminder reads which app was in the foreground and when it was left, and turns that into a single
        continuous-use timer. When the timer passes the threshold, it posts one notification and resets.
        Locking the phone or switching to a different session ends the count.</p>
        <p>It is deliberately a reminder, not a manager: it cannot block apps, close them or shame you into
        closing them. The only action it takes is one notification you can dismiss.</p>

        <h2>What it does not do</h2>
        <p>The app does not request the internet permission at all. That is not a promise in a policy
        document; it is a permission that is absent from the manifest, so the app has no technical way to
        send anything anywhere. Every number it records stays in its own private storage on the phone, is
        removed when you uninstall, and is never uploaded, sold or shared.</p>
        <p>There are no accounts, no advertising SDK, no analytics SDK and no crash reporter. The project’s
        source is public, so the claim can be checked rather than trusted.</p>

        <h2>Compatibility and version</h2>
        <dl class="facts">
          <dt>Platform</dt><dd>Android 8.0 (API 26) and later.</dd>
          <dt>Permission</dt><dd>Usage access, used only to see which app is in the foreground and for how long.</dd>
          <dt>Internet</dt><dd>Not requested. The app cannot connect to a network.</dd>
          <dt>Price</dt><dd>Free, with no ads and no in-app purchases.</dd>
          <dt>Source</dt><dd><a href="https://github.com/owaiskhan-ash/ScreenTime-Reminder">ScreenTime-Reminder repository on GitHub</a></dd>
          <dt>Made by</dt><dd>Owais Khan (Just Apps), an independent studio in Mumbai, India. <a href="https://github.com/owaiskhan-ash">github.com/owaiskhan-ash</a>.</dd>
        </dl>
        """,
        "faq": [
            ("Does Screen Time Reminder block apps?",
             "No. It is a reminder, not a blocker or a parental control. It counts continuous use and sends one notification when a session runs long; it cannot close or restrict anything."),
            ("Does Screen Time Reminder need an internet connection?",
             "No, and it could not use one. The app does not request the internet permission, so it has no technical way to send or receive data."),
            ("What permission does Screen Time Reminder need?",
             "Usage access, which is Android’s name for permission to see which app is in the foreground and for how long. Without it the app has nothing to measure."),
            ("Does Screen Time Reminder keep a streak or score?",
             "No. There are no streaks, scores, badges or daily targets. You get a running count and a seven-day history, and that is all."),
            ("Is Screen Time Reminder really free?",
             "Yes. It is free to download and use, with no ads, no subscription and no in-app purchases."),
        ],
        "software": {
            "name": "Screen Time Reminder",
            "applicationCategory": "HealthApplication",
            "operatingSystem": "Android 8.0 and later",
            "description": "Counts continuous phone use and sends one gentle break reminder when a session runs long, with a seven-day history. Free, ad-free, and without the internet permission.",
            "softwareVersion": "1.2.7",
            "image": BASE + "/assets/screentime/icon-512.png",
            "screenshot": [
                BASE + "/assets/screentime/today-780.webp",
                BASE + "/assets/screentime/break-780.webp",
                BASE + "/assets/screentime/week-780.webp",
            ],
            "featureList": [
                "Live count of continuous phone use",
                "One gentle break reminder",
                "Seven-day history",
                "No streaks, scores or targets",
                "No internet permission",
                "No ads, accounts or analytics",
            ],
            "downloadUrl": "https://github.com/owaiskhan-ash/ScreenTime-Reminder/releases/download/v1.2.7/ScreenTimeReminder.apk",
            "sameAs": ["https://github.com/owaiskhan-ash/ScreenTime-Reminder"],
        },
        "cta_primary": "https://github.com/owaiskhan-ash/ScreenTime-Reminder/releases/download/v1.2.7/ScreenTimeReminder.apk",
    },
    {
        "slug": "subscription-tracker",
        "name": "Subscription Tracker",
        "kicker": "03 · Money",
        "nav_cta": "Get the app",
        "title": "Subscription Tracker: Recurring Bills | Just Apps",
        "description": "Free, offline Android app for subscriptions and recurring bills: normalized monthly and yearly totals, plus renewal reminders. No bank connection.",
        "og": "og-subscription-tracker.png",
        "h1": "Subscription Tracker: every subscription and recurring bill in one place.",
        "lede": "Subscription Tracker is a free Android app for keeping track of what renews, when, and what it really costs. Add subscriptions and bills by hand, see a monthly and yearly total you can compare, and get a reminder before each renewal.",
        "answer": "<p><strong>In one line:</strong> Subscription Tracker is a free, offline Android app that records your recurring bills, converts them into comparable monthly and yearly totals, and reminds you before a renewal, without connecting to your bank.</p>",
        "cta": """          <a class="btn btn-primary" href="https://github.com/owaiskhan-ash/Subscription-Tracker/releases/download/v1.2.0/subscription-tracker-v1.2.0.apk">Download the APK</a>
          <a class="btn btn-ghost" href="https://github.com/owaiskhan-ash/Subscription-Tracker">Source on GitHub</a>""",
        "cta_note": "Version 1.2.0, free, Android 8.0 and later. Distributed as a signed APK from the project’s GitHub releases.",
        "shots": [
            shot("/assets/subscriptions/today-400.webp",
                 "Subscription Tracker monthly overview with stitched petrol suede card and upcoming renewals",
                 "This month’s total, and what renews next.",
                 400, 866,
                 "/assets/subscriptions/today-400.webp 400w, /assets/subscriptions/today-780.webp 780w",
                 "(max-width: 620px) 42vw, 210px"),
            shot("/assets/subscriptions/all-400.webp",
                 "Subscription Tracker list of tracked subscriptions across stitched suede cards",
                 "Every entry keeps its own billing cycle.",
                 400, 866,
                 "/assets/subscriptions/all-400.webp 400w, /assets/subscriptions/all-780.webp 780w",
                 "(max-width: 620px) 42vw, 210px"),
            shot("/assets/subscriptions/settings-400.webp",
                 "Subscription Tracker currency, monthly budget and local reminder settings",
                 "Reminders are optional and local.",
                 400, 866,
                 "/assets/subscriptions/settings-400.webp 400w, /assets/subscriptions/settings-780.webp 780w",
                 "(max-width: 620px) 42vw, 210px"),
        ],
        "body": """
        <h2>What it does</h2>
        <ul>
          <li><strong>One list of everything that recurs</strong>: streaming, cloud storage, insurance, the Wi-Fi bill, anything with a renewal date.</li>
          <li><strong>A monthly and yearly total</strong> that you can actually compare, because each entry is normalised from its own billing cycle.</li>
          <li><strong>Upcoming renewals</strong> in date order, so nothing arrives as a surprise.</li>
          <li><strong>Optional reminders</strong> before a payment is due, scheduled on the phone.</li>
          <li><strong>Works offline</strong>, with no bank connection and no account.</li>
        </ul>

        <h2>Why the totals are normalised</h2>
        <p>“₹149 a month” and “₹1,499 a year” are not comparable until they are on the same timeline, and a
        list of mixed cycles makes it very easy to underestimate what you spend. Every entry therefore keeps
        its real billing cycle and is also converted to a monthly equivalent, so a yearly plan, a weekly plan
        and a monthly plan all contribute to one honest figure. The yearly total is that same figure across
        twelve months.</p>
        <p>The result is a number that answers the question people actually have: <em>what do all of these
        cost me, together, this month?</em></p>

        <h2>Manual by design</h2>
        <p>There is no bank connection, no SMS scraping and no account aggregation. You add each subscription
        yourself, which sounds like more work and is in fact the privacy feature: nothing about your finances
        is ever uploaded, and no third party is told which services you pay for. The app does not request an
        account from you, and its data lives in its own storage on the phone.</p>
        <p>That also means the numbers are only as good as the list. The app deliberately does not guess at
        subscriptions from your messages or notifications.</p>

        <h2>Compatibility and version</h2>
        <dl class="facts">
          <dt>Platform</dt><dd>Android 8.0 (API 26) and later.</dd>
          <dt>Version</dt><dd>1.2.0.</dd>
          <dt>Price</dt><dd>Free, with no ads and no in-app purchases.</dd>
          <dt>Bank access</dt><dd>None. Entries are added by hand and stored on the device.</dd>
          <dt>Source</dt><dd><a href="https://github.com/owaiskhan-ash/Subscription-Tracker">Subscription-Tracker repository on GitHub</a></dd>
          <dt>Made by</dt><dd>Owais Khan (Just Apps), an independent studio in Mumbai, India. <a href="https://github.com/owaiskhan-ash">github.com/owaiskhan-ash</a>.</dd>
        </dl>
        """,
        "faq": [
            ("Does Subscription Tracker connect to my bank?",
             "No. You add each subscription and its renewal date yourself. The app has no bank integration, no SMS access and no account aggregation, so your financial accounts are never linked to it."),
            ("How are monthly and yearly totals calculated?",
             "Each entry keeps its own billing cycle and is converted to a monthly equivalent, so weekly, monthly and yearly plans can be compared and added together. The yearly total is that monthly figure across twelve months."),
            ("Does Subscription Tracker work offline?",
             "Yes. The app is built to work without a connection; subscriptions and totals are stored on the device."),
            ("Will it detect subscriptions automatically?",
             "No. Entries are added by hand, on purpose; automatic detection would mean reading your messages or connecting to your bank, and the app does neither."),
            ("Is Subscription Tracker free?",
             "Yes. Free to download and use, with no ads, no subscription and no in-app purchases."),
        ],
        "software": {
            "name": "Subscription Tracker",
            "applicationCategory": "FinanceApplication",
            "operatingSystem": "Android 8.0 and later",
            "softwareVersion": "1.2.0",
            "description": "Manually track subscriptions and recurring bills, view normalized monthly and yearly spending, and get on-device renewal reminders. Free, offline and private, with no bank connection.",
            "image": BASE + "/assets/subscriptions/icon-512.png",
            "screenshot": [
                BASE + "/assets/subscriptions/today-780.webp",
                BASE + "/assets/subscriptions/all-780.webp",
                BASE + "/assets/subscriptions/settings-780.webp",
            ],
            "featureList": [
                "One list of subscriptions and recurring bills",
                "Normalized monthly and yearly totals",
                "Upcoming renewals in date order",
                "Optional reminders before payment",
                "Works offline",
                "No bank connection, no account, no ads",
            ],
            "downloadUrl": "https://github.com/owaiskhan-ash/Subscription-Tracker/releases/download/v1.2.0/subscription-tracker-v1.2.0.apk",
            "sameAs": ["https://github.com/owaiskhan-ash/Subscription-Tracker"],
        },
        "cta_primary": "https://github.com/owaiskhan-ash/Subscription-Tracker/releases/download/v1.2.0/subscription-tracker-v1.2.0.apk",
    },
    {
        "slug": "vaccine-routine",
        "name": "Vaccine Routine",
        "kicker": "04 · Family",
        "nav_cta": "Get the app",
        "title": "Vaccine Routine: Baby Vaccine Log | Just Apps",
        "description": "Free, offline-first vaccine log and reminder for babies and children, with India's National Immunization Schedule as optional suggestions. No account, no ads.",
        "og": "og-vaccine-routine.png",
        "h1": "Vaccine Routine: a calm, offline vaccine log for little ones.",
        "lede": "Vaccine Routine keeps a child’s vaccination record on your phone, helps you plan the next dose and reminds you when it is due. India’s National Immunization Schedule is offered as a suggestion, never a prescription.",
        "answer": "<p><strong>In one line:</strong> Vaccine Routine is a free, offline-first vaccine log and reminder for babies and children, with India’s National Immunization Schedule available as optional suggestions rather than medical advice.</p>",
        "cta": """          <a class="btn btn-primary" href="https://github.com/owaiskhan-ash/vaccine-Tracker/releases/download/v1.0/Vaccine-Routine-1.0.apk">Download the APK</a>
          <a class="btn btn-ghost" href="https://github.com/owaiskhan-ash/vaccine-Tracker">Source on GitHub</a>""",
        "cta_note": "Version 1.0, free. Available for Android and on the web; signed APK distributed from the project’s GitHub releases.",
        "shots": [
            shot("/assets/vaccine/today-400.webp",
                 "Today: a child's vaccine record with given and planned doses",
                 "Today: what has been given and what is next.", 400, 866),
            shot("/assets/vaccine/schedule-400.webp",
                 "Planned and completed vaccine entries grouped by month",
                 "The record, grouped by month.", 400, 866),
            shot("/assets/vaccine/reminders-400.webp",
                 "Upcoming vaccination dates and notification settings",
                 "Reminders for the dates you choose.", 400, 866),
        ],
        "body": """
        <h2>What it does</h2>
        <ul>
          <li><strong>A local vaccine record</strong> for a child, kept on the phone rather than in an account.</li>
          <li><strong>A plan of upcoming doses</strong>, so the next visit is not a surprise.</li>
          <li><strong>Gentle reminders</strong> on the dates you set.</li>
          <li><strong>India’s National Immunization Schedule</strong> as optional suggestions you can accept, ignore or edit.</li>
          <li><strong>Offline-first</strong>: the record opens and saves with no connection.</li>
        </ul>

        <h2>The schedule is a suggestion, not a prescription</h2>
        <p>The app can show the doses in India’s National Immunization Schedule as a starting point, because
        an empty form is not a helpful place to begin. It is a template, not an instruction. Timing varies
        with the child, the state and the vaccines available, and some children follow a different schedule
        for medical reasons.</p>
        <p>Nothing in the app is medical advice, and it does not replace the health worker who sees your
        child. Treat every date it suggests as something to confirm with them, and record what actually
        happened rather than what was planned.</p>

        <h2>Private by construction</h2>
        <p>A child’s health record is about the most sensitive list a phone can hold, which is why Vaccine
        Routine is built without an account, a sync service or an analytics SDK. Records are written to the
        app’s own storage on the device and are removed when the app is uninstalled. There is nothing to
        log in to, so there is no server holding a copy.</p>
        <p>That trade-off is deliberate: no cloud sync means no account to leak and nothing to subscribe to.
        If you change phones, the record moves with Android’s own backup or not at all; the app does not
        upload it anywhere.</p>

        <h2>Compatibility and version</h2>
        <dl class="facts">
          <dt>Platform</dt><dd>Android app and web app.</dd>
          <dt>Price</dt><dd>Free, with no ads and no in-app purchases.</dd>
          <dt>Account</dt><dd>Not required; there is no sign-in and no sync.</dd>
          <dt>Storage</dt><dd>On the device, removed when you uninstall.</dd>
          <dt>Medical status</dt><dd>Not a medical device and not a substitute for professional advice.</dd>
          <dt>Source</dt><dd><a href="https://github.com/owaiskhan-ash/vaccine-Tracker">vaccine-Tracker repository on GitHub</a></dd>
          <dt>Made by</dt><dd>Owais Khan (Just Apps), an independent studio in Mumbai, India. <a href="https://github.com/owaiskhan-ash">github.com/owaiskhan-ash</a>.</dd>
        </dl>
        """,
        "faq": [
            ("Is the vaccine schedule in the app medical advice?",
             "No. India’s National Immunization Schedule is included as an optional template, not as an instruction. Timing differs between children, states and vaccines, so confirm every date with the health worker who sees your child."),
            ("Where is my child’s record stored?",
             "On your device, in the app’s own private storage. There is no account and no sync service, so no copy is uploaded to a server, and uninstalling the app removes it."),
            ("Does it work without a connection?",
             "Yes. Vaccine Routine is offline-first: the record opens and saves with no network, and reminders are scheduled on the device."),
            ("Can I edit the suggested schedule?",
             "Yes. The national schedule is a starting point you can accept, ignore or edit, so the record reflects what actually happened rather than what was planned."),
            ("Is Vaccine Routine free?",
             "Yes. Free to download and use, with no ads, no subscription and no in-app purchases."),
        ],
        "software": {
            "name": "Vaccine Routine",
            "applicationCategory": "HealthApplication",
            "operatingSystem": "Android and web",
            "description": "An offline-first vaccine log and reminder for babies and children, with India's National Immunization Schedule as optional suggestions. Free, private, no account.",
            "image": BASE + "/assets/vaccine/icon-192.png",
            "screenshot": [
                BASE + "/assets/vaccine/today-585.webp",
                BASE + "/assets/vaccine/schedule-585.webp",
            ],
            "featureList": [
                "Local vaccine record for a child",
                "Planned doses and gentle reminders",
                "India's National Immunization Schedule as a suggestion",
                "Works offline",
                "No account, no sync, no ads",
            ],
            "softwareVersion": "1.0",
            "downloadUrl": "https://github.com/owaiskhan-ash/vaccine-Tracker/releases/download/v1.0/Vaccine-Routine-1.0.apk",
            "sameAs": ["https://github.com/owaiskhan-ash/vaccine-Tracker"],
        },
        "cta_primary": "https://github.com/owaiskhan-ash/vaccine-Tracker/releases/download/v1.0/Vaccine-Routine-1.0.apk",
    },
    {
        "slug": "water-reminder",
        "date_published": "2026-10-28",
        "name": "Water Reminder",
        "kicker": "05 · Hydration",
        "nav_cta": "Get the app",
        "title": "Water Reminder: Drink Water Every Two Hours | Just Apps",
        "description": "Free Android water reminder that nudges you every two hours, with 1, 3 or 4 hour intervals and quiet hours overnight. No intake log, no account, no network.",
        "og": "og-water-reminder.png",
        "h1": "Water Reminder: a nudge to drink water every two hours, and nothing else.",
        "lede": "Water Reminder is a free Android app with one job: it sends a water reminder every two hours, aligned to your own clock, and stays quiet overnight if you ask it to. It keeps no intake log, asks you for nothing, and cannot connect to the internet.",
        "answer": "<p><strong>In one line:</strong> Water Reminder is a free, offline Android app that sends a water reminder every two hours, or every one, three or four hours, skips a quiet-hours window at night, and deliberately keeps no intake log, counter or account.</p>",
        "cta": """          <a class="btn btn-primary" href="https://github.com/owaiskhan-ash/Water-Reminder/releases/download/v1.0.0/Water-Reminder-v1.0.0.apk">Download the APK</a>
          <a class="btn btn-ghost" href="https://github.com/owaiskhan-ash/Water-Reminder">Source on GitHub</a>""",
        "cta_note": "Version 1.0.0 for Android 7.0 and later. Free, signed APK from the project’s GitHub releases. The app does not request the internet permission.",
        "shots": [
            shot("/assets/water/home-400.webp",
                 "Water Reminder home screen showing the next reminder at 6:00 PM, the two-hour interval and the quiet-hours setting",
                 "The next reminder, the interval and the quiet-hours switch, on felt.",
                 400, 867,
                 "/assets/water/home-400.webp 400w, /assets/water/home-780.webp 780w",
                 "(max-width: 620px) 42vw, 210px"),
        ],
        "body": """
        <h2>What it does</h2>
        <ul>
          <li><strong>One reminder every two hours</strong> by default, with one, three and four hour intervals available in Settings.</li>
          <li><strong>Clock-aligned slots</strong>, so a two-hour interval lands on 8:00, 10:00, 12:00 and so on rather than drifting from whenever you installed it.</li>
          <li><strong>Optional quiet hours</strong>, from 10 PM to 8 AM, for people who would rather not be told to drink water at midnight.</li>
          <li><strong>Exact alarms</strong>, so a reminder still arrives in Android’s Doze mode, and the schedule is re-armed after a reboot, an app update or a time-zone change.</li>
          <li><strong>No intake log, no counter, no chart.</strong> The app never asks how much you drank.</li>
        </ul>

        <h2>What it deliberately does not do</h2>
        <p>Most hydration apps are trackers: a glass counter, a daily target, a chart of the week and a streak that
        breaks. Water Reminder is the opposite. There is no place to log a glass of water, no target to miss and no
        history to feel guilty about, because the app is only responsible for the nudge.</p>
        <p>That narrowness is the feature. A reminder that cannot accumulate data also cannot accumulate a privacy
        problem, and there is nothing to reset when you skip a day.</p>

        <h2>How the reminders are scheduled</h2>
        <p>Scheduling happens entirely on the device, with Android’s alarm manager. Nothing is sent from a server, so
        the reminders work with no connection, survive a reboot, and cannot be affected by a service being
        unavailable. Each slot is checked against your quiet-hours window when it comes due: a slot that falls inside
        the window is skipped rather than queued, so you do not wake to a burst of late notifications.</p>
        <p>Android 12 and later can require the Alarms and reminders permission for exact timing. If it is not
        granted, Android may deliver a reminder a little late, which is the one case where a nudge can arrive off the
        hour.</p>

        <h2>What stays on your phone</h2>
        <p>There is no account, no sync and no analytics library. Everything the app knows lives in its own private
        storage on the device.</p>
        <dl class="facts">
          <dt>Interval and quiet hours</dt><dd>Stored in the app’s private storage on the phone. Removed when you uninstall.</dd>
          <dt>Internet permission</dt><dd>Not requested. The app has no technical way to send or receive data.</dd>
          <dt>Intake data</dt><dd>None is collected. The app has no logging screen and no database of drinks.</dd>
          <dt>Analytics and ads</dt><dd>None. No advertising SDK, no crash-reporting SDK, no tracking.</dd>
        </dl>
        <p>The full detail is on the <a href="/privacy">privacy policy page</a>.</p>

        <h2>Compatibility and version</h2>
        <dl class="facts">
          <dt>Platform</dt><dd>Android 7.0 (API 24) and later.</dd>
          <dt>Version</dt><dd>1.0.0.</dd>
          <dt>Price</dt><dd>Free, with no ads and no in-app purchases.</dd>
          <dt>Account</dt><dd>Not required, and not possible; there is no sign-in.</dd>
          <dt>Source</dt><dd><a href="https://github.com/owaiskhan-ash/Water-Reminder">Water-Reminder repository on GitHub</a></dd>
          <dt>Made by</dt><dd>Owais Khan (Just Apps), an independent studio in Mumbai, India. <a href="https://github.com/owaiskhan-ash">github.com/owaiskhan-ash</a>.</dd>
        </dl>
        """,
        "faq": [
            ("How often does Water Reminder notify me?",
             "Every two hours by default. Settings offers one, three and four hour intervals instead, and each slot is aligned to your local clock, so a two-hour interval lands on the hour rather than drifting from install time."),
            ("Does Water Reminder log how much water I drink?",
             "No. There is no intake log, no glass counter, no chart and no daily target. The app sends a reminder and nothing else, and it never asks how much you drank."),
            ("Does Water Reminder need an internet connection?",
             "No, and it could not use one. Water Reminder does not request Android’s internet permission, so it has no technical way to send or receive data."),
            ("Will Water Reminder wake me at night?",
             "Not if you leave quiet hours on. The default window is 10 PM to 8 AM, and a reminder slot that falls inside it is skipped entirely rather than delivered late once the window ends."),
            ("Do the reminders survive a restart?",
             "Yes. Reminders are scheduled on the device with Android’s alarm manager and are re-armed after a reboot, an app update or a time-zone change. Android 12 and later may require the Alarms and reminders permission for exact timing."),
            ("Is Water Reminder free?",
             "Yes. Free to download and use, with no ads, no subscription and no in-app purchases."),
        ],
        "software": {
            "name": "Water Reminder",
            "applicationCategory": "HealthApplication",
            "operatingSystem": "Android 7.0 and later",
            "description": "A water reminder that nudges you every two hours by default, with adjustable one to four hour intervals, clock-aligned slots and optional quiet hours. No intake logging, counters, account or network access.",
            "image": BASE + "/assets/water/icon.png",
            "screenshot": BASE + "/assets/water/home-780.webp",
            "featureList": [
                "Water reminders every two hours by default, aligned to the local clock",
                "Adjustable one, two, three or four hour interval",
                "Optional quiet hours from 10 PM to 8 AM",
                "Exact alarms that survive Doze, reboots and time-zone changes",
                "No intake logging, counters, charts, account or network requests",
            ],
            "softwareVersion": "1.0.0",
            "downloadUrl": "https://github.com/owaiskhan-ash/Water-Reminder/releases/download/v1.0.0/Water-Reminder-v1.0.0.apk",
            "sameAs": ["https://github.com/owaiskhan-ash/Water-Reminder"],
        },
        "cta_primary": "https://github.com/owaiskhan-ash/Water-Reminder/releases/download/v1.0.0/Water-Reminder-v1.0.0.apk",
    },
    {
        "slug": "steps-reminder",
        "date_published": "2026-10-28",
        "name": "Step Reminder",
        "kicker": "06 · Movement",
        "nav_cta": "Get the app",
        "title": "Step Reminder: Daily Step Goal and One Nudge | Just Apps",
        "description": "Free Android step counter with a daily target from 2,000 to 20,000 steps, one reminder at the hour you choose and a seven-day history. No account, no cloud.",
        "og": "og-step-reminder.png",
        "h1": "Step Reminder: a daily step goal, one nudge, and a seven-day trail.",
        "lede": "Step Reminder counts your steps against a target you choose, keeps a seven-day history that builds itself, and sends one plain-spoken reminder at the hour you pick. It reads the phone’s own step counter, so it needs no login, no Google Fit and no cloud.",
        "answer": "<p><strong>In one line:</strong> Step Reminder is a free Android step counter with a daily goal between 2,000 and 20,000 steps, one daily reminder at a chosen hour and a seven-day history, all kept on the phone with no account, cloud or fitness-service connection.</p>",
        "cta": """          <a class="btn btn-primary" href="https://github.com/owaiskhan-ash/Steps-Reminder/releases/download/v1.4.0/SC-Step-Reminder-1.4.0.apk">Download the APK</a>
          <a class="btn btn-ghost" href="https://github.com/owaiskhan-ash/Steps-Reminder">Source on GitHub</a>""",
        "cta_note": "Version 1.4.0 for Android 6.0 and later, with a web build. Free signed APK from the project’s GitHub releases.",
        "shots": [
            shot("/assets/steps/today-400.webp",
                 "Step Reminder Today screen with sample progress of 6,240 steps toward an 8,000-step goal",
                 "Today: 6,240 of 8,000 steps, with the day’s remainder and walking time.",
                 400, 867,
                 "/assets/steps/today-400.webp 400w, /assets/steps/today-780.webp 780w",
                 "(max-width: 620px) 42vw, 210px"),
            shot("/assets/steps/trail-400.webp",
                 "Step Reminder Trail screen showing the weekly total and daily step ledger with sample data",
                 "Trail: the week so far and a day-by-day ledger.",
                 400, 867,
                 "/assets/steps/trail-400.webp 400w, /assets/steps/trail-780.webp 780w",
                 "(max-width: 620px) 42vw, 210px"),
            shot("/assets/steps/tune-400.webp",
                 "Step Reminder Tune screen showing a daily target, chosen reminder time and phone step-counter settings",
                 "Tune: the target, the reminder hour and the sensor.",
                 400, 867,
                 "/assets/steps/tune-400.webp 400w, /assets/steps/tune-780.webp 780w",
                 "(max-width: 620px) 42vw, 210px"),
        ],
        "body": """
        <h2>What it does</h2>
        <ul>
          <li><strong>A daily step target</strong> between 2,000 and 20,000 steps, with presets for the first run.</li>
          <li><strong>Today’s real total</strong>, read from the phone’s own step counter, including the steps you took while the app was closed.</li>
          <li><strong>One reminder a day</strong> at the hour you choose, with copy that states exactly how many steps are left.</li>
          <li><strong>A seven-day history</strong> that fills in by itself, with a daily ledger and a weekly total.</li>
          <li><strong>No account, no Google Fit, no Health Connect, no cloud</strong> and no analytics.</li>
        </ul>

        <h2>Where the steps come from</h2>
        <p>Android keeps a cumulative step counter that runs whether or not an app is open. Step Reminder reads that
        counter and subtracts a midnight baseline, so opening the app at any hour gives you the day’s real total
        rather than a number that only counts while the app is on screen. On Android 10 and later, reading it needs the
        activity recognition permission; if that is refused, the app says so and counts nothing instead of guessing.</p>
        <p>If the phone was restarted after midnight, every step in the counter happened today and the counter
        <em>is</em> the total. If it was restarted before midnight, the older steps cannot be attributed to a day, so
        the app starts counting from the restart time and labels that honestly rather than inventing a baseline.</p>
        <p>A midnight alarm banks the finished day, which is why a week of history exists even if you never open the
        app, and a boot receiver re-arms that alarm after a restart. Phones without a step counter can use an optional
        motion-sensor fallback, which is off until you switch it on.</p>

        <h2>One reminder, in plain words</h2>
        <p>The reminder is a single notification a day, and its text is written at the moment it fires: if you are
        short of the target it says how many steps are missing out of the goal, so the notification is information
        rather than a generic nudge. There are no streaks to break, no badges and no second reminder.</p>
        <p>The web build is the same app in a browser. Its reminder appears as a browser notification only while the
        tab is open, and the in-app nudge is always shown, so the web version never pretends to have Android’s
        scheduling behind it.</p>

        <h2>What stays on your phone</h2>
        <dl class="facts">
          <dt>Steps, goal and history</dt><dd>Stored on the device only: in the app’s private storage on Android, and in the browser’s local storage on the web build.</dd>
          <dt>Fitness services</dt><dd>None. No Google Fit, no Health Connect, no Samsung Health and no third-party sync.</dd>
          <dt>Account</dt><dd>Not required, and not possible; there is no sign-in.</dd>
          <dt>Analytics and ads</dt><dd>None. No advertising SDK, no crash-reporting SDK, no tracking.</dd>
        </dl>
        <p>The full detail is on the <a href="/privacy">privacy policy page</a>.</p>

        <h2>Compatibility and version</h2>
        <dl class="facts">
          <dt>Platform</dt><dd>Android 6.0 and later, with a web build for desktop and mobile browsers.</dd>
          <dt>Version</dt><dd>1.4.0.</dd>
          <dt>Price</dt><dd>Free, with no ads and no in-app purchases.</dd>
          <dt>Permissions</dt><dd>Activity recognition, for the phone’s step counter, and notifications for the daily reminder. No location permission is requested.</dd>
          <dt>Source</dt><dd><a href="https://github.com/owaiskhan-ash/Steps-Reminder">Steps-Reminder repository on GitHub</a></dd>
          <dt>Made by</dt><dd>Owais Khan (Just Apps), an independent studio in Mumbai, India. <a href="https://github.com/owaiskhan-ash">github.com/owaiskhan-ash</a>.</dd>
        </dl>
        """,
        "faq": [
            ("Does Step Reminder need Google Fit or Health Connect?",
             "No. It reads Android’s own cumulative step counter directly, so there is no fitness-service connection, no login and no data leaving the phone."),
            ("How many steps can I set as a goal?",
             "Any daily target between 2,000 and 20,000 steps. Presets are offered on the first run, and the goal can be changed at any time in Tune."),
            ("Does it count steps while the app is closed?",
             "Yes. Android keeps the step counter running in the background, and a midnight alarm banks the finished day, so the history builds even when you never open the app."),
            ("Why does the total start from a time rather than midnight?",
             "Only when the phone was restarted before midnight, because the steps the counter kept before that restart cannot be attributed to a day. The app labels the total as counting from the restart time instead of guessing."),
            ("Do web reminders work with the tab closed?",
             "No. The web build fires a browser notification only while the page is open, and always shows an in-app nudge. Reliable background reminders are an Android feature."),
            ("Is Step Reminder free?",
             "Yes. Free to download and use, with no ads, no subscription and no in-app purchases."),
        ],
        "software": {
            "name": "Step Reminder",
            "applicationCategory": "HealthApplication",
            "operatingSystem": "Android 6.0 and later, web",
            "description": "A daily step counter with a goal you choose, a seven-day history and one reminder at a chosen hour. Steps, goals and history stay on the device, with no Google Fit, Health Connect, cloud or analytics.",
            "image": BASE + "/assets/steps/icon-192.png",
            "screenshot": [
                BASE + "/assets/steps/today-780.webp",
                BASE + "/assets/steps/trail-780.webp",
                BASE + "/assets/steps/tune-780.webp",
            ],
            "featureList": [
                "Daily step targets from 2,000 to 20,000",
                "Reads the phone's own cumulative step counter",
                "Seven-day history and a daily ledger that build themselves",
                "One reminder at a chosen hour, with live copy naming the steps still missing",
                "No account, Google Fit, Health Connect, cloud or analytics",
            ],
            "softwareVersion": "1.4.0",
            "downloadUrl": "https://github.com/owaiskhan-ash/Steps-Reminder/releases/download/v1.4.0/SC-Step-Reminder-1.4.0.apk",
            "sameAs": ["https://github.com/owaiskhan-ash/Steps-Reminder"],
        },
        "cta_primary": "https://github.com/owaiskhan-ash/Steps-Reminder/releases/download/v1.4.0/SC-Step-Reminder-1.4.0.apk",
    },
    {
        "slug": "remindme",
        "date_published": "2026-10-28",
        "name": "RemindME",
        "kicker": "07 · Reminders",
        "nav_cta": "Get the app",
        "title": "RemindME: Conversational Reminders | Just Apps",
        "description": "Free Android reminder app: write a phrase with a date and time and get an alarm you cannot miss. Seven languages, on-device storage, no account, no ads.",
        "og": "og-remindme.png",
        "h1": "RemindME: write a reminder the way you would say it.",
        "lede": "RemindME turns a sentence such as “tomorrow at 9 AM, call the clinic” into a scheduled Android alarm. It works in seven languages, requires a real date and time rather than guessing one, and rings on the alarm stream so silent mode cannot swallow it.",
        "answer": "<p><strong>In one line:</strong> RemindME is a free Android reminder app that parses a natural-language phrase with a date and time into a device alarm, in seven languages, with snooze and done actions, and keeps every reminder on the phone.</p>",
        "cta": """          <a class="btn btn-primary" href="https://github.com/owaiskhan-ash/RemindME/raw/v1.0.6/release/RemindME-v1.0.6.apk">Download the APK</a>
          <a class="btn btn-ghost" href="https://github.com/owaiskhan-ash/RemindME">Source on GitHub</a>""",
        "cta_note": "Version 1.0.6 for Android 8.0 and later. Free, signed APK from the project’s GitHub releases.",
        "shots": [
            shot("/assets/remindme/home-400.webp",
                 "RemindME Home screen with conversational reminder input, a live Smart Parse preview and an upcoming reminder card",
                 "Home: type a sentence, then watch the parse preview.",
                 400, 866,
                 "/assets/remindme/home-400.webp 400w, /assets/remindme/home-780.webp 780w",
                 "(max-width: 620px) 42vw, 210px"),
            shot("/assets/remindme/previous-400.webp",
                 "RemindME Previous reminders screen showing completed reminders history and a clear completed action",
                 "Previous: what has already rung, and a way to clear it.",
                 400, 866,
                 "/assets/remindme/previous-400.webp 400w, /assets/remindme/previous-780.webp 780w",
                 "(max-width: 620px) 42vw, 210px"),
            shot("/assets/remindme/settings-400.webp",
                 "RemindME Settings screen showing seven language choices, alarm stream sound options and a dark mode toggle",
                 "Settings: seven languages, the alarm sound and dark mode.",
                 400, 866,
                 "/assets/remindme/settings-400.webp 400w, /assets/remindme/settings-780.webp 780w",
                 "(max-width: 620px) 42vw, 210px"),
        ],
        "body": """
        <h2>What it does</h2>
        <ul>
          <li><strong>Conversational input.</strong> Type “tomorrow at 9 AM, check in with Abdullah about homework” and the parse panel shows the exact time it understood before you save.</li>
          <li><strong>Seven languages</strong>: English, Bahasa Indonesia, Español, Português, हिन्दी, العربية with a right-to-left layout, and 简体中文, in the interface and in the parser.</li>
          <li><strong>Device alarms</strong>, scheduled with Android’s alarm manager, so they arrive after the app is closed.</li>
          <li><strong>Alarm-stream audio</strong>, so ring or vibrate mode does not mute a reminder that is due.</li>
          <li><strong>Snooze 10 min and Mark done</strong> actions on the notification itself, a three-tab dock, and dark mode by default.</li>
          <li><strong>Automatic restoration</strong> of outstanding reminders after a reboot or an app update.</li>
        </ul>

        <h2>How a phrase becomes an alarm</h2>
        <p>The parser looks for a date, a weekday, a clock time, a day period and relative durations such as
        “in 10 minutes”, “mañana a las 9”, “amanhã às 18:30”, “कल शाम 6 बजे”, “غدا الساعة 9 مساء”,
        “明天上午9点” and “besok jam 9 pagi”. It also corrects common English misspellings such as
        “tomrws” or “ceckin”, because typing a reminder quickly is the normal case.</p>
        <p>What it will not do is invent a time. A reminder needs an explicit date and time, and when one is missing
        the preview names the missing detail instead of accepting the phrase and scheduling it for an
        arbitrary hour. That is the difference between a reminder app you can trust with something important and one
        that quietly fails.</p>

        <h2>Why it cuts through silent mode</h2>
        <p>A due reminder plays on Android’s dedicated alarm audio stream, which is separate from the ring volume that
        silent and vibrate modes control. A phone on silent, or on vibrate, still rings. The stream is not a way
        around your own choices: the alarm volume can be turned down by hand, and Do Not Disturb still applies unless
        you have granted the app access to it.</p>
        <p>Exact delivery needs Android’s Alarms and reminders permission on Android 12 and later, and notifications
        need to be allowed on Android 13 and later. Without the exact-alarm access, RemindME falls back to Android’s
        battery-friendly inexact scheduling and says so rather than silently drifting.</p>

        <h2>What stays on your phone</h2>
        <dl class="facts">
          <dt>Reminder text and settings</dt><dd>In the app’s private storage on the device. Removed when you uninstall.</dd>
          <dt>Network use</dt><dd>None by default. If you switch on the optional RemindME alarm clip, only that MP3 is fetched over HTTPS when an alarm plays; no reminder text is ever sent with the request.</dd>
          <dt>Account</dt><dd>Not required, and not possible; there is no sign-in.</dd>
          <dt>Analytics and ads</dt><dd>None. No advertising SDK, no crash-reporting SDK, no tracking.</dd>
        </dl>
        <p>The full detail is on the <a href="/privacy">privacy policy page</a>.</p>

        <h2>Compatibility and version</h2>
        <dl class="facts">
          <dt>Platform</dt><dd>Android 8.0 and later.</dd>
          <dt>Version</dt><dd>1.0.6.</dd>
          <dt>Price</dt><dd>Free, with no ads and no in-app purchases.</dd>
          <dt>Permissions</dt><dd>Notifications, exact alarms for minute-accurate delivery, and optionally Do Not Disturb access if you want reminders during DND.</dd>
          <dt>Source</dt><dd><a href="https://github.com/owaiskhan-ash/RemindME">RemindME repository on GitHub</a></dd>
          <dt>Made by</dt><dd>Owais Khan (Just Apps), an independent studio in Mumbai, India. <a href="https://github.com/owaiskhan-ash">github.com/owaiskhan-ash</a>.</dd>
        </dl>
        """,
        "faq": [
            ("Does RemindME need an internet connection?",
             "No. Reminders are parsed and stored on the device and scheduled with Android’s alarm manager. The only network use is the optional RemindME alarm clip, which is streamed over HTTPS when an alarm plays and is not used at all if you keep the device’s default alarm sound."),
            ("Does silent mode mute a reminder?",
             "No. A due reminder plays on Android’s alarm audio stream, which silent and vibrate modes do not control. You can still lower the alarm volume by hand, and Do Not Disturb applies unless you grant the app access to it."),
            ("Which languages does it support?",
             "Seven: English, Bahasa Indonesia, Español, Português, हिन्दी, العربية with a right-to-left layout, and 简体中文. The interface, the alarm actions and the natural-language parser all follow the language you pick."),
            ("What happens if I forget to include a time?",
             "The preview asks for the missing date or time instead of guessing one. RemindME only schedules a reminder once it has an explicit time to schedule it for."),
            ("Do reminders survive a restart?",
             "Yes. Outstanding reminders are rescheduled after a reboot or an app update, so a restart does not lose them."),
            ("Is RemindME free?",
             "Yes. Free to download and use, with no ads, no subscription and no in-app purchases."),
        ],
        "software": {
            "name": "RemindME",
            "applicationCategory": "ProductivityApplication",
            "operatingSystem": "Android 8.0 and later",
            "description": "A conversational reminder app that turns natural-language phrases with a date and time into reliable Android alarm-stream alerts, with seven languages, snooze and done actions, a three-tab dock and local-only storage.",
            "image": BASE + "/assets/remindme/icon-128.png",
            "screenshot": [
                BASE + "/assets/remindme/home-780.webp",
                BASE + "/assets/remindme/previous-780.webp",
                BASE + "/assets/remindme/settings-780.webp",
            ],
            "featureList": [
                "Conversational Smart Parse for natural phrases that include a date and time",
                "Seven languages in the interface and in the parser: English, Bahasa Indonesia, Español, Português, हिन्दी, العربية with RTL, and 简体中文",
                "Plays on the Android alarm audio stream, with Snooze 10 min and Mark done notification actions",
                "Persistent three-tab dock, dark mode by default, and automatic alarm restoration after a reboot",
            ],
            "inLanguage": ["en", "id", "es", "pt", "hi", "ar", "zh-CN"],
            "softwareVersion": "1.0.6",
            "downloadUrl": "https://github.com/owaiskhan-ash/RemindME/raw/v1.0.6/release/RemindME-v1.0.6.apk",
            "sameAs": ["https://github.com/owaiskhan-ash/RemindME"],
        },
        "cta_primary": "https://github.com/owaiskhan-ash/RemindME/raw/v1.0.6/release/RemindME-v1.0.6.apk",
    },
    {
        "slug": "arabic-clock",
        "date_published": "2026-10-28",
        "name": "Arabic Clock",
        "kicker": "08 · Home Screen",
        "nav_cta": "Get the app",
        "title": "Arabic Clock: Transparent Arabic-Indic Widget | Just Apps",
        "description": "Free Android widget that shows 24-hour time in Arabic-Indic numerals on any phone, with six offline fonts, outlines and true transparency. No ads, no network.",
        "og": "og-arabic-clock.png",
        "h1": "Arabic Clock: Arabic-Indic numerals on a widget that is 100% transparent.",
        "lede": "Arabic Clock is a free Android home-screen widget that shows local 24-hour time in Arabic-Indic numerals, ٠١٢٣٤٥٦٧٨٩, even when the phone’s language is English. The numerals are drawn by the app itself, so a launcher cannot swap them for Western digits, and the widget has no background at all.",
        "answer": "<p><strong>In one line:</strong> Arabic Clock is a free, fully transparent Android clock widget that renders local 24-hour time in Arabic-Indic numerals using six bundled offline fonts, with controls for numeral width, size, colour, opacity and outline, and no internet permission.</p>",
        "cta": """          <a class="btn btn-primary" href="https://github.com/owaiskhan-ash/Arabic-Clock-For-Android-/releases/download/v2.4.0/Arabic-Clock-2.4.0.apk">Download the APK</a>
          <a class="btn btn-ghost" href="https://github.com/owaiskhan-ash/Arabic-Clock-For-Android-">Source on GitHub</a>""",
        "cta_note": "Version 2.4.0 for Android 8.0 and later. Free, signed APK from the project’s GitHub releases.",
        "shots": [
            shot("/assets/arabic-clock/widget-400.webp",
                 "Android home screen showing the 100% transparent Arabic Clock widget displaying 12:42 in Arabic-Indic numerals",
                 "The widget on a home screen: numerals only, no panel.",
                 400, 866,
                 "/assets/arabic-clock/widget-400.webp 400w, /assets/arabic-clock/widget-780.webp 780w",
                 "(max-width: 620px) 42vw, 210px"),
            shot("/assets/arabic-clock/customizer-400.webp",
                 "Arabic Clock single-screen customizer with a live checkerboard preview, an Amiri font choice and numeral width stretch",
                 "The customizer: live preview above, settings below.",
                 400, 866,
                 "/assets/arabic-clock/customizer-400.webp 400w, /assets/arabic-clock/customizer-780.webp 780w",
                 "(max-width: 620px) 42vw, 210px"),
            shot("/assets/arabic-clock/styles-400.webp",
                 "Arabic Clock stacked hours-over-minutes mode with gold numerals, a font outline and opacity controls",
                 "Stacked hours over minutes, with an outline and opacity.",
                 400, 866,
                 "/assets/arabic-clock/styles-400.webp 400w, /assets/arabic-clock/styles-780.webp 780w",
                 "(max-width: 620px) 42vw, 210px"),
        ],
        "body": """
        <h2>What it does</h2>
        <ul>
          <li><strong>A transparent widget</strong> with no panel, border or background image, so it reads as part of the wallpaper.</li>
          <li><strong>Arabic-Indic numerals</strong> in local 24-hour time, on an English-language phone as well as an Arabic one.</li>
          <li><strong>Six bundled offline fonts</strong>: Amiri, Scheherazade New, Janna LT Bold, Arslan Wessam A, 18 Khebrat Musamim and Avenir Heavy.</li>
          <li><strong>Numeral widths</strong> at natural, 15, 30, 50 or 75 percent wider, with separator dots as a separate, unstretched view.</li>
          <li><strong>Size, spacing and margins</strong> from 24 to 240 sp, including a HUGE mode that fills the space the launcher gives the widget.</li>
          <li><strong>Colour and outline</strong>: white, gold, black or any hex colour, with an optional 1 to 8 dp outline, or hollow numerals in outline-only mode.</li>
          <li><strong>Opacity from 0 to 100 percent</strong>, applied once to the combined fill and outline, on a background that never appears.</li>
        </ul>

        <h2>Why the numerals are drawn by the app</h2>
        <p>A text widget normally asks the launcher to draw text, and a launcher with an English locale can substitute
        Western digits for Arabic-Indic ones, or fall back to a font that has no Arabic-Indic glyphs at all. Arabic
        Clock avoids that by rendering the time to a transparent bitmap inside the app, with the bundled font you
        selected and real Arabic-Indic Unicode digits. What the launcher receives is an image of the clock, not a
        string it can reinterpret.</p>
        <p>The clock refreshes on a minute alarm, with a 30-minute widget-host update as a fallback, and it also
        refreshes when you open settings, when the time or time zone changes and after a reboot. On Android 12 and
        later, allowing precise clock updates through Alarms and reminders keeps that minute accurate; without it,
        Android may batch updates and the time can lag.</p>

        <h2>What it will not do</h2>
        <p>There are no alarms, stopwatches, seconds, dates, weather or per-widget profiles. The time is always local,
        always 24-hour, and settings apply to every placed instance. The widget declares both home-screen and
        keyguard categories, but that only helps on devices whose lock screen offers a third-party widget picker:
        many Android versions and manufacturers do not expose one, and the app cannot replace or restyle the built-in
        lock-screen clock.</p>
        <p>The checkerboard in the customizer preview illustrates transparency. It is never part of the widget itself.</p>

        <h2>What stays on your phone</h2>
        <dl class="facts">
          <dt>Settings</dt><dd>Font, width, size, colour, outline and opacity are stored locally and applied to every placed widget.</dd>
          <dt>Internet permission</dt><dd>Not requested. The app cannot connect to a network.</dd>
          <dt>Services</dt><dd>No foreground service, no background worker, no account and no sync.</dd>
          <dt>Analytics and ads</dt><dd>None. No advertising SDK, no crash-reporting SDK, no tracking.</dd>
        </dl>
        <p>The full detail is on the <a href="/privacy">privacy policy page</a>.</p>

        <h2>Compatibility and version</h2>
        <dl class="facts">
          <dt>Platform</dt><dd>Android 8.0 (API 26) and later, on a launcher that supports Android app widgets.</dd>
          <dt>Version</dt><dd>2.4.0.</dd>
          <dt>Price</dt><dd>Free, with no ads and no in-app purchases.</dd>
          <dt>Lock screen</dt><dd>Supported only where the device offers a third-party lock-screen widget picker.</dd>
          <dt>Source</dt><dd><a href="https://github.com/owaiskhan-ash/Arabic-Clock-For-Android-">Arabic-Clock-For-Android repository on GitHub</a></dd>
          <dt>Made by</dt><dd>Owais Khan (Just Apps), an independent studio in Mumbai, India. <a href="https://github.com/owaiskhan-ash">github.com/owaiskhan-ash</a>.</dd>
        </dl>
        """,
        "faq": [
            ("Is the widget really transparent?",
             "Yes. There is no panel, border or background image; only the numerals are drawn. The checkerboard in the customizer preview exists to show that transparency and is never part of the widget."),
            ("Why do the numerals stay Arabic-Indic on an English phone?",
             "Because the clock is rendered to a transparent bitmap inside the app, using bundled fonts and real Arabic-Indic Unicode digits. The launcher receives an image, so it cannot substitute Western digits or a fallback font."),
            ("Which fonts are included?",
             "Six, all offline: Amiri, Scheherazade New, Janna LT Bold, Arslan Wessam A, 18 Khebrat Musamim and Avenir Heavy. Each is bundled in the APK, so no font is downloaded."),
            ("Will it appear on my lock screen?",
             "Only if your device offers a third-party lock-screen widget picker. The app declares keyguard support, but many Android versions and manufacturers do not expose such a picker, and Arabic Clock cannot replace the built-in lock-screen clock."),
            ("Does Arabic Clock need an internet connection?",
             "No, and it could not use one. The app does not request the internet permission, and the clock is drawn on the device."),
            ("Is Arabic Clock free?",
             "Yes. Free to download and use, with no ads, no subscription and no in-app purchases."),
        ],
        "software": {
            "name": "Arabic Clock",
            "applicationCategory": "UtilitiesApplication",
            "operatingSystem": "Android 8.0 and later",
            "description": "A 100% transparent Android clock widget that displays local 24-hour time in Arabic-Indic numerals even on English-language phones, with six bundled offline fonts, numeral stretch, a HUGE fill mode, stacked layout, custom outlines and full-range opacity.",
            "image": BASE + "/assets/arabic-clock/icon-512.png",
            "screenshot": [
                BASE + "/assets/arabic-clock/widget-780.webp",
                BASE + "/assets/arabic-clock/customizer-780.webp",
                BASE + "/assets/arabic-clock/styles-780.webp",
            ],
            "featureList": [
                "100% transparent home-screen clock widget in Arabic-Indic numerals",
                "Renders the numerals inside the app, so English-language launchers cannot substitute fallback digits",
                "Six bundled offline fonts: Amiri, Scheherazade New, Janna LT Bold, Arslan Wessam A, 18 Khebrat Musamim and Avenir Heavy",
                "Numeral width stretch, 24 to 240 sp sizing and a HUGE fill mode",
                "Stacked hours over minutes, full-range opacity and hollow or solid outlines",
                "No internet permission, no ads, no accounts and local-only settings",
            ],
            "inLanguage": ["en", "ar"],
            "softwareVersion": "2.4.0",
            "downloadUrl": "https://github.com/owaiskhan-ash/Arabic-Clock-For-Android-/releases/download/v2.4.0/Arabic-Clock-2.4.0.apk",
            "sameAs": ["https://github.com/owaiskhan-ash/Arabic-Clock-For-Android-"],
        },
        "cta_primary": "https://github.com/owaiskhan-ash/Arabic-Clock-For-Android-/releases/download/v2.4.0/Arabic-Clock-2.4.0.apk",
    },
]

TEMPLATE = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{base}/{slug}">
<meta name="theme-color" content="#064B4D">
<meta name="color-scheme" content="dark light">
<meta property="og:type" content="article">
<meta property="og:url" content="{base}/{slug}">
<meta property="og:site_name" content="Just Apps">
<meta property="og:locale" content="en_IN">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{base}/assets/og/{og}">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{name} | Just Apps">
<meta property="article:published_time" content="{date_published}">
<meta property="article:modified_time" content="{date_modified}">
<meta name="author" content="Owais Khan">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{base}/assets/og/{og}">
<meta name="twitter:image:alt" content="{name} | Just Apps">
<link rel="icon" type="image/png" sizes="96x96" href="/favicon-96x96.png">
<link rel="icon" href="/favicon.ico" sizes="16x16 32x32 48x48">
<link rel="icon" type="image/svg+xml" href="/assets/just-apps-icon.svg">
<link rel="apple-touch-icon" sizes="180x180" href="/assets/just-apps-icon-180.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/assets/fonts/plus-jakarta-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/instrument-serif-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/styles.css">
<script src="/theme.js"></script>
<script type="application/ld+json">
{jsonld}
</script>
</head>
<body>

<a class="skip-link" href="#main">Skip to content</a>

<div class="page-shell">
<div class="leather-stage leather-stage-sub" aria-hidden="true">
{stage_sub}
</div>
<div class="leather-stage leather-stage-bot" aria-hidden="true">
{stage_bot}
</div>

<header class="nav">
  <div class="wrap nav-inner">
    <a class="nav-brand" href="/" aria-label="Just Apps home">
      <img class="nav-logo" src="/assets/just-apps-icon-64.png" srcset="/assets/just-apps-icon-64.png 1x, /assets/just-apps-icon-128.png 2x, /assets/just-apps-icon-256.png 3x" width="34" height="34" alt="" decoding="async">
      <span class="nav-title">JUST APPS</span>
    </a>
    <nav class="nav-links" id="primary-nav" aria-label="Primary">
      <a href="/#apps">Apps</a>
      <a href="/#features">Our approach</a>
      <a href="/#faq">FAQ</a>
      <a class="nav-cta" href="/#apps">Explore apps</a>
    </nav>
    <button class="nav-toggle" type="button" data-nav-toggle aria-expanded="false" aria-controls="primary-nav" aria-label="Open menu">
      <svg class="icon-menu" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true" focusable="false">
        <path d="M4 7h16M4 12h16M4 17h16"></path>
      </svg>
      <svg class="icon-close" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true" focusable="false">
        <path d="M6 6l12 12M18 6L6 18"></path>
      </svg>
    </button>
    <button class="theme-toggle" type="button" data-theme-toggle aria-pressed="false" aria-label="Switch to light mode" title="Switch to light mode">
      <svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" aria-hidden="true" focusable="false">
        <circle cx="12" cy="12" r="4.2"></circle>
        <path d="M12 2.6v2.1M12 19.3v2.1M4.2 4.2l1.5 1.5M18.3 18.3l1.5 1.5M2.6 12h2.1M19.3 12h2.1M4.2 19.8l1.5-1.5M18.3 5.7l1.5-1.5"></path>
      </svg>
      <svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">
        <path d="M20.6 14.2A8.6 8.6 0 0 1 9.8 3.4a8.6 8.6 0 1 0 10.8 10.8Z"></path>
      </svg>
    </button>
  </div>
</header>

<main class="wrap app-page" id="main">
  <div class="doc-card">

  <nav class="breadcrumb" aria-label="Breadcrumb">
    <a href="/">Just Apps</a>
    <span class="sep" aria-hidden="true">/</span>
    <a href="/#apps">Apps</a>
    <span class="sep" aria-hidden="true">/</span>
    <span aria-current="page">{name}</span>
  </nav>

  <p class="app-kicker">{kicker}</p>
  <h1>{h1}</h1>
  <p class="lede">{lede}</p>

  <div class="answer">
{answer}
  </div>

  <div class="cta-row">
{cta}
  </div>
  <p class="cta-note">{cta_note}</p>

  <div class="shots">
{shots}
  </div>

{body}
  <p class="updated">Last reviewed {date_long} by Owais Khan.</p>

  <h2>Common questions</h2>
  <div class="faq-list">
{faq}
  </div>

  <h2>Other apps in the collection</h2>
  <div class="related">
{related}
  </div>
  <p style="margin-top:26px"><a href="/">← Back to all eight apps</a></p>

  </div>
</main>

<footer>
  <div class="wrap foot-inner">
    <div class="foot-brand">
      <img class="nav-logo nav-logo--footer" src="/assets/just-apps-icon-64.png" srcset="/assets/just-apps-icon-64.png 1x, /assets/just-apps-icon-128.png 2x" width="28" height="28" alt="" loading="lazy" decoding="async">
      <span>{name} · one of eight free Just Apps apps · no ads, no accounts, no tracking</span>
    </div>
    <nav class="foot-links" aria-label="Footer">
      <a href="/">Apps</a>
      <a href="/privacy">Privacy</a>
      <a href="https://github.com/owaiskhan-ash">GitHub</a>
    </nav>
  </div>
</footer>
</div>

<script src="/nav.js"></script>
<script src="/motion.js"></script>
</body>
</html>
"""


def build_jsonld(app):
    url = f"{BASE}/{app['slug']}"
    software = {
        "@type": "SoftwareApplication",
        "@id": url + "#software",
        **app["software"],
    }
    # Defaults, so a per-app value (RemindME's seven languages, Arabic Clock's
    # en/ar) survives instead of being flattened to "en" by the template.
    software.setdefault("url", url)
    software.setdefault("isAccessibleForFree", True)
    software.setdefault("inLanguage", "en")
    software.setdefault(
        "offers", {"@type": "Offer", "price": 0, "priceCurrency": "INR"})
    software.setdefault("publisher", {"@id": BASE + "/#organization"})
    graph = [
        # Full publisher/web nodes so a page fetched on its own (as answer
        # engines do) resolves the entity instead of dangling at an @id that
        # only exists on the home page. Values mirror ORGANIZATION/WEBSITE.
        ORGANIZATION,
        WEBSITE,
        {
            "@type": "WebPage",
            "@id": url + "#webpage",
            "url": url,
            "name": app["title"],
            "description": app["description"],
            "isPartOf": {"@id": BASE + "/#website"},
            "about": {"@id": url + "#software"},
            "primaryImageOfPage": {"@id": url + "#primaryimage"},
            "author": AUTHOR,
            "inLanguage": "en",
            "datePublished": app.get("date_published", DATE_PUBLISHED),
            "dateModified": DATE_MODIFIED,
            "breadcrumb": {"@id": url + "#breadcrumb"},
            # AISO: name the passages an answer engine may quote or read
            # aloud, so the lede and the one-line answer are never the
            # paragraphs it has to guess at.
            "speakable": {
                "@type": "SpeakableSpecification",
                "cssSelector": [".app-page h1", ".app-page .lede",
                                ".app-page .answer p"],
            },
        },
        {
            "@type": "ImageObject",
            "@id": url + "#primaryimage",
            "url": f"{BASE}/assets/og/{app['og']}",
            "contentUrl": f"{BASE}/assets/og/{app['og']}",
            "width": 1200,
            "height": 630,
        },
        {
            "@type": "BreadcrumbList",
            "@id": url + "#breadcrumb",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Just Apps", "item": BASE + "/"},
                {"@type": "ListItem", "position": 2, "name": "Apps", "item": BASE + "/#apps"},
                {"@type": "ListItem", "position": 3, "name": app["name"], "item": url},
            ],
        },
        software,
        {
            "@type": "FAQPage",
            "@id": url + "#faq",
            "isPartOf": {"@id": url + "#webpage"},
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {"@type": "Answer", "text": a},
                }
                for q, a in app["faq"]
            ],
        },
    ]
    return json.dumps({"@context": "https://schema.org", "@graph": graph},
                      indent=2, ensure_ascii=False)


def build_related(app):
    out = []
    for other in APPS:
        if other["slug"] == app["slug"]:
            continue
        out.append(
            f'    <a href="/{other["slug"]}"><strong>{other["name"]}</strong>'
            f'<span>{other["kicker"].split("· ")[1].capitalize()}</span></a>'
        )
    return "\n".join(out)


def main():
    with open(STAGES_PATH, "r", encoding="utf-8") as sf:
        stages = json.load(sf)

    for app in APPS:
        faq_html = "\n".join(
            f"    <details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>"
            for q, a in app["faq"]
        )
        page = TEMPLATE.format(
            base=BASE,
            slug=app["slug"],
            name=app["name"],
            kicker=app["kicker"],
            title=app["title"],
            description=app["description"],
            og=app["og"],
            h1=app["h1"],
            lede=app["lede"],
            answer=app["answer"],
            cta=app["cta"],
            cta_note=app["cta_note"],
            shots="\n".join("          " + s for s in app["shots"]),
            body=app["body"].strip("\n"),
            faq=faq_html,
            date_long=long_date(DATE_MODIFIED),
            related=build_related(app),
            jsonld=build_jsonld(app),
            date_published=app.get("date_published", DATE_PUBLISHED),
            date_modified=DATE_MODIFIED,
            stage_sub=stages["sub"],
            stage_bot=stages["bot"],
        )
        page = "\n".join(line.rstrip() for line in page.splitlines()) + "\n"
        os.makedirs(ROOT, exist_ok=True)
        path = os.path.join(ROOT, app["slug"] + ".html")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(page)
        print(f"wrote {os.path.relpath(path, ROOT)} ({len(page)} bytes)")


if __name__ == "__main__":
    main()
