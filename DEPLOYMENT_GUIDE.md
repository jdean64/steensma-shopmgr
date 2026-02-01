# Steensma Shop Manager - Deployment Guide

## Overview
The Steensma Shop Manager Dashboard displays daily shop operations including schedules, parts inventory, and mechanic performance metrics for Steensma Lawn Battle Creek.

**Current URL**: https://shop.coresteensma.com  
**Port**: 5001  
**Technology**: Flask (Python 3.12), Nginx reverse proxy with SSL

---

## System Requirements

- **Python**: 3.12 or higher
- **Operating System**: Linux (Ubuntu/Debian preferred)
- **Web Server**: Nginx
- **SSL Certificate**: Let's Encrypt (optional, for HTTPS)
- **Memory**: 512MB minimum
- **Storage**: 100MB for application + space for datasheet files

---

## Directory Structure

```
/home/ubuntu/shopmgr/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── wsgi.py                        # Production WSGI entry point
├── venv/                          # Python virtual environment
├── templates/
│   └── dashboard.html             # Dashboard UI
├── datasheets/                    # Data files (*.txt, *.xls, *.xlsx)
│   ├── Sales and Gross.txt        # Mechanic metrics (text export)
│   ├── Scheduled Shop Jobs*.txt   # Shop schedule (text export)
│   └── Open Back Orders*.xls      # Parts inventory (Excel)
└── archive/                       # Old data files (optional)
```

---

## Installation Steps

### 1. Install System Dependencies

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.12 and pip
sudo apt install python3.12 python3.12-venv python3-pip -y

# Install Nginx (if using reverse proxy)
sudo apt install nginx -y
```

### 2. Set Up Application Directory

```bash
# Create application directory
sudo mkdir -p /home/ubuntu/shopmgr
sudo chown -R ubuntu:ubuntu /home/ubuntu/shopmgr

# Navigate to directory
cd /home/ubuntu/shopmgr

# Create subdirectories
mkdir -p datasheets archive templates
```

### 3. Copy Application Files

Transfer the following files to the server:
- `app.py`
- `requirements.txt`
- `templates/dashboard.html`
- Initial datasheet files to `datasheets/`

### 4. Install Python Dependencies

```bash
# Create virtual environment
cd /home/ubuntu/shopmgr
python3.12 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**requirements.txt contents:**
```
Flask==3.1.2
pandas==2.3.3
openpyxl==3.1.2
xlrd==2.0.2
gunicorn==21.2.0
```

### 5. Configure File Permissions

```bash
# Set ownership
sudo chown -R ubuntu:ubuntu /home/ubuntu/shopmgr

# Set directory permissions
chmod 755 /home/ubuntu/shopmgr
chmod 755 /home/ubuntu/shopmgr/datasheets
chmod 755 /home/ubuntu/shopmgr/templates

# Set file permissions
chmod 644 /home/ubuntu/shopmgr/app.py
chmod 644 /home/ubuntu/shopmgr/templates/dashboard.html
```

---

## Running the Application

### Option A: Development Mode (Testing)

```bash
cd /home/ubuntu/shopmgr
source venv/bin/activate
python app.py
```

Access at: http://localhost:5001

### Option B: Background Process (Simple Production)

```bash
cd /home/ubuntu/shopmgr
nohup venv/bin/python app.py > /tmp/shopmgr.log 2>&1 &
```

Check logs: `tail -f /tmp/shopmgr.log`

### Option C: Systemd Service (Recommended Production)

Create service file:

```bash
sudo nano /etc/systemd/system/shopmgr.service
```

**Service file contents:**
```ini
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
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable shopmgr.service
sudo systemctl start shopmgr.service

# Check status
sudo systemctl status shopmgr.service

# View logs
journalctl -u shopmgr.service -f
```

**Service management commands:**
```bash
sudo systemctl start shopmgr    # Start service
sudo systemctl stop shopmgr     # Stop service
sudo systemctl restart shopmgr  # Restart service
sudo systemctl status shopmgr   # Check status
```

---

## Nginx Reverse Proxy Configuration

### 1. Create Nginx Site Configuration

```bash
sudo nano /etc/nginx/sites-available/shop.coresteensma.com
```

**Configuration contents:**
```nginx
server {
    listen 80;
    server_name shop.coresteensma.com;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    access_log /var/log/nginx/shop.coresteensma.com.access.log;
    error_log /var/log/nginx/shop.coresteensma.com.error.log;
}
```

### 2. Enable Site

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/shop.coresteensma.com /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### 3. Configure SSL (Optional but Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d shop.coresteensma.com

# Certificate will auto-renew via cron/systemd timer
```

After SSL setup, Nginx config will be automatically updated to include HTTPS.

---

## Data File Management

### Supported File Formats

1. **Shop Schedule**: `Scheduled Shop Jobs - [DATE].txt`
   - Text export from shop management system
   - Contains today/tomorrow schedules and fit-in jobs
   - Format: CSV with mechanic sections

2. **Mechanic Metrics**: `Sales and Gross.txt`
   - Text export with mechanic efficiency and labor sales
   - Contains "Hours Worked:" lines with efficiency percentages
   - Summary lines starting with "bDennis Smurr," etc.

3. **Parts Inventory**: `Open Back Orders - [DATE].xls`
   - Excel format (.xls)
   - Filters for "Received" or "Released" status

### Updating Data Files

```bash
# Upload new files to datasheets directory
cd /home/ubuntu/shopmgr/datasheets

# The application automatically finds the most recent file matching each pattern
# No restart needed - data refreshes every 5 minutes on dashboard
```

### Archive Old Files (Optional)

```bash
# Move files older than 7 days to archive
find /home/ubuntu/shopmgr/datasheets -type f -mtime +7 -exec mv {} /home/ubuntu/shopmgr/archive/ \;
```

---

## Troubleshooting

### Check if Application is Running

```bash
# Check process
ps aux | grep "python.*app.py" | grep -v grep

# Check port
sudo netstat -tlnp | grep :5001
# or
sudo ss -tlnp | grep :5001
```

### View Application Logs

```bash
# If running with nohup
tail -f /tmp/shopmgr.log

# If running with systemd
journalctl -u shopmgr.service -f

# Nginx logs
sudo tail -f /var/log/nginx/shop.coresteensma.com.access.log
sudo tail -f /var/log/nginx/shop.coresteensma.com.error.log
```

### Common Issues

**Port 5001 already in use:**
```bash
# Find process using port 5001
sudo lsof -i :5001

# Kill process
kill <PID>
```

**Permission denied on datasheets:**
```bash
sudo chown -R ubuntu:ubuntu /home/ubuntu/shopmgr
chmod 755 /home/ubuntu/shopmgr/datasheets
```

**Empty dashboard sections:**
- Check data files exist: `ls -lh /home/ubuntu/shopmgr/datasheets/`
- Verify file naming matches patterns in app.py
- Check logs for parsing errors

**Mechanic metrics showing 0:**
- Ensure "Sales and Gross.txt" contains "Hours Worked:" lines
- Check file has mechanic summary lines starting with "b"

**Schedule not showing:**
- Ensure "Scheduled Shop Jobs*.txt" file exists
- Check date format in file matches today's date (M/D/YYYY)

### Manual Testing

```bash
# Test API endpoint
curl http://127.0.0.1:5001/api/data | python3 -m json.tool

# Check specific sections
curl -s http://127.0.0.1:5001/api/data | python3 -c "import sys, json; d=json.load(sys.stdin); print('Today:', len(d['schedule']['today']), 'Mechanics:', len(d['mechanic_metrics']['mechanics']))"
```

---

## Maintenance

### Update Application Code

```bash
# Stop service
sudo systemctl stop shopmgr

# Backup current version
cp /home/ubuntu/shopmgr/app.py /home/ubuntu/shopmgr/app.py.backup

# Update files (upload new app.py, etc.)

# Test syntax
cd /home/ubuntu/shopmgr
source venv/bin/activate
python -m py_compile app.py

# Restart service
sudo systemctl start shopmgr
sudo systemctl status shopmgr
```

### Update Dependencies

```bash
cd /home/ubuntu/shopmgr
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Restart application
sudo systemctl restart shopmgr
```

### Backup

**Backup application:**
```bash
tar -czf shopmgr-backup-$(date +%Y%m%d).tar.gz /home/ubuntu/shopmgr --exclude=venv
```

**Restore from backup:**
```bash
tar -xzf shopmgr-backup-YYYYMMDD.tar.gz -C /
cd /home/ubuntu/shopmgr
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Security Considerations

1. **Firewall**: Only expose ports 80 (HTTP) and 443 (HTTPS)
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

2. **File Permissions**: Ensure datasheets directory is not world-writable

3. **SSL Certificate**: Use HTTPS in production with valid SSL certificate

4. **Updates**: Keep system packages and Python dependencies updated

---

## Moving to Different Server/Home Network

### Export Configuration

1. **Backup all files:**
   ```bash
   cd /home/ubuntu
   tar -czf shopmgr-full-backup.tar.gz shopmgr/
   ```

2. **Document current settings:**
   - Domain name: shop.coresteensma.com
   - Port: 5001
   - Python version: 3.12
   - File patterns used in app.py

### Import on New Server

1. **Transfer backup file to new server**

2. **Extract:**
   ```bash
   tar -xzf shopmgr-full-backup.tar.gz -C /home/ubuntu/
   ```

3. **Recreate virtual environment:**
   ```bash
   cd /home/ubuntu/shopmgr
   python3.12 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Configure Nginx** (follow steps in "Nginx Reverse Proxy Configuration" section)

5. **Set up systemd service** (follow steps in "Option C: Systemd Service" section)

6. **Update DNS** to point shop.coresteensma.com to new server IP

7. **Obtain new SSL certificate** (if using different server)

---

## Quick Reference Commands

```bash
# Start application (background)
cd /home/ubuntu/shopmgr && nohup venv/bin/python app.py > /tmp/shopmgr.log 2>&1 &

# Stop application
pkill -f "python.*shopmgr.*app.py"

# View logs
tail -f /tmp/shopmgr.log

# Test API
curl http://127.0.0.1:5001/api/data | python3 -m json.tool

# Restart Nginx
sudo systemctl restart nginx

# Check service status
sudo systemctl status shopmgr
```

---

## Support Information

**Application Details:**
- Name: Steensma Shop Manager Dashboard
- Version: 1.0 (January 2026)
- Technology: Flask, Python 3.12, Pandas, Nginx
- Data Sources: Text exports and Excel files from shop management system

**Key Files:**
- Main application: `/home/ubuntu/shopmgr/app.py`
- Dashboard UI: `/home/ubuntu/shopmgr/templates/dashboard.html`
- Configuration: `/etc/nginx/sites-available/shop.coresteensma.com`
- Service file: `/etc/systemd/system/shopmgr.service`
- Data directory: `/home/ubuntu/shopmgr/datasheets/`

**Dashboard Features:**
- Today's Schedule (jobs scheduled for current date)
- Tomorrow's Schedule (jobs scheduled for next date)
- Fit-In Work (priority jobs)
- Parts Received (14 most recent received/released parts)
- Mechanic Metrics (Dennis Smurr, Jake Glas, Ray Page efficiency and labor sales)
- Auto-refresh every 5 minutes
- Real-time weather widget

---

## Contact

For issues or questions about this deployment, reference this guide and check logs first. Most issues can be resolved by checking:
1. Application logs (`/tmp/shopmgr.log`)
2. Nginx logs (`/var/log/nginx/`)
3. Data file presence and format
4. Service status (`systemctl status shopmgr`)
