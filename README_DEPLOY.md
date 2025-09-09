# Deployment Options (No Preinstalled Environment)

This project provides two ways to run on a customer Windows PC without preinstalled Python:

- Standalone executables via PyInstaller (recommended)
- Portable CLI using Python’s Windows embeddable distribution (optional, no web UI)

## 1) Standalone Executables (Recommended)
Produces self-contained `.exe` files that bundle Python.

Build on your machine:

1. Ensure internet access, then run the build script:
   - PowerShell: `powershell -ExecutionPolicy Bypass -File .\\build\\build_windows_exe.ps1`
2. Find outputs under `dist/`:
   - `organize_jpgs.exe` (CLI)
   - `web_organize.exe` (Web UI)

Distribute to the customer:
- Copy the needed `.exe` to the customer’s PC (no install required).

Usage examples (CLI):
- Preview on a root folder and all first-level subfolders:
  - `organize_jpgs.exe "D:\\Photos\\Root" --scope subdirs --dry-run`
- Execute move across all folders recursively:
  - `organize_jpgs.exe "D:\\Photos\\Root" --scope recursive`
- Copy instead of move:
  - `organize_jpgs.exe "D:\\Photos\\Root" --copy`

Web UI:
- Run `web_organize.exe` and open `http://127.0.0.1:5000`

## 2) Portable CLI (No Compiler, No Internet on customer)
If you cannot build EXEs, you can still deliver the CLI using the official Python Windows Embeddable package (no install).

Steps (perform on your machine):
1. Download "Windows embeddable package (64-bit)" for Python 3.12 from python.org.
2. Unzip it into a folder, e.g., `portable_cli\\python\\`.
3. Copy `organize_jpgs.py` next to it and add a `run_cli.bat`:

```
@echo off
setlocal
set PYDIR=%~dp0python
set PY=%PYDIR%\\python.exe
if not exist "%PY%" (
  echo Python embeddable runtime not found under %PYDIR%
  pause
  exit /b 1
)
"%PY%" "%~dp0organize_jpgs.py" %*
```

4. Deliver the `portable_cli` folder to the customer.

Customer usage:
- Double-click `run_cli.bat`, or run from Command Prompt with arguments, e.g.:
  - `run_cli.bat "D:\\Photos\\Root" --scope subdirs --dry-run`

Note: The web UI requires Flask and is not supported in the embeddable (no-pip) setup unless you prebundle dependencies.

## Notes
- File grouping rule: pick the 4 digits after `IMGK` or `IMG_` (case-insensitive) in filenames.
- Supported extensions: `.jpg`, `.jpeg`.
- Name collisions are handled by appending `(1)`, `(2)`, etc.

