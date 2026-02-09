# 📧 Email-to-Website Automation - COMPLETE SETUP

## ✅ What's Been Created

Your email-to-website automation system is now ready! Here's what we built:

### 🔧 Core Components

1. **gdrive_sync.py** - Monitors Google Drive folder and syncs files to server
   - Location: `/home/ubuntu/shopmgr/gdrive_sync.py`
   - Checks Google Drive every 60 seconds for new files
   - Downloads Excel files to `~/shopmgr/datasheets/`
   - Logs all activity to `gdrive_sync.log`

2. **file_watcher.py** - Already existed, automatically processes new files
   - Watches `~/shopmgr/datasheets/` for new Excel files
   - Converts .xlsx → .csv automatically
   - Archives originals to `~/shopmgr/archive/`

3. **Systemd Services** - For automatic startup and reliability
   - `shopmgr-gdrive-sync.service` - Google Drive monitoring
   - `shopmgr-file-watcher.service` - File processing

### 📄 Documentation Files

- **GDRIVE_SETUP_GUIDE.md** - Comprehensive setup instructions
- **WORKFLOW_DIAGRAM.txt** - Visual workflow diagram
- **QUICK_START_GDRIVE.sh** - Quick reference guide
- **test_gdrive.sh** - Connection test script
- **setup_gdrive_services.sh** - Service installer

---

## 🚀 How to Complete Setup

### Step 1: Set Up Gmail Automation (ONE TIME)

You need to create a Gmail filter/automation that saves attachments to Google Drive.

**Option A: Use Zapier (Recommended - Easiest)**
1. Go to https://zapier.com
2. Create new Zap:
   - **Trigger**: Gmail - New Email Matching Search
     - Search: `subject:shopmgr has:attachment`
     - From: (your email address)
   - **Action**: Google Drive - Upload File
     - Drive: Your Google Drive (jdean64@gmail.com)
     - Folder: `shopmgr`
     - File: (attachment from email)
3. Test and turn on

**Option B: Use Gmail Add-on**
1. Install "Save Emails and Attachments" by cloudHQ
2. Configure:
   - Filter: Subject contains "shopmgr"
   - Save to: Google Drive → shopmgr folder
   - Save: Attachments only

**Option C: Use IFTTT**
Similar to Zapier - create applet with Gmail → Google Drive

### Step 2: Install Services on Server

```bash
cd ~/shopmgr

# Test connection first
./test_gdrive.sh

# Install services
sudo ./setup_gdrive_services.sh

# Start services
sudo systemctl start shopmgr-gdrive-sync
sudo systemctl start shopmgr-file-watcher

# Verify they're running
sudo systemctl status shopmgr-gdrive-sync
sudo systemctl status shopmgr-file-watcher
```

### Step 3: Test End-to-End

1. **Send test email**:
   - To: jdean64@gmail.com
   - Subject: shopmgr
   - Attach: One of your Excel reports

2. **Watch the magic happen**:
   ```bash
   # In one terminal, watch the sync log
   tail -f ~/shopmgr/gdrive_sync.log
   
   # In another, watch the datasheets folder
   watch -n 2 'ls -lh ~/shopmgr/datasheets/'
   ```

3. **Check the website**:
   - Open https://shop.coresteensma.com
   - Verify data updated (within ~2 minutes)

---

## 📋 Daily Usage (After Setup Complete)

**It's this simple:**

1. Create your report in Infinity
2. Email to `jdean64@gmail.com` with subject `shopmgr`
3. Attach your Excel file
4. Done! ✅

The website updates automatically in ~90-120 seconds.

---

## 📊 Supported Files

Your Excel file name should contain one of these:

| File Name Contains | Converts To | Dashboard Shows |
|-------------------|-------------|-----------------|
| Shop Schedule | Scheduled Shop Jobs | Shop schedule |
| Feb Shop Report | Scheduled Shop Jobs | Shop schedule |
| Gross Profit | Sales and Gross | Sales/profit data |
| Feb Gross Profit | Sales and Gross | Sales/profit data |
| Open Back Orders | Open Back Orders | Back orders |
| Open ROs | Open Back Orders | Back orders |

**Requirements**:
- Format: `.xlsx` (Excel 2007+)
- Will be auto-converted to CSV

---

## 🔍 Monitoring & Logs

### Check if services are running
```bash
sudo systemctl status shopmgr-gdrive-sync
sudo systemctl status shopmgr-file-watcher
```

### View logs
```bash
# Google Drive sync activity
tail -f ~/shopmgr/gdrive_sync.log

# Service logs
sudo journalctl -u shopmgr-gdrive-sync -f
sudo journalctl -u shopmgr-file-watcher -f
```

### Check files
```bash
# What's in datasheets?
ls -lh ~/shopmgr/datasheets/

# What's in Google Drive?
rclone ls gdrive:shopmgr

# Check archive
ls -lh ~/shopmgr/archive/$(date +%Y-%m-%d)/
```

---

## 🛠️ Troubleshooting

### Files not appearing in Google Drive?
```bash
# Check Gmail
# 1. Go to Gmail
# 2. Search: label:ShopMgr OR subject:shopmgr
# 3. Verify emails are arriving

# Verify Zapier/add-on is working
# Check Google Drive web interface: drive.google.com
# Look for /shopmgr folder
```

### Files in Google Drive but not downloading?
```bash
# Check service
sudo systemctl status shopmgr-gdrive-sync

# Check logs
tail -50 ~/shopmgr/gdrive_sync.log

# Manual test
rclone copy gdrive:shopmgr ~/shopmgr/datasheets/ -v

# Restart service
sudo systemctl restart shopmgr-gdrive-sync
```

### Files downloaded but not converted?
```bash
# Check file watcher service
sudo systemctl status shopmgr-file-watcher

# Check file name pattern
ls -lh ~/shopmgr/datasheets/*.xlsx

# Make sure it matches a supported pattern
# Restart service
sudo systemctl restart shopmgr-file-watcher
```

### Website not updating?
```bash
# Check if CSV files exist
ls -lh ~/shopmgr/datasheets/*.csv

# Check website service
sudo systemctl status shopmgr  # or whatever the service name is

# Check recent files
ls -lt ~/shopmgr/datasheets/ | head
```

---

## 🔐 Security

- ✅ Gmail filter only accepts from your email address
- ✅ Google Drive folder is private to your account
- ✅ rclone uses OAuth2 (no passwords stored)
- ✅ Original files are archived, never deleted
- ✅ All activity is logged
- ✅ Services run as limited user (ubuntu)

---

## 🎯 Quick Reference Commands

```bash
# Status
./QUICK_START_GDRIVE.sh

# Start
sudo systemctl start shopmgr-gdrive-sync

# Stop
sudo systemctl stop shopmgr-gdrive-sync

# Restart
sudo systemctl restart shopmgr-gdrive-sync

# Logs
tail -f ~/shopmgr/gdrive_sync.log

# Test
./test_gdrive.sh

# Manual sync
rclone copy gdrive:shopmgr ~/shopmgr/datasheets/ -v
```

---

## 📞 Need Help?

1. **Check the workflow diagram**: `cat ~/shopmgr/WORKFLOW_DIAGRAM.txt`
2. **Run the test**: `cd ~/shopmgr && ./test_gdrive.sh`
3. **Check logs**: `tail -50 ~/shopmgr/gdrive_sync.log`
4. **Review full guide**: `cat ~/shopmgr/GDRIVE_SETUP_GUIDE.md`

---

## 🎉 What You Achieved

You now have a completely automated pipeline from email to live website:

```
Email (Outlook)
    ↓
Gmail (filter)
    ↓
Google Drive (storage)
    ↓
Server (sync + process)
    ↓
Website (live data)
```

**Total automation time**: ~90-120 seconds from email sent to website updated!

No API needed. No manual uploads. Just send an email and forget about it! 🚀

---

## 🔄 Next Steps

1. Set up the Gmail automation (Zapier/add-on)
2. Run `./test_gdrive.sh` to verify connection
3. Install services: `sudo ./setup_gdrive_services.sh`
4. Start services: `sudo systemctl start shopmgr-gdrive-sync shopmgr-file-watcher`
5. Send a test email!

**Once it's working, you'll never have to think about it again.** Just email your reports! 📧✨
