# Play listing assets

Everything the Play Console asks for, except the feature graphic.

| File | Where it goes | Requirement |
| --- | --- | --- |
| `icon-1024.png` | source artwork, keep here | — |
| `../app/src/main/ic_launcher-playstore.png` | *Store listing → App icon* | 512×512 PNG |
| `screenshots/*-1080x1920.png` | *Store listing → Phone screenshots* | 9:16, 1080×1920 |

The screenshots were letterboxed from the in-app captures onto the app's own
dark background, so they satisfy Play's 2:1 aspect limit without stretching the
UI. Recapture and repeat if the design changes.

Still missing: a **feature graphic** (1024×500 PNG or JPEG, no transparency) and
the short/full description copy.
