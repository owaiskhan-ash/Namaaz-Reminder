# Namaaz Reminder

A clean, minimal, monochrome **prayer times & reminder app for India**.

- Live countdown to the next prayer, with a card per prayer (Fajr, Dhuhr, Asr, Maghrib, Isr).
- City picker and calculation method selection, backed by the [Aladhan](https://aladhan.com) API.
- Offline cache: the last successful schedule is stored locally and re-anchored to the current day.
- Notifications for upcoming prayer times, with exact alarms (Android 12+) and a boot receiver that
  re-arms the schedule after a restart.
- Light / dark / system theme, and a settings sheet for muted prayers, reminder lead time and
  calculation method.

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
adb install -r NamaazReminder-1.0-release.apk
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
│   └── repository/PrayerRepository.kt# Aladhan API + offline cache fallback
├── notification/
│   ├── AlarmRescheduler.kt          # Re-arms exact alarms
│   └── PrayerNotificationManager.kt # Channels, reminders, permission prompts
├── receiver/                        # Boot + prayer alarm broadcast receivers
└── ui/                              # Screen, view model, components, theme
```

## Permissions

`INTERNET`, `ACCESS_NETWORK_STATE` (schedule fetch), `POST_NOTIFICATIONS` (Android 13+ reminders),
`VIBRATE`, `RECEIVE_BOOT_COMPLETED` (re-arm alarms after reboot) and `SCHEDULE_EXACT_ALARM`
(Android 12+ precise prayer alarms — granted in-app on first launch).
