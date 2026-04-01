# Caffeine for Alfred

## Overview

Alfred workflow that prevents Mac from sleeping using macOS native `caffeinate` command.
Keyword: `caf`

## Project Structure

- `script_filter.py` — Alfred Script Filter. Outputs JSON items based on query and current caffeinate state.
- `action.sh` — Executes caffeinate actions (on/off/toggle/timed). Manages PID tracking and process lifecycle.
- `info.plist` — Alfred workflow definition. Connects Script Filter → Run Script → Notification.
- `icon.png` — Workflow icon (256x256, coffee cup).
- `Caffeine.alfredworkflow` — Packaged workflow (zip). **Not tracked in git**, distributed via GitHub Releases only.

## Build & Release

Package the workflow:

```sh
zip -j Caffeine.alfredworkflow info.plist script_filter.py action.sh icon.png
```

Create a release:

```sh
gh release create v<version> Caffeine.alfredworkflow --repo lnto3408/alfred_caffeine --title "v<version>" --notes "..."
```

## Testing

Run locally without Alfred:

```sh
export alfred_workflow_data="/tmp/alfred_caffeine"

# Script filter
python3 script_filter.py ""       # list commands
python3 script_filter.py "30"     # timed option
python3 script_filter.py "off"    # filter by keyword

# Actions
bash action.sh "on"               # start indefinitely
bash action.sh "off"              # stop
bash action.sh "toggle"           # toggle
bash action.sh "time:30"          # start for 30 minutes
```

After testing, always verify no orphan processes remain:

```sh
pgrep caffeinate
```

## Key Details

- PID file and state are stored in `$alfred_workflow_data/` (Alfred sets this per-workflow).
- `caffeinate` is launched with `nohup` and flags `-d -i -s` (display, idle, system sleep prevention).
- `script_filter.py` checks PID file to determine current state and validates the process is alive via `kill -0`.
- No external dependencies — uses only Python 3 (macOS built-in) and standard shell utilities.
