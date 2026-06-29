# Wet Hot American Summer — Table Read Production Kit

A complete professional sound production package for a live table read of **Wet Hot American Summer**, generated from the screenplay (`Wet Hot American Summer_v2.pdf`) as the single source of truth.

## Repository Structure

```
assets/
  ambience/          # Looping environmental beds (camp, lake, mess hall, etc.)
  sfx/               # One-shot and comedy sound effects
  generated/         # Screenplay extract, silence markers, generated refs

data/
  master_cues.xlsx           # Master cue spreadsheet (all cues, chronological)
  master_sound_assets.xlsx   # Unique sound assets referenced by cues
  licensed_music.xlsx        # Licensed music clearance guide
  cues.json                  # JSON export for the soundboard app
  assets.json                # JSON export of sound asset library

docs/
  CueBook.docx               # Professional cue book (one cue per entry)
  CueBook.pdf                # PDF cue book for printing
  StageManagerBook.docx      # Large-format live-run cue book

app/
  soundboard.py              # Windows/macOS/Linux tkinter cue navigator

tools/
  cues_data.py               # Screenplay-derived master cue database
  generate_production_kit.py # Regenerates all deliverables from cues_data.py
```

## How Cues Relate to Sound Assets

Each row in `data/master_cues.xlsx` is a **performance cue** — a moment in the script where sound supports the read.

Each row in `data/master_sound_assets.xlsx` is a **unique audio file** the production needs. Multiple cues may reference the same asset (e.g., "Mess Hall Crowd Ambience" used across several scenes).

| Cue Field | Purpose |
|-----------|---------|
| Cue ID | Unique identifier (`CUE-001` …) for call sheets and the app |
| Asset ID | Canonical reusable sound file (`AST-001` …) |
| Script Page | Screenplay page reference |
| Trigger Dialogue | Exact line or stage direction that fires the cue |
| Category | Music, Ambience, SFX, Transition, Silence, Comedy |
| Priority | Critical / High / Medium / Low / Optional |

| Asset Field | Purpose |
|-------------|---------|
| Asset ID | Unique file identifier (`AST-001` …) linked from master cues |
| Playback Mode | How the asset plays: `Loop`, `One Shot`, `Music`, or `Silence` |
| Suggested Volume | Default level by mode: Loop 30, One Shot 85, Music 70, Silence 0 |
| Filename | Target path under `assets/` |
| Used By Cue IDs | All cues that share this file |
| Royalty Free? | Whether the asset can be sourced royalty-free |
| Status | Production tracking (`Needed`, etc.) |

**Cue-level mix is preserved:** each cue keeps its own `Volume`, `Fade`, and `Loop` in `master_cues.xlsx`. Multiple cues can share one asset file while behaving differently in context (e.g., Mess Hall Crowd at breakfast vs. dinner with different fades/volumes).

**Licensed music** is tracked separately in `data/licensed_music.xlsx` because it requires rights clearance (Jefferson Starship, Rick Springfield, Lovin' Spoonful, Godspell, etc.).

## Regenerating the Kit

After editing `tools/cues_data.py` (when the screenplay changes):

```bash
pip install -r requirements.txt
python tools/generate_production_kit.py
```

This rebuilds all spreadsheets, Word/PDF cue books, and JSON exports. Assets are consolidated via `tools/asset_library.py` (78 reusable files serving 239 cues). The generator verifies **all 90 screenplay pages** have cue coverage before completing.

## Soundboard Application

The tkinter app reads `data/cues.json` and plays cues via **python-vlc** (requires [VLC](https://www.videolan.org/vlc/) installed on the system).

```bash
pip install python-vlc
python app/soundboard.py
```

**Controls:**
- **PLAY / Enter** — play current cue
- **NEXT / PREVIOUS** — step through cues in screenplay order
- **Spacebar** — advance to next cue
- **ESC** — stop all playback

**Playback behavior:**
- **Ambience** loops on a dedicated bed; starting a new ambience stops the previous one
- **SFX / transitions** fire as one-shots (overlap ambience)
- **Music** plays on a separate channel; loops when the cue `loop` field is `Yes`
- **Silence** cues stop the ambience bed

**Display:** current cue name, trigger dialogue, script page, and upcoming cue.

## Future Workflow

1. **Source assets** — Populate `assets/sfx/` and `assets/ambience/` using `master_sound_assets.xlsx` as a shopping list. Update Status and Download URL columns as files are acquired.
2. **Clear music** — Use `licensed_music.xlsx` to secure sync/performance rights or plan live musician/karaoke substitutes for the table read.
3. **Rehearse** — Stage manager runs from `docs/StageManagerBook.docx`; sound op uses the soundboard app in parallel with the script.
4. **Implement playback** — Wire `app/soundboard.py` PLAY button to a cross-platform audio engine (e.g., `sounddevice` + preloaded buffers, or a Windows-specific backend).
5. **Screenplay updates** — Re-extract text from an updated PDF, revise `tools/cues_data.py`, and regenerate.

## Source of Truth

All cues are derived from `Wet Hot American Summer_v2.pdf` (90 pages, Second Draft, February 23, 2026). The extracted screenplay text is archived at `assets/generated/screenplay_extract.txt` for audit and diffing.
