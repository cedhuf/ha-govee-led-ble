meta:
  id: h60a1_status_reply
  title: Govee H60A1 AA status envelope (decode-only)
  endian: le
  imports:
    - ../govee_segment_page
doc: |
  SPECULATIVE H60A1, support issue not yet filed.
  Evidence source class: owner-run BLE exchanges through an ESPHome proxy and a
  decrypted official-app capture (iPhone PacketLogger), 2026-10-09/10.
  Compatibility hypothesis: the H617A static segment command applies unchanged,
  and AA A5 readback returns 14 logical segments (1-13 back light ring,
  14 front panel) in pages of four brightness/RGB records, zero-filled after the
  last segment. AA 01 power replies match. Other AA domains are left opaque:
  their layouts were seen but not qualified.
seq:
  - id: header
    contents: [0xaa]
  - id: domain
    type: u1
    enum: aa_domain
  - id: body
    size: 17
    type:
      switch-on: domain
      cases:
        'aa_domain::power': power_body
        'aa_domain::segments': govee_segment_page(14, 4, true)
  - id: checksum
    type: u1
enums:
  aa_domain:
    0x01: power
    0xa5: segments
types:
  power_body:
    seq:
      - id: is_on
        type: u1
      - id: unknown_tail
        size-eos: true
