# Plainwell Shop Dashboard - Setup Complete

**Date:** February 3, 2026  
**Location:** shop.coresteensma.com (Port 5001)  
**Status:** ✅ READY FOR PLAINWELL DATA

---

## ✅ What's Been Completed

### Code Migration (BC → Plainwell)
- ✅ Mechanics updated: Derek Snyder, Chris Deman, Brandon Wallace
- ✅ Weather location: Plainwell, MI
- ✅ Address: Steensma Lawn Plainwell, MI
- ✅ Support for 'p' prefix mechanic names (pDerek Snyder, pChris Deman, etc.)
- ✅ Support for House Account and Fit-In categories
- ✅ CSV and Text file formats supported

### Files Modified
- `/home/ubuntu/shopmgr/app.py` (backed up as `app.py.backup_BC_*`)
- `/home/ubuntu/shopmgr/templates/dashboard.html` (backed up as `dashboard.html.backup_BC_*`)
- `/home/ubuntu/shopmgr/file_watcher.py` (auto-converter enhanced)

---

## 📋 DAILY WORKFLOW - Export from Infinity

### Step 1: Export as TEXT from Infinity

Export these 3 reports as **TEXT format** (.txt):

#### 1️⃣ Shop Schedule Report
- **Export as:** `Scheduled Shop Jobs - [DATE].txt`
- **Place in:** `/home/ubuntu/shopmgr/datasheets/`
- **Format:** Tab-delimited with columns including:
  - Mechanic names: pDerek Snyder, pChris Deman, pBrandon Wallace
  - Special categories: .pHouse Account, Fit-In

#### 2️⃣ Gross Profit / Sales Report  
- **Export as:** `Sales and Gross - [DATE].txt`
- **Place in:** `/home/ubuntu/shopmgr/datasheets/`
- **Format:** CSV-like with mechanic rows starting with:
  - `pBrandon Wallace,` (with invoice details)
  - `pDerek Snyder,` (with invoice details)
  - `pChris Deman,` (with invoice details)
- **Required columns:**
  - Time Billed (HH:MM format)
  - Time Actual (HH:MM format)
  - Labor Sales ($XXX.XX format)

#### 3️⃣ Open Back Orders (Optional)
- **Export as:** `Open Back Orders - [DATE].txt`
- **Place in:** `/home/ubuntu/shopmgr/datasheets/`
- **Shows:** Parts received/released for payment

---

## 🚀 Quick Start Instructions

### Option A: Text Export (RECOMMENDED - Easiest)

```bash
# 1. Export from Infinity as TEXT
# 2. Upload to server
scp "Sales and Gross - 2-4-26.txt" ubuntu@your-server:/home/ubuntu/shopmgr/datasheets/
scp "Scheduled Shop Jobs - 2-4-26.txt" ubuntu@your-server:/home/ubuntu/shopmgr/datasheets/

# 3. Dashboard auto-refreshes every 5 minutes!
```

### Option B: Excel Export (If needed)

```bash
# If you have Excel files with corrupt styles:
cd /home/ubuntu/shopmgr/datasheets

# Convert manually using Python:
python3 << 'PY'
import zipfile, xml.etree.ElementTree as ET, csv

def xlsx_to_csv(xlsx_file, csv_file):
    with zipfile.ZipFile(xlsx_file, 'r') as z:
        shared_strings = []
        try:
            with z.open('xl/sharedStrings.xml') as f:
                tree = ET.parse(f)
                root = tree.getroot()
                ns = {'': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                for si in root.findall('.//t', ns):
                    shared_strings.append(si.text or '')
        except: pass
        
        with z.open('xl/worksheets/sheet1.xml') as f:
            tree = ET.parse(f)
            root = tree.getroot()
            ns = {'': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            
            rows_data = []
            for row in root.findall('.//row', ns):
                row_data = []
                for cell in row.findall('.//c', ns):
                    cell_type = cell.get('t')
                    v = cell.find('v', ns)
                    if v is not None and v.text:
                        if cell_type == 's':
                            idx = int(v.text)
                            row_data.append(shared_strings[idx] if idx < len(shared_strings) else '')
                        else:
                            row_data.append(v.text)
                    else:
                        row_data.append('')
                if row_data:
                    rows_data.append(row_data)
            
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerows(rows_data)
    print(f"✓ Converted {len(rows_data)} rows")

# Convert your files:
xlsx_to_csv('Feb Shop Report.xlsx', 'Scheduled Shop Jobs - 2-4-26.csv')
xlsx_to_csv('Feb Gross Profit.xlsx', 'Sales and Gross - 2-4-26.csv')
PY
```

---

## 📁 File Naming Patterns (Auto-Detection)

The app automatically finds the **most recent** file matching these patterns:

| Report Type | Pattern Matches | Output Format |
|-------------|----------------|---------------|
| **Schedule** | `Scheduled Shop Jobs`, `Shop Schedule`, `Feb Shop Report` | Today/Tomorrow/Recent jobs |
| **Metrics** | `Sales and Gross`, `Gross Profit`, `Feb Gross Profit` | Derek/Chris/Brandon efficiency & sales |
| **Parts** | `Open Back Orders`, `Open ROs` | Parts received/released |

**Date doesn't matter** - app picks the newest file!

---

## 🧪 Testing Your Setup

```bash
# 1. Start the dashboard
cd /home/ubuntu/shopmgr
source venv/bin/activate
python app.py

# 2. Check in browser
# Visit: http://shop.coresteensma.com
# Or: http://localhost:5001

# 3. Verify data loads
curl http://localhost:5001/api/data | python3 -m json.tool

# 4. Check for errors in logs
tail -f /tmp/shopmgr.log
```

---

## 🔍 Verification Checklist

After uploading new files, verify:

- [ ] **Weather:** Shows "Plainwell, MI"
- [ ] **Address:** Shows "Steensma Lawn Plainwell, MI"
- [ ] **Today's Schedule:** Lists jobs for Derek/Chris/Brandon
- [ ] **Fit-Ins/House Account:** Special jobs appear in their section
- [ ] **Mechanic Metrics:** Shows efficiency % and labor sales for:
  - Derek Snyder
  - Chris Deman  
  - Brandon Wallace
- [ ] **Parts Received:** Shows inventory (if you exported Open Back Orders)

---

## 🛠️ Troubleshooting

### No data appearing?
```bash
# Check what files are present
ls -lh /home/ubuntu/shopmgr/datasheets/*.{txt,csv}

# Check app can find files
cd /home/ubuntu/shopmgr
source venv/bin/activate
python -c "from app import get_latest_file; print('Schedule:', get_latest_file(['Scheduled Shop Jobs', 'Shop Schedule'])); print('Metrics:', get_latest_file(['Sales and Gross', 'Gross Profit']))"
```

### Mechanic names not matching?
Check that your Infinity export includes mechanic names exactly as:
- `pDerek Snyder` or `Derek Snyder`
- `pChris Deman` or `Chris Deman`  
- `pBrandon Wallace` or `Brandon Wallace`

### Wrong cell locations in Excel?
If using Excel format and metrics show 0, update cell references in `app.py` lines 344-346:
```python
mechanics = {
    'Derek Snyder': {'efficiency_cell': 'G120', 'labor_cell': 'O119'},
    'Chris Deman': {'efficiency_cell': 'G189', 'labor_cell': 'O188'},
    'Brandon Wallace': {'efficiency_cell': 'G233', 'labor_cell': 'O232'}
}
```

---

## 🔄 Auto-Refresh

Dashboard automatically refreshes every **5 minutes**. No need to reload the page!

---

## 📂 Directory Structure

```
/home/ubuntu/shopmgr/
├── app.py                          # Main application
├── templates/
│   └── dashboard.html              # Dashboard UI
├── datasheets/                     # 👈 DROP YOUR FILES HERE
│   ├── Scheduled Shop Jobs - 2-4-26.txt
│   ├── Sales and Gross - 2-4-26.txt
│   └── Open Back Orders - 2-4-26.txt
├── archive/                        # Automatic daily backups
│   └── 2026-02-03/
│       └── [old files]
└── file_watcher.py                 # Optional: Auto-converter for Excel
```

---

## 🎯 Production Deployment

```bash
# Start dashboard on boot (systemd service)
sudo tee /etc/systemd/system/shopmgr.service << 'EOF'
[Unit]
Description=Steensma Shop Manager Dashboard
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/shopmgr
Environment="PATH=/home/ubuntu/shopmgr/venv/bin"
ExecStart=/home/ubuntu/shopmgr/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable shopmgr
sudo systemctl start shopmgr
sudo systemctl status shopmgr
```

---

## 📞 Quick Reference

| Item | Value |
|------|-------|
| **Dashboard URL** | http://shop.coresteensma.com |
| **Port** | 5001 |
| **Upload Directory** | `/home/ubuntu/shopmgr/datasheets/` |
| **File Format** | Text (.txt) or CSV (.csv) |
| **Refresh Rate** | Every 5 minutes |
| **Mechanics** | Derek Snyder, Chris Deman, Brandon Wallace |

---

## ✅ Next Steps

1. **From home:** Export your 3 reports from Infinity as TEXT
2. **Upload** them to `/home/ubuntu/shopmgr/datasheets/`
3. **Wait 5 minutes** (or restart app immediately)
4. **View dashboard** at http://shop.coresteensma.com
5. **Repeat daily** with fresh exports

**That's it! No conversions, no Excel corruption issues!** 🎉

---

*Last updated: February 3, 2026*  
*Migration: Battle Creek → Plainwell Complete*
