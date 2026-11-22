# Privacy policy — Namaaz Reminder

Last updated 22 November 2026 · applies to Namaaz Reminder 1.7.4 and later
(package `com.aistudio.namaztimes.vxqpl`).

**The short version.** Namaaz Reminder has no accounts, no analytics, no
advertising and no tracking. It does not request your location. The only thing
it sends over the network is the name of the city you picked, so a prayer-time
service can return timings for that city.

## Information we collect

We do not collect, store, sell or share any personal information. The app
contains no analytics SDK, no crash-reporting SDK, no advertising SDK and no
social login.

## Location

Namaaz Reminder does **not** request the Android location permission and never
reads your GPS, network or cell-tower position. You choose your city by name
from a list or by typing it. That city name is the only location information
the app has.

## Network requests

To fetch prayer times, the app sends the city name and the selected calculation
method over HTTPS to the Aladhan prayer-times API:

- `api.aladhan.com` receives the city name, the country (India) and the
  calculation method number, and returns the day's timings. No device
  identifier, account or advertising ID is attached.
- The Madinah Azaan audio is bundled inside the app package. It is not
  downloaded, and no request is made to any audio host.

Prayer-time requests are ordinary HTTPS requests. As with any web request, the
receiving server can see your IP address and the time of the request; we do not
log, retain or correlate them, and we do not control that third party. Their
own policies apply to what they receive.

## What is stored on your device

- **Settings** covers city, calculation method, reminder timing, sound and
  vibration choices, and theme. Stored in the app's private storage
  (`namaz_times_prefs`) and never uploaded.
- **Offline cache** holds the timings for the current day, so the screen still
  works without a connection.
- **Azaan audio** you import yourself is copied into the app's own storage; the
  bundled Madinah Azaan stays inside the installed package.

Uninstalling the app removes its private storage and cache. A custom audio file
you imported is removed with it.

## Notifications

Reminders are scheduled locally on your device with Android's alarm manager. To
do this the app asks for notification permission, the ability to schedule exact
alarms, and permission to restore reminders after a reboot. Notification content
is generated on the device; nothing is sent to a push service.

## Backups

Android's backup can copy your app settings so a new phone restores your city
and preferences. The prayer-time cache is not included in backups.

## Children

The app is suitable for all ages, contains no advertising and collects no data
from anyone, including children.

## Your choices

- Change or clear your city at any time from the city picker.
- Turn reminders off, or clear the offline cache, from Settings.
- Remove a custom Azaan from Settings.
- Uninstall the app to remove everything it stores.

## Changes to this policy

If a future version changes how the app handles data, this file will be updated
before that version is published, and the date at the top will change.

## Contact

Questions about this policy can be raised at
[the owaiskhan-ash GitHub profile](https://github.com/owaiskhan-ash) or in
[the Namaaz-Reminder repository](https://github.com/owaiskhan-ash/Namaaz-Reminder).
