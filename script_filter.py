#!/usr/bin/env python3
"""Alfred Script Filter for Caffeine workflow."""

import json
import os
import subprocess
import sys


def is_caffeinated():
    """Check if caffeinate is currently running (started by this workflow)."""
    pid = get_caffeinate_pid()
    if not pid:
        return False, None, None
    # Read remaining time info
    data_dir = os.environ.get("alfred_workflow_data", "/tmp/alfred_caffeine")
    info_file = os.path.join(data_dir, "caffeinate_info")
    mode = "indefinite"
    end_time = None
    if os.path.exists(info_file):
        with open(info_file) as f:
            lines = f.read().strip().split("\n")
            if len(lines) >= 1:
                mode = lines[0]
            if len(lines) >= 2:
                end_time = lines[1]
    return True, mode, end_time


def get_caffeinate_pid():
    """Get PID of caffeinate process started by this workflow."""
    data_dir = os.environ.get("alfred_workflow_data", "/tmp/alfred_caffeine")
    pid_file = os.path.join(data_dir, "caffeinate.pid")
    if not os.path.exists(pid_file):
        return None
    with open(pid_file) as f:
        pid = f.read().strip()
    if not pid:
        return None
    # Verify process is still running
    try:
        subprocess.check_output(["kill", "-0", pid], stderr=subprocess.DEVNULL)
        return pid
    except subprocess.CalledProcessError:
        # Process no longer running, clean up
        try:
            os.remove(pid_file)
        except OSError:
            pass
        return None


def format_duration(minutes):
    """Format minutes into human-readable duration."""
    if minutes < 60:
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    hours = minutes // 60
    mins = minutes % 60
    if mins == 0:
        return f"{hours} hour{'s' if hours != 1 else ''}"
    return f"{hours}h {mins}m"


def build_items(query):
    """Build Alfred items based on query and current state."""
    active, mode, end_time = is_caffeinated()
    items = []
    query = query.strip().lower() if query else ""

    if active:
        # Show status and off option
        if mode == "indefinite":
            status_sub = "Running indefinitely"
        elif mode.startswith("timed:"):
            import datetime
            try:
                end_ts = float(end_time) if end_time else 0
                end_dt = datetime.datetime.fromtimestamp(end_ts)
                now = datetime.datetime.now()
                remaining = end_dt - now
                if remaining.total_seconds() > 60:
                    mins = int(remaining.total_seconds() / 60)
                    status_sub = f"~{format_duration(mins)} remaining (until {end_dt.strftime('%H:%M')})"
                elif remaining.total_seconds() > 0:
                    status_sub = f"Less than a minute remaining (until {end_dt.strftime('%H:%M')})"
                else:
                    status_sub = "Timer expired"
            except (ValueError, OSError):
                status_sub = "Timed session active"
        else:
            status_sub = "Active"

        status_item = {
            "title": "☕ Caffeinated",
            "subtitle": status_sub,
            "valid": False,
            "icon": {"path": "icon.png"},
        }

        off_item = {
            "title": "Decaffeinate",
            "subtitle": "Stop keeping your Mac awake",
            "arg": "off",
            "icon": {"path": "icon.png"},
        }

        toggle_item = {
            "title": "Toggle Caffeination",
            "subtitle": "Currently ON — will turn OFF",
            "arg": "toggle",
            "icon": {"path": "icon.png"},
        }

        candidates = [status_item, off_item, toggle_item]
    else:
        on_item = {
            "title": "Caffeinate",
            "subtitle": "Keep your Mac awake indefinitely",
            "arg": "on",
            "icon": {"path": "icon.png"},
        }

        toggle_item = {
            "title": "Toggle Caffeination",
            "subtitle": "Currently OFF — will turn ON",
            "arg": "toggle",
            "icon": {"path": "icon.png"},
        }

        candidates = [on_item, toggle_item]

    # If query is a number, show timed option
    try:
        minutes = int(query)
        if minutes > 0:
            timed_item = {
                "title": f"Caffeinate for {format_duration(minutes)}",
                "subtitle": f"Keep your Mac awake for {format_duration(minutes)}",
                "arg": f"time:{minutes}",
                "icon": {"path": "icon.png"},
            }
            items.insert(0, timed_item)
    except ValueError:
        pass

    # Filter candidates by query (match title, subtitle, or arg)
    for item in candidates:
        if not query:
            items.append(item)
        else:
            searchable = item["title"].lower() + " " + item.get("subtitle", "").lower() + " " + item.get("arg", "").lower()
            if query in searchable:
                items.append(item)

    if not items:
        items.append({
            "title": "No matching commands",
            "subtitle": "Try: a number for timed, or 'on', 'off', 'toggle'",
            "valid": False,
        })

    return items


def main():
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    items = build_items(query)
    output = {"items": items}
    print(json.dumps(output))


if __name__ == "__main__":
    main()
