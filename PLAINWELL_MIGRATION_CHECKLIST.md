# Plainwell Migration Checklist - Completed Changes

## ✅ Code Changes Applied (Feb 3, 2026)

### Mechanics Updated (BC → Plainwell):
- ❌ Dennis Smurr → ✅ **Derek Snyder**
- ❌ Jake Glas → ✅ **Chris Deman**
- ❌ Ray Page → ✅ **Brandon Wallace**

### Location Changes:
- ❌ Battle Creek, MI → ✅ **Plainwell, MI**
- ❌ 1588 W. Dickman Rd, Battle Creek → ✅ **Steensma Lawn Plainwell, MI**

### Enhanced Features:
- ✅ Added support for 'p' prefix in mechanic names (pDerek, pChris, pBrandon)
- ✅ Added support for '.pHouse Account' category
- ✅ Enhanced 'Fit-In' detection (handles 'FIT IN WORK', '.pFIT IN', 'Fit-In')

### Files Modified:
- `/home/ubuntu/shopmgr/app.py` - Backuped to `app.py.backup_BC_*`
- `/home/ubuntu/shopmgr/templates/dashboard.html` - Backuped to `dashboard.html.backup_BC_*`

---

## 📋 NEXT STEPS - Action Required

### 1. Update Plainwell Data Files
Place these files in `/home/ubuntu/shopmgr/datasheets/`:

✅ **Shop Schedule** - Must contain:
   - Mechanic names: Derek Snyder, Chris Deman, Brandon Wallace
   - Additional categories: Fit-In, House Account (or .pHouse Account)
   - File pattern: `Shop Schedule - 5 Day - [DATE].[xlsx|txt]`

✅ **Open Back Orders** - Parts inventory
   - File pattern: `Open Back Orders - [DATE].xls`
   - Must have Status, Part Number, Customer columns

✅ **Gross Profit Mechanic** - **VERIFY CELL LOCATIONS!**
   - File pattern: `Gross Profit Mechanic - [DATE].xls`
   - **Current cell references (may need adjustment):**
     - Derek Snyder: Efficiency G120, Labor Sales O119
     - Chris Deman: Efficiency G189, Labor Sales O188
     - Brandon Wallace: Efficiency G233, Labor Sales O232

### 2. Verify Excel Cell References
**IMPORTANT:** Open your Plainwell "Gross Profit Mechanic" Excel file and verify:
- Is Derek Snyder's efficiency at cell G120?
- Is Chris Deman's efficiency at cell G189?
- Is Brandon Wallace's efficiency at cell G233?

If not, update lines 316-318 in `/home/ubuntu/shopmgr/app.py`

### 3. Test the Dashboard
```bash
cd /home/ubuntu/shopmgr
source venv/bin/activate
python app.py
```
Then visit: http://localhost:5001

Check:
- [ ] Weather shows Plainwell, MI
- [ ] Address shows "Steensma Lawn Plainwell, MI"
- [ ] Today's schedule shows Derek/Chris/Brandon
- [ ] Fit-In and House Account jobs appear
- [ ] Mechanic metrics display correctly

### 4. Production Deployment
Once tested, update your production deployment (if running on server)

---

## 🔄 Rollback Instructions (if needed)
```bash
cd /home/ubuntu/shopmgr
cp app.py.backup_BC_* app.py
cd templates
cp dashboard.html.backup_BC_* dashboard.html
```

---

## 📞 Questions to Confirm
1. ✅ Mechanics: Derek Snyder, Chris Deman, Brandon Wallace
2. ✅ Location: Plainwell, MI
3. ⚠️  Excel cell locations for metrics - need verification
4. ❓ Full Plainwell address for dashboard? (Currently just "Steensma Lawn Plainwell, MI")
