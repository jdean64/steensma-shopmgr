#!/usr/bin/env python3
"""
Google Drive Sync for Steensma Shop Manager
Watches a Google Drive folder for files and syncs them to ~/shopmgr/datasheets/
Works in conjunction with file_watcher.py for automatic processing

Usage:
    ./gdrive_sync.py
    
Configuration:
    Edit GDRIVE_FOLDER below to match your Google Drive folder path
"""
import os
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================
GDRIVE_REMOTE = "gdrive:"  # rclone remote name
GDRIVE_FOLDER = "shopmgr"  # Folder in Google Drive to watch
LOCAL_DIR = "/home/ubuntu/shopmgr/datasheets"
STATE_FILE = "/home/ubuntu/shopmgr/.gdrive_sync_state.json"
CHECK_INTERVAL = 60  # Check every 60 seconds
LOG_FILE = "/home/ubuntu/shopmgr/gdrive_sync.log"

# ============================================================================
# Logging
# ============================================================================
def log(message, also_print=True):
    """Log a message to file and optionally print it"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {message}"
    
    if also_print:
        print(log_msg)
    
    try:
        with open(LOG_FILE, 'a') as f:
            f.write(log_msg + '\n')
    except:
        pass

# ============================================================================
# State Management
# ============================================================================
def load_state():
    """Load the last known state of files in Google Drive"""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_state(state):
    """Save the current state of files in Google Drive"""
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        log(f"Error saving state: {e}")

# ============================================================================
# Google Drive Functions
# ============================================================================
def list_gdrive_files():
    """List all files in the Google Drive folder"""
    try:
        cmd = [
            "rclone", "lsjson",
            f"{GDRIVE_REMOTE}{GDRIVE_FOLDER}",
            "--files-only"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            files = json.loads(result.stdout)
            # Return dict with filename as key, modified time as value
            return {f['Name']: f['ModTime'] for f in files}
        else:
            log(f"Error listing GDrive files: {result.stderr}", also_print=False)
            return None
    except subprocess.TimeoutExpired:
        log("Timeout listing GDrive files", also_print=False)
        return None
    except Exception as e:
        log(f"Exception listing GDrive files: {e}", also_print=False)
        return None

def copy_file_from_gdrive(filename):
    """Copy a file from Google Drive to local datasheets folder"""
    try:
        remote_path = f"{GDRIVE_REMOTE}{GDRIVE_FOLDER}/{filename}"
        local_path = os.path.join(LOCAL_DIR, filename)
        
        log(f"📥 Downloading: {filename}")
        
        cmd = [
            "rclone", "copy",
            remote_path,
            LOCAL_DIR,
            "-v"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0 and os.path.exists(local_path):
            log(f"✓ Downloaded successfully: {filename}")
            return True
        else:
            log(f"✗ Download failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        log(f"✗ Timeout downloading: {filename}")
        return False
    except Exception as e:
        log(f"✗ Error downloading {filename}: {e}")
        return False

def delete_from_gdrive(filename):
    """Delete a file from Google Drive after successful processing"""
    try:
        remote_path = f"{GDRIVE_REMOTE}{GDRIVE_FOLDER}/{filename}"
        
        cmd = ["rclone", "delete", remote_path]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            log(f"🗑️  Removed from GDrive: {filename}")
            return True
        else:
            log(f"⚠️  Could not remove from GDrive: {filename}")
            return False
    except Exception as e:
        log(f"⚠️  Error removing from GDrive: {e}")
        return False

# ============================================================================
# Main Sync Logic
# ============================================================================

# ============================================================================
# REPORT NAME FILTERS - Only download these 6 report types
# ============================================================================
ALLOWED_REPORTS = [
    "No Bins",
    "Open Back Orders",
    "PO Over 30",
    "Sales and Gross",
    "Scheduled Shop Jobs",
    "Site Lead"
]

def is_allowed_report(filename):
    """Check if filename matches one of the 6 allowed report types"""
    # Check if any of the allowed report names are in the filename
    for report_name in ALLOWED_REPORTS:
        if report_name in filename:
            return True
    return False

def check_for_new_files():
    """Check Google Drive for new or modified files"""
    current_files = list_gdrive_files()
    
    if current_files is None:
        return  # Error occurred, skip this check
    
    previous_state = load_state()
    new_or_modified = []
    
    # Find new or modified files
    for filename, mod_time in current_files.items():
        # Only process text/Excel files that match our report types
        if not filename.endswith(('.txt', '.xlsx', '.xls', '.csv')):
            continue
        
        # Filter: Only download the 6 specific report types
        if not is_allowed_report(filename):
            continue
            
        if filename not in previous_state:
            # New file
            new_or_modified.append(filename)
        elif previous_state[filename] != mod_time:
            # Modified file
            new_or_modified.append(filename)
    
    # Process each new/modified file
    for filename in new_or_modified:
        log(f"🔔 New file detected in Google Drive: {filename}")
        
        if copy_file_from_gdrive(filename):
            # Give the file watcher time to process
            time.sleep(5)
            
            # Optionally delete from GDrive after successful download
            # Uncomment the next line if you want to auto-delete after sync
            # delete_from_gdrive(filename)
    
    # Update state
    if new_or_modified:
        save_state(current_files)

def verify_setup():
    """Verify that rclone and Google Drive are properly configured"""
    log("Verifying setup...")
    
    # Check rclone is installed
    try:
        result = subprocess.run(["rclone", "version"], capture_output=True, timeout=5)
        if result.returncode != 0:
            log("✗ rclone not found! Please install rclone first.")
            return False
    except:
        log("✗ rclone not found! Please install rclone first.")
        return False
    
    # Check gdrive remote is configured
    try:
        result = subprocess.run(["rclone", "listremotes"], capture_output=True, text=True, timeout=5)
        if GDRIVE_REMOTE not in result.stdout:
            log(f"✗ rclone remote '{GDRIVE_REMOTE}' not configured!")
            log("  Run: rclone config")
            return False
    except:
        log("✗ Could not check rclone remotes")
        return False
    
    # Check if Google Drive folder exists
    try:
        result = subprocess.run(
            ["rclone", "lsd", f"{GDRIVE_REMOTE}{GDRIVE_FOLDER}"],
            capture_output=True,
            timeout=10
        )
        # If folder doesn't exist, create it
        if result.returncode != 0:
            log(f"ℹ️  Creating folder in Google Drive: {GDRIVE_FOLDER}")
            subprocess.run(
                ["rclone", "mkdir", f"{GDRIVE_REMOTE}{GDRIVE_FOLDER}"],
                timeout=10
            )
    except Exception as e:
        log(f"⚠️  Could not verify GDrive folder: {e}")
    
    # Check local directory exists
    if not os.path.exists(LOCAL_DIR):
        log(f"✗ Local directory not found: {LOCAL_DIR}")
        return False
    
    log("✓ Setup verification complete")
    return True

def main():
    """Main sync loop"""
    print("=" * 70)
    print("Steensma Shop Manager - Google Drive Sync")
    print("=" * 70)
    print(f"Google Drive: {GDRIVE_REMOTE}{GDRIVE_FOLDER}")
    print(f"Local Directory: {LOCAL_DIR}")
    print(f"Check Interval: {CHECK_INTERVAL} seconds")
    print()
    
    if not verify_setup():
        print("\n✗ Setup verification failed. Please fix the issues above.")
        return 1
    
    print()
    print("📧 Workflow:")
    print("  1. Email attachment to jdean64@gmail.com with subject 'shopmgr'")
    print("  2. Gmail rule saves attachment to Google Drive folder")
    print("  3. This script detects the new file and downloads it")
    print("  4. file_watcher.py automatically processes the Excel file")
    print("  5. shop.coresteensma.com updates with new data")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 70)
    print()
    
    log("🚀 Google Drive sync started")
    
    try:
        while True:
            check_for_new_files()
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping Google Drive sync...")
        log("🛑 Google Drive sync stopped")
    except Exception as e:
        log(f"💥 Fatal error: {e}")
        raise
    
    print("✓ Sync stopped.")
    return 0

if __name__ == '__main__':
    exit(main())
