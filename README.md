# Steensma Shop Manager Dashboard

A daily operations dashboard for Steensma Lawn Battle Creek shop management, displaying schedules, parts inventory, and mechanic performance metrics.

## Features

- **Daily Shop Schedule**: Displays today's schedule, tomorrow's schedule, and fit-in jobs
- **Parts Received**: Shows parts in stock with "Received" or "Released for Payment" status
- **Mechanic Metrics**: Displays efficiency and labor sales for Dennis Smurr, Jake Glas, and Ray Page
- **Real-time Updates**: Auto-refreshes every 5 minutes
- **Weather Widget**: Shows current weather for Battle Creek, MI
- **Responsive Design**: Clean, modern interface with Steensma branding

## Installation

1. **Create virtual environment**:
   ```bash
   cd /home/ubuntu/shopmgr
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## File Requirements

Place the following files in the `/home/ubuntu/shopmgr/datasheets/` directory:

1. **Shop Schedule - 5 Day - [DATE].xlsx**
   - Contains daily schedule with `ScheduledStartTime` column for today/tomorrow
   - `Mechanic` column for identifying Fit-In jobs

2. **Open Back Orders - [DATE].xls**
   - Column R: Status (filter for "Received" or "Released for Payment")
   - Column J: Part Number
   - Customer column: Customer name

3. **Gross Profit Mechanic - [DATE] - Graphic.xls**
   - Fixed cell locations:
     - Dennis Smurr: Efficiency G120, Labor Sales O119
     - Jake Glas: Efficiency G189, Labor Sales O188
     - Ray Page: Efficiency G233, Labor Sales O232

## Running the Application

```bash
cd /home/ubuntu/shopmgr
source venv/bin/activate
python app.py
```

The dashboard will be available at: `http://localhost:5001`

## File Naming Convention

The application automatically finds the most recent files matching these patterns:
- `Shop Schedule` (for shop schedule files)
- `Open Back Orders` (for parts inventory)
- `Gross Profit Mechanic` (for mechanic metrics)

## Important Notes

### Shop Schedule File Issue

The current "Shop Schedule - 5 Day - 1-15-26.xlsx" file has a formatting corruption issue. To fix:

1. Open the file in Excel or LibreOffice
2. Select all data (Ctrl+A)
3. Copy the data
4. Create a new workbook
5. Paste the data
6. Save as a new .xlsx file

Alternatively, save the file as a CSV and the application can be modified to read CSV format.

### Data Extraction

The application uses the following logic:

**Schedule**:
- Filters rows by `ScheduledStartTime` date (today/tomorrow)
- Identifies Fit-Ins by checking if "Fit-In" appears in the `Mechanic` column

**Parts**:
- Finds header row containing "Status", "Part Number", and "Customer"
- Filters where Status contains "Received" or "Released for Payment"

**Metrics**:
- Extracts values from fixed cell locations for each mechanic
- Calculates overall efficiency as average of three mechanics

## Directory Structure

```
/home/ubuntu/shopmgr/
├── app.py                 # Main Flask application
├── templates/
│   └── dashboard.html     # Dashboard UI template
├── datasheets/            # Input Excel files (place files here)
│   ├── Shop Schedule - 5 Day - [DATE].xlsx
│   ├── Open Back Orders - [DATE].xls
│   └── Gross Profit Mechanic - [DATE].xls
├── archive/               # Historical data (auto-created)
├── requirements.txt       # Python dependencies
├── venv/                  # Virtual environment
└── README.md             # This file
```

## Future Enhancements

1. **File Watching**: Automatic detection of new files in a watched directory (Google Drive)
2. **Historical Tracking**: Compare daily changes and store historical data
3. **Notifications**: Alert when new parts arrive or schedule changes
4. **Mobile Responsive**: Optimize for tablet/mobile viewing
5. **CSV Export**: Export daily reports

## Troubleshooting

**"Could not read Shop Schedule file" error**:
- The Excel file may be corrupted. Resave it as described in "Shop Schedule File Issue" above.

**No data appearing**:
- Check that files are in the `datasheets/` directory
- Verify file names contain the expected patterns
- Check application console for error messages

**Port already in use**:
- Change the port in `app.py`: `app.run(port=5002)`

## Contact

For issues or questions, contact the Steensma IT team.

## Parts Management Features

### No Bins Tracking
Displays parts that need bin location assignments:
- Automatically parses "No Bins - [DATE].txt" files from datasheets/
- Shows: Line code, part number, description, available quantity
- Expandable section in Parts Management area

### Back Orders Over 5 Days
Monitors overdue customer back orders with priority levels:
- Automatically filters "Open Back Orders - [DATE].txt" for items >= 5 days old
- **Priority Levels**:
  - 🔴 Critical: 30+ days old
  - 🟠 High: 15-29 days old
  - 🟡 Medium: 10-14 days old
  - 🟢 Normal: 5-9 days old
- Shows: Customer name, phone, part number, age, status
- Action required: Contact customers about delays

### Purchase Orders Over 30 Days
Tracks long-standing POs by vendor with priority indicators:
- Automatically parses "PO Over 30 - [DATE].txt" for orders >= 30 days old
- Grouped by vendor for efficient follow-up
- **Priority Levels**:
  - 🔴 Critical: 90+ days old
  - 🟠 High: 60-89 days old
  - 🟡 Medium: 45-59 days old
  - 🟢 Normal: 30-44 days old
- Shows: Vendor, PO number, age, status, date placed, item count, total amount
- Action required: Vendor follow-up on delivery

### Gross Profit YTD Tracker
Annual progress monitoring against $7.5M goal:
- Uses "Site Lead - [DATE].txt" quarterly sales data
- Visual progress bar showing completion percentage
- On-track/Behind pace indicator (compares actual vs. expected by month)
- Breakdown by category:
  - New Equipment YTD
  - Parts YTD
  - Labor YTD
- Expected pace: ~8.33% per month, 16.7% by month 2, etc.

All features auto-refresh with daily data file uploads.
