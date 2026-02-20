# Agent Instructions & Project Overview

This document serves as a guide for AI agents working on this project. Please read carefully before making changes.

## 1. Environment & Setup

- **Root Directory**: `c:\Data\app_testing`
- **OS**: Windows
- **Python Environment**:
  - A shared virtual environment exists at `c:\Data\app_testing\.venv`.
  - **CRITICAL**: Always use the python interpreter and pip from this virtual environment.
  - **Execution**: Prefer using full paths to executables or explicitly activating the environment.
    - Python: `c:\Data\app_testing\.venv\Scripts\python.exe`
    - Pip: `c:\Data\app_testing\.venv\Scripts\pip.exe`
  - **Do not** create new virtual environments unless explicitly asked.

## 2. Project Structure

- **`counter/`**: A mobile-first counter app.
  - Status: Successfully built for Android (`flet build apk`).
  - Configuration: `pyproject.toml` defines app name and settings.
  
- **`player/`**: A desktop/music player app.
  - Status: Currently running in native mode with Python-side workarounds.
  - **Key Architecture Decisions**:
    - **Audio**: Uses `pygame` instead of `flet.Audio` or `flet_audio`.
      - *Reason*: The standard Flet client binary (v0.80.5) throws "Unknown control: Audio".
    - **File Selection**: Uses `tkinter.filedialog` instead of `flet.FilePicker`.
      - *Reason*: The standard Flet client binary throws "Unknown control: FilePicker" or "FilePickerResultEvent" errors.
    - **Execution**: Run via standard Python execution (`python main.py`), not `flet run`.

## 3. Known Issues & Constraints

### Flet v0.80.5+ Quirks
- The pre-built Flet client often lacks support for certain controls (`Audio`, `FilePicker`) in this environment without a custom build.
- **Avoid** using `flet.Audio` or `flet.FilePicker` for the `player` app unless a custom client is successfully built and configured.
- **Prefer** pure Python libraries (like `pygame`, `tkinter`, `requests`) for backend logic where Flet controls fail.

### Build Issues
- `flet build windows` has been attempted for `player` but failed with `MSB3073`.
- **User Preference**: The user currently prefers running the app via Python interpreter (`python main.py`) rather than troubleshooting native builds errors (DLLs, CMake, etc.). Focus on getting code running in Python first.

## 4. Common Commands

```powershell
# Run Player App
& "c:\Data\app_testing\.venv\Scripts\python.exe" c:\Data\app_testing\player\src\main.py

# Install Package
& "c:\Data\app_testing\.venv\Scripts\pip.exe" install <package_name>
```
