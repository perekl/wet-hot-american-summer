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
  background_cues.py         # Background/foreground classification + expected beds
  generate_production_kit.py # Regenerates all deliverables from cues_data.py
```

## How Cues Relate to Sound Assets

Each row in `data/master_cues.xlsx` is a **performance cue** — a moment in the script where sound supports the read.

Each row in `data/master_sound_assets.xlsx` is a **unique audio file** the production needs. Multiple cues may reference the same asset (e.g., "Mess Hall Crowd Ambience" used across several scenes).

| Cue Field | Purpose |
|-----------|---------|
| Cue ID | Unique identifier (`CUE-001` …) for call sheets and the app |
| Asset ID | Canonical reusable sound file (`AST-001` …) |
| Cue Type | `BACKGROUND` (persistent bed) or `FOREGROUND` (one-shot / music / beat) |
| Expected Background Asset | Optional — which background bed *should* be active for this cue |
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

This rebuilds all spreadsheets, Word/PDF cue books, and JSON exports. Assets are consolidated via `tools/asset_library.py` (78 reusable files serving 239 cues). Background/foreground classification and expected-background fields are added by `tools/background_cues.py`. The generator verifies **all 90 screenplay pages** have cue coverage before completing.

## Soundboard Application

The tkinter app reads `data/cues.json` and plays cues via **python-vlc** (requires [VLC](https://www.videolan.org/vlc/) installed on the system).

```bash
pip install python-vlc
python app/soundboard.py
```

**Effects controls (keyboard):**
- **GO / Enter** — fire the current effect cue
- **NEXT / PREVIOUS** or arrow keys — step through the **effects queue** only
- **Spacebar** — advance to next effect (does not auto-play)
- **ESC** — stop all playback (background + effects)

**Background controls (mouse only):**
- **PREV / GO / NEXT** in the Background panel — step through and fire the **background queue** separately
- **Play**, **Pause**, **Stop**, **Fade Out**, **Switch to Expected**, volume slider

### Separate Queues

The app maintains two independent cue queues loaded from `cues.json`:

| Queue | Count | Contents |
|-------|-------|----------|
| **Effects** | 163 foreground cues | SFX, music, transitions, comedy, dramatic silence beats |
| **Background** | 76 background cues | Ambience loops and bed-clearing silence cues |

Keyboard shortcuts apply **only to the effects queue**. Background is operated entirely via mouse clicks so the operator can run beds and hits independently during a live read.

### Background Cue System

The soundboard separates **persistent background beds** from **foreground** sound effects. This is designed to assist a live human operator during a table read — not to automate cue progression.

**Background cues** (`cue_type: BACKGROUND`) change the current background audio:
- Ambience loops (campfire, mess hall crowd, lake, radio station, etc.)
- Background **Silence** cues that fade out or clear the bed (e.g., pre-show hold, “drop crowd bed”)

When **GO** is pressed on a background cue (Background panel, mouse only):
1. Fade out any current background
2. Start the new background (or silence)
3. Update the **Background** panel

The background continues until another background cue changes it.

**Foreground cues** (`cue_type: FOREGROUND`) behave as before:
- SFX, transitions, comedy hits, music stings
- Dramatic silence *beats* (momentary pauses — they do **not** stop the background bed)
- Foreground playback never interrupts background playback

### Expected Background

Every foreground cue may include an optional `expected_background_asset_id` in `cues.json` (and **Expected Background Asset** in `master_cues.xlsx`). This field is **informational only** — it describes which background should currently be active for the scene. It is not a command.

When the selected effect’s expected background does not match what is playing:
- A **yellow warning banner** appears on the effects panel
- Pressing **GO** (Enter) opens a **Background Out of Sync** dialog with **Switch Background** or **Ignore**
- Nothing happens automatically; the operator decides

When they match, a **green checkmark** confirms sync.

### Background Panel

A persistent panel at the top of the soundboard shows:
- **Background queue** position with PREV / GO / NEXT (mouse only)
- Currently **playing** background name, status, and elapsed time
- **Play**, **Pause**, **Stop**, **Fade Out**, **Switch to Expected** (matches current effect’s expected bed)
- Volume slider

**Display:** current effect name, trigger dialogue, script page, expected background, sync status, and upcoming effect.

## Sourcing Royalty-Free Assets

Automated sourcing tries **Pixabay first**, then **BBC Sound Effects**:

```bash
python tools/source_assets.py
```

- Downloads BBC metadata from Internet Archive (`BBCSoundEffects.csv`)
- Converts audio to the expected `.mp3` / `.wav` paths in `assets/`
- Updates `data/assets.json`, `data/master_sound_assets.xlsx`, and writes `data/asset_sourcing_report.md`
- **71 royalty-free assets** are included; licensed music must still be acquired manually

Pixabay sound effects are not available via official API; automated Pixabay access may be blocked by Cloudflare — see the sourcing report for per-asset status.

## Future Workflow

1. **Source assets** — Run `python tools/source_assets.py` for royalty-free SFX/ambience; manually acquire licensed tracks from `licensed_music.xlsx`.
2. **Clear music** — Use `licensed_music.xlsx` to secure sync/performance rights or plan live musician/karaoke substitutes for the table read.
3. **Rehearse** — Stage manager runs from `docs/StageManagerBook.docx`; sound op uses the soundboard app in parallel with the script.
4. **Rehearse with playback** — Place audio files at paths listed in `master_sound_assets.xlsx`, then run the soundboard live.
5. **Screenplay updates** — Re-extract text from an updated PDF, revise `tools/cues_data.py`, and regenerate.

## Source of Truth

All cues are derived from `Wet Hot American Summer_v2.pdf` (90 pages, Second Draft, February 23, 2026). The extracted screenplay text is archived at `assets/generated/screenplay_extract.txt` for audit and diffing.
