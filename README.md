# Kuo Photo Image Organizer

Simple Windows tool to organize JPG/JPEG files into folders by the 4 digits after IMGK/IMG_, with a small Flask web UI. Includes an extra QR helper to pull QR_*.jpg out of nested `QR` folders.

## Features
- Grouping rule: use 4 digits after `IMGK` or `IMG_` (case-insensitive)
- Extensions: `.jpg`, `.jpeg`
- Collision handling: appends (1), (2), …
- Web UI: dark/light theme (Dracula default), QR extra actions
- CLI: fast batch operations, optional `--extract-qr`

## Binaries
- `dist/web_organize.exe` (Web UI)
- `dist/organize_jpgs.exe` (CLI)

## Quick Start (Web)
1. Run `dist/web_organize.exe`
2. Open `http://127.0.0.1:5000`
3. Set folder, choose scope, optionally enable:
   - Copy mode (preserve originals)
   - Extract QR (move or copy QR_*.jpg out of child `QR` folders; removes empty `QR` in move mode)
4. Preview first, then Execute

## CLI Usage
```
# Preview, process first-level subfolders
organize_jpgs.exe "D:\\Photos\\Root" --scope subdirs --dry-run

# Execute recursively and extract QR first
organize_jpgs.exe "D:\\Photos\\Root" --scope recursive --extract-qr

# Copy instead of move (keeps originals, does not delete QR folders)
organize_jpgs.exe "D:\\Photos\\Root" --copy
```

## Build (Reproducible)
- Specs are versioned: `web_organize.spec`, `organize_jpgs.spec`
- Frozen requirements snapshot: `requirements.freeze.txt`

Option A: One-liner script (recommended on Windows):
```
powershell -ExecutionPolicy Bypass -File .\\build\\build_windows_exe.ps1
```

Option B: Manual
```
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.freeze.txt
pip install pyinstaller
pyinstaller web_organize.spec
pyinstaller organize_jpgs.spec
```

## Notes
- Web UI uses Flask and bundles templates for PyInstaller one-file mode
- Console window is enabled for `web_organize.exe` for easy logs
- Antivirus may need an exclusion for the `dist/` folder

## License
Proprietary. All rights reserved by the author.
