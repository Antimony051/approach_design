#!/bin/bash
set -euo pipefail
test "$EUID" -eq 0 || { echo "Run this deployment script with sudo." >&2; exit 1; }
test "$#" -eq 1 || { echo "Usage: $0 <Git commit or tag>" >&2; exit 2; }

repo=/opt/pavewatch-recorder
service=pavewatch-recorder.service
watchdog=pavewatch-watchdog.service
watchdog_unit="/etc/systemd/system/$watchdog"
release=$(git -C "$repo" rev-parse --verify "$1^{commit}")
exec 8>/run/lock/pavewatch-recorder.lock
flock -w 10 8
case "$(systemctl show "$service" --property=ActiveState --value)" in
    inactive|failed) ;;
    *) echo "Stop the active recorder before deploying." >&2; exit 1 ;;
esac
if systemctl is-active --quiet collect-camera.service; then
    echo "Stop the legacy camera recorder before deploying." >&2
    exit 1
fi

stage=$(mktemp -d /tmp/pavewatch-release.XXXXXX)
trap 'rm -rf -- "$stage"' EXIT
git -C "$repo" archive "$release" | tar -x -C "$stage"
units=("$stage/$service")
if test -f "$stage/$watchdog"; then
    test -f "$stage/recorder_watchdog.py"
    units+=("$stage/$watchdog")
fi
systemd-analyze verify "${units[@]}"

replace() {
    local src=$1 dest=$2 perm=$3
    local temporary
    temporary=$(mktemp "$dest.deploy.XXXXXX")
    install -o root -g root -m "$perm" "$src" "$temporary"
    mv -T -- "$temporary" "$dest"
}

library=/usr/local/lib/pavewatch-lidar
receiver_config=/etc/sysctl.d/90-pavewatch-compact-receiver.conf
previous_buffer="$repo/.git/pavewatch-rmem-max-before"
if test -f "$stage/90-pavewatch-compact-receiver.conf"; then
    if ! test -f "$previous_buffer"; then
        test ! -e "$receiver_config"
        sysctl -n net.core.rmem_max > "$previous_buffer"
    fi
    replace "$stage/90-pavewatch-compact-receiver.conf" "$receiver_config" 0644
    sysctl -q -p "$receiver_config"
elif test -f "$receiver_config" && test -f "$previous_buffer"; then
    rm -- "$receiver_config"
    sysctl -q -w "net.core.rmem_max=$(cat "$previous_buffer")"
fi
if test -f "$watchdog_unit"; then
    systemctl stop "$watchdog"
fi
for module in recorder_watchdog.py lidar_telemetry.py managed_collect.py collect_v2.py; do
    if test -f "$stage/$module"; then
        replace "$stage/$module" "$library/$module" 0644
    fi
done
replace "$stage/lidar_control.py" "$library/lidar_control.py" 0755
replace "$stage/idle_at_boot.sh" "$library/idle_at_boot.sh" 0755
replace "$stage/collect" /usr/local/bin/collect 0755
replace "$stage/lidar" /usr/local/bin/lidar 0755
replace "$stage/$service" "/etc/systemd/system/$service" 0644
if test -f "$stage/$watchdog"; then
    replace "$stage/$watchdog" "$watchdog_unit" 0644
elif test -f "$watchdog_unit"; then
    rm -- "$watchdog_unit"
fi
systemctl daemon-reload
if test "$(systemctl show "$service" --property=ActiveState --value)" = failed; then
    systemctl reset-failed "$service"
fi
printf '%s\n' "$release" > "$repo/.git/pavewatch-active"
printf 'Installed recorder release %s\n' "$release"
