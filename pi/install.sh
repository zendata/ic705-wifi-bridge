#!/bin/sh
# Install the bridge's services on the Pi. Run from a checkout in ~/ic705-wifi-bridge:
#   sudo pi/install.sh
set -e
here=$(dirname "$(readlink -f "$0")")
install -m755 "$here/bridge-mode" /usr/local/sbin/bridge-mode
install -m644 "$here/systemd/wfserver.service" "$here/systemd/bridge-status.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now bridge-status.service
echo "Installed. 'sudo bridge-mode radio' switches the USB port to the IC-705."
