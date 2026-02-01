#!/bin/bash
# Startup script for Steensma Shop Manager Dashboard

cd /home/ubuntu/shopmgr

# Activate virtual environment
source venv/bin/activate

# Check if running in production or development
if [ "$1" == "prod" ]; then
    echo "Starting Steensma Shop Manager in PRODUCTION mode..."
    echo "Dashboard will be available at: http://$(hostname -I | awk '{print $1}'):5001"
    
    # Use gunicorn for production
    if ! command -v gunicorn &> /dev/null; then
        echo "Installing gunicorn..."
        pip install gunicorn
    fi
    
    gunicorn -w 4 -b 0.0.0.0:5001 app:app
else
    echo "Starting Steensma Shop Manager in DEVELOPMENT mode..."
    echo "Dashboard will be available at: http://localhost:5001"
    echo "Press Ctrl+C to stop"
    
    python app.py
fi
