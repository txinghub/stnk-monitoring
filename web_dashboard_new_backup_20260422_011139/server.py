#!/usr/bin/env python3
import http.server
import socketserver
import json
import os
import sys
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
import logging

PORT = 8085  # Port baru untuk menghindari konflik
WEB_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(WEB_DIR, 'data.json')
BACKUP_DIR = os.path.join(WEB_DIR, 'backups')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(WEB_DIR, 'server.log')),
        logging.StreamHandler()
    ]
)

# Buat backup directory jika belum ada
os.makedirs(BACKUP_DIR, exist_ok=True)

def load_data():
    """Load data from JSON file"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        return []

def save_data(data):
    """Save data to JSON file with backup"""
    try:
        # Buat backup sebelum menyimpan
        backup_file = os.path.join(BACKUP_DIR, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(load_data(), f, ensure_ascii=False, indent=2)
        
        # Simpan data baru
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logging.info(f"Data saved successfully. Backup created: {backup_file}")
        return True
    except Exception as e:
        logging.error(f"Error saving data: {e}")
        return False

def calculate_status(days):
    """Calculate status based on days to expiry"""
    if days <= 30:
        return 'priority'
    elif days <= 90:
        return 'warning'
    else:
        return 'safe'

def update_vehicle_status(vehicle):
    """Update vehicle status based on dates"""
    today = datetime.now().date()
    
    # Handle null dates
    if vehicle['stnk_date'] is None or vehicle['pajak_date'] is None:
        vehicle['hari_menuju_jatuh_tempo'] = None
        vehicle['status'] = 'active'
        vehicle['warna_status'] = 'success'
        return vehicle
    
    # Hitung hari menuju jatuh tempo (gunakan tanggal yang lebih dekat)
    stnk_date = datetime.strptime(vehicle['stnk_date'], '%Y-%m-%d').date()
    pajak_date = datetime.strptime(vehicle['pajak_date'], '%Y-%m-%d').date()
    
    # Gunakan tanggal yang lebih dekat
    nearest_date = min(stnk_date, pajak_date)
    days_to_expiry = (nearest_date - today).days
    
    # Update status
    vehicle['hari_menuju_jatuh_tempo'] = days_to_expiry
    vehicle['status'] = calculate_status(days_to_expiry)
    vehicle['warna_status'] = {
        'safe': 'success',
        'warning': 'warning',
        'priority': 'danger'
    }[vehicle['status']]
    
    return vehicle

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/data':
            self.handle_api_data()
        elif parsed_path.path == '/api/stats':
            self.handle_api_stats()
        elif parsed_path.path == '/api/backups':
            self.handle_api_backups()
        else:
            # Serve static files
            super().do_GET()
    
    def do_POST(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/update':
            self.handle_api_update()
        elif parsed_path.path == '/api/add-vehicle':
            self.handle_api_add_vehicle()
        else:
            self.send_error(404, "Endpoint not found")
    
    def do_DELETE(self):
        parsed_path = urlparse(self.path)
        
        # Check if path matches /api/delete-vehicle/<id>
        import re
        delete_match = re.match(r'^/api/delete-vehicle/(\d+)$', parsed_path.path)
        
        if delete_match:
            vehicle_id = int(delete_match.group(1))
            self.handle_api_delete_vehicle(vehicle_id)
        else:
            self.send_error(404, "Endpoint not found")
    
    def handle_api_data(self):
        """Handle GET /api/data"""
        try:
            data = load_data()
            
            # Update status untuk semua kendaraan
            updated_data = [update_vehicle_status(vehicle) for vehicle in data]
            
            response = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'vehicles': updated_data,
                'count': len(updated_data)
            }
            
            self.send_json_response(200, response)
            
        except Exception as e:
            logging.error(f"Error in /api/data: {e}")
            self.send_json_response(500, {
                'success': False,
                'error': str(e)
            })
    
    def handle_api_stats(self):
        """Handle GET /api/stats"""
        try:
            data = load_data()
            updated_data = [update_vehicle_status(vehicle) for vehicle in data]
            
            stats = {
                'total': len(updated_data),
                'safe': len([v for v in updated_data if v['status'] == 'safe']),
                'warning': len([v for v in updated_data if v['status'] == 'warning']),
                'priority': len([v for v in updated_data if v['status'] == 'priority']),
                'last_updated': datetime.now().isoformat()
            }
            
            self.send_json_response(200, {
                'success': True,
                'stats': stats
            })
            
        except Exception as e:
            logging.error(f"Error in /api/stats: {e}")
            self.send_json_response(500, {
                'success': False,
                'error': str(e)
            })
    
    def handle_api_backups(self):
        """Handle GET /api/backups"""
        try:
            backups = []
            for filename in os.listdir(BACKUP_DIR):
                if filename.endswith('.json'):
                    filepath = os.path.join(BACKUP_DIR, filename)
                    stat = os.stat(filepath)
                    backups.append({
                        'filename': filename,
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            
            # Urutkan berdasarkan tanggal dibuat (terbaru dulu)
            backups.sort(key=lambda x: x['created'], reverse=True)
            
            self.send_json_response(200, {
                'success': True,
                'backups': backups[:10]  # 10 backup terbaru
            })
            
        except Exception as e:
            logging.error(f"Error in /api/backups: {e}")
            self.send_json_response(500, {
                'success': False,
                'error': str(e)
            })
    
    def handle_api_update(self):
        """Handle POST /api/update"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            update_data = json.loads(post_data.decode('utf-8'))
            
            vehicle_id = update_data.get('vehicleId')
            new_stnk_date = update_data.get('newStnkDate')
            new_pajak_date = update_data.get('newPajakDate')
            note = update_data.get('note', '')
            
            if not all([vehicle_id, new_stnk_date, new_pajak_date]):
                self.send_json_response(400, {
                    'success': False,
                    'error': 'Missing required fields'
                })
                return
            
            # Load data
            data = load_data()
            
            # Cari kendaraan
            vehicle_found = False
            for vehicle in data:
                if vehicle['id'] == vehicle_id:
                    # Simpan data lama untuk catatan
                    old_stnk = vehicle['stnk_date']
                    old_pajak = vehicle['pajak_date']
                    
                    # Update data
                    vehicle['stnk_date'] = new_stnk_date
                    vehicle['pajak_date'] = new_pajak_date
                    
                    # Update catatan
                    update_note = f"Diupdate pada {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    if note:
                        update_note += f" - {note}"
                    
                    if vehicle['catatan']:
                        vehicle['catatan'] += f" | {update_note}"
                    else:
                        vehicle['catatan'] = update_note
                    
                    # Update status
                    vehicle = update_vehicle_status(vehicle)
                    
                    vehicle_found = True
                    break
            
            if not vehicle_found:
                self.send_json_response(404, {
                    'success': False,
                    'error': 'Vehicle not found'
                })
                return
            
            # Save updated data
            if save_data(data):
                logging.info(f"Vehicle {vehicle_id} updated: STNK {new_stnk_date}, Pajak {new_pajak_date}")
                
                self.send_json_response(200, {
                    'success': True,
                    'message': 'Data updated successfully',
                    'vehicle_id': vehicle_id,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                self.send_json_response(500, {
                    'success': False,
                    'error': 'Failed to save data'
                })
                
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error in /api/update: {e}")
            self.send_json_response(400, {
                'success': False,
                'error': 'Invalid JSON data'
            })
        except Exception as e:
            logging.error(f"Error in /api/update: {e}")
            self.send_json_response(500, {
                'success': False,
                'error': str(e)
            })
    
    def handle_api_add_vehicle(self):
        """Handle POST /api/add-vehicle - Add new vehicle"""
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            new_vehicle = json.loads(post_data.decode('utf-8'))
            
            logging.info(f"Adding new vehicle: {new_vehicle.get('merk')} - {new_vehicle.get('no_polisi')}")
            
            # Load existing data
            data = load_data()
            
            # Check if vehicle with same license plate already exists
            existing_plate = any(
                v.get('no_polisi', '').upper() == new_vehicle.get('no_polisi', '').upper()
                for v in data
            )
            
            if existing_plate:
                self.send_json_response(400, {
                    'success': False,
                    'error': f"Kendaraan dengan nomor polisi {new_vehicle.get('no_polisi')} sudah ada"
                })
                return
            
            # Convert to server format
            server_vehicle = {
                'id': new_vehicle.get('id', len(data) + 1),
                'merk': new_vehicle.get('merk', ''),
                'no_polisi': new_vehicle.get('no_polisi', ''),
                'kategori': new_vehicle.get('kategori', ''),
                'pemilik': new_vehicle.get('pemilik', '-'),
                'stnk_date': new_vehicle.get('tanggal_stnk', ''),
                'pajak_date': new_vehicle.get('tanggal_pajak', ''),
                'catatan': new_vehicle.get('catatan', '-'),
                'hari_menuju_jatuh_tempo': new_vehicle.get('hari_menuju_jatuh_tempo', 0),
                'status': new_vehicle.get('status', 'safe'),
                'warna_status': new_vehicle.get('status_color', 'success')
            }
            
            # Add to data
            data.append(server_vehicle)
            
            # Save data
            if save_data(data):
                logging.info(f"New vehicle added successfully: {server_vehicle['merk']} - {server_vehicle['no_polisi']}")
                
                self.send_json_response(201, {
                    'success': True,
                    'message': 'Kendaraan berhasil ditambahkan',
                    'vehicle_id': server_vehicle['id'],
                    'timestamp': datetime.now().isoformat()
                })
            else:
                self.send_json_response(500, {
                    'success': False,
                    'error': 'Gagal menyimpan data'
                })
                
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error in /api/add-vehicle: {e}")
            self.send_json_response(400, {
                'success': False,
                'error': 'Data JSON tidak valid'
            })
        except Exception as e:
            logging.error(f"Error in /api/add-vehicle: {e}")
            self.send_json_response(500, {
                'success': False,
                'error': str(e)
            })
    
    def handle_api_delete_vehicle(self, vehicle_id):
        """Handle DELETE /api/delete-vehicle/<id> - Delete vehicle"""
        try:
            logging.info(f"Deleting vehicle with ID: {vehicle_id}")
            
            # Load existing data
            data = load_data()
            
            # Find vehicle index
            vehicle_index = None
            vehicle_info = None
            for i, vehicle in enumerate(data):
                if vehicle.get('id') == vehicle_id:
                    vehicle_index = i
                    vehicle_info = vehicle
                    break
            
            if vehicle_index is None:
                self.send_json_response(404, {
                    'success': False,
                    'error': f'Kendaraan dengan ID {vehicle_id} tidak ditemukan'
                })
                return
            
            # Remove vehicle
            deleted_vehicle = data.pop(vehicle_index)
            
            # Save data
            if save_data(data):
                logging.info(f"Vehicle deleted successfully: {deleted_vehicle.get('merk')} - {deleted_vehicle.get('no_polisi')}")
                
                self.send_json_response(200, {
                    'success': True,
                    'message': 'Kendaraan berhasil dihapus',
                    'deleted_vehicle': {
                        'id': deleted_vehicle.get('id'),
                        'merk': deleted_vehicle.get('merk'),
                        'no_polisi': deleted_vehicle.get('no_polisi')
                    },
                    'timestamp': datetime.now().isoformat()
                })
            else:
                self.send_json_response(500, {
                    'success': False,
                    'error': 'Gagal menyimpan data setelah penghapusan'
                })
                
        except Exception as e:
            logging.error(f"Error in /api/delete-vehicle: {e}")
            self.send_json_response(500, {
                'success': False,
                'error': str(e)
            })
    
    def send_json_response(self, status_code, data):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response_json = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response_json.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to use our logging"""
        logging.info("%s - %s" % (self.address_string(), format % args))

def main():
    print(f"🚗 STNK Monitoring Dashboard")
    print(f"📊 Port: {PORT}")
    print(f"📁 Directory: {WEB_DIR}")
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Open browser to: http://localhost:{PORT}")
    print(f"📡 API endpoints:")
    print(f"   • http://localhost:{PORT}/api/data")
    print(f"   • http://localhost:{PORT}/api/stats")
    print(f"   • http://localhost:{PORT}/api/backups")
    print(f"   • POST http://localhost:{PORT}/api/update")
    print("-" * 50)
    
    # Cek data file
    if not os.path.exists(DATA_FILE):
        print(f"⚠️  Warning: data.json not found at {DATA_FILE}")
        print("   Creating sample data...")
        sample_data = [
            {
                "id": 1,
                "merk": "HONDA CS 1",
                "no_polisi": "BK 2302 WAM",
                "kategori": "Roda Dua",
                "stnk_date": "2026-05-06",
                "pajak_date": "2026-05-06",
                "ktp": "LINGGO THIO PUTRO",
                "catatan": "STNK dan Pajak sama tanggal"
            }
        ]
        save_data(sample_data)
    
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
        except Exception as e:
            print(f"\n❌ Server error: {e}")
            sys.exit(1)

if __name__ == '__main__':
    main()