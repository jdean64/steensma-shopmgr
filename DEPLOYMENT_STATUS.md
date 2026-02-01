# ✅ Steensma Shop Manager - LIVE & DEPLOYED

## 🌐 Live URL
**https://shop.coresteensma.com**

## ✅ What's Configured

1. **Domain Setup**: shop.coresteensma.com
2. **SSL Certificate**: ✅ Installed (Let's Encrypt, expires April 15, 2026)
3. **Nginx Proxy**: ✅ Configured to port 5001
4. **Flask App**: ✅ Running on port 5001
5. **Systemd Service**: ✅ Enabled (auto-starts on reboot)

## 🚀 Status

- **Dashboard**: LIVE at https://shop.coresteensma.com
- **Parts Received**: Working (14 parts detected)
- **Auto-refresh**: Every 5 minutes
- **Weather Widget**: Active

## ⚠️ Pending Items

1. **Shop Schedule File** - Needs to be resaved (formatting corruption)
2. **Gross Profit Files** - Need to be resaved (formatting corruption)

Once these files are repaired, all dashboard sections will be fully operational.

## 🔧 Service Management

```bash
# Check status
sudo systemctl status shopmgr.service

# Start service
sudo systemctl start shopmgr.service

# Stop service
sudo systemctl stop shopmgr.service

# Restart service
sudo systemctl restart shopmgr.service

# View logs
sudo journalctl -u shopmgr.service -f
```

## 📁 File Locations

- **App**: /home/ubuntu/shopmgr/
- **Nginx Config**: /etc/nginx/sites-available/shop.coresteensma.com
- **Systemd Service**: /etc/systemd/system/shopmgr.service
- **SSL Cert**: /etc/letsencrypt/live/shop.coresteensma.com/

## 🎯 Next Steps

1. Visit https://shop.coresteensma.com
2. Resave the corrupted Excel files
3. Place them in /home/ubuntu/shopmgr/datasheets/
4. Refresh dashboard to see all sections populated

---

**Deployment Date**: January 15, 2026  
**Status**: ✅ Production Ready
