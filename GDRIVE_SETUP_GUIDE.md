# Google Drive Sync Setup Guide
## Automated Shop Manager Updates via Email

This guide explains how to set up automatic file syncing from email → Google Drive → shop.coresteensma.com

---

## 📋 Overview

### Workflow
1. **You**: Create report in Infinity → Save to OneDrive/Documents/Plainwell/metrics/
2. **You**: Open Outlook → Email attachment to `jdean64@gmail.com` with subject "shopmgr"
3. **Gmail**: Rule automatically saves attachment to Google Drive `/shopmgr` folder
4. **Server**: `gdrive_sync.py` detects new file → Downloads to `~/shopmgr/datasheets/`
5. **Server**: `file_watcher.py` detects new file → Converts to CSV
6. **Server**: `app.py` (shop.coresteensma.com) automatically displays updated data

### Benefits
- ✅ Near real-time updates without API access
- ✅ Simple email workflow - no special tools needed
- ✅ Automatic processing end-to-end
- ✅ Audit trail (files archived automatically)
- ✅ Works from anywhere (just send an email!)

---

## 🔧 Setup Steps

### 1. Configure Gmail Rule

1. **Open Gmail** (jdean64@gmail.com)

2. **Create a new Filter**:
   - Click the search box dropdown arrow (or search options)
   - Set criteria:
     - **From**: (your email address)
     - **Subject**: `shopmgr`
     - **Has attachment**: Yes
   - Click "Create filter"

3. **Filter Actions**:
   - Check: "Skip the Inbox (Archive it)"
   - Check: "Star it" (optional, makes it easy to find)
   - Check: "Apply the label" → Create new label "ShopMgr"
   - **Important**: Check "Also apply filter to matching conversations"

4. **Save Attachment to Google Drive**:
   - Unfortunately Gmail doesn't have a built-in "save to Drive" filter action
   - **Option A**: Use Gmail Add-on like "Save Emails to Google Drive" or "cloudHQ"
   - **Option B**: Use Zapier/IFTTT to create automation:
     - Trigger: New email matching filter (subject: shopmgr)
     - Action: Save attachment to Google Drive folder `/shopmgr`

### 2. Verify Google Drive Folder

1. **Open Google Drive** (jdean64@gmail.com)

2. **Create folder** if it doesn't exist:
   - Create folder named: `shopmgr`
   - This is where email attachments will be saved

3. **Test it**:
   - Email yourself at jdean64@gmail.com with subject "shopmgr" and an Excel attachment
   - Verify the attachment appears in Google Drive `/shopmgr` folder

### 3. Configure rclone (Already Done!)

The server already has rclone configured with Google Drive. To verify:

```bash
rclone listremotes
# Should show: gdrive:

rclone lsd gdrive:
# Should list your Google Drive folders
```

If you need to reconfigure:
```bash
rclone config
```

### 4. Start the Sync Services

There are two services that need to run:

#### A. Google Drive Sync (NEW!)
```bash
cd ~/shopmgr
python3 gdrive_sync.py
```

This watches Google Drive and downloads new files to `datasheets/`

#### B. File Watcher (Already Running?)
```bash
cd ~/shopmgr
python3 file_watcher.py
```

This watches `datasheets/` and converts Excel → CSV

### 5. Run Both Services as Systemd Services (Recommended)

Create service files so they start automatically:

#### Create `/etc/systemd/system/shopmgr-gdrive-sync.service`:
```ini
[Unit]
Description=Shop Manager Google Drive Sync
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/shopmgr
ExecStart=/home/ubuntu/shopmgr/venv/bin/python3 /home/ubuntu/shopmgr/gdrive_sync.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Create `/etc/systemd/system/shopmgr-file-watcher.service`:
```ini
[Unit]
Description=Shop Manager File Watcher
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/shopmgr
ExecStart=/home/ubuntu/shopmgr/venv/bin/python3 /home/ubuntu/shopmgr/file_watcher.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Enable and start services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable shopmgr-gdrive-sync
sudo systemctl enable shopmgr-file-watcher
sudo systemctl start shopmgr-gdrive-sync
sudo systemctl start shopmgr-file-watcher
```

#### Check status:
```bash
sudo systemctl status shopmgr-gdrive-sync
sudo systemctl status shopmgr-file-watcher
```

---

## 📧 Daily Usage

### Simple 3-Step Process:

1. **Generate your report** in Infinity
   - Save to OneDrive/Documents/Plainwell/metrics/ (or anywhere)

2. **Send email** to jdean64@gmail.com
   - Subject: **shopmgr**
   - Attach your Excel file(s)
   - Can attach multiple files in one email!

3. **Done!** 
   - Within ~2 minutes, shop.coresteensma.com will update automatically

### What Happens Behind the Scenes:

```
Email arrives
    ↓ (~instant)
Gmail saves to GDrive
    ↓ (~60 seconds - next sync check)
gdrive_sync.py downloads
    ↓ (~5 seconds)
file_watcher.py converts to CSV
    ↓ (~2 seconds)
shop.coresteensma.com shows new data
```

---

## 📊 Supported Files

The system recognizes these file patterns:

| Email Attachment Name Contains | Converts To | Dashboard Section |
|-------------------------------|-------------|-------------------|
| "Shop Schedule" or "Feb Shop Report" | Scheduled Shop Jobs | Shop Schedule |
| "Gross Profit" or "Feb Gross Profit" | Sales and Gross | Sales/Gross Profit |
| "Open Back Orders" or "Open ROs" | Open Back Orders | Back Orders |

**File requirements**:
- Must be `.xlsx` format (Excel 2007+)
- Will be automatically converted to CSV
- Original files archived in `~/shopmgr/archive/YYYY-MM-DD/`

---

## 🔍 Monitoring & Troubleshooting

### Check Logs
```bash
# Google Drive sync log
tail -f ~/shopmgr/gdrive_sync.log

# Check service status
sudo systemctl status shopmgr-gdrive-sync
sudo systemctl status shopmgr-file-watcher
sudo journalctl -u shopmgr-gdrive-sync -f
```

### Manual Test

1. **Upload directly to Google Drive**:
   - Upload a test Excel file to Google Drive `/shopmgr` folder
   - Within 60 seconds it should download

2. **Check what's in datasheets**:
   ```bash
   ls -lh ~/shopmgr/datasheets/
   ```

3. **Manually trigger sync**:
   ```bash
   cd ~/shopmgr
   rclone copy gdrive:shopmgr ~/shopmgr/datasheets/ -v
   ```

### Common Issues

**Problem**: Files not appearing in Google Drive
- **Check**: Gmail filter is working (search for "label:ShopMgr")
- **Check**: Email subject is exactly "shopmgr" (case insensitive)
- **Fix**: Use Gmail add-on or Zapier as described in Setup Step 1

**Problem**: Files in Google Drive but not downloading
- **Check**: `sudo systemctl status shopmgr-gdrive-sync`
- **Check**: `tail ~/shopmgr/gdrive_sync.log`
- **Fix**: Restart service: `sudo systemctl restart shopmgr-gdrive-sync`

**Problem**: Files downloaded but not converted
- **Check**: `sudo systemctl status shopmgr-file-watcher`
- **Check**: File name matches one of the supported patterns
- **Fix**: Ensure file_watcher.py is running

---

## 🔐 Security Notes

- Gmail filter only accepts emails from your trusted address
- Google Drive folder can be set to private
- Server uses rclone with OAuth tokens (no passwords stored)
- Original files are archived, not deleted
- All activity is logged

---

## 🎯 Configuration Options

Edit `/home/ubuntu/shopmgr/gdrive_sync.py`:

```python
# Line ~15
GDRIVE_FOLDER = "shopmgr"  # Change Google Drive folder name

# Line ~17
CHECK_INTERVAL = 60  # Change check frequency (seconds)

# Line ~113
delete_from_gdrive(filename)  # Uncomment to auto-delete after sync
```

---

## 📞 Questions?

- Check logs: `~/shopmgr/gdrive_sync.log`
- Monitor activity: `sudo systemctl status shopmgr-gdrive-sync`
- Test manually: Upload file directly to Google Drive `/shopmgr` folder

The system is designed to "just work" - send the email and forget about it! ✉️ → 📊
