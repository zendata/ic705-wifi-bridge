#!/bin/sh
# Install the bridge's services on the Pi. Run from a checkout in ~/ic705-wifi-bridge:
#   sudo pi/install.sh
set -e
here=$(dirname "$(readlink -f "$0")")
install -m755 "$here/bridge-mode" /usr/local/sbin/bridge-mode
install -m755 "$here/bridge-login" /usr/local/bin/bridge-login
install -m644 "$here/systemd/wfserver.service" "$here/systemd/bridge-status.service" /etc/systemd/system/
# WiFi power saving adds latency and drops audio packets; PackageKit takes CPU the
# Zero W does not have to spare.
printf '[connection]\nwifi.powersave = 2\n' > /etc/NetworkManager/conf.d/90-wifi-powersave-off.conf
systemctl mask --now packagekit.service 2>/dev/null || true
systemctl daemon-reload
systemctl enable --now bridge-status.service
echo "Installed. 'sudo bridge-mode radio' switches the USB port to the IC-705."
