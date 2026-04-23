#!/usr/bin/env python3
"""
Modern STNK Dashboard Server - TIDAL Style
Premium dark theme dashboard with gradient animations
"""

import json
import os
import sys
from datetime import datetime, date
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import traceback
from pathlib import Path
import logging

# Configuration
PORT = 8087  # New port for modern dashboard
DATA_FILE = "data.json"
BACKUP_DIR = "backups"
LOG_FILE = "server.log"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ModernDashboardHandler(BaseHTTPRequestHandler):
    """HTTP request handler for modern dashboard"""
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path
            
            # API endpoints
            if path == '/api/data':
                self.handle_api_data()
            elif path == '/api/stats':
                self.handle_api_stats()
            elif path == '/api/backups':
                self.handle_api_backups()
            elif path == '/api/health':
                self.handle_api_health()
            # Static files
            elif path == '/':
                self.serve_file('index_admin.html', 'text/html')
            elif path == '/script.js':
                self.serve_file('script.js', 'application/javascript')
            elif path.endswith('.css'):
                self.serve_file(path[1:], 'text/css')
            elif path.endswith('.js'):
                self.serve_file(path[1:], 'application/javascript')
            else:
                self.send_error(404, "File not found")
                
        except Exception as e:
            logger.error(f"Error handling GET request: {e}")
            self.send_error(500, f"Internal server error: {str(e)}")
    
    def do_POST(self):
        """Handle POST requests"""
        try:
            if self.path == '/api/update':
                self.handle_api_update()
            else:
                self.send_error(404, "Endpoint not found")
        except Exception as e:
            logger.error(f"Error handling POST request: {e}")
            self.send_error(500, f"Internal server error: {str(e)}")
    
    def handle_api_data(self):
        """Return vehicle data with calculated status"""
        try:
            data = self.load_data()
            enriched_data = []
            
            for vehicle in data:
                # Calculate days to expiry
                days_stnk = self.calculate_days(vehicle.get('STNK') or vehicle.get('stnk_date'))
                days_pajak = self.calculate_days(vehicle.get('PAJAK') or vehicle.get('pajak_date'))
                
                # Use the earliest expiry date
                days_to_expiry = min(days_stnk, days_pajak)
                
                # Determine status
                status = self.calculate_status(days_to_expiry)
                
                # Enrich vehicle data
                enriched_vehicle = {
                    **vehicle,
                    'days_to_expiry': days_to_expiry,
                    'status': status,
                    'stnk_days': days_stnk,
                    'pajak_days': days_pajak
                }
                enriched_data.append(enriched_vehicle)
            
            self.send_json_response(enriched_data)
            
        except Exception as e:
            logger.error(f"Error in handle_api_data: {e}")
            self.send_error(500, f"Error processing data: {str(e)}")
    
    def handle_api_stats(self):
        """Return dashboard statistics"""
        try:
            data = self.load_data()
            stats = {
                'total': len(data),
                'by_status': {'safe': 0, 'warning': 0, 'priority': 0},
                'by_category': {},
                'recent_updates': []
            }
            
            for vehicle in data:
                days_stnk = self.calculate_days(vehicle.get('STNK') or vehicle.get('stnk_date'))
                days_pajak = self.calculate_days(vehicle.get('PAJAK') or vehicle.get('pajak_date'))
                days_to_expiry = min(days_stnk, days_pajak)
                status = self.calculate_status(days_to_expiry)
                
                stats['by_status'][status] += 1
                
                # Count by category
                category = vehicle.get('Jenis', 'Unknown')
                stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
            
            self.send_json_response(stats)
            
        except Exception as e:
            logger.error(f"Error in handle_api_stats: {e}")
            self.send_error(500, f"Error calculating stats: {str(e)}")
    
    def handle_api_backups(self):
        """Return list of backup files"""
        try:
            backups = []
            backup_path = Path(BACKUP_DIR)
            
            if backup_path.exists():
                for file in backup_path.glob('*.json'):
                    backups.append({
                        'filename': file.name,
                        'size': file.stat().st_size,
                        'modified': datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                    })
            
            # Sort by modified time (newest first)
            backups.sort(key=lambda x: x['modified'], reverse=True)
            
            self.send_json_response(backups)
            
        except Exception as e:
            logger.error(f"Error in handle_api_backups: {e}")
            self.send_error(500, f"Error listing backups: {str(e)}")
    
    def handle_api_update(self):
        """Update vehicle dates after payment"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            update_data = json.loads(post_data.decode('utf-8'))
            
            # Validate required fields
            required_fields = ['id', 'stnk_date', 'pajak_date']
            for field in required_fields:
                if field not in update_data:
                    self.send_error(400, f"Missing required field: {field}")
                    return
            
            # Create backup before update
            self.create_backup()
            
            # Load current data
            data = self.load_data()
            
            # Find and update vehicle
            vehicle_found = False
            for i, vehicle in enumerate(data):
                if vehicle.get('id') == update_data['id']:
                    # Update dates
                    data[i]['stnk_date'] = update_data['stnk_date']
                    data[i]['pajak_date'] = update_data['pajak_date']
                    
                    # Add update note if provided
                    if 'note' in update_data and update_data['note']:
                        current_note = data[i].get('catatan', '')
                        new_note = f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] {update_data['note']}"
                        if current_note:
                            data[i]['catatan'] = f"{current_note}\n{new_note}"
                        else:
                            data[i]['catatan'] = new_note
                    
                    vehicle_found = True
                    break
            
            if not vehicle_found:
                self.send_error(404, f"Vehicle with ID {update_data['id']} not found")
                return
            
            # Save updated data
            self.save_data(data)
            
            # Return success response
            response = {
                'success': True,
                'message': 'Data updated successfully',
                'backup_created': True,
                'updated_at': datetime.now().isoformat()
            }
            
            self.send_json_response(response)
            logger.info(f"Vehicle {update_data['id']} updated successfully")
            
        except json.JSONDecodeError:
            self.send_error(400, "Invalid JSON data")
        except Exception as e:
            logger.error(f"Error in handle_api_update: {e}")
            self.send_error(500, f"Error updating data: {str(e)}")
    
    def handle_api_health(self):
        """Health check endpoint"""
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'data_file_exists': os.path.exists(DATA_FILE),
            'backup_dir_exists': os.path.exists(BACKUP_DIR),
            'data_count': len(self.load_data()) if os.path.exists(DATA_FILE) else 0
        }
        self.send_json_response(health_status)
    
    def serve_file(self, filename, content_type):
        """Serve static file"""
        try:
            filepath = Path(filename)
            if not filepath.exists():
                self.send_error(404, f"File not found: {filename}")
                return
            
            with open(filepath, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(content)
            
        except Exception as e:
            logger.error(f"Error serving file {filename}: {e}")
            self.send_error(500, f"Error serving file: {str(e)}")
    
    def send_json_response(self, data):
        """Send JSON response"""
        try:
            json_data = json.dumps(data, ensure_ascii=False, indent=2)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(json_data.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error sending JSON response: {e}")
            self.send_error(500, f"Error encoding JSON: {str(e)}")
    
    def load_data(self):
        """Load vehicle data from JSON file"""
        try:
            if not os.path.exists(DATA_FILE):
                # Create sample data if file doesn't exist
                sample_data = self.create_sample_data()
                self.save_data(sample_data)
                return sample_data
            
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Ensure all vehicles have required fields
            for vehicle in data:
                if 'id' not in vehicle:
                    vehicle['id'] = data.index(vehicle) + 1
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON from {DATA_FILE}: {e}")
            # Try to restore from backup
            return self.restore_from_backup()
        except Exception as e:
            logger.error(f"Error loading data from {DATA_FILE}: {e}")
            return []
    
    def save_data(self, data):
        """Save vehicle data to JSON file"""
        try:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"Data saved to {DATA_FILE}")
        except Exception as e:
            logger.error(f"Error saving data to {DATA_FILE}: {e}")
            raise
    
    def create_backup(self):
        """Create backup of current data"""
        try:
            # Create backup directory if it doesn't exist
            os.makedirs(BACKUP_DIR, exist_ok=True)
            
            # Load current data
            data = self.load_data()
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(BACKUP_DIR, f'backup_{timestamp}.json')
            
            # Save backup
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Backup created: {backup_file}")
            return backup_file
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None
    
    def restore_from_backup(self):
        """Restore data from latest backup"""
        try:
            backup_path = Path(BACKUP_DIR)
            if not backup_path.exists():
                return self.create_sample_data()
            
            # Find latest backup
            backups = list(backup_path.glob('*.json'))
            if not backups:
                return self.create_sample_data()
            
            latest_backup = max(backups, key=lambda x: x.stat().st_mtime)
            
            with open(latest_backup, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Save restored data
            self.save_data(data)
            logger.info(f"Data restored from backup: {latest_backup}")
            
            return data
            
        except Exception as e:
            logger.error(f"Error restoring from backup: {e}")
            return self.create_sample_data()
    
    def create_sample_data(self):
        """Create sample vehicle data"""
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
            },
            {
                "id": 2,
                "merk": "TOYOTA AVANZA",
                "no_polisi": "B 1234 ABC",
                "kategori": "Roda Empat",
                "stnk_date": "2026-08-15",
                "pajak_date": "2026-07-20",
                "ktp": "JOHN DOE",
                "catatan": "Pajak lebih dulu dari STNK"
            },
            {
                "id": 3,
                "merk": "SUZUKI SATRIA",
                "no_polisi": "F 5678 XYZ",
                "kategori": "Roda Dua",
                "stnk_date": "2026-03-10",
                "pajak_date": "2026-03-10",
                "ktp": "JANE SMITH",
                "catatan": "Segera diperpanjang"
            },
            {
                "id": 4,
                "merk": "MITSUBISHI PAJERO",
                "no_polisi": "B 9876 DEF",
                "kategori": "Roda Empat",
                "stnk_date": "2026-12-01",
                "pajak_date": "2026-11-15",
                "ktp": "ROBERT BROWN",
                "catatan": "Masih lama"
            },
            {
                "id": 5,
                "merk": "YAMAHA NMAX",
                "no_polisi": "BK 1122 EFG",
                "kategori": "Roda Dua",
                "stnk_date": "2026-01-30",
                "pajak_date": "2026-01-30",
                "ktp": "ALICE WONDER",
                "catatan": "Prioritas tinggi"
            }
        ]
        
        # Save sample data
        self.save_data(sample_data)
        logger.info("Sample data created")
        
        return sample_data
    
    def calculate_days(self, date_str):
        """Calculate days from today to given date"""
        if not date_str:
            return 9999  # Far future if no date
        
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            today = date.today()
            
            # Handle past dates (negative days)
            delta = (target_date - today).days
            return max(delta, 0)  # Return 0 for expired dates
            
        except ValueError:
            return 9999
    
    def calculate_status(self, days):
        """Calculate status based on days to expiry"""
        if days <= 30:
            return 'priority'
        elif days <= 90:
            return 'warning'
        else:
            return 'safe'
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info("%s - %s" % (self.address_string(), format % args))

def main():
    """Main function to start the server"""
    # Create necessary directories
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Check if data file exists, create sample if not
    if not os.path.exists(DATA_FILE):
        handler = ModernDashboardHandler
        handler.create_sample_data(handler)
    
    # Start server
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, ModernDashboardHandler)
    
    logger.info(f"🚀 Modern STNK Dashboard Server starting on port {PORT}")
    logger.info(f"📊 Dashboard URL: http://localhost:{PORT}")
    logger.info(f"📁 Data file: {os.path.abspath(DATA_FILE)}")
    logger.info(f"💾 Backup directory: {os.path.abspath(BACKUP_DIR)}")
    logger.info("Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("\n🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()