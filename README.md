# IC-705 WiFi Bridge

A Raspberry Pi Zero W, plugged into the Icom IC-705's USB port, that stands in for the radio's built-in WiFi.

The IC-705's internal WiFi can be unreliable. This project turns that off and lets a Pi do the networking instead:

```
IC-705 ──USB (CI-V + audio)──► Pi Zero W ──WiFi──► home router ──► RS-BA1 / wfview / any Icom network client
```

The Pi talks to the radio over USB and serves Icom's network protocol (UDP ports 50001 control, 50002 CI-V, 50003 audio). To a client on the network the Pi looks like an IC-705 with working WiFi. It does not depend on any particular client software.

## Status

Just starting. The plan:

1. **Try wfview's server mode on the Pi.** wfview 2.03 is packaged for Raspberry Pi OS. This shows whether a Zero W can keep up with CI-V, audio and the scope, and whether clients connect cleanly.
2. **Decide what to build.** If wfview works, this repo holds the setup plus an e-paper status display. If it is too heavy for the Zero W, this repo grows a lean bridge of its own.

## Hardware

- Raspberry Pi Zero W (v1.1) running Raspberry Pi OS Lite or desktop, 32-bit (Trixie). A Zero 2 W gives more headroom.
- Micro-USB **OTG** cable from the Pi's inner **USB** port to the IC-705's USB port. The Pi is the USB host.
- Separate power to the Pi's outer **PWR** port. The IC-705 does not power it.
- Optional: Waveshare 2.13" e-paper HAT, for showing the Pi's IP address, WiFi signal, connected client and frequency.

Turn the IC-705's own WiFi off while using the bridge.

## Licence

MIT. See [LICENSE](LICENSE).
