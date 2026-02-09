#!/bin/bash
# Quick test of the Google Drive sync workflow

echo "=========================================="
echo "Testing Google Drive Sync Workflow"
echo "=========================================="
echo ""

# Test 1: Check rclone
echo "1️⃣  Checking rclone..."
if rclone version > /dev/null 2>&1; then
    echo "   ✓ rclone is installed"
else
    echo "   ✗ rclone not found!"
    exit 1
fi

# Test 2: Check gdrive remote
echo "2️⃣  Checking Google Drive remote..."
if rclone listremotes | grep -q "gdrive:"; then
    echo "   ✓ gdrive: remote configured"
else
    echo "   ✗ gdrive: remote not configured"
    echo "   Run: rclone config"
    exit 1
fi

# Test 3: Check Google Drive folder
echo "3️⃣  Checking Google Drive folder..."
if rclone lsd gdrive: | grep -q "shopmgr"; then
    echo "   ✓ gdrive:shopmgr folder exists"
else
    echo "   ℹ️  Creating gdrive:shopmgr folder..."
    rclone mkdir gdrive:shopmgr
    echo "   ✓ Created"
fi

# Test 4: Check local directory
echo "4️⃣  Checking local datasheets directory..."
if [ -d "/home/ubuntu/shopmgr/datasheets" ]; then
    echo "   ✓ /home/ubuntu/shopmgr/datasheets exists"
else
    echo "   ✗ Directory not found!"
    exit 1
fi

# Test 5: List files in Google Drive
echo "5️⃣  Checking files in Google Drive..."
FILE_COUNT=$(rclone lsjson gdrive:shopmgr --files-only | jq length 2>/dev/null || echo "0")
echo "   ℹ️  Found $FILE_COUNT file(s) in gdrive:shopmgr"

# Test 6: Create a test file and upload
echo "6️⃣  Testing file upload..."
TEST_FILE="/tmp/shopmgr_test_$(date +%s).txt"
echo "This is a test file created at $(date)" > "$TEST_FILE"
rclone copy "$TEST_FILE" gdrive:shopmgr -v
if [ $? -eq 0 ]; then
    echo "   ✓ Test file uploaded successfully"
    echo "   ℹ️  Check gdrive:shopmgr in your Google Drive web interface"
else
    echo "   ✗ Upload failed"
fi
rm -f "$TEST_FILE"

# Test 7: Test download
echo "7️⃣  Testing file download..."
rclone ls gdrive:shopmgr | head -5
echo ""

echo "=========================================="
echo "✅ Tests complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Set up Gmail filter (see GDRIVE_SETUP_GUIDE.md)"
echo "  2. Install services: sudo ./setup_gdrive_services.sh"
echo "  3. Start services: sudo systemctl start shopmgr-gdrive-sync"
echo "  4. Test by emailing a file to jdean64@gmail.com"
echo ""
