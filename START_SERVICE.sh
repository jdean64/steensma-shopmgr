#!/bin/bash
# Start Steensma Shop Manager using systemd service
# This is the recommended way to run the dashboard

echo "🔧 Steensma Shop Manager - Service Control"
echo "=========================================="
echo

# Kill any manual processes first
if pgrep -f "python.*app.py" > /dev/null; then
    echo "⚠️  Found manual Python process, stopping..."
    pkill -9 -f "python.*app.py"
    sleep 2
fi

# Enable and start service
echo "🚀 Starting systemd service..."
sudo systemctl enable shopmgr
sudo systemctl start shopmgr
sleep 2

# Check status
if systemctl is-active --quiet shopmgr; then
    echo "✅ Service is running"
    echo
    echo "Status:"
    sudo systemctl status shopmgr --no-pager -l
    echo
    echo "🌐 Dashboard: http://localhost:5001"
    echo "🌐 Public:    https://shop.coresteensma.com"
    echo "💚 Health:    http://localhost:5001/health"
    echo
    echo "Useful commands:"
    echo "  sudo systemctl status shopmgr   - Check status"
    echo "  sudo systemctl restart shopmgr  - Restart service"
    echo "  sudo systemctl stop shopmgr     - Stop service"
    echo "  sudo journalctl -u shopmgr -f   - View live logs"
else
    echo "❌ Service failed to start"
    echo
    sudo journalctl -u shopmgr -n 20 --no-pager
fi
