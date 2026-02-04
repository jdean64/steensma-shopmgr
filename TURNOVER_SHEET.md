# Shop Manager Dashboard - Turnover Sheet

## Overview
The **Steensma Shop Manager Dashboard** runs on a laptop at Plainwell HQ (port 5001) and displays real-time shop operations: today's schedule, mechanic efficiency, parts inventory, and quarterly sales metrics. You manage it from home via GitHub—no coding required.

---

## Daily Workflow (Takes ~2 minutes)

### Every Morning Before 8am:
1. **Open Infinity** on the work laptop
2. **Export these 4 text files** (same process each day):
   - Scheduled Shop Jobs
   - Sales and Gross (Individual Page per Mechanic format)
   - Open Back Orders
   - Site Lead Statement (quarterly sales)

3. **Name files** with today's date (e.g., `Feb 5-26.txt`)
4. **Upload** all 4 to the `datasheets` folder on the work laptop:
   ```
   /home/ubuntu/shopmgr/datasheets/
   ```
5. **Done.** Dashboard auto-refreshes within 5 minutes.

### Accessing the Dashboard
- **At work (same laptop):** Open browser → `localhost:5001`
- **From home:** Open browser → `shop.coresteensma.com` (requires VPN/auth) OR use SSH tunnel

---

## How It Works (No Code Knowledge Needed)

The app runs continuously on the work laptop. Each time you upload new files:
1. App auto-detects newest files
2. Parses shop schedule, mechanic metrics, parts, and quarterly sales
3. Updates dashboard live
4. Refreshes every 5 minutes

**Current Targets (Plainwell Q1):**
- New Equipment Sales: **$795,000**
- Parts Sales: **$328,000**

---

## Making Changes from Home (Optional)

If you want to update the app code or targets from home:

### Via GitHub (No Terminal Needed):
1. Go to https://github.com/jdean64/heirfinity
2. Click file to edit → Edit button (pencil icon)
3. Make change (e.g., update bonus targets)
4. Commit with description
5. **Work laptop pulls changes automatically** (runs `git pull` in background)

### Or Use SSH Terminal (If Comfortable):
```bash
cd /home/ubuntu/shopmgr
git pull origin main
```

---

## File Locations

| File | Location | Purpose |
|------|----------|---------|
| App Code | `/home/ubuntu/shopmgr/app.py` | Main backend |
| Dashboard HTML | `/home/ubuntu/shopmgr/templates/dashboard.html` | Frontend display |
| Data Files | `/home/ubuntu/shopmgr/datasheets/` | Daily Infinity exports |
| Backups | `/home/ubuntu/shopmgr/archive/` | Old files (auto-archived) |
| Logs | `/tmp/shopmgr.log` | Debugging info |

---

## Key Metrics Displayed

### Schedule
- **Today's Jobs** - Derek, Chris, Brandon assignments
- **Tomorrow's Jobs** - Lookahead
- **Fit-Ins** - Same-day repairs
- **House Account** - Internal work

### Mechanic Metrics
- **Efficiency %** - Labor hours vs. billable hours
- **Labor Sales** - Gross margin per mechanic
- **Overall % to Target** - Team performance

### Parts
- **Back-Ordered** - Parts waiting to arrive
- **On Order** - Parts in transit
- *(Does NOT show Received/Released—those are admin tracking)*

### Quarterly Sales
- **New Equipment Sales** - Month and YTD $ with progress to $795k target
- **Parts Sales** - Month and YTD $ with progress to $328k target
- **Progress Bars** - Visual indicator toward Q1 bonus

---

## Troubleshooting

### Dashboard Shows Old Data
1. Wait 5 minutes (auto-refresh cycle)
2. Or manually refresh browser (F5 or Cmd+R)
3. Check that files uploaded to `/home/ubuntu/shopmgr/datasheets/`

### Dashboard Won't Load (404 or Blank)
1. Check work laptop is on and connected to network
2. Verify app is running:
   - Open terminal on work laptop
   - Run: `ps aux | grep python | grep app`
   - If empty, restart (see below)

### Dashboard Shows Wrong Data (Old Files)
1. Verify new files uploaded with today's date
2. Delete old .txt files if naming is confusing
3. Refresh browser

### Restart the App (If Needed)
On work laptop, open terminal:
```bash
pkill -9 -f "python app.py"
sleep 2
cd /home/ubuntu/shopmgr && source venv/bin/activate && python app.py > /tmp/shopmgr.log 2>&1 &
```
(App should restart within 2 seconds)

---

## Updating Bonus Targets

If Q1 targets change:
1. Go to GitHub repo: https://github.com/jdean64/heirfinity
2. Find `app.py` → Edit
3. Search for `795000` and `328000`
4. Update both values
5. Commit
6. Work laptop auto-syncs (or manual `git pull`)

Or contact: [Your Name/Support Contact]

---

## GitHub Workflow (From Home)

All code lives in GitHub. To push changes from home:

```bash
cd /path/to/heirfinity
git add .
git commit -m "Description of change"
git push origin main
```

Work laptop automatically pulls latest every 30 minutes (or restart app to sync immediately).

---

## Remote Access (VPN/SSH)

To access work laptop from home:
1. **Web:** Use `shop.coresteensma.com` (if configured for external access)
2. **SSH Tunnel:** 
   ```bash
   ssh -L 5001:localhost:5001 ubuntu@[work-laptop-ip]
   # Then access: http://localhost:5001
   ```

---

## Questions?

| Issue | Contact |
|-------|---------|
| Files not uploading | Check `/home/ubuntu/shopmgr/datasheets/` permissions |
| App crashed | Restart using command above or contact IT |
| Code changes needed | Use GitHub or contact development team |
| Bonus targets need change | Update via GitHub `app.py` lines ~583-584 |

---

## Quick Reference

**Upload folder:** `/home/ubuntu/shopmgr/datasheets/`  
**Dashboard URL (work):** `http://localhost:5001`  
**Dashboard URL (home):** `https://shop.coresteensma.com`  
**GitHub:** `https://github.com/jdean64/heirfinity`  
**Current Q1 Targets:** Equipment $795,000 | Parts $328,000  
**Auto-refresh:** Every 5 minutes  

---

## Summary

✅ Upload 4 files each morning → Dashboard auto-updates  
✅ Manage code from home via GitHub  
✅ No terminals or coding needed for daily use  
✅ Work laptop stays on, app runs 24/7  
✅ Minimal hands-on involvement  

**You're good to go!**
