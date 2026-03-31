#!/bin/bash
# Alfred Caffeine - Action handler
# Manages caffeinate process based on argument

DATA_DIR="${alfred_workflow_data:-/tmp/alfred_caffeine}"
PID_FILE="$DATA_DIR/caffeinate.pid"
INFO_FILE="$DATA_DIR/caffeinate_info"

mkdir -p "$DATA_DIR"

start_caffeinate() {
    stop_caffeinate_silent
    # -d: prevent display sleep
    # -i: prevent idle sleep
    # -s: prevent system sleep (on AC power)
    if [ -n "$1" ]; then
        local seconds=$(( $1 * 60 ))
        /usr/bin/caffeinate -d -i -s -t "$seconds" &
        local pid=$!
        echo "$pid" > "$PID_FILE"
        local end_time=$(python3 -c "import time; print(time.time() + $seconds)")
        printf "timed:%s\n%s\n" "$1" "$end_time" > "$INFO_FILE"
        echo "Caffeinated for $(format_duration $1)"
    else
        /usr/bin/caffeinate -d -i -s &
        local pid=$!
        echo "$pid" > "$PID_FILE"
        printf "indefinite\n" > "$INFO_FILE"
        echo "Caffeinated"
    fi
}

stop_caffeinate() {
    stop_caffeinate_silent
    echo "Decaffeinated"
}

stop_caffeinate_silent() {
    if [ -f "$PID_FILE" ]; then
        local pid
        pid=$(cat "$PID_FILE")
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null
            # Also kill any child caffeinate processes
            pkill -P "$pid" 2>/dev/null
        fi
        rm -f "$PID_FILE" "$INFO_FILE"
    fi
    # Also kill any orphaned caffeinate processes started by this workflow
    # (safety net)
}

is_running() {
    if [ -f "$PID_FILE" ]; then
        local pid
        pid=$(cat "$PID_FILE")
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            return 0
        fi
        rm -f "$PID_FILE" "$INFO_FILE"
    fi
    return 1
}

format_duration() {
    local minutes=$1
    if [ "$minutes" -lt 60 ]; then
        echo "${minutes} minute(s)"
    else
        local hours=$((minutes / 60))
        local mins=$((minutes % 60))
        if [ "$mins" -eq 0 ]; then
            echo "${hours} hour(s)"
        else
            echo "${hours}h ${mins}m"
        fi
    fi
}

ACTION="$1"

case "$ACTION" in
    on)
        start_caffeinate
        ;;
    off)
        stop_caffeinate
        ;;
    toggle)
        if is_running; then
            stop_caffeinate
        else
            start_caffeinate
        fi
        ;;
    time:*)
        minutes="${ACTION#time:}"
        start_caffeinate "$minutes"
        ;;
    *)
        echo "Unknown action: $ACTION"
        ;;
esac
