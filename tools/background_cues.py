"""Classify background vs foreground cues and derive expected background beds."""

from __future__ import annotations

CUE_TYPE_BACKGROUND = "BACKGROUND"
CUE_TYPE_FOREGROUND = "FOREGROUND"

# Scene substring -> canonical asset key (fallback before first BACKGROUND cue).
_SCENE_BACKGROUND_KEYS: list[tuple[str, str]] = [
    ("mess hall", "amb_mess_hall_crowd"),
    ("kitchen", "amb_kitchen_backroom"),
    ("radio", "amb_radio_station"),
    ("campfire", "amb_campfire_night"),
    ("fire pit", "amb_campfire_night"),
    ("river", "amb_river"),
    ("rapids", "amb_river"),
    ("lake", "amb_lake_waterfront"),
    ("waterfront", "amb_lake_waterfront"),
    ("swimming", "amb_swimming_hole"),
    ("arts and crafts", "amb_arts_crafts"),
    ("arts & crafts", "amb_arts_crafts"),
    ("bunk", "amb_bunk_interior"),
    ("bbq", "amb_bbq_pit"),
    ("barbecue", "amb_bbq_pit"),
    ("picnic", "amb_bbq_pit"),
    ("rec hall", "amb_rehearsal_room"),
    ("talent show", "amb_talent_show_audience"),
    ("capture the flag", "amb_capture_the_flag"),
    ("science", "amb_science_clearing"),
    ("highway", "amb_highway_drive"),
    ("parking lot", "amb_camp_exterior_day"),
    ("epilogue", "amb_epilogue_room"),
    ("projector", "amb_projector_room"),
]


def _is_background_silence(cue: dict) -> bool:
    """Silence cues that change/stop the persistent background bed."""
    notes = cue.get("Notes", "").lower()
    name = cue.get("Cue Name", "").lower()
    if "drop" in notes or "hold black" in notes:
        return True
    if "house lights" in name or "pre-show" in name:
        return True
    return False


def classify_cue_type(cue: dict) -> str:
    category = cue.get("Category", "")
    if category == "Ambience":
        return CUE_TYPE_BACKGROUND
    if category == "Silence" and _is_background_silence(cue):
        return CUE_TYPE_BACKGROUND
    return CUE_TYPE_FOREGROUND


def _scene_fallback_asset_id(cue: dict, asset_id_for_key) -> str:
    scene = cue.get("Scene", "").lower()
    for fragment, key in _SCENE_BACKGROUND_KEYS:
        if fragment in scene:
            return asset_id_for_key(key)
    if "morning" in scene or "dawn" in scene or "sunrise" in scene:
        return asset_id_for_key("amb_outdoor_dawn")
    if "night" in scene:
        return asset_id_for_key("amb_night_exterior")
    return asset_id_for_key("amb_camp_exterior_day")


def enrich_background_fields(cues: list[dict], asset_id_for_key) -> list[dict]:
    """Add Cue Type and Expected Background Asset to each cue row."""
    current_background = ""
    enriched: list[dict] = []

    for cue in cues:
        row = dict(cue)
        cue_type = classify_cue_type(cue)
        row["Cue Type"] = cue_type

        if cue_type == CUE_TYPE_BACKGROUND:
            current_background = cue["Asset ID"]
            row["Expected Background Asset"] = ""
        else:
            expected = current_background or _scene_fallback_asset_id(cue, asset_id_for_key)
            row["Expected Background Asset"] = expected

        enriched.append(row)

    return enriched
