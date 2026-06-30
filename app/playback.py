"""Cue playback for the WHAS table-read soundboard.

Background beds use VLC (reliable looping). Foreground SFX/music use pygame so
Windows volume sliders stay independent — VLC ties all its players to one mixer.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

try:
    import vlc
except ImportError as exc:
    raise ImportError(
        "python-vlc is required for playback. Install: pip install python-vlc"
    ) from exc

try:
    import pygame
except ImportError:
    pygame = None  # type: ignore[assignment]


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
    else:
        aout = os.environ.get("VLC_AOUT")
        if aout:
            args.append(f"--aout={aout}")
        elif sys.platform == "win32":
            args.append("--aout=directsound")
    return vlc.Instance(*args)


def _init_pygame_mixer() -> bool:
    if pygame is None:
        return False
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
        return True
    except pygame.error:
        return False


class VLCPlaybackEngine:
    """Background via VLC; foreground SFX/music via pygame (independent volume)."""

    def __init__(self, root: Path):
        self.root = root
        self._bg_instance = _vlc_instance()
        self._background = self._bg_instance.media_player_new()
        self._current_background_asset: str | None = None
        self._current_background_cue: dict | None = None
        self._background_volume = 30
        self._foreground_volume = 70
        self._background_started_at: float | None = None
        self._background_paused_elapsed = 0.0
        self._background_pause_started: float | None = None
        self._pygame_ready = _init_pygame_mixer()
        self._fg_channel = None

    def _media(self, path: Path, loop: bool) -> vlc.Media:
        media = self._bg_instance.media_new(str(path))
        if loop:
            media.add_option("input-repeat=65535")
        return media

    def _play_background_file(self, path: Path, volume: int) -> None:
        vol = _clamp_volume(volume)
        self._background.stop()
        self._background.set_media(self._media(path, loop=True))
        self._background.play()
        self._background.audio_set_volume(vol)

    def _resolve_path(self, cue: dict) -> Path:
        return self.root / cue.get("asset_filename", "")

    def _fg_gain(self) -> float:
        return self._foreground_volume / 100.0

    def current_background_asset_id(self) -> str | None:
        return self._current_background_asset

    def set_background_volume(self, volume: int) -> None:
        self._background_volume = _clamp_volume(volume)
        self._background.audio_set_volume(self._background_volume)

    def background_volume(self) -> int:
        return self._background_volume

    def set_foreground_volume(self, volume: int) -> None:
        self._foreground_volume = _clamp_volume(volume)
        if not self._pygame_ready or pygame is None:
            return
        gain = self._fg_gain()
        pygame.mixer.music.set_volume(gain)
        if self._fg_channel is not None and self._fg_channel.get_busy():
            self._fg_channel.set_volume(gain)

    def foreground_volume(self) -> int:
        return self._foreground_volume

    def foreground_is_playing(self) -> bool:
        if not self._pygame_ready or pygame is None:
            return False
        if pygame.mixer.music.get_busy():
            return True
        return bool(self._fg_channel is not None and self._fg_channel.get_busy())

    def stop_foreground(self) -> None:
        if not self._pygame_ready or pygame is None:
            return
        pygame.mixer.music.stop()
        pygame.mixer.stop()
        self._fg_channel = None

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
        self.stop_foreground()
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

        if mode == "Silence" or category == "Silence":
            self.stop_background()
            self._current_background_asset = cue.get("asset_id")
            self._current_background_cue = cue
            return True, f"Background silence ({cue['id']})"

        path = self._resolve_path(cue)
        if not path.is_file():
            return False, f"Missing audio file: {path.relative_to(self.root)}"

        self._play_background_file(path, 0 if fade_in_ms else self._background_volume)
        self._current_background_asset = cue.get("asset_id")
        self._current_background_cue = cue
        self._mark_background_started()
        if fade_in_ms:
            self.set_background_volume(0)
        else:
            self.set_background_volume(self._background_volume)
        return True, f"Background: {path.name} @ {self._background_volume}"

    def play_foreground(self, cue: dict) -> tuple[bool, str]:
        """Play SFX/music via pygame — does not touch the VLC background channel."""
        mode = cue.get("playback_mode", "")
        category = cue.get("category", "")
        path = self._resolve_path(cue)

        if mode == "Silence" or category == "Silence":
            return True, f"Foreground silence beat ({cue['id']}) — background unchanged"

        if not self._pygame_ready:
            self._pygame_ready = _init_pygame_mixer()
        if not self._pygame_ready or pygame is None:
            return False, "Foreground playback unavailable — pip install pygame"

        if not path.is_file():
            return False, f"Missing audio file: {path.relative_to(self.root)}"

        self.stop_foreground()
        gain = self._fg_gain()
        loop = cue.get("loop") == "Yes" or mode == "Loop"

        try:
            sound = pygame.mixer.Sound(str(path))
        except pygame.error as exc:
            return False, f"Could not load SFX: {exc}"

        channel = sound.play(loops=-1 if loop else 0)
        if channel is None:
            return False, f"Could not play SFX: {path.name}"
        channel.set_volume(gain)
        self._fg_channel = channel
        kind = "loop" if loop else "one-shot"
        return True, f"Playing SFX {kind}: {path.name} @ {self._foreground_volume}"

    def play_cue(self, cue: dict) -> tuple[bool, str]:
        """Legacy entry: route by cue_type when present, else category."""
        cue_type = cue.get("cue_type", "")
        if cue_type == "BACKGROUND":
            return self.play_background(cue)
        if cue_type == "FOREGROUND":
            return self.play_foreground(cue)
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
