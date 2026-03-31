# Caffeine for Alfred

Prevent your Mac from sleeping using the native macOS `caffeinate` command.

![Alfred Caffeine](icon.png)

## Installation

1. Download `Caffeine.alfredworkflow` from the [latest release](https://github.com/lnto3408/alfred_caffeine/releases/latest)
2. Double-click the file to install in Alfred

> Requires [Alfred](https://www.alfredapp.com/) with Powerpack.

## Usage

Type `caf` in Alfred to get started.

### Commands

| Input | Action |
|-------|--------|
| `caf` | Show caffeinate / toggle options |
| `caf 30` | Keep awake for 30 minutes |
| `caf 120` | Keep awake for 2 hours |
| `caf off` | Stop caffeination |

### States

**When OFF** — shows options to turn on or toggle.

**When ON** — shows current status (with remaining time for timed sessions), decaffeinate, and toggle options.

## How It Works

Uses macOS built-in `caffeinate` with the following flags:

- `-d` prevent display sleep
- `-i` prevent idle sleep
- `-s` prevent system sleep (on AC power)

Process management is handled via PID files stored in Alfred's workflow data directory. No background daemons or login items required.

## License

MIT
