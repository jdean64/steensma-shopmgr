# Steensma Shop Manager - Setup & Usage Guide

## 🚀 Quick Start

The Steensma Shop Manager dashboard is now set up and ready to use!

### Access the Dashboard

**Local Access:**
```
http://localhost:5001
```

**Network Access:**
```
http://172.31.24.123:5001
```

### Starting the Application

```bash
cd /home/ubuntu/shopmgr
./start.sh
```

Or for production mode:
```bash
./start.sh prod
```

## 📁 File Management

### Required Files

Place your daily Excel files in the `datasheets/` directory:

```
/home/ubuntu/shopmgr/datasheets/
├── Shop Schedule - 5 Day - [DATE].xlsx
├── Open Back Orders - [DATE].xls
└── Gross Profit Mechanic - [DATE].xls
```

### File Formats Expected

**1. Shop Schedule - 5 Day - [DATE].xlsx**
- **Columns needed:**
  - `ScheduledStartTime` - DateTime field for filtering today/tomorrow
  - `Customer` - Customer name
  - `Description` - Job description
  - `Mechanic` - Mechanic assigned (contains "Fit-In" for fit-in jobs)
  - `Notes` - Additional notes

**2. Open Back Orders - [DATE].xls**
- **Columns needed:**
  - Column with "Status" - Filter for "Received" or "Released for Payment"
  - Column with "Part Number" - Part identification
  - Column with "Customer" - Customer name

**3. Gross Profit Mechanic - [DATE].xls**
- **Fixed cell locations (do not change):**
  - Dennis Smurr: Efficiency at G120, Labor Sales at O119
  - Jake Glas: Efficiency at G189, Labor Sales at O188
  - Ray Page: Efficiency at G233, Labor Sales at O232

## ⚠️ Current File Issue

### Shop Schedule File Corruption

The current "Shop Schedule - 5 Day - 1-15-26.xlsx" file has a formatting corruption that prevents it from being read by Python libraries.

**How to Fix:**

1. Open the file in Microsoft Excel or Google Sheets
2. Select all data (Ctrl+A or Cmd+A)
3. Copy the data (Ctrl+C or Cmd+C)
4. Create a new blank spreadsheet
5. Paste the data (Ctrl+V or Cmd+V)
6. Save the new file with the same naming pattern: `Shop Schedule - 5 Day - MM-DD-YY.xlsx`
7. Place it in the `/home/ubuntu/shopmgr/datasheets/` directory

**Alternative - Convert to CSV:**

The application can be modified to accept CSV files if Excel format continues to have issues. Let me know if you'd prefer this approach.

## 🎨 Dashboard Features

### Today's View

- **Today's Schedule**: Jobs scheduled for today
- **Fit-In Jobs**: Walk-in or urgent jobs marked as "Fit-In"
- **Tomorrow's Schedule**: Next day planning
- **Parts Received**: Parts ready for installation
- **Mechanic Metrics**: Real-time performance data

### Automatic Refresh

The dashboard automatically refreshes data every 5 minutes to stay current.

### Weather Widget

Shows current weather for Battle Creek, MI in the footer.

## 🔄 File Watching (Future Enhancement)

The `file_watcher.py` script can monitor a directory (like Google Drive sync folder) for new files:

```bash
cd /home/ubuntu/shopmgr
source venv/bin/activate
python file_watcher.py
```

This will:
- Detect new Excel files automatically
- Archive old files with timestamps
- Compare daily changes (future feature)

## 📊 Data Flow

```
Daily Excel Files → datasheets/ → Flask App → Web Dashboard
                         ↓
                    archive/
                (Historical Data)
```

## 🔧 Troubleshooting

### Dashboard shows "No data"

1. Check files are in `/home/ubuntu/shopmgr/datasheets/`
2. Verify file names match expected patterns
3. Check Flask console for errors

### "Could not read Shop Schedule file" error

The Excel file needs to be repaired (see "Shop Schedule File Corruption" above).

### Port 5001 already in use

Change the port in `app.py`:
```python
app.run(host='0.0.0.0', port=5002, debug=True)  # Change 5001 to 5002
```

### Application won't start

Ensure virtual environment is activated:
```bash
cd /home/ubuntu/shopmgr
source venv/bin/activate
python app.py
```

## 🎯 Next Steps

### Immediate Actions Needed

1. **Fix Shop Schedule file** - Resave the corrupted Excel file (instructions above)
2. **Test with today's data** - Place fresh files in datasheets folder
3. **Verify cell locations** - Ensure mechanic metrics cells match (G120, O119, etc.)

### Future Enhancements

1. **Google Drive Integration**
   - Sync datasheets folder with Google Drive
   - Automatic file detection and processing

2. **Historical Tracking**
   - Store daily snapshots in database
   - Compare metrics day-over-day
   - Generate weekly/monthly reports

3. **Notifications**
   - Email alerts for new parts received
   - SMS for urgent schedule changes
   - Slack integration for team updates

4. **Advanced Features**
   - Mobile-responsive design improvements
   - Print-friendly views
   - PDF export of daily reports
   - Custom mechanic cell configuration

## 📞 Support

For technical support or feature requests, contact:
- **Developer**: Available in this chat
- **Location**: /home/ubuntu/shopmgr/

## 📝 File Structure Reference

```
/home/ubuntu/shopmgr/
├── app.py                    # Main Flask application
├── start.sh                  # Startup script
├── fix_excel.py              # Excel repair utility
├── file_watcher.py           # File monitoring script
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── SETUP_GUIDE.md           # This file
├── venv/                     # Python virtual environment
├── templates/
│   └── dashboard.html        # Dashboard UI
├── datasheets/               # ⭐ Place daily Excel files here
│   ├── Shop Schedule - 5 Day - [DATE].xlsx
│   ├── Open Back Orders - [DATE].xls
│   └── Gross Profit Mechanic - [DATE].xls
└── archive/                  # Historical data storage
    └── YYYY-MM-DD/
        ├── [archived files]
```

## ⚡ Quick Reference Commands

```bash
# Start dashboard (development)
cd /home/ubuntu/shopmgr && ./start.sh

# Start dashboard (production with gunicorn)
cd /home/ubuntu/shopmgr && ./start.sh prod

# Start file watcher
cd /home/ubuntu/shopmgr && source venv/bin/activate && python file_watcher.py

# Repair corrupted Excel file
cd /home/ubuntu/shopmgr && source venv/bin/activate && python fix_excel.py "path/to/file.xlsx"

# Install/Update dependencies
cd /home/ubuntu/shopmgr && source venv/bin/activate && pip install -r requirements.txt
```

---

**Version**: 1.0  
**Date**: January 15, 2026  
**Status**: ✅ Dashboard Working | ⚠️ Shop Schedule file needs repair
