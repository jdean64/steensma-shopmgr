#!/bin/bash
# Health check monitor for Steensma Shop Manager
# Checks if app is responding and restarts via systemd if not

HEALTH_URL="http://localhost:5001/health"
LOG_FILE="/tmp/shopmgr_monitor.log"
MAX_FAILURES=3
FAILURE_COUNT=0

log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Check if service is running
if ! systemctl is-active --quiet shopmgr; then
    log_message "WARNING: shopmgr service not running, starting..."
    sudo systemctl start shopmgr
    sleep 3
fi

# Health check with timeout
response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$HEALTH_URL" 2>/dev/null)

if [ "$response" != "200" ]; then
    FAILURE_COUNT=$((FAILURE_COUNT + 1))
    log_message "FAILED: Health check returned $response (attempt $FAILURE_COUNT/$MAX_FAILURES)"
    
    if [ $FAILURE_COUNT -ge $MAX_FAILURES ]; then
        log_message "CRITICAL: Max failures reached, restarting service..."
        sudo systemctl restart shopmgr
        FAILURE_COUNT=0
        sleep 5
        
        # Verify restart worked
        new_response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$HEALTH_URL" 2>/dev/null)
        if [ "$new_response" = "200" ]; then
            log_message "SUCCESS: Service restarted and responding"
        else
            log_message "ERROR: Service restart failed, manual intervention needed"
        fi
    fi
else
    # Reset failure count on success
    if [ $FAILURE_COUNT -gt 0 ]; then
        log_message "RECOVERED: Health check passed after $FAILURE_COUNT failures"
        FAILURE_COUNT=0
    fi
fi
