#!/usr/bin/env python3
"""Show the bridge's state on a Waveshare 2.13" e-paper HAT.

Redraws only when something on the screen changes, because each e-paper
refresh takes a few seconds, flashes the panel and wears it a little.

    status.py            run forever, checking every 30 s
    status.py --once     draw once and exit
    EPD_DRIVER=epd2in13_V3 status.py   pick another panel version (default V4)
"""
import glob
import importlib
import os
import socket
import subprocess
import sys
import time

from PIL import Image, ImageDraw, ImageFont

POLL_SECONDS = 30
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ICOM_USB_VENDOR = "0c26"


def run(*cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def signal_band(dbm):
    """A coarse rating, so a signal wobbling by a dB or two does not redraw the panel."""
    if dbm is None:
        return None
    for floor, name in ((-55, "excellent"), (-67, "good"), (-75, "fair")):
        if dbm >= floor:
            return name
    return "weak"


def wifi():
    """(network name, signal band) for wlan0, or (None, None) when not joined."""
    ssid = None
    for line in run("nmcli", "-t", "-f", "ACTIVE,SSID", "dev", "wifi", "list", "--rescan", "no").splitlines():
        if line.startswith("yes:"):
            ssid = line[4:].replace("\\:", ":")
    dbm = None
    try:
        with open("/proc/net/wireless") as f:
            for line in f:
                if line.strip().startswith("wlan0:"):
                    dbm = int(float(line.split()[3]))
    except (OSError, ValueError, IndexError):
        pass
    return ssid, signal_band(dbm) if ssid else None


def ipv4(ifname):
    for word in run("ip", "-4", "-o", "addr", "show", ifname).split():
        if "/" in word and word[0].isdigit():
            return word.split("/")[0]
    return None


def radio_on_usb():
    """The IC-705 shows up as an Icom (vendor 0c26) USB device when the Pi is its host."""
    for path in glob.glob("/sys/bus/usb/devices/*/idVendor"):
        with open(path) as f:
            if f.read().strip() == ICOM_USB_VENDOR:
                return True
    return False


def server_state():
    if run("systemctl", "is-active", "wfserver") == "active":
        return "running"
    return "stopped"


def usb_mode():
    """'gadget' when the Pi is a USB device for a computer, else 'host' (for the radio)."""
    return "gadget" if os.path.exists("/sys/class/net/usb0") else "host"


def gather():
    ssid, band = wifi()
    return {
        "host": socket.gethostname(),
        "ssid": ssid,
        "signal": band,
        "ip": ipv4("wlan0"),
        "usb": usb_mode(),
        "radio": radio_on_usb(),
        "server": server_state(),
    }


def lines_for(s):
    if s["ssid"]:
        signal = f", {s['signal']}" if s["signal"] else ""
        wifi_line = f"WiFi {s['ssid']}{signal}"
    else:
        wifi_line = "WiFi not connected"
    if s["usb"] == "gadget":
        radio_line = "USB: gadget mode (computer)"
    else:
        radio_line = "IC-705 on USB" if s["radio"] else "No radio on USB"
    return [
        wifi_line,
        f"IP {s['ip'] or '-'}",
        radio_line,
        f"Server {s['server']}",
    ]


def render(epd, s):
    # The panel is 122 x 250 portrait; draw landscape and let the driver rotate.
    img = Image.new("1", (epd.height, epd.width), 255)
    d = ImageDraw.Draw(img)
    title = ImageFont.truetype(FONT_BOLD, 17)
    body = ImageFont.truetype(FONT, 15)
    d.rectangle((0, 0, epd.height - 1, 22), fill=0)
    d.text((5, 1), f"IC-705 Bridge  {s['host']}", font=title, fill=255)
    for i, text in enumerate(lines_for(s)):
        d.text((5, 27 + i * 23), text, font=body, fill=0)
    epd.init()
    epd.display(epd.getbuffer(img))
    epd.sleep()


def main():
    driver = importlib.import_module("waveshare_epd." + os.environ.get("EPD_DRIVER", "epd2in13_V4"))
    epd = driver.EPD()
    shown = None
    while True:
        s = gather()
        if s != shown:
            render(epd, s)
            shown = s
        if "--once" in sys.argv:
            return
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
