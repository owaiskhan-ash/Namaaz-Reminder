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

BASE = "https://www.justsimpleapps.online"
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs")
STAGES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_stages.json")

# Bump whenever any copy in this file changes; it feeds WebPage.dateModified
# and should agree with the <lastmod> for the same URL in docs/sitemap.xml.
DATE_MODIFIED = "2026-10-25"

# The publisher entity, defined here so every app page resolves it on its own.
# The same @ids and field values are used on docs/index.html; keep them equal.
ORGANIZATION = {
    "@type": "Organization",
    "@id": BASE + "/#organization",
    "name": "Just Apps",
    "alternateName": "Just Simple Apps",
    "url": BASE + "/",
    "description": "A small studio making free, quiet Android apps for everyday life: prayer times, screen breaks, step goals, water reminders, conversational reminders, subscriptions and childhood vaccine records.",
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
        "https://github.com/owaiskhan-ash/ScreenTime-Reminder",
        "https://github.com/owaiskhan-ash/Subscription-Tracker",
        "https://github.com/owaiskhan-ash/vaccine-Tracker",
        "https://github.com/owaiskhan-ash/Steps-Reminder",
        "https://github.com/owaiskhan-ash/Water-Reminder",
        "https://github.com/owaiskhan-ash/RemindME",
    ],
}
WEBSITE = {
    "@type": "WebSite",
    "@id": BASE + "/#website",
    "url": BASE + "/",
    "name": "Just Apps",
    "alternateName": "Just Simple Apps",
    "description": "Free, ad-free apps for prayer times, screen breaks, step goals, water reminders, conversational reminders, subscriptions and vaccine records.",
    "publisher": {"@id": BASE + "/#organization"},
    "inLanguage": "en",
}
AUTHOR = {
    "@type": "Person",
    "name": "Owais Khan",
    "url": "https://github.com/owaiskhan-ash",
}


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
        "cta": """          <span class="pill"><span class="dot"></span>Coming to Google Play</span>
          <a class="btn btn-ghost" href="/privacy">Privacy policy</a>""",
        "cta_note": "Version 1.6.2 for Android 7.0 and later. There is no public download while the app is being prepared for the Play Store.",
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
          <dt>Version</dt><dd>1.6.2 (versionCode 10).</dd>
          <dt>Price</dt><dd>Free, with no in-app purchases.</dd>
          <dt>Account</dt><dd>Not required, and not possible; there is no sign-in.</dd>
          <dt>Made by</dt><dd>Owais Khan (Just Apps), an independent studio in Mumbai, India. <a href="https://github.com/owaiskhan-ash">github.com/owaiskhan-ash</a>.</dd>
        </dl>
        """,
        "faq": [
            ("Does Namaaz Reminder need an internet connection?",
             "Only to fetch the timings. Once a schedule has been downloaded it is cached on the phone, so the main screen and the countdown keep working offline. Reminders are scheduled on the device and need no connection at all."),
            ("Does it use my GPS location?",
             "No. The app does not request Android’s location permission and never reads GPS, Wi-Fi or cell-tower position. You choose a city by name, and that name is the only location information involved."),
            ("When do the reminders fire?",
             "By default five minutes after the prayer time, which is when the adhan has ended and the salah begins. The offset is adjustable in Settings down to zero, and individual prayers can be muted."),
            ("Which calculation method is used?",
             "Method 1, the University of Islamic Sciences, Karachi convention, is the default because it is the most common choice in India. Other methods can be selected in Settings, and any single prayer time can be corrected by hand for the day."),
            ("Is it free?",
             "Yes. Namaaz Reminder is free, has no ads, no subscriptions and no in-app purchases, and it does not ask you to create an account."),
            ("Which cities are supported?",
             "Any city you can name, with Delhi as the default. The request is made against India as the country and the API returns the city’s own time zone."),
            ("Is Namaaz Reminder on Google Play?",
             "Not yet. The app is being prepared for the Play Store, and this page shows the current status. It will be free when the listing goes live, with no ads and no account."),
        ],
        "software": {
            "name": "Namaaz Reminder",
            "applicationCategory": "LifestyleApplication",
            "operatingSystem": "Android 7.0 and later",
            "softwareVersion": "1.6.2",
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
        },
        "cta_primary": None,
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
        "cta": """          <a class="btn btn-primary" href="https://github.com/owaiskhan-ash/ScreenTime-Reminder/releases/latest">Download the APK</a>
          <a class="btn btn-ghost" href="https://github.com/owaiskhan-ash/ScreenTime-Reminder">Source on GitHub</a>""",
        "cta_note": "Version 1.2.3 for Android 8.0 and later. Free, signed APK from the project’s GitHub releases.",
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
            ("Does it need an internet connection?",
             "No, and it could not use one. The app does not request the internet permission, so it has no technical way to send or receive data."),
            ("What permission does it need?",
             "Usage access, which is Android’s name for permission to see which app is in the foreground and for how long. Without it the app has nothing to measure."),
            ("Does it keep a streak or score?",
             "No. There are no streaks, scores, badges or daily targets. You get a running count and a seven-day history, and that is all."),
            ("Is it really free?",
             "Yes. It is free to download and use, with no ads, no subscription and no in-app purchases."),
        ],
        "software": {
            "name": "Screen Time Reminder",
            "applicationCategory": "HealthApplication",
            "operatingSystem": "Android 8.0 and later",
            "description": "Counts continuous phone use and sends one gentle break reminder when a session runs long, with a seven-day history. Free, ad-free, and without the internet permission.",
            "softwareVersion": "1.2.3",
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
            "downloadUrl": "https://github.com/owaiskhan-ash/ScreenTime-Reminder/releases/latest",
            "sameAs": ["https://github.com/owaiskhan-ash/ScreenTime-Reminder"],
        },
        "cta_primary": "https://github.com/owaiskhan-ash/ScreenTime-Reminder/releases/latest",
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
        "cta": """          <a class="btn btn-primary" href="https://github.com/owaiskhan-ash/Subscription-Tracker/releases/latest">Download the APK</a>
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
            ("Does it work offline?",
             "Yes. The app is built to work without a connection; subscriptions and totals are stored on the device."),
            ("Will it detect subscriptions automatically?",
             "No. Entries are added by hand, on purpose; automatic detection would mean reading your messages or connecting to your bank, and the app does neither."),
            ("Is it free?",
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
            "downloadUrl": "https://github.com/owaiskhan-ash/Subscription-Tracker/releases/latest",
            "sameAs": ["https://github.com/owaiskhan-ash/Subscription-Tracker"],
        },
        "cta_primary": "https://github.com/owaiskhan-ash/Subscription-Tracker/releases/latest",
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
        "cta": """          <a class="btn btn-primary" href="https://github.com/owaiskhan-ash/vaccine-Tracker/releases/latest">Download the app</a>
          <a class="btn btn-ghost" href="https://github.com/owaiskhan-ash/vaccine-Tracker">Source on GitHub</a>""",
        "cta_note": "Free. Available for Android and on the web. Distributed from the project’s GitHub releases.",
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
            ("Is it free?",
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
            "downloadUrl": "https://github.com/owaiskhan-ash/vaccine-Tracker/releases/latest",
            "sameAs": ["https://github.com/owaiskhan-ash/vaccine-Tracker"],
        },
        "cta_primary": "https://github.com/owaiskhan-ash/vaccine-Tracker/releases/latest",
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
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{base}/assets/og/{og}">
<meta name="twitter:image:alt" content="{name} | Just Apps">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" type="image/svg+xml" href="/assets/just-apps-icon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/just-apps-icon-32.png">
<link rel="icon" type="image/png" sizes="64x64" href="/assets/just-apps-icon-64.png">
<link rel="apple-touch-icon" sizes="180x180" href="/assets/just-apps-icon-180.png">
<link rel="manifest" href="/site.webmanifest">
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

  <h2>Common questions</h2>
  <div class="faq-list">
{faq}
  </div>

  <h2>Other apps in the collection</h2>
  <div class="related">
{related}
  </div>
  <p style="margin-top:26px"><a href="/">← Back to all seven apps</a></p>

  </div>
</main>

<footer>
  <div class="wrap foot-inner">
    <div class="foot-brand">
      <img class="nav-logo nav-logo--footer" src="/assets/just-apps-icon-64.png" srcset="/assets/just-apps-icon-64.png 1x, /assets/just-apps-icon-128.png 2x" width="28" height="28" alt="" loading="lazy" decoding="async">
      <span>{name} · Free · no ads · no tracking</span>
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
        "url": url,
        "isAccessibleForFree": True,
        "inLanguage": "en",
        "offers": {"@type": "Offer", "price": 0, "priceCurrency": "INR"},
        "publisher": {"@id": BASE + "/#organization"},
    }
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
            "dateModified": DATE_MODIFIED,
            "breadcrumb": {"@id": url + "#breadcrumb"},
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
            related=build_related(app),
            jsonld=build_jsonld(app),
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
