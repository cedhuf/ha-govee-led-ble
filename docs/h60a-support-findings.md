# H60A1 / H60A6 ceiling lights — owner evidence

Owner devices: H60A6 Ceiling Light Pro (firmware 1.00.41, hardware 1.04.03) and H60A1
Ceiling Light (firmware 1.02.20, hardware 1.04.03). Both are also commissioned over Matter;
LAN control is unavailable in the app. Evidence comes from owner-run BLE sessions through an
ESPHome proxy (2026-10-09) and decrypted official-app captures from iOS PacketLogger
(2026-10-09/10). No APK analysis was used. Support is Experimental.

## Transport

| Surface | Evidence | Notes |
| --- | --- | --- |
| Advertisement | Local names `GVH60A6…` / `GVH60A1…` (no underscore); Govee manufacturer data with flags `0x43` | Bit `0x40` advertises encryption; the current name pattern does not match these names, so setup is manual |
| GATT | Service `…1910`, write `…2b11`, notify `…2b10`; no `…2b12` marker; extra `0xfff6` service unused | |
| Encryption | v1 (AES-ECB + RC4) handshake `e7 01` / `e7 02` with the app key; session key from the `e7 01` reply | Plaintext frames are acknowledged at ATT level and silently ignored |
| Keepalive | App sends `aa 00` every 3 s; the lamp drops an idle link after about 10 s | The integration's 5 s keep-alive holds the link |

## Static control (H617A command grammar)

| Surface | Evidence | Remaining qualification |
| --- | --- | --- |
| Power | `33 01 00/01`, reply `33 01 00` then unsolicited `ee 30 01 …` | |
| Logical segments | H60A6: 13 (1–12 back light ring, 13 front panel). H60A1: 14 (1–13 ring, 14 panel). `33 05 15 01` RGB + 24-bit mask; zones and single segments verified by eye | |
| Kelvin | `33 05 15 01 00 00 00` + big-endian Kelvin + preview RGB + mask; drives the white emitters, brighter than RGB `ffffff` | H60A1 cannot show panel Kelvin white and ring colour together: either write blanks the other zone |
| Brightness | `33 04 PP` (0–100) dims the front panel only; `33 04 64` exceeds Matter's full brightness | No visible effect on the ring |
| Segment brightness | `33 05 15 02` is acknowledged and read back, but not rendered | Ring dimming must scale RGB |
| Whole-device colour | `33 05 0d` and `33 05 02` are ignored | |
| Segment readback | `aa a5 01..04`, four records (brightness + RGB) per page, zeroes after the last segment | Exact roots `h60a1_status_reply` / `h60a6_status_reply` |
| Power readback | `aa 01` → `aa 01 0X` | `aa 04` reads back on the H60A1 only (always `01` on the H60A6); not enabled |

## Captured but not implemented

| Surface | Evidence |
| --- | --- |
| Scenes | `a3 00 … a3 ff` parameter frames, then `33 05 04 <code lo> 4a` (codes `0x4a81`, `0x4a83`–`0x4a85` seen) |
| Paint mode (H60A6) | One long `a4` write, `a4 ff ff a4`, then `33 05 0a 20 03`. 133 point indices: `00`–`0b` ring, `0c`–`3b` panel outer ring (48), `3c`–`5f` (36), `60`–`77` (24), `78`–`83` (12), `84` centre. Effect byte `01`–`07` (twinkle, breathing, clockwise, anticlockwise, chase, diffuse, cross) and speed `00`–`64`; effect `00` renders nothing. RGB only |
| Zone power | `33 30 00 01` followed by `ee 30 01 01 01 0X`; meaning untested |
| Session setup | `33 09 …` after the handshake (likely clock), `ac 03 02 30 a5` bulk status, `ab 01 02/04/05` identity strings |

Paint mode replaces segment mode while active; any segment write switches back and restores the
ring's last segment colours.
