# Shop Manager Dashboard - Restart Instructions

## Quick Start (After System Reboot/Update)

### 1. Navigate to Project Directory
```bash
cd /home/ubuntu/shopmgr
```

### 2. Start the Application
```bash
python3 app.py &
```
(The `&` runs it in the background)

### 3. Verify It's Running
```bash
# Check if the process is running
ps aux | grep "python.*app.py"

# Check if port 5001 is listening
curl http://localhost:5001
```

### 4. Access the Dashboard
Open your browser to: **http://localhost:5001**

---

## Alternative: Run in Screen Session (Recommended)
```bash
cd /home/ubuntu/shopmgr
screen -S shopmgr
python3 app.py
# Press Ctrl+A then D to detach
```

To reattach later: `screen -r shopmgr`

---

## Troubleshooting

### Port Already in Use
```bash
# Kill any existing Python processes
pkill -9 -f "python.*app.py"

# Then restart
python3 app.py &
```

### Application Won't Start
```bash
# Check for errors
python3 app.py

# If missing dependencies
pip3 install -r requirements.txt
```

### Check Logs
```bash
# See what's happening
tail -f nohup.out
```

---

## Latest Updates Deployed
✅ All Parts Management features (No Bins, Back Orders Over 5, PO Over 30, Gross Profit YTD)  
✅ $6.6M annual target updated  
✅ Back Ordered filter (removed On Order)  
✅ Prior year comparison (2025 vs 2026)  
✅ Mobile responsive design  

**Repository:** jdean64/steensma-shopmgr  
**Current Commit:** b928340 (mobile CSS fixed)  
**Port:** 5001
