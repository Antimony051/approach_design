#!/bin/sh
# A delayed scanner can come online after the Pi. The controller never stops an active capture.
for attempt in $(seq 1 30); do
    if /usr/bin/python3 /usr/local/lib/pavewatch-lidar/lidar_control.py idle-if-inactive \
        >/tmp/lidar-idle-boot.log 2>&1; then
        echo "$(date -Is) LiDAR idle check finished (attempt $attempt)"
        exit 0
    fi
    sleep 10
done
echo "$(date -Is) could not confirm LiDAR idle after 30 attempts" >&2
exit 1
