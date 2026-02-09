#!/bin/bash
# Setup script for Google Drive Sync services

echo "=========================================="
echo "Shop Manager - Google Drive Sync Setup"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  This script needs sudo to install systemd services"
    echo "Run with: sudo ./setup_gdrive_services.sh"
    exit 1
fi

echo "📋 Installing systemd services..."
echo ""

# Copy service files
cp /home/ubuntu/shopmgr/shopmgr-gdrive-sync.service /etc/systemd/system/
cp /home/ubuntu/shopmgr/shopmgr-file-watcher.service /etc/systemd/system/

# Set proper permissions
chmod 644 /etc/systemd/system/shopmgr-gdrive-sync.service
chmod 644 /etc/systemd/system/shopmgr-file-watcher.service

# Reload systemd
echo "🔄 Reloading systemd daemon..."
systemctl daemon-reload

# Enable services
echo "✓ Enabling shopmgr-gdrive-sync service..."
systemctl enable shopmgr-gdrive-sync

echo "✓ Enabling shopmgr-file-watcher service..."
systemctl enable shopmgr-file-watcher

echo ""
echo "=========================================="
echo "✅ Services installed and enabled!"
echo "=========================================="
echo ""
echo "To start the services now:"
echo "  sudo systemctl start shopmgr-gdrive-sync"
echo "  sudo systemctl start shopmgr-file-watcher"
echo ""
echo "To check status:"
echo "  sudo systemctl status shopmgr-gdrive-sync"
echo "  sudo systemctl status shopmgr-file-watcher"
echo ""
echo "To view logs:"
echo "  sudo journalctl -u shopmgr-gdrive-sync -f"
echo "  tail -f /home/ubuntu/shopmgr/gdrive_sync.log"
echo ""
