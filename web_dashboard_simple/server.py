#!/usr/bin/env python3
import http.server
import socketserver
import json
import os
from datetime import datetime

PORT = 8084
WEB_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(WEB_DIR, 'data.json')

def load_data():
    """Load data from JSON file"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading data: {e}")
        return []

def calculate_status(days):
    """Calculate status based on days to expiry"""
    if days <= 30:
        return {'status': 'PRIORITAS', 'color': 'danger', 'icon': '⛔'}
    elif days <= 90:
        return {'status': 'PERINGATAN', 'color': 'warning', 'icon': '⚠️'}
    else:
        return {'status': 'AMAN', 'color': 'success', 'icon': '✅'}

def get_status_info(vehicle):
    """Get status information for vehicle"""
    today = datetime.now().date()
    stnk_date = datetime.strptime(vehicle['stnk_date'], '%Y-%m-%d').date()
    pajak_date = datetime.strptime(vehicle['pajak_date'], '%Y-%m-%d').date()
    
    # Gunakan tanggal yang lebih dekat
    nearest_date = min(stnk_date, pajak_date)
    days_to_expiry = (nearest_date - today).days
    
    status_info = calculate_status(days_to_expiry)
    return {
        'days': days_to_expiry,
        'status': status_info['status'],
        'color': status_info['color'],
        'icon': status_info['icon']
    }

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            data = load_data()
            stats = {
                'total': len(data),
                'priority': 0,
                'warning': 0,
                'safe': 0
            }
            
            vehicles_html = ''
            for vehicle in data:
                status = get_status_info(vehicle)
                
                # Update stats
                if status['status'] == 'PRIORITAS':
                    stats['priority'] += 1
                elif status['status'] == 'PERINGATAN':
                    stats['warning'] += 1
                else:
                    stats['safe'] += 1
                
                # Format dates
                stnk_date = datetime.strptime(vehicle['stnk_date'], '%Y-%m-%d').strftime('%d %b %Y')
                pajak_date = datetime.strptime(vehicle['pajak_date'], '%Y-%m-%d').strftime('%d %b %Y')
                
                vehicles_html += f'''
                <div class="vehicle-card status-{status['color']}">
                    <div class="vehicle-header">
                        <span class="status-badge">{status['icon']} {status['status']}</span>
                        <span class="days-badge">{status['days']} hari</span>
                    </div>
                    <div class="vehicle-info">
                        <h3>{vehicle['merk']}</h3>
                        <p class="plate">{vehicle['no_polisi']}</p>
                        <div class="details">
                            <div class="detail-item">
                                <span class="label">Kategori:</span>
                                <span class="value">{vehicle['kategori']}</span>
                            </div>
                            <div class="detail-item">
                                <span class="label">STNK:</span>
                                <span class="value">{stnk_date}</span>
                            </div>
                            <div class="detail-item">
                                <span class="label">Pajak:</span>
                                <span class="value">{pajak_date}</span>
                            </div>
                            <div class="detail-item">
                                <span class="label">Pemilik:</span>
                                <span class="value">{vehicle['ktp']}</span>
                            </div>
                            {f'<div class="detail-item"><span class="label">Catatan:</span><span class="value">{vehicle["catatan"]}</span></div>' if vehicle.get('catatan') else ''}
                        </div>
                    </div>
                </div>
                '''
            
            html = f'''<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 STNK Monitor</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            color: white;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
        }}
        
        .header p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-card.total {{ border-top: 5px solid #667eea; }}
        .stat-card.safe {{ border-top: 5px solid #28a745; }}
        .stat-card.warning {{ border-top: 5px solid #ffc107; }}
        .stat-card.priority {{ border-top: 5px solid #dc3545; }}
        
        .stat-icon {{
            font-size: 2.5rem;
            margin-bottom: 15px;
        }}
        
        .stat-number {{
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            font-size: 1.1rem;
            color: #666;
            font-weight: 500;
        }}
        
        .vehicles-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }}
        
        .vehicle-card {{
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}
        
        .vehicle-card:hover {{
            box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        }}
        
        .vehicle-card.status-danger {{
            border-left: 5px solid #dc3545;
        }}
        
        .vehicle-card.status-warning {{
            border-left: 5px solid #ffc107;
        }}
        
        .vehicle-card.status-success {{
            border-left: 5px solid #28a745;
        }}
        
        .vehicle-header {{
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #eee;
        }}
        
        .status-badge {{
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.9rem;
        }}
        
        .vehicle-card.status-danger .status-badge {{
            background: rgba(220, 53, 69, 0.1);
            color: #dc3545;
        }}
        
        .vehicle-card.status-warning .status-badge {{
            background: rgba(255, 193, 7, 0.1);
            color: #ffc107;
        }}
        
        .vehicle-card.status-success .status-badge {{
            background: rgba(40, 167, 69, 0.1);
            color: #28a745;
        }}
        
        .days-badge {{
            font-weight: 700;
            font-size: 1.2rem;
        }}
        
        .vehicle-card.status-danger .days-badge {{
            color: #dc3545;
        }}
        
        .vehicle-card.status-warning .days-badge {{
            color: #ffc107;
        }}
        
        .vehicle-card.status-success .days-badge {{
            color: #28a745;
        }}
        
        .vehicle-info {{
            padding: 20px;
        }}
        
        .vehicle-info h3 {{
            font-size: 1.4rem;
            margin-bottom: 10px;
            color: #333;
        }}
        
        .plate {{
            font-family: 'Courier New', monospace;
            font-size: 1.2rem;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 15px;
            padding: 5px 10px;
            background: #f8f9fa;
            border-radius: 5px;
            display: inline-block;
        }}
        
        .details {{
            margin-top: 15px;
        }}
        
        .detail-item {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        .detail-item:last-child {{
            border-bottom: none;
        }}
        
        .label {{
            font-weight: 600;
            color: #666;
        }}
        
        .value {{
            color: #333;
            text-align: right;
            max-width: 60%;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: white;
            opacity: 0.8;
            font-size: 0.9rem;
        }}
        
        .update-time {{
            background: rgba(255,255,255,0.1);
            padding: 10px 20px;
            border-radius: 20px;
            display: inline-block;
            margin-top: 10px;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 2rem;
            }}
            
            .vehicles-grid {{
                grid-template-columns: 1fr;
            }}
            
            .stat-number {{
                font-size: 2.5rem;
            }}
        }}
        
        @media (max-width: 480px) {{
            .header h1 {{
                font-size: 1.8rem;
            }}
            
            .vehicle-card {{
                margin: 0 -10px;
                border-radius: 10px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-car"></i> STNK & PAJAK MONITOR</h1>
            <p>Pantau masa berlaku STNK dan Pajak kendaraan Anda</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card total">
                <div class="stat-icon">📊</div>
                <div class="stat-number">{stats['total']}</div>
                <div class="stat-label">TOTAL KENDARAAN</div>
            </div>
            
            <div class="stat-card safe">
                <div class="stat-icon">✅</div>
                <div class="stat-number">{stats['safe']}</div>
                <div class="stat-label">AMAN</div>
            </div>
            
            <div class="stat-card warning">
                <div class="stat-icon">⚠️</div>
                <div class="stat-number">{stats['warning']}</div>
                <div class="stat-label">PERINGATAN</div>
            </div>
            
            <div class="stat-card priority">
                <div class="stat-icon">⛔</div>
                <div class="stat-number">{stats['priority']}</div>
                <div class="stat-label">PRIORITAS</div>
            </div>
        </div>
        
        <div class="vehicles-grid">
            {vehicles_html}
        </div>
        
        <div class="footer">
            <p>Sistem Monitoring STNK & Pajak v2.0</p>
            <div class="update-time">
                <i class="fas fa-sync-alt"></i> Terakhir update: {datetime.now().strftime('%d %B %Y %H:%M')}
            </div>
        </div>
    </div>
    
    <script>
        // Auto refresh setiap 60 detik
        setTimeout(() => {{
            location.reload();
        }}, 60000);
        
        // Animasi saat hover
        document.querySelectorAll('.vehicle-card').forEach(card => {{
            card.addEventListener('mouseenter', function() {{
                this.style.transform = 'translateY(-5px)';
            }});
            
            card.addEventListener('mouseleave', function() {{
                this.style.transform = 'translateY(0)';
            }});
        }});
    </script>
</body>
</html>'''
            
            self.wfile.write(html.encode('utf-8'))
        
        elif self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            data = load_data()
            for vehicle in data:
                status = get_status_info(vehicle)
                vehicle['status_info'] = status
            
            response = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'vehicles': data,
                'count': len(data)
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        
        else:
            super().do_GET()
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def main():
    print(f"🚗 STNK Monitor Sederhana")
    print(f"📊 Port: {PORT}")
    print(f"📁 Directory: {WEB_DIR}")
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Open browser to: http://localhost:{PORT}")
    print(f"📡 API endpoint: http://localhost:{PORT}/api/data")
    print("-" * 50)
    
    # Copy data.json jika belum ada
    if not os.path.exists(DATA_FILE):
        print(f"⚠️  data.json not found. Creating from template...")
        source_data = '/root/stnk_monitoring/web_dashboard_new/data.json'
        if os.path.exists(source_data):
            import shutil
            shutil.copy(source_data, DATA_FILE)
            print(f"✅ Copied data.json from template")
        else:
            print(f"❌ Source data not found at {source_data}")
    
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")

if __name__ == '__main__':
    main()