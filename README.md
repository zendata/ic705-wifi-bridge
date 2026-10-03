# IC-705 WiFi Bridge

A Raspberry Pi Zero W, plugged into the Icom IC-705's USB port, that stands in for the radio's built-in WiFi.

The IC-705's internal WiFi can be unreliable. This project turns that off and lets a Pi do the networking instead:

```
IC-705 ──USB (CI-V + audio)──► Pi Zero W ──WiFi──► home router ──► RS-BA1 / wfview / any Icom network client
```

The Pi talks to the radio over USB and serves Icom's network protocol (UDP ports 50001 control, 50002 CI-V, 50003 audio). To a client on the network the Pi looks like an IC-705 with working WiFi. It does not depend on any particular client software.

## Status

**Working with the IC-705 (2026-10-03).** A Pi Zero W runs wfview's `wfserver` (2.03, from the Raspberry Pi OS packages). A network client logs in, reads and sets the radio over CI-V, and receives 48 kHz audio. wfserver uses about 7% of the Zero W's CPU with no client and about 32% while streaming. About 0.3% of audio packets are lost over WiFi, one 20 ms packet at a time. Clients can recover these by asking for retransmits.

Run as a service, wfserver needs a stdin that blocks. With /dev/null its keyboard thread spins on the whole CPU and starves the audio. `wfserver.service` handles this.

The plan:

1. **Try wfview's server mode on the Pi.** wfview 2.03 is packaged for Raspberry Pi OS. This shows whether a Zero W can keep up with CI-V, audio and the scope, and whether clients connect cleanly.
2. **Decide what to build.** If wfview works, this repo holds the setup plus an e-paper status display. If it is too heavy for the Zero W, this repo grows a lean bridge of its own.

## Hardware

- Raspberry Pi Zero W (v1.1) running Raspberry Pi OS Lite or desktop, 32-bit (Trixie). A Zero 2 W gives more headroom.
- Micro-USB **OTG** cable from the Pi's inner **USB** port to the IC-705's USB port. The Pi is the USB host.
- Separate power to the Pi's outer **PWR** port. The IC-705 does not power it.
- Optional: Waveshare 2.13" e-paper HAT, for showing the Pi's IP address, WiFi signal, connected client and frequency.

Turn the IC-705's own WiFi off while using the bridge.

## Setup on the Pi

```
sudo apt install wfview          # provides wfserver
sudo raspi-config nonint do_spi 0   # for the e-paper HAT, then reboot
git clone https://github.com/zendata/ic705-wifi-bridge ~/ic705-wifi-bridge
sudo ~/ic705-wifi-bridge/pi/install.sh
```

`install.sh` installs:

- `bridge-status.service`: the e-paper status screen (`epaper/status.py`). It shows the WiFi network and signal, the IP address, whether the IC-705 is on USB, and whether the server is running. It redraws only when one of those changes.
- `wfserver.service`: wfserver with its settings in `~/wfserver/wfserver.ini`. It is enabled by `bridge-mode radio`.
- `bridge-login`: sets the user name and password that clients log in to wfserver with. Use the IC-705's own Network User ID and password, so existing clients connect unchanged. Then run `sudo systemctl restart wfserver`.
- `bridge-mode`: switches the Pi's single USB port, then reboots:
  - `sudo bridge-mode radio`: the Pi is USB host for the IC-705 and wfserver runs.
  - `sudo bridge-mode computer`: the Pi is a USB network gadget for a computer, and wfserver is off.

The e-paper driver defaults to the 2.13" V4 panel. For other versions, set `EPD_DRIVER=epd2in13_V3` or `epd2in13_V2` in the service. The drivers in `epaper/waveshare_epd/` come from [Waveshare's e-Paper repo](https://github.com/waveshareteam/e-Paper) under its MIT-style licence.

## wfserver settings for the IC-705

In `~/wfserver/wfserver.ini` (wfserver creates it on first run with `-s`):

```
1\AudioInput="plughw:CARD=CODEC,DEV=0"
1\AudioOutput="plughw:CARD=CODEC,DEV=0"
1\RigCIVuInt=164
1\RigName=IC-705
1\SerialPortRadio=/dev/serial/by-id/usb-Icom_Inc._IC-705_IC-705_<serial>-if00
```

Keep the quotes around the audio names. Qt's INI reader treats an unquoted value with commas as a list, which leaves wfserver with an empty device name and no audio. Use `bridge-login` for the user name and password.

To spare the Zero W's CPU, boot it to the console (`sudo raspi-config nonint do_boot_behaviour B1`). Raspberry Pi Connect's remote shell still works, but its screen sharing needs the desktop.

## On the IC-705

- Set **SET > Function > USB Power Input (Phone, Tablet, PC)** to **OFF**. Otherwise the radio tries to charge its battery from the Pi's USB port.
- Turn the radio's own WiFi off.

## Licence

MIT. See [LICENSE](LICENSE).
