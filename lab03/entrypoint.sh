#!/bin/sh

create_log_file() {
    echo "=== Creating cron log file ==="
    touch /var/log/cron.log
    chmod 666 /var/log/cron.log
    echo "Log file created at /var/log/cron.log"
}

monitor_logs() {
    echo "=== Monitoring cron logs ==="
    tail -n +1 -F /var/log/cron.log
}

run_cron() {
    echo "=== Starting cron daemon ==="
    exec cron -f
}

# Create application directories
mkdir -p /app/data

# Create log file
create_log_file

# Display cron logs in Docker console
monitor_logs &

# Start cron in foreground
run_cron
