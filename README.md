# STNK MONITORING DASHBOARD BACKUP
Created: 2026-04-19 14:22:20

## SYSTEM INFO
- Dashboard URL: http://100.121.49.116:8082/
- Static server: http://100.121.49.116:8081/
- Server ports: 8081 (static), 8082 (dynamic)

## FILES
- index.html - Main dashboard
- server.py - Python HTTP server
- data.json - Vehicle data
- config.json - Configuration
- data/ - Data files
- csv_data/ - CSV data
- extracted_data/ - Original Excel

## RESTORE
1. tar -xzf stnk_dashboard_backup_20260419_142217.tar.gz
2. cd stnk_dashboard_backup_20260419_142217
3. python3 server.py
