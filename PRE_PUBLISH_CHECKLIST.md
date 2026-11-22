# Pre-publish checklist

Audit of build **1.3.1** (`versionCode` 5) before the first store upload.
Android Lint: **0 errors**, 44 warnings; 33 dependency/plugin version
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

1. **Package name**: currently `com.aistudio.namaztimes.vxqpl`. The
   `applicationId` is permanent once published; change it now if a different
   name is wanted.
2. **Signing key**: *done*: a dedicated upload key exists
   (`namaaz-upload-key.jks`, alias `upload`, PKCS12, 4096-bit RSA, valid to
   2054). Add it to the repository as the `KEYSTORE_BASE64`,
   `STORE_PASSWORD` and `KEY_PASSWORD` secrets; the workflow then builds and
   publishes a `.aab` signed with it. Until the secrets exist the workflow
   keeps signing the APKs with the committed debug key and builds **no**
   bundle, so a throwaway key can never become the Play upload key.
   Enrol in **Play App Signing** on the first upload.
3. **Upload format**: Play accepts the **AAB** now produced by CI
   (`NamaazReminder-<version>-release.aab`), not the APK.
4. **Exact alarms**: `SCHEDULE_EXACT_ALARM` is a restricted permission. Fill
   in the *Alarms & reminders* declaration in the Play Console (prayer times
   are the core function) and make sure the in-app rationale is visible.
5. **Data safety**: the app sends the selected city name to
   `api.aladhan.com`, and downloads the Azaan audio from a public bucket.
   Declare this, and add a privacy policy URL.
6. **Azaan audio**: *resolved in 1.7.4*: the audio now ships inside the APK
   and is never downloaded. The public Supabase bucket that used to serve it
   has been deleted (its hostname no longer resolves), which previously broke
   the CI build outright.
7. **Reminder default**: reminders fire 5 minutes *after* the prayer by
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

---

# Audit of 1.7.4 (`versionCode` 15) — 22 November 2026

Second full read of the app before the first Play upload: every Kotlin file, the
manifest, resources, Gradle/version catalog, CI workflow, tests and the landing
pages. Version bumped to **1.7.4 / 15** so this build can be uploaded over
1.7.3.

## Fixed in this pass

| Area | Problem | Fix |
| --- | --- | --- |
| Next prayer | `PrayerScheduleCustomizer` picked the first future prayer **in list order**. A custom time that moved a prayer past another (e.g. Dhuhr edited to 23:50) made the countdown target the wrong prayer | The earliest future primary prayer by target time is chosen; test added |
| Alarms after clock change | Alarms are absolute `RTC_WAKEUP` times. Changing the clock or time zone (including DST) left every reminder at the old wall-clock time until the app was opened | `BootReceiver` now also re-arms on `TIME_SET`, `TIMEZONE_CHANGED` and `MY_PACKAGE_REPLACED` |
| Azaan playback | A failed `MediaPlayer` setup (bad custom file, unsupported codec) leaked an unreleased native player on every reminder | The half-initialised player is released before falling back |
| City switching | A slow in-flight schedule request could land after the user picked another city and overwrite it | `loadTimings` cancels the previous load |
| Countdown | After the last prayer the countdown could sit frozen on a stale positive value while the refresh was in flight | Shows `00h 00m 00s` immediately and refreshes |
| Settings robustness | A corrupted/hand-edited preference (empty city, unknown theme, negative offset) went straight into API calls and alarm maths | Values are validated/clamped on load (offset 0–120, known theme, non-empty city) |
| API parsing | `Calendar.set()` silently rolls over invalid times (`25:99` became the next day), producing a bogus alarm | Out-of-range hours/minutes are rejected and fall back to 12:00 |
| Test reminder | The test notification always claimed the Madinah Azaan stream was active, even with sound off or no sound selected | Message reflects the actual state |
| Prayer list | `LazyColumn` used positional keys while the list changes with the schedule | Stable `PrayerType` keys |
| Build/CI | The versioned release did not attach the `.aab`; release notes always claimed the release APK is debug-key signed | `.aab` attached when built; notes now describe the real signing key and state when no upload key is configured |
| Repo hygiene | `*.jks`/`*.keystore` and the CI-downloaded `res/raw/` MP3 could be committed | Ignored (the debug key stays tracked) |
| Version strings | README, landing page, privacy page, `llms.txt`, sitemap and JSON-LD still pointed at 1.7.3 | All at 1.7.4 / `versionCode` 15, dates moved to 2026-11-22 |
| Dependencies | `okhttp` 4.10.0 (2022) | 4.12.0 |
| Azaan audio (blocker) | The default Madinah Azaan was downloaded at runtime and fetched by CI from `oxtqzqynhtybrgushmjp.supabase.co`. That project has been deleted, so **the CI build failed outright** and a fresh install could not get the audio | The app no longer makes that request (audio is APK-bundled, playback already fell back to the device alarm tone); CI recovers the same file from the previous release APK and warns instead of failing when it cannot |

## Still required in the Play Console (cannot be done from the repo)

1. **Upload key**: the repository has **no** `KEYSTORE_BASE64` secret (CI keeps
   building debug-key APKs and no `.aab`). Create the key once, keep the `.jks`
   somewhere safe and add three secrets:

   ```bash
   keytool -genkeypair -v -keystore namaaz-upload-key.jks -storetype PKCS12 \
     -storepass <STORE_PASSWORD> -keypass <KEY_PASSWORD> -alias upload \
     -keyalg RSA -keysize 4096 -validity 10000 \
     -dname "CN=Namaaz Reminder, O=Namaaz, L=Mumbai, ST=Maharashtra, C=IN"
   base64 -w0 namaaz-upload-key.jks   # -> KEYSTORE_BASE64
   ```

   Then `Settings → Secrets and variables → Actions`: `KEYSTORE_BASE64`,
   `STORE_PASSWORD`, `KEY_PASSWORD`. The next CI run publishes
   `NamaazReminder-1.7.4-release.aab`; enrol in **Play App Signing** with it.
2. **App content**: Alarms & reminders declaration (`SCHEDULE_EXACT_ALARM`),
   Data safety (city name to `api.aladhan.com`, no audio download, no
   accounts/analytics/ads/location), privacy policy URL
   (`https://github.com/owaiskhan-ash/Namaaz-Reminder/blob/main/PRIVACY.md`),
   content rating, target audience, ads = none.
3. **Store listing**: the 512×512 icon and three 1080×1920 phone screenshots
   are in `store-listing/`; a feature graphic (1024×500) still has to be made.
