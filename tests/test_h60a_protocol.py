"""H60A1/H60A6 frames decrypted from owner sessions, not APK hypotheses."""

import pytest

from custom_components.ha_govee_led_ble.generated_protocol_adapter import build_segment_query, parse_status
from custom_components.ha_govee_led_ble.light_commands import build_segment_color

# Back light ring blue, front panel at 4000 K (H60A6), and back light ring blue
# with the front panel in the lamp's default warm white (H60A1).
CAPTURED_PAGES = {
    "H60A6": {
        "aaa501640000ff640000ff640000ff640000ff0e": [(100, (0, 0, 255))] * 4,
        "aaa50464ffd5a1000000000000000000000000e4": [(100, (255, 213, 161))],
    },
    "H60A1": {
        "aaa504640000ff64ff6d55000000000000000033": [(100, (0, 0, 255)), (100, (255, 109, 85))],
    },
}


@pytest.mark.parametrize(
    ("model", "frame", "records"),
    [(model, frame, records) for model, pages in CAPTURED_PAGES.items() for frame, records in pages.items()],
)
def test_captured_segment_pages_decode(model, frame, records):
    parsed = parse_status(bytes.fromhex(frame), model)

    assert parsed is not None
    assert parsed.body.num_segments == len(records)
    assert [(r.brightness, (r.colour.red, r.colour.green, r.colour.blue)) for r in parsed.body.segments] == records


@pytest.mark.parametrize("model", ["H60A1", "H60A6"])
def test_captured_power_reply_decodes(model):
    parsed = parse_status(bytes.fromhex("aa010100000000000000000000000000000000aa"), model)

    assert parsed is not None
    assert parsed.body.is_on == 1


@pytest.mark.parametrize("model", ["H60A1", "H60A6"])
def test_segment_queries_match_owner_frames(model):
    assert build_segment_query(1, model).hex() == "aaa501000000000000000000000000000000000e"


def test_front_panel_write_matches_owner_frame():
    # 33 05 15 01 + RGB, mask 0x1000 (segment 13), as sent and verified on an H60A6.
    assert build_segment_color([13], 255, 0, 0, "H60A6").hex() == "33051501ff0000000000000000100000000000cd"
