"""VLC-backed cue playback for the WHAS table-read soundboard."""

from __future__ import annotations

import os
import time
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
    """Three-channel player: background (persistent bed), sfx (one-shots), music."""

    def __init__(self, root: Path):
        self.root = root
        self._instance = _vlc_instance()
        self._background = self._instance.media_player_new()
        self._sfx = self._instance.media_player_new()
        self._music = self._instance.media_player_new()
        self._current_background_asset: str | None = None
        self._current_background_cue: dict | None = None
        self._background_volume = 30
        self._background_started_at: float | None = None
        self._background_paused_elapsed = 0.0
        self._background_pause_started: float | None = None

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

    def _resolve_path(self, cue: dict) -> Path:
        return self.root / cue.get("asset_filename", "")

    def current_background_asset_id(self) -> str | None:
        return self._current_background_asset

    def set_background_volume(self, volume: int) -> None:
        self._background_volume = _clamp_volume(volume)
        self._background.audio_set_volume(self._background_volume)

    def background_volume(self) -> int:
        return self._background_volume

    def background_is_playing(self) -> bool:
        return bool(self._background.is_playing())

    def background_is_active(self) -> bool:
        """True when a background bed is loaded (playing or paused)."""
        if self._current_background_asset is None:
            return False
        state = self._background.get_state()
        return state in (
            vlc.State.Playing,
            vlc.State.Paused,
            vlc.State.Buffering,
            vlc.State.Opening,
        )

    def background_elapsed_seconds(self) -> float:
        if self._current_background_asset is None:
            return 0.0
        if self._background_pause_started is not None:
            return self._background_paused_elapsed
        if self._background_started_at is None:
            return 0.0
        return self._background_paused_elapsed + (time.monotonic() - self._background_started_at)

    def _mark_background_started(self) -> None:
        self._background_started_at = time.monotonic()
        self._background_paused_elapsed = 0.0
        self._background_pause_started = None

    def _clear_background_tracking(self) -> None:
        self._background_started_at = None
        self._background_paused_elapsed = 0.0
        self._background_pause_started = None

    def stop_background(self) -> None:
        self._background.stop()
        self._current_background_asset = None
        self._current_background_cue = None
        self._clear_background_tracking()

    def stop_all(self) -> None:
        self._background.stop()
        self._sfx.stop()
        self._music.stop()
        self._current_background_asset = None
        self._current_background_cue = None
        self._clear_background_tracking()

    def pause_background(self) -> None:
        if not self.background_is_active():
            return
        if self._background_pause_started is None and self._background_started_at is not None:
            self._background_paused_elapsed += time.monotonic() - self._background_started_at
            self._background_pause_started = time.monotonic()
            self._background_started_at = None
        self._background.pause()

    def resume_background(self) -> None:
        if self._current_background_asset is None:
            return
        if self._background_pause_started is not None:
            self._background_started_at = time.monotonic()
            self._background_pause_started = None
        self._background.play()

    def play_background(self, cue: dict, *, fade_in_ms: int = 0) -> tuple[bool, str]:
        """Switch persistent background bed (fade out previous, start new)."""
        mode = cue.get("playback_mode", "")
        category = cue.get("category", "")
        volume = resolve_volume(cue)

        if mode == "Silence" or category == "Silence":
            self.stop_background()
            self._current_background_asset = cue.get("asset_id")
            self._current_background_cue = cue
            return True, f"Background silence ({cue['id']})"

        path = self._resolve_path(cue)
        if not path.is_file():
            return False, f"Missing audio file: {path.relative_to(self.root)}"

        self._background.stop()
        self._play(self._background, path, 0 if fade_in_ms else volume, loop=True)
        self._current_background_asset = cue.get("asset_id")
        self._current_background_cue = cue
        self._mark_background_started()
        if fade_in_ms:
            self.set_background_volume(0)
        else:
            self.set_background_volume(volume)
        return True, f"Background: {path.name} @ {volume}"

    def play_foreground(self, cue: dict) -> tuple[bool, str]:
        """Play SFX/music without touching the background channel."""
        mode = cue.get("playback_mode", "")
        category = cue.get("category", "")
        volume = resolve_volume(cue)
        path = self._resolve_path(cue)

        if mode == "Silence" or category == "Silence":
            return True, f"Foreground silence beat ({cue['id']}) — background unchanged"

        if not path.is_file():
            return False, f"Missing audio file: {path.relative_to(self.root)}"

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

    def play_cue(self, cue: dict) -> tuple[bool, str]:
        """Legacy entry: route by cue_type when present, else category."""
        cue_type = cue.get("cue_type", "")
        if cue_type == "BACKGROUND":
            return self.play_background(cue)
        if cue_type == "FOREGROUND":
            return self.play_foreground(cue)
        # Backward compatibility for projects without cue_type
        category = cue.get("category", "")
        if category == "Ambience":
            return self.play_background(cue)
        if category == "Silence":
            return self.play_background(cue)
        return self.play_foreground(cue)

    def background_cue_for_asset(self, asset_id: str, cues: list[dict]) -> dict | None:
        """Find a BACKGROUND cue that uses the given asset."""
        for cue in cues:
            if cue.get("cue_type") != "BACKGROUND":
                continue
            if cue.get("asset_id") == asset_id:
                return cue
        for cue in cues:
            if cue.get("category") == "Ambience" and cue.get("asset_id") == asset_id:
                return cue
        return None
