# Signed artifacts

Downloadable copies of the Play upload bundle. The file in this folder is
signed with the Namaaz upload key (certificate
`F9:7B:FE:10:FD:51:D6:EA:6E:5C:4A:B8:A2:90:19:8B:63:BB:F5:FC:17:AC:57:4A:F8:4F:4A:9F:BD:77:22:22`).

| File | Version | SHA-256 |
| --- | --- | --- |
| `NamaazReminder-1.3.1-release.aab` | 1.3.1 (versionCode 5) | `9fcca45f5d3a57ce93a6f5f2ff57534e7f80cb98864282ecd9a514147ac18d62` |

Once the `KEYSTORE_BASE64`, `STORE_PASSWORD` and `KEY_PASSWORD` secrets are
configured, **Android CI** publishes this bundle to the rolling
[`apk-latest` release](https://github.com/owaiskhan-ash/Namaaz-Reminder/releases/tag/apk-latest)
on every run and this folder is no longer needed.
