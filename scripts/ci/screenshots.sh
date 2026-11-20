#!/usr/bin/env bash
# Boots an iPhone simulator, installs the Debug simulator build and captures screenshots of key screens.
set -euo pipefail
APP=simbuild/Build/Products/Debug-iphonesimulator/Offleet.app
BUNDLE=app.offleet.ios
UDID=$(xcrun simctl list devices available -j | python3 -c "
import json, sys
d = json.load(sys.stdin)['devices']
c = [x for k, v in d.items() if 'iOS' in k for x in v if x['name'].startswith('iPhone')]
pref = [x for x in c if x['name'].endswith('Pro')] or c
print(pref[-1]['udid'])")
echo "Using simulator $UDID"
xcrun simctl boot "$UDID" || true
xcrun simctl bootstatus "$UDID" -b
xcrun simctl status_bar "$UDID" override --time 9:41 --batteryState charged --batteryLevel 100 --cellularBars 4 || true
xcrun simctl install "$UDID" "$APP"
mkdir -p shots

shot() {
  local name=$1; shift
  xcrun simctl terminate "$UDID" "$BUNDLE" >/dev/null 2>&1 || true
  xcrun simctl launch "$UDID" "$BUNDLE" "$@" >/dev/null
  sleep "${WAIT:-6}"
  xcrun simctl io "$UDID" screenshot --type=png "shots/$name.png" >/dev/null
  echo "captured $name"
}

while read -r name args; do
  [ -z "$name" ] && continue
  case "$name" in \#*) continue;; esac
  if [ "$name" = "dark" ]; then xcrun simctl ui "$UDID" appearance dark; continue; fi
  # shellcheck disable=SC2086
  shot "$name" $args
done < scripts/ci/screens.txt
