#!/bin/bash
# Emergency Recovery Script for Shop Manager Dashboard
# Use this if you need to restore from GitHub after a system failure

set -e  # Exit on any error

echo "=========================================="
echo "Shop Manager Emergency Recovery Script"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "ERROR: Not in shopmgr directory. Run this from /home/ubuntu/shopmgr"
    exit 1
fi

# Stop any running instances
echo "1. Stopping any running instances..."
pkill -9 -f "python.*app.py" 2>/dev/null || true
sleep 2

# Pull latest code from GitHub
echo "2. Pulling latest code from GitHub..."
git fetch origin
git reset --hard origin/main
echo "   ✓ Code updated from GitHub"

# Set up virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "3. Creating virtual environment..."
    python3 -m venv venv
    echo "   ✓ Virtual environment created"
else
    echo "3. Virtual environment already exists"
fi

# Activate venv and install/fix dependencies
echo "4. Installing dependencies..."
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Fix NumPy version (critical!)
echo "5. Fixing NumPy version compatibility..."
pip install -q 'numpy<2' --force-reinstall
echo "   ✓ NumPy downgraded to 1.x"

# Start the application
echo "6. Starting Shop Manager Dashboard..."
python app.py &
sleep 3

# Verify it's running
if curl -s http://localhost:5001 > /dev/null 2>&1; then
    echo ""
    echo "=========================================="
    echo "✓ SUCCESS! Dashboard is running"
    echo "=========================================="
    echo ""
    echo "Access at: http://localhost:5001"
    echo ""
    echo "To check status: ps aux | grep app.py"
    echo "To stop: pkill -f 'python.*app.py'"
    echo ""
else
    echo ""
    echo "=========================================="
    echo "⚠ WARNING: App started but not responding"
    echo "=========================================="
    echo ""
    echo "Check logs with: tail -f nohup.out"
    echo "Or run manually: python app.py"
fi
