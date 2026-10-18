# Pre-publish checklist

Audit of build **1.3.1** (`versionCode` 5) before the first store upload.
Android Lint: **0 errors**, 44 warnings — 33 dependency/plugin version
suggestions, 9 KTX style hints, 1 target-SDK notice.

## Fixed in this pass

| Area | Problem | Fix |
| --- | --- | --- |
| Offline cache | A cached schedule kept the date it was fetched, so it showed an old Gregorian date above today's timings | Date line now comes from the device clock; the Hijri date is only shown when the payload really describes today |
| Notifications | Settings said reminders come **before** each prayer; the offset is applied *after* it | Copy now says "at or after" |
| Notifications | Turning **Enable Reminders** off left posted reminders in the shade | Also cancels the app's notifications |
| Notifications | Every sound/vibration change created another channel and never removed the old one | Superseded channels are deleted |
| Notification test | "Test notification sent!" was shown even with notifications denied on Android 13+ | Explains that notifications are blocked |
| Boot / alarm re-arm | A blocking OkHttp call was bounded with `withTimeoutOrNull`, which cannot interrupt a socket read; a slow network could outlive the broadcast window | Dedicated 3 s socket timeouts |
| Custom times | `clearCustomPrayerTime` was unreachable, so a custom time could never be undone; the documented `CUSTOM` badge did not exist | Long press → **Reset to calculated**; badge added |
| Backup | Auto Backup uploaded the downloaded Azaan audio (up to 40 MB) | Only the settings are backed up |
| Resources | Template `colors.xml`, unused `channel_name`, bitmap drawables in the densityless folder (decoded at mdpi scale) | Removed; bitmaps moved to `drawable-xxxhdpi` |
| Dead code | `ExampleUnitTest` (2 + 2 == 4), unused `CHANNEL_ID`, always-true `SDK_INT >= M` check, redundant activity label | Removed |
| Docs | README claimed DataStore, notification groups, prayer-time timestamps, automatic pruning and a lead-time offset | Rewritten to match the code |

## Must be decided before the store upload

1. **Package name** — currently `com.aistudio.namaztimes.vxqpl`. The
   `applicationId` is permanent once published; change it now if a different
   name is wanted.
2. **Signing key** — CI signs the release build with the *committed debug
   key* (`debug.keystore`, password `android`), which is fine for side-loading
   but must not be the upload key for a store listing. Generate a private
   keystore, store it as a secret, and set `KEYSTORE_PATH`, `STORE_PASSWORD`
   and `KEY_PASSWORD`. Enrol in **Play App Signing**.
3. **Upload format** — Play accepts the **AAB** now produced by CI
   (`NamaazReminder-<version>-release.aab`), not the APK.
4. **Exact alarms** — `SCHEDULE_EXACT_ALARM` is a restricted permission. Fill
   in the *Alarms & reminders* declaration in the Play Console (prayer times
   are the core function) and make sure the in-app rationale is visible.
5. **Data safety** — the app sends the selected city name to
   `api.aladhan.com`, and downloads the Azaan audio from a public bucket.
   Declare this, and add a privacy policy URL.
6. **Azaan auto-download** — the Madinah Azaan (public Supabase bucket) is
   downloaded on first launch and saved to the public Ringtones collection.
   Decide whether that should stay automatic or wait for a tap.
7. **Reminder default** — reminders fire 5 minutes *after* the prayer by
   default (0 = at adhan). Confirm that is the intended behaviour.

## Nice to have, not blocking

- 33 dependency upgrades suggested by lint (AGP 9.4.1, Gradle 9.8.1,
  Compose/lifecycle bumps). Test on a branch rather than with the release.
- 9 `UseKtx` style hints (`String.toUri`, `SharedPreferences.edit {}`).
- R8/minification is off for the release build; enabling it would shrink the
  APK but needs its own test pass.
- The notification small icon is still the mosque vector, so it does not match
  the new NR launcher mark.
- All UI strings are inline in Compose, so the app is English-only.
- `metadata.json` and `.env.example` still carry AI Studio/Gemini scaffolding
  that this app does not use.
