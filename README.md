# Namaaz Reminder

A clean, minimal, monochrome **prayer times & reminder app for India**.

- Live countdown to the next prayer, with a card per prayer (Fajr, Dhuhr, Asr, Maghrib, Isr).
- City picker and calculation method selection, backed by the [Aladhan](https://aladhan.com) API.
- Offline cache: the last successful schedule is stored locally and re-anchored to the current day.
- Notifications for upcoming prayer times, with exact alarms (Android 12+) and a boot receiver that
  re-arms the schedule after a restart.
- Light / dark / system theme, and a settings sheet for muted prayers, reminder lead time and
  calculation method.

Current version: **1.2** (`versionCode` 3).

## Getting the APKs

Every push to `main` or an `arena/**` branch runs the **Android CI** workflow, which produces two
signed APKs:

| Build | What it is | Notes |
| --- | --- | --- |
| `NamaazReminder-<version>-debug.apk` | Debug build | Includes Compose tooling; signed with the standard Android debug key. |
| `NamaazReminder-<version>-release.apk` | Release build | Release variant, minification off, signed with the same certificate, so it upgrades the debug build in place. |

They are available in three places:

1. **Actions artifacts** — every run of *Android CI* uploads an `NamaazReminder-apks` artifact.
2. **The rolling `apk-latest` release** — <https://github.com/owaiskhan-ash/Namaaz-Reminder/releases/tag/apk-latest>
   always holds the newest pair of APKs.
3. **The `apk-builds` branch** — the same APKs are mirrored into `apk-builds/` on that branch, so
   they can be downloaded straight from the branch page.

Install over ADB with:

```bash
adb install -r NamaazReminder-1.2-release.apk
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
`app/build.gradle.kts`. Provide it through the environment:

| Variable | Meaning |
| --- | --- |
| `KEYSTORE_PATH` | Path to the keystore containing the `upload` alias. Defaults to `./my-upload-key.jks`. |
| `STORE_PASSWORD` | Keystore password. |
| `KEY_PASSWORD` | Key password. |

CI derives the `upload` alias from the committed, publicly known `debug.keystore`, so the release
APK keeps a stable signature across builds. For a Play Store upload, point `KEYSTORE_PATH` at your
own upload key instead.

## Project layout

```
app/src/main/java/com/example/
├── MainActivity.kt                  # Compose entry point, notification channel setup
├── data/
│   ├── local/PreferencesManager.kt   # DataStore-backed settings + cached schedule
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

Each prayer reminder stays a separate notification — the system never bundles the daily
reminders into one merged group:

- every prayer gets its own notification id **and** its own group, so a Fajr reminder never
  disappears into a stack of "5 notifications",
- the reminder carries the prayer time as its timestamp (not the moment it happened to be
  posted), the city as its subtitle and mentions the next prayer,
- reminders posted on an earlier day are pruned automatically, so the shade does not fill up
  with stale, identical looking reminders,
- turning **Enable Reminders** off also clears the reminders that are already in the shade,
- sound and vibration live in separate channels (`Prayer Reminders`, `Prayer Reminders (Sound
  only)`, `Prayer Reminders (Azaan)`, `Prayer Reminders (Silent)`) — from Android 8.0
  the system reads both from the channel, not from the individual notification, so a single
  channel cannot honour the sound / vibration toggles.

## Azaan (reminder sound)

The reminder can play a full azaan instead of the short system sound:

- the audio is **not** shipped inside the APK — it is fetched from the public asset bucket the
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
- the times survive a restart and can be removed again with **RESET** in the same dialog.

## Permissions

`INTERNET`, `ACCESS_NETWORK_STATE` (schedule fetch), `POST_NOTIFICATIONS` (Android 13+ reminders),
`VIBRATE`, `RECEIVE_BOOT_COMPLETED` (re-arm alarms after reboot) and `SCHEDULE_EXACT_ALARM`
(Android 12+ precise prayer alarms — granted in-app on first launch).
