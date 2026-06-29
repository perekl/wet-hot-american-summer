"""VLC-backed cue playback for the WHAS table-read soundboard."""

from __future__ import annotations

import os
from pathlib import Path

try:
    import vlc
except ImportError as exc:
    raise ImportError(
        "python-vlc is required for playback. Install: pip install python-vlc"
    ) from exc


def _clamp_volume(value: int) -> int:
    return max(0, min(100, value))


def resolve_volume(cue: dict) -> int:
    volume = cue.get("volume")
    if isinstance(volume, int):
        return _clamp_volume(volume)
    if isinstance(volume, str) and volume.isdigit():
        return _clamp_volume(int(volume))
    return _clamp_volume(int(cue.get("suggested_volume", 70)))


def _vlc_instance() -> vlc.Instance:
    args = ["--no-video", "--quiet"]
    if os.environ.get("VLC_DUMMY_AUDIO"):
        args.append("--aout=dummy")
    return vlc.Instance(*args)


class VLCPlaybackEngine:
    """Three-channel player: ambience (single loop bed), sfx (one-shots), music."""

    def __init__(self, root: Path):
        self.root = root
        self._instance = _vlc_instance()
        self._ambience = self._instance.media_player_new()
        self._sfx = self._instance.media_player_new()
        self._music = self._instance.media_player_new()
        self._current_ambience_asset: str | None = None

    def _media(self, path: Path, loop: bool) -> vlc.Media:
        media = self._instance.media_new(str(path))
        if loop:
            media.add_option("input-repeat=65535")
        return media

    def _play(self, player: vlc.MediaPlayer, path: Path, volume: int, loop: bool) -> None:
        player.stop()
        player.set_media(self._media(path, loop))
        player.audio_set_volume(_clamp_volume(volume))
        player.play()

    def stop_ambience(self) -> None:
        self._ambience.stop()
        self._current_ambience_asset = None

    def stop_all(self) -> None:
        self._ambience.stop()
        self._sfx.stop()
        self._music.stop()
        self._current_ambience_asset = None

    def _resolve_path(self, cue: dict) -> Path:
        return self.root / cue.get("asset_filename", "")

    def play_cue(self, cue: dict) -> tuple[bool, str]:
        """Play a cue. Returns (ok, status_message)."""
        mode = cue.get("playback_mode", "")
        category = cue.get("category", "")
        volume = resolve_volume(cue)
        path = self._resolve_path(cue)

        if mode == "Silence" or category == "Silence":
            self.stop_ambience()
            return True, f"Silence — stopped ambience ({cue['id']})"

        if not path.is_file():
            return False, f"Missing audio file: {path.relative_to(self.root)}"

        if category == "Ambience":
            self.stop_ambience()
            self._play(self._ambience, path, volume, loop=True)
            self._current_ambience_asset = cue.get("asset_id")
            return True, f"Playing ambience loop: {path.name} @ {volume}"

        if mode == "One Shot" or category in ("SFX", "Transition", "Comedy"):
            loop = cue.get("loop") == "Yes"
            self._play(self._sfx, path, volume, loop=loop)
            kind = "loop" if loop else "one-shot"
            return True, f"Playing SFX {kind}: {path.name} @ {volume}"

        if mode == "Music" or category == "Music":
            loop = cue.get("loop") == "Yes"
            self._play(self._music, path, volume, loop=loop)
            kind = "loop" if loop else "music"
            return True, f"Playing {kind}: {path.name} @ {volume}"

        if mode == "Loop":
            self._play(self._sfx, path, volume, loop=True)
            return True, f"Playing loop: {path.name} @ {volume}"

        self._play(self._sfx, path, volume, loop=False)
        return True, f"Playing: {path.name} @ {volume}"
