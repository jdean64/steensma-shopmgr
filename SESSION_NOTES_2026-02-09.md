# Session Notes - February 9, 2026

## Executive Summary
Today we prototyped a company-wide multi-dashboard architecture but decided to table it for more thorough implementation. Instead, we added EOS Strategic Planning as an accordion section to the existing shop dashboard for immediate visibility.

## What We Built Today

### 1. Multi-Dashboard Architecture (TABLED - Preserved for Future)
Created a 4-card landing page approach with drill-down detail pages:

**Landing Page Structure:**
- 🔧 Shop Operations card (today/tomorrow jobs, parts requests, efficiency)
- 📈 Sales Performance card (monthly/YTD revenue, target %, top category)
- 📦 Parts Management card (No Bins, PO Over 30, BO Over 5, OSS)
- 🎯 EOS Strategic card (rocks progress, goals on track, open issues)

**Detail Pages Created:**
- `/landing` - Executive summary with 4 cards (works, just not default route)
- `/shop` - Full shop operations (copy of main dashboard)
- `/sales` - Sales revenue breakdown
- `/parts` - CSR tracking tables (No Bins, PO Over 30, BO Over 5)
- `/eos` - Strategic planning detail (rocks, goals, issues)

**New API Endpoint:**
- `/api/summary` - Calculates summary metrics for all 4 cards
- Returns aggregated stats: job counts, efficiency, revenue, parts issues, EOS progress

**Files Created:**
- `templates/landing.html` - 4-card landing page
- `templates/shop.html` - Shop detail page
- `templates/sales.html` - Sales detail page
- `templates/parts.html` - Parts detail page
- `templates/eos.html` - EOS detail page
- `templates/default1.html` - Backup of current dashboard

### 2. EOS Strategic Planning Integration (LIVE NOW)
**What's Live:**
- Added EOS accordion section to main shop dashboard
- Positioned below Gross Profit YTD section
- Collapsible for clean UX

**EOS Accordion Contains:**
- **Quarterly Rocks** - Shows Q1 2026 rocks with owner and status
  - Color-coded by status (Complete: green, On Track: blue, At Risk: orange)
  - Currently shows 8 rocks, 1 complete (12% progress)
  
- **Annual Goals** - Progress bars with current vs. target
  - Percentage completion calculated automatically
  - Currently shows 5 goals, 2 on track (40%)
  - Color-coded progress bars
  
- **Issues List** - Open issues with owner tracking
  - Currently shows 5 open issues
  - Red highlighting for visibility

**Data Source:**
- Reads from `datasheets/Strategic Plan - 2-9-26.txt`
- Pipe-delimited format: `Description|Owner|Status`
- Auto-updates via existing email → Google Drive → Server pipeline

## Current State

### What's Running
- **Main Dashboard:** shop.coresteensma.com (port 5001)
- **Route:** `/` serves `dashboard.html` with EOS accordion
- **Services Active:**
  - `shopmgr.service` - Flask app
  - `shopmgr-gdrive-sync.service` - Google Drive poller (60s)
  - `shopmgr-file-watcher.service` - File processor

### Current Data (as of 3:53 UTC)
**Shop Metrics:**
- Today's jobs: 0
- Tomorrow's jobs: 0
- Parts requests: 4
- Team efficiency: 81%

**Sales Metrics:**
- Monthly revenue: $88,893
- YTD revenue: $523,358
- Target achievement: 77%
- Top category: New Equipment

**Parts Metrics:**
- No Bins: 2 items
- PO Over 30: 15 items
- BO Over 5: 4 items

**EOS Metrics:**
- Rocks: 8 total, 1 complete (12%)
- Goals: 5 total, 2 on track (40%)
- Open issues: 5

### Files & Routes
```
/home/ubuntu/shopmgr/
├── app.py (modified with new routes + /api/summary)
├── templates/
│   ├── dashboard.html (main shop dashboard with EOS accordion)
│   ├── default1.html (backup of dashboard.html)
│   ├── landing.html (multi-dashboard landing - preserved)
│   ├── shop.html (detail page - preserved)
│   ├── sales.html (detail page - preserved)
│   ├── parts.html (detail page - preserved)
│   └── eos.html (detail page - preserved)
```

**Active Routes:**
- `/` → dashboard.html (main shop operations + EOS accordion)
- `/api/data` → Full dashboard data
- `/api/summary` → Summary metrics for 4 cards
- `/landing` → Multi-dashboard landing page (future use)
- `/shop`, `/sales`, `/parts`, `/eos` → Detail pages (future use)

## Why We Tabled Multi-Dashboard

**User Quote:** *"I like this. I just think we have A LOT of work to get this done. Agreed?"*

**Reasons:**
1. **Sales & Parts data needs validation** - Current sources working, but need to verify metrics are correct for executive view
2. **Information architecture needs refinement** - Who sees what? When? Mobile vs desktop?
3. **Transparent leadership model** - All staff access means we need to design for multiple audiences
4. **OSS (Offseason Storage) data not available yet** - Parts card shows placeholder
5. **Testing needed** - Executive summary numbers need validation before company-wide rollout

**What We Preserved:**
- All templates built and functional
- API endpoint working and tested
- Can access `/landing` anytime to see prototype
- Architecture decisions documented in git commits

## Strategic Vision (User's Direction)

**Original Quote:** *"How do you see it? Similar to havyn with a 1000 foot view in the cards like you have shown in the Plainwell EOS Tab"*

**Key Concepts:**
1. **Transparent Operations** - All Plainwell staff have access
2. **Executive View First** - Landing page shows "1000-foot view"
3. **Drill-Down Available** - Click cards to see operational detail
4. **EOS Integration** - Company runs on EOS methodology, dashboard should reflect it
5. **4 Business Areas:** Shop, Sales, Parts, EOS

**Paradigm Shift:**
- From: "Shop guidance tool"
- To: "Plainwell EOS Shop Direction Dashboard"
- Focus: What leverages leadership out? What's the 10-second glance?

## Next Steps (When Ready)

### Phase 1: Validation
- [ ] Verify sales metrics calculations with actual targets
- [ ] Confirm parts metrics (No Bins, PO Over 30, BO Over 5) are accurate
- [ ] Get OSS (Offseason Storage) data source identified
- [ ] Test `/api/summary` endpoint against known good data

### Phase 2: Design Refinement
- [ ] Answer: Who looks at this dashboard? (Users, roles, frequency)
- [ ] Answer: What's the ideal 10-second glance for leadership?
- [ ] Answer: What decisions does leadership make from this data?
- [ ] Design mobile-responsive executive view
- [ ] Plan collapsible sections vs separate routes

### Phase 3: Implementation
- [ ] Make `/landing` the default route when validated
- [ ] Build out sales detail page with actual data needs
- [ ] Build out parts detail page with CSR workflow
- [ ] Add navigation between views
- [ ] Test with staff for feedback

### Phase 4: Polish
- [ ] Add user analytics (who's looking at what?)
- [ ] Role-based views if needed
- [ ] Real-time refresh indicators
- [ ] Export/report functions
- [ ] Mobile app consideration

## Technical Notes

### Parser Working Correctly
- Strategic plan parser fixed on 2/9/2026 at 3:13 UTC
- Issue: Section splitting with "===" delimiter was off by one
- Fix: Check `sections[i+1]` for data when header found in `sections[i]`
- Validated: 8 rocks, 5 goals, 5 issues parsing correctly

### Email Automation Pipeline
```
Outlook → Gmail (subject: "shopmgr")
    ↓
Google Apps Script (saves attachments)
    ↓
Google Drive (/shopmgr folder)
    ↓
rclone sync (every 60s via shopmgr-gdrive-sync.service)
    ↓
/home/ubuntu/shopmgr/datasheets/
    ↓
file_watcher.py (converts Excel → CSV)
    ↓
Dashboard updates (Flask app reads files)
```

**Gmail Setup Status:** 
- Apps Script documented but not configured by user yet
- Manual testing done: 2 emails, 6 files successfully processed

### Git Commits Today
1. `4f91dae` - Strategic Dashboard Prototype (pre-landing page)
2. `c3fe4c6` - Multi-Dashboard Architecture: Landing + Detail Pages
3. `3cfe25c` - Table Multi-Dashboard, Add EOS Accordion to Shop View

**Repository:** github.com/jdean64/steensma-shopmgr (main branch)

## Quick Commands for Tomorrow

**View current dashboard:**
```bash
curl http://localhost:5001/
```

**View landing page prototype:**
```bash
curl http://localhost:5001/landing
```

**Test summary API:**
```bash
curl http://localhost:5001/api/summary | python3 -m json.tool
```

**Restart service:**
```bash
sudo systemctl restart shopmgr
sudo systemctl status shopmgr
```

**Check logs:**
```bash
journalctl -u shopmgr -f
```

**Database location:**
```bash
ls -lh /home/ubuntu/shopmgr/datasheets/
```

## Questions to Answer Before Resuming Multi-Dashboard

1. **Who are the users?**
   - Jeff (owner/leadership)
   - Shop leads/managers
   - CSR team
   - Sales team
   - All staff?

2. **What's the primary use case?**
   - Daily stand-up reference?
   - Weekly leadership review?
   - Real-time monitoring?
   - EOS quarterly planning?

3. **Mobile vs Desktop?**
   - Staff accessing from shop floor?
   - Leadership viewing on phone?
   - Office desktop primary?

4. **What drives decisions?**
   - Which metrics trigger action?
   - What's the "red alert" threshold?
   - What's "good enough" vs "needs attention"?

5. **Data refresh frequency?**
   - Current: Every 5 minutes
   - Need real-time for any metrics?
   - Overnight batch okay for some?

## Conclusion

We built a solid foundation for a company-wide executive dashboard but wisely decided to table it until we can do it right. The EOS accordion gives immediate strategic visibility in the current dashboard while we plan the bigger architecture properly.

**All work is preserved, committed to GitHub, and ready to resume when the time is right.**

---

**Status:** ✅ Dashboard operational with EOS accordion  
**Next Session:** Continue with user input on multi-dashboard questions  
**Backup:** All work saved in templates/ and committed to main branch
