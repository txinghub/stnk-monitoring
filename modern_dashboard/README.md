# stnk-modern-dashboard-tidal

Modern STNK monitoring dashboard with TIDAL style design, animations, and premium features

## 📋 Project Information
- **Created**: 2026-04-22 14:53:17
- **Location**: /root/stnk_monitoring/modern_dashboard
- **GitHub**: https://github.com/txinghub/stnk-modern-dashboard-tidal
- **Server**: openclaw-hermes
- **Tailscale IP**: 100.121.49.116

## 🚀 Dashboard Access Links

### Primary Dashboard (Modern TIDAL Style)
- **URL**: http://100.121.49.116:8087
- **Port**: 8087
- **Features**: TIDAL design, animations, dark/light mode, charts, export

### Dashboard Portal (All Links)
- **URL**: http://100.121.49.116:8099
- **Port**: 8099
- **Features**: All dashboard links in one page

### Other Dashboards
- Simple Dashboard: http://100.121.49.116:8084
- Complete Dashboard: http://100.121.49.116:8085

## 📁 Project Structure
```
modern_dashboard/
├── index.html          # Main dashboard UI (TIDAL style)
├── script.js           # Frontend logic with animations
├── server.py           # Python backend (port 8087)
├── data.json           # Vehicle data (10 samples)
├── portal.html         # All links portal (port 8099)
├── share_dashboard.sh  # WhatsApp sharing script
├── send_all_links.sh   # Send all links via WhatsApp
├── README.md           # This documentation
├── requirements.txt    # Python dependencies
├── .gitignore          # Git ignore file
├── backups/            # Auto-generated backups
└── server.log          # Server logs
```

## 🔧 Technical Details

### Server Configuration
- **Port**: 8087 (Modern Dashboard), 8099 (Portal)
- **Bind Address**: 0.0.0.0 (accessible via Tailscale)
- **Auto Backup**: Before every update
- **Auto Refresh**: 30 seconds interval

### Features Implemented
✅ TIDAL style dark blue gradient design  
✅ AOS animations and hover effects  
✅ Interactive charts (Chart.js)  
✅ Sidebar navigation with icons  
✅ Dark/light mode toggle  
✅ Export to CSV functionality  
✅ Mobile responsive design  
✅ Auto backup system  
✅ WhatsApp integration  
✅ Tailscale remote access  

### API Endpoints
- `GET /api/data` - Vehicle data with status
- `GET /api/stats` - Dashboard statistics  
- `GET /api/backups` - List of backup files
- `POST /api/update` - Update vehicle dates
- `GET /api/health` - Health check

## 🔐 Security & Access

### Authorized WhatsApp Numbers
- +628159153720 (主任 - user)
- +6285261919099 (Owner/pemilik utama)
- +8615017041161 (Mandarin/English contact)

### Access Requirements
1. Tailscale installed on device
2. Login with shared account
3. Status must be "Connected"
4. Open dashboard link in browser

## 🛠 Backup & Restoration

### GitHub Backup
This repository serves as the primary backup. To restore:

```bash
# Clone repository
git clone https://github.com/txinghub/stnk-modern-dashboard-tidal.git

# Start dashboard
cd stnk-modern-dashboard-tidal
python3 server.py
```

### NAS Backup
Backup also stored on NAS at: `/root/nas_backups/`

### Manual Backup Commands
```bash
# Create timestamped backup
cd /root/stnk_monitoring
tar -czf modern_dashboard_backup_$(date +%Y%m%d_%H%M%S).tar.gz modern_dashboard/

# Restore from backup
tar -xzf modern_dashboard_backup_YYYYMMDD_HHMMSS.tar.gz
```

## 📞 Support & Troubleshooting

### Common Issues
1. **Cannot access dashboard**: Check Tailscale connection status
2. **Charts not loading**: Check internet connection (CDN dependencies)
3. **Update not working**: Check server logs and backup directory permissions
4. **Mobile display issues**: Use responsive design, check browser compatibility

### Server Status Check
```bash
# Check if server is running
ss -tlnp | grep ':8087'
ss -tlnp | grep ':8099'

# Check server logs
tail -f /root/stnk_monitoring/modern_dashboard/server.log
```

## 📅 Version History

### v1.0 - 2026-04-22
- Initial release with TIDAL style design
- Complete dashboard with all premium features
- Portal page with all access links
- WhatsApp integration for link sharing
- GitHub and NAS backup setup

---

**Last Updated**: 2026-04-22 14:53:17 
**Backup Status**: ✅ Complete (GitHub + NAS)
**Dashboard Status**: ✅ Running on ports 8087 & 8099
