# Shop Manager Dashboard - Testing Checklist

## Pre-Testing Setup (Work Laptop)

### 1. Pull Latest Changes
```bash
cd /home/ubuntu/shopmgr
git pull origin main
```

### 2. Restart Service
```bash
# If running as a service:
sudo systemctl restart shopmgr

# Or if running manually:
pkill -9 -f "python app.py"
cd /home/ubuntu/shopmgr && source venv/bin/activate && python app.py > /tmp/shopmgr.log 2>&1 &
```

### 3. Upload Fresh Data Files
Upload these 4 files to `/home/ubuntu/shopmgr/datasheets/`:
- [ ] Scheduled Shop Jobs - [DATE].txt
- [ ] Open Back Orders - [DATE].txt
- [ ] Site Lead Statement - [DATE].txt
- [ ] No Bins - [DATE].txt (new requirement)
- [ ] PO Over 30 - [DATE].txt (new requirement)

**Note**: Now need 5 files instead of 4!

---

## Testing New Features

### Test 1: No Bins Section ✓
1. Open dashboard: http://localhost:5001
2. Scroll to "Parts Management" section
3. Click "📦 No Bins" to expand
4. **Expected**:
   - Table shows parts needing bin locations
   - Columns: Line Code, Part Number, Description, Available Qty
   - Should match "No Bins - [DATE].txt" file data

### Test 2: Back Orders Over 5 Days ✓
1. Click "⏳ Back Orders Over 5 Days" to expand
2. **Expected**:
   - Only shows back orders >= 5 days old
   - Priority badges with colors:
     - Red (Critical): 30+ days
     - Orange (High): 15-29 days
     - Yellow (Medium): 10-14 days
     - Green (Normal): 5-9 days
   - Shows: Customer, Phone, Part#, Age, Status
   - Sorted by priority (Critical first)

### Test 3: PO Over 30 Days ✓
1. Click "📋 PO Over 30 Days" to expand
2. **Expected**:
   - Only shows POs >= 30 days old
   - Grouped by vendor
   - Priority badges (same color scheme as backorders)
   - Shows: Vendor, PO#, Age, Status, Since date, Items count, Total $
   - Expandable vendor sections

### Test 4: Gross Profit YTD ✓
1. Click "📈 Gross Profit YTD" to expand
2. **Expected**:
   - Total YTD gross profit displayed
   - Progress bar showing % of $7.5M goal
   - Status: "✓ On Track" (green) or "⚠ Behind Pace" (orange)
   - Breakdown: Equipment, Parts, Labor YTD amounts
   - Expected percentage shown (based on current month)

### Test 5: Existing Features Still Work ✓
1. Verify these sections still display correctly:
   - [ ] Today's Schedule
   - [ ] Tomorrow's Schedule
   - [ ] Fit-Ins
   - [ ] House Account Jobs
   - [ ] Mechanic Metrics (Dennis, Jake, Ray)
   - [ ] Quarterly Sales (with targets)

### Test 6: Auto-Refresh ✓
1. Wait 5 minutes
2. **Expected**: Dashboard auto-refreshes without page reload
3. Check browser console (F12) for errors

---

## Data File Requirements (Updated)

### Required Files (Daily Upload):
1. **Scheduled Shop Jobs - [DATE].txt** - Shop schedule
2. **Open Back Orders - [DATE].txt** - Parts inventory (now used for 2 features)
3. **Site Lead Statement - [DATE].txt** - Sales data (now used for 2 features)
4. **No Bins - [DATE].txt** - Parts needing bins (NEW)
5. **PO Over 30 - [DATE].txt** - Purchase orders (NEW)

**Old workflow**: 4 files  
**New workflow**: 5 files (add No Bins + PO Over 30)

---

## Troubleshooting

### No Bins section shows "No data"
- Check: "No Bins - [DATE].txt" file exists in datasheets/
- Check: File is dated today
- Check: File has data (at least 1 row)

### Back Orders section empty
- File must have orders >= 5 days old
- Check column 6 (Age) has numeric values
- Recent orders won't appear (working as designed)

### PO Over 30 section empty
- File must have POs >= 30 days old
- Check age column in PO Over 30 file
- Recent POs won't appear (working as designed)

### Gross Profit shows wrong data
- Check Site Lead - [DATE].txt file
- Verify YTD values in source file
- Calculator: New Equipment + Parts + Labor = Total YTD

### Dashboard won't load
```bash
# Check if app is running:
ps aux | grep python | grep app

# Check logs:
tail -f /tmp/shopmgr.log

# Check port:
netstat -tuln | grep 5001
```

---

## Commit History (All Phases Complete)

- ✅ Phase 1: No Bins parser and display (commit e09a821)
- ✅ Phase 2: Back Orders Over 5 Days (commit 0b7ba4b)
- ✅ Phase 3: PO Over 30 Days (commit 27a99f4)
- ✅ Phase 4: Gross Profit YTD tracker (commit 4772567)
- ✅ Documentation updates (commit 47da0a7)

All changes pushed to: https://github.com/jdean64/steensma-shopmgr

---

## Success Criteria

✅ All 4 new sections expand/collapse properly  
✅ Data displays correctly with proper formatting  
✅ Priority color coding works (critical=red, high=orange, etc.)  
✅ Existing features continue working  
✅ Auto-refresh works every 5 minutes  
✅ No console errors in browser  
✅ Mobile/responsive layout works  

---

## Contact

Issues or questions: Tag @jdean64 in GitHub issues or notify IT team.

**Ready for production testing!** 🚀
