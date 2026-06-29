# AGENTS.md

## Cursor Cloud specific instructions

This is a small Python project (a sound-cue production kit for a live table read). There are two entry points and no test suite or linter configured.

### Environment
- Python deps live in a virtualenv at `.venv` (created by the startup update script from `requirements.txt`). Use `.venv/bin/python` / `.venv/bin/pip`.
- The soundboard is a Tkinter GUI, so it requires the `python3-tk` system package (installed in the VM image) and an X display. The cloud VM exposes one at `DISPLAY=:1`.

### Running the two components (from repo root)
- Regenerate deliverables: `.venv/bin/python tools/generate_production_kit.py` (must be run from repo root; the script puts `tools/` on `sys.path` itself). It prints page-coverage and asset counts and verifies all 90 screenplay pages are covered.
- Launch the soundboard GUI: `DISPLAY=:1 .venv/bin/python app/soundboard.py`. Controls: NEXT/PREVIOUS/Spacebar navigate cues; PLAY only queues a cue (audio playback is intentionally unimplemented). It reads `data/cues.json`, so run the generator first if that file is missing.

### Gotchas
- `generate_production_kit.py` rewrites the binary `data/*.xlsx` and `docs/*.{docx,pdf}` outputs with fresh internal timestamps on every run, so `git status` shows them as modified even when the underlying data is unchanged (the `data/*.json` exports stay stable). Revert that binary noise (`git checkout -- data/ docs/`) unless the cue data actually changed.
