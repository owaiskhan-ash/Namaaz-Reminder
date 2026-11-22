#!/usr/bin/env bash
# Put the Madinah Azaan MP3 into app/src/main/res/raw before a build.
#
# The audio ships inside the APK/AAB so the azaan plays offline and on the alarm
# stream. Sources, in order:
#   1. a file already in the tree (developer build),
#   2. the storage bucket URL below,
#   3. the last published release APK, which already contains the same file -
#      the bucket this project used has been deleted, so no build may depend on it.
#
# If none of them yields the file the build goes on without it: the app falls
# back to the device alarm sound instead of failing every reminder. The script
# never exits non-zero, so it cannot fail a job by itself.
#
# Requires: unzip, stat, curl; `gh` with GH_TOKEN for step 3.
set -uo pipefail

AZAAN_URL="${AZAAN_URL:-https://oxtqzqynhtybrgushmjp.supabase.co/storage/v1/object/public/Just%20Apps/Namaaz%20reminder/Madinah%20Azaan.mp3}"
TARGET="app/src/main/res/raw/madinah_azaan.mp3"
mkdir -p app/src/main/res/raw

if [ ! -s "$TARGET" ]; then
  curl -fsSL --retry 2 --retry-delay 2 "$AZAAN_URL" -o "$TARGET" || rm -f "$TARGET"
fi

if [ ! -s "$TARGET" ]; then
  echo "::warning::Azaan bucket unavailable; trying to recover the file from the last release APK."
  for TAG in v1.7.3 v1.7.2 v1.7.1 v1.7.0; do
    rm -rf /tmp/azaan
    mkdir -p /tmp/azaan/out
    echo "Trying $TAG ..."
    if ! gh release download "$TAG" --pattern '*-release.apk' --dir /tmp/azaan --repo "${GITHUB_REPOSITORY:-owaiskhan-ash/Namaaz-Reminder}"; then
      echo "$TAG: download failed."
      continue
    fi
    APK="$(ls /tmp/azaan/*.apk 2>/dev/null | head -1)"
    echo "$TAG: $(ls -lh "$APK" | awk '{print $5}')"
    # Release builds can rename raw resources, so look at res/raw/* first and
    # then at any .mp3 in the archive, and keep the biggest file found.
    unzip -o -j -q "$APK" 'res/raw/*' -d /tmp/azaan/out >/dev/null 2>&1 || true
    unzip -o -j -q "$APK" '*.mp3' -d /tmp/azaan/out >/dev/null 2>&1 || true
    unzip -l "$APK" | grep -i "mp3" | head -5 || true
    CANDIDATE="$(ls -S /tmp/azaan/out 2>/dev/null | head -1)"
    if [ -n "$CANDIDATE" ] && [ -s "/tmp/azaan/out/$CANDIDATE" ] && \
       [ "$(stat -c%s "/tmp/azaan/out/$CANDIDATE")" -gt 100000 ]; then
      cp "/tmp/azaan/out/$CANDIDATE" "$TARGET"
      echo "Recovered $CANDIDATE from $TAG."
      break
    fi
    echo "$TAG: no usable audio found."
  done
fi

if [ -s "$TARGET" ]; then
  ls -lh "$TARGET"
else
  echo "::warning::Building without bundled Azaan audio; the app will use the device alarm sound."
fi

exit 0
