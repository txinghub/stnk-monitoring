#!/usr/bin/env python3
"""
Modern STNK Dashboard Server - TIDAL Style
Premium dark theme dashboard with gradient animations
SQLite Backend with User Authentication
"""

import json
import os
import sys
import sqlite3
import hashlib
import secrets
import re
from datetime import datetime, date, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from pathlib import Path
import logging

# Configuration
PORT = 8087
DATA_FILE = "data.json"
DATABASE_FILE = "vehicles.db"
BACKUP_DIR = "backups"
LOG_FILE = "server.log"
SESSION_DURATION_HOURS = 24

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


def get_db_connection():
    """Get SQLite database connection"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize SQLite database with tables"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create vehicles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY,
            "No." TEXT,
            MERK TEXT,
            Jenis TEXT,
            "No.Polisi" TEXT,
            STNK TEXT,
            PAJAK TEXT,
            KTP TEXT,
            Catatan TEXT
        )
    ''')

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            display_name TEXT,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()

    # Create default users if not exist
    admin_hash = hashlib.sha256("syncmaster740".encode()).hexdigest()
    try:
        # UPDATE existing admin password to ensure it's correct
        cursor.execute('UPDATE users SET password_hash = ? WHERE username = ?', (admin_hash, 'admin'))
        if cursor.rowcount == 0:
            # Insert only if admin doesn't exist
            cursor.execute('''
                INSERT INTO users (username, password_hash, display_name, role)
                VALUES (?, ?, ?, ?)
            ''', ('admin', admin_hash, 'Administrator', 'admin'))
        conn.commit()
        print("✅ Admin user ready")
    except Exception as e:
        pass

    demo_hash = hashlib.sha256("demo123".encode()).hexdigest()
    try:
        cursor.execute('UPDATE users SET password_hash = ? WHERE username = ?', (demo_hash, 'demo'))
        if cursor.rowcount == 0:
            cursor.execute('''
                INSERT INTO users (username, password_hash, display_name, role)
                VALUES (?, ?, ?, ?)
            ''', ('demo', demo_hash, 'Demo User', 'user'))
        conn.commit()
        print("✅ Demo user ready")
    except Exception as e:
        pass

    conn.close()


class AuthHandler(BaseHTTPRequestHandler):
    """Base handler with auth utilities"""

    def get_token_from_header(self):
        """Extract token from Authorization header"""
        auth_header = self.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]
        return None

    def validate_session(self):
        """Validate session token and return user info"""
        token = self.get_token_from_header()
        if not token:
            return None

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.id, u.username, u.display_name, u.role, s.expires_at
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.token = ? AND s.expires_at > ?
        ''', (token, datetime.now().isoformat()))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def require_auth(self):
        """Require valid session - returns 401 if not authenticated"""
        user = self.validate_session()
        if not user:
            self.send_error(401, "Authentication required")
            return None
        return user

    def send_json_response(self, data, status=200):
        """Send JSON response"""
        try:
            json_data = json.dumps(data, ensure_ascii=False, indent=2)
            self.send_response(status)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, PUT, OPTIONS')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(json_data.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error sending JSON response: {e}")
            self.send_error(500, f"Error encoding JSON: {str(e)}")

    def send_file(self, filename, content_type):
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

    def load_data(self):
        """Load vehicle data from SQLite database"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id, "No.", MERK, Jenis, "No.Polisi", STNK, PAJAK, KTP, Catatan FROM vehicles ORDER BY id')
            rows = cursor.fetchall()
            conn.close()

            data = []
            for row in rows:
                vehicle = {
                    'id': row[0],
                    'No.': row[1],
                    'MERK': row[2],
                    'Jenis': row[3],
                    'No.Polisi': row[4],
                    'STNK': row[5],
                    'PAJAK': row[6],
                    'KTP': row[7],
                    'Catatan': row[8] or ''
                }
                data.append(vehicle)
            return data
        except Exception as e:
            logger.error(f"Error loading data from database: {e}")
            return []

    def calculate_days(self, date_str):
        """Calculate days from today to given date"""
        if not date_str:
            return 9999
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            today = date.today()
            return (target_date - today).days
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


class ModernDashboardHandler(AuthHandler):
    """HTTP request handler for modern dashboard"""

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, PUT, OPTIONS')
        self.end_headers()

    def do_GET(self):
        """Handle GET requests"""
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path

            # Auth endpoints (no auth required)
            if path == '/api/login':
                self.handle_login()
            elif path == '/api/logout':
                self.handle_logout()
            elif path in ('/api/me', '/api/verify'):
                self.handle_me()
            elif path == '/api/users':
                self.handle_list_users()

            # Protected API endpoints
            elif path in ('/api/data', '/api/vehicles'):
                if not self.validate_session():
                    self.send_error(401, "Authentication required")
                    return
                self.handle_api_data()
            elif path == '/api/stats':
                if not self.validate_session():
                    self.send_error(401, "Authentication required")
                    return
                self.handle_api_stats()
            elif path == '/api/backups':
                if not self.validate_session():
                    self.send_error(401, "Authentication required")
                    return
                self.handle_api_backups()
            elif path == '/api/health':
                self.handle_api_health()

            # Static files
            elif path == '/' or path == '/index_admin.html':
                self.send_file('index_admin.html', 'text/html')
            elif path == '/login.html':
                self.send_file('login.html', 'text/html')
            elif path == '/login2.html':
                self.send_file('login2.html', 'text/html')
            elif path == '/script.js':
                self.send_file('script.js', 'application/javascript')
            elif path.endswith('.css'):
                self.send_file(path[1:], 'text/css')
            elif path.endswith('.js'):
                self.send_file(path[1:], 'application/javascript')
            else:
                self.send_error(404, "File not found")

        except Exception as e:
            logger.error(f"Error handling GET request: {e}")
            self.send_error(500, f"Internal server error: {str(e)}")

    def do_POST(self):
        """Handle POST requests"""
        try:
            if self.path == '/api/login':
                self.handle_login()
            elif self.path == '/api/logout':
                self.handle_logout()
            elif self.path == '/api/register':
                self.handle_register()
            elif self.path == '/api/update':
                if not self.require_auth():
                    return
                user = self.validate_session()
                if user.get('role') != 'admin':
                    self.send_error(403, "Admin only")
                    return
                self.handle_api_update()
            elif self.path == '/api/add':
                if not self.require_auth():
                    return
                user = self.validate_session()
                if user.get('role') != 'admin':
                    self.send_error(403, "Admin only")
                    return
                self.handle_api_add()
            elif self.path == '/api/delete':
                if not self.require_auth():
                    return
                user = self.validate_session()
                if user.get('role') != 'admin':
                    self.send_error(403, "Admin only")
                    return
                self.handle_api_delete()
            elif self.path == '/api/edit':
                if not self.require_auth():
                    return
                user = self.validate_session()
                if user.get('role') != 'admin':
                    self.send_error(403, "Admin only")
                    return
                self.handle_api_edit()
            elif self.path == '/api/users':
                if not self.require_auth():
                    return
                user = self.validate_session()
                if user.get('role') != 'admin':
                    self.send_error(403, "Admin only")
                    return
                self.handle_list_users()
            elif self.path == '/api/users/delete':
                if not self.require_auth():
                    return
                user = self.validate_session()
                if user.get('role') != 'admin':
                    self.send_error(403, "Admin only")
                    return
                self.handle_delete_user()
            else:
                self.send_error(404, "Endpoint not found")
        except Exception as e:
            logger.error(f"Error handling POST request: {e}")
            self.send_error(500, f"Internal server error: {str(e)}")

    def do_DELETE(self):
        """Handle DELETE requests"""
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path = parsed_path.path

            # /api/users/{id} - delete user
            if path.startswith('/api/users/'):
                user_id = path.split('/')[-1]
                if not user_id.isdigit():
                    self.send_error(400, "Invalid user ID")
                    return
                if not self.require_auth():
                    return
                user = self.validate_session()
                if user.get('role') != 'admin':
                    self.send_error(403, "Admin only")
                    return
                self.handle_delete_user(int(user_id))
            else:
                self.send_error(404, "Endpoint not found")
        except Exception as e:
            logger.error(f"Error handling DELETE request: {e}")
            self.send_error(500, f"Internal server error: {str(e)}")

    def handle_login(self):
        """Handle login request"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            login_data = json.loads(post_data.decode('utf-8'))

            username = login_data.get('username', '').strip()
            password = login_data.get('password', '')

            if not username or not password:
                self.send_json_response({'success': False, 'error': 'Username dan password required'}, 400)
                return

            # Validate input
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                self.send_json_response({'success': False, 'error': 'Username tidak valid'}, 400)
                return

            password_hash = hashlib.sha256(password.encode()).hexdigest()

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id, username, display_name, role FROM users WHERE username = ? AND password_hash = ?',
                         (username, password_hash))
            user = cursor.fetchone()
            conn.close()

            if not user:
                self.send_json_response({'success': False, 'error': 'Username atau password salah'}, 401)
                return

            # Create session token
            token = secrets.token_urlsafe(32)
            expires_at = (datetime.now() + timedelta(hours=SESSION_DURATION_HOURS)).isoformat()

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)',
                         (user['id'], token, expires_at))
            conn.commit()
            conn.close()

            logger.info(f"User logged in: {username}")

            self.send_json_response({
                'success': True,
                'token': token,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'display_name': user['display_name'],
                    'role': user['role']
                }
            })

        except json.JSONDecodeError:
            self.send_json_response({'success': False, 'error': 'Invalid JSON'}, 400)
        except Exception as e:
            logger.error(f"Error in handle_login: {e}")
            self.send_json_response({'success': False, 'error': str(e)}, 500)

    def handle_logout(self):
        """Handle logout request"""
        token = self.get_token_from_header()
        if token:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM sessions WHERE token = ?', (token,))
            conn.commit()
            conn.close()
            logger.info(f"User logged out: {token[:20]}...")
        self.send_json_response({'success': True})

    def handle_me(self):
        """Get current user info"""
        user = self.validate_session()
        if not user:
            self.send_error(401, "Not authenticated")
            return
        self.send_json_response({
            'authenticated': True,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'display_name': user['display_name'],
                'role': user['role']
            }
        })

    def handle_register(self):
        """Handle user registration (admin only in production)"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            reg_data = json.loads(post_data.decode('utf-8'))

            username = reg_data.get('username', '').strip()
            password = reg_data.get('password', '')
            display_name = reg_data.get('display_name', username)
            role = reg_data.get('role', 'user').strip()

            if not username or not password:
                self.send_json_response({'success': False, 'error': 'Username dan password required'}, 400)
                return

            if len(password) < 4:
                self.send_json_response({'success': False, 'error': 'Password minimal 4 karakter'}, 400)
                return

            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                self.send_json_response({'success': False, 'error': 'Username tidak valid'}, 400)
                return

            password_hash = hashlib.sha256(password.encode()).hexdigest()

            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO users (username, password_hash, display_name, role) VALUES (?, ?, ?, ?)',
                             (username, password_hash, display_name, role))
                conn.commit()
                user_id = cursor.lastrowid
                self.send_json_response({'success': True, 'user_id': user_id})
                logger.info(f"User registered: {username}")
            except sqlite3.IntegrityError:
                self.send_json_response({'success': False, 'error': 'Username sudah ada'}, 400)
            conn.close()

        except json.JSONDecodeError:
            self.send_json_response({'success': False, 'error': 'Invalid JSON'}, 400)
        except Exception as e:
            logger.error(f"Error in handle_register: {e}")
            self.send_json_response({'success': False, 'error': str(e)}, 500)

    def handle_list_users(self):
        """List all users (admin only)"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, display_name, role, created_at FROM users ORDER BY id')
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        self.send_json_response(users)

    def handle_delete_user(self, user_id=None):
        """Delete a user (admin only)"""
        try:
            # Get user_id from parameter (DELETE request) or body (POST request)
            if user_id is None:
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                user_id = data.get('id')
            
            if not user_id:
                self.send_json_response({'success': False, 'error': 'User ID required'}, 400)
                return

            # Can't delete yourself
            current_user = self.validate_session()
            if current_user['id'] == user_id:
                self.send_json_response({'success': False, 'error': 'Tidak bisa hapus diri sendiri'}, 400)
                return

            conn = get_db_connection()
            cursor = conn.cursor()

            # Delete user's sessions first
            cursor.execute('DELETE FROM sessions WHERE user_id = ?', (user_id,))
            # Delete user (any role, except can't delete yourself)
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            conn.close()

            self.send_json_response({'success': True})
            logger.info(f"User deleted: ID {user_id}")

        except json.JSONDecodeError:
            self.send_json_response({'success': False, 'error': 'Invalid JSON'}, 400)
        except Exception as e:
            logger.error(f"Error in handle_delete_user: {e}")
            self.send_json_response({'success': False, 'error': str(e)}, 500)

    def handle_api_data(self):
        """Return vehicle data with calculated status"""
        try:
            data = self.load_data()
            enriched_data = []
            for vehicle in data:
                days_stnk = self.calculate_days(vehicle.get('STNK'))
                days_pajak = self.calculate_days(vehicle.get('PAJAK'))
                days_to_expiry = min(days_stnk, days_pajak)
                status = self.calculate_status(days_to_expiry)
                
                # Calculate individual status for STNK and PAJAK
                if days_stnk <= 0:
                    stnk_status = 'expired'
                elif days_stnk <= 30:
                    stnk_status = 'expiry_soon'
                else:
                    stnk_status = 'valid'
                    
                if days_pajak <= 0:
                    pajak_status = 'expired'
                elif days_pajak <= 30:
                    pajak_status = 'expiry_soon'
                else:
                    pajak_status = 'valid'
                
                enriched_vehicle = {
                    **vehicle,
                    'days_to_expiry': days_to_expiry,
                    'status': status,
                    'stnk_days': days_stnk,
                    'pajak_days': days_pajak,
                    'stnk_status': stnk_status,
                    'pajak_status': pajak_status
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
                'by_category': {}
            }
            for vehicle in data:
                days_stnk = self.calculate_days(vehicle.get('STNK'))
                days_pajak = self.calculate_days(vehicle.get('PAJAK'))
                days_to_expiry = min(days_stnk, days_pajak)
                status = self.calculate_status(days_to_expiry)
                stats['by_status'][status] += 1
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
            backups.sort(key=lambda x: x['modified'], reverse=True)
            self.send_json_response(backups)
        except Exception as e:
            logger.error(f"Error in handle_api_backups: {e}")
            self.send_error(500, f"Error listing backups: {str(e)}")

    def handle_api_health(self):
        """Health check endpoint"""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM vehicles')
        count = cursor.fetchone()[0]
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        conn.close()
        self.send_json_response({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database_exists': os.path.exists(DATABASE_FILE),
            'data_count': count,
            'user_count': user_count
        })

    def handle_api_update(self):
        """Update vehicle data"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            update_data = json.loads(post_data.decode('utf-8'))

            required_fields = ['id']
            for field in required_fields:
                if field not in update_data:
                    self.send_json_response({'success': False, 'error': f'Missing: {field}'}, 400)
                    return

            conn = get_db_connection()
            cursor = conn.cursor()

            # Build dynamic update query - quote field names that need it
            updates = []
            params = []
            
            field_mapping = {
                'merk': 'MERK',
                'no_polisi': '"No.Polisi"',
                'jenis': 'Jenis',
                'ktp': 'KTP',
                'stnk_exp': 'STNK',
                'pajak_exp': 'PAJAK'
            }
            
            for frontend_field, db_field in field_mapping.items():
                if frontend_field in update_data:
                    updates.append(f'{db_field} = ?')
                    params.append(update_data[frontend_field])
            
            if not updates:
                conn.close()
                self.send_json_response({'success': False, 'error': 'No fields to update'}, 400)
                return

            params.append(update_data['id'])
            cursor.execute(f'UPDATE vehicles SET {", ".join(updates)} WHERE id = ?', params)
            conn.commit()
            conn.close()

            self.send_json_response({'success': True, 'message': 'Data updated'})

        except json.JSONDecodeError:
            self.send_json_response({'success': False, 'error': 'Invalid JSON'}, 400)
        except Exception as e:
            logger.error(f"Error in handle_api_update: {e}")
            self.send_json_response({'success': False, 'error': str(e)}, 500)

    def handle_api_add(self):
        """Add new vehicle data"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            add_data = json.loads(post_data.decode('utf-8'))

            if not add_data.get('merk') or not add_data.get('no_polisi'):
                self.send_json_response({'success': False, 'error': 'merk dan no_polisi required'}, 400)
                return

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT MAX(id) FROM vehicles')
            max_id = cursor.fetchone()[0] or 0
            cursor.execute('SELECT MAX(CAST("No." AS INTEGER)) FROM vehicles')
            max_no = cursor.fetchone()[0] or 0

            cursor.execute('''INSERT INTO vehicles (id, "No.", MERK, Jenis, "No.Polisi", STNK, PAJAK, KTP, Catatan)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                         (max_id + 1, str(max_no + 1),
                          add_data.get('merk', ''), add_data.get('jenis', ''),
                          add_data.get('no_polisi', ''), add_data.get('stnk_exp', ''),
                          add_data.get('pajak_exp', ''), add_data.get('ktp', ''),
                          add_data.get('catatan', '')))
            conn.commit()
            conn.close()

            self.send_json_response({'success': True, 'message': 'Kendaraan ditambahkan'})

        except json.JSONDecodeError:
            self.send_json_response({'success': False, 'error': 'Invalid JSON'}, 400)
        except Exception as e:
            logger.error(f"Error in handle_api_add: {e}")
            self.send_json_response({'success': False, 'error': str(e)}, 500)

    def handle_api_delete(self):
        """Delete vehicle by ID"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            delete_data = json.loads(post_data.decode('utf-8'))

            vehicle_id = delete_data.get('id')
            if not vehicle_id:
                self.send_json_response({'success': False, 'error': 'ID required'}, 400)
                return

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM vehicles WHERE id = ?', (vehicle_id,))

            # Re-index
            cursor.execute('SELECT id FROM vehicles ORDER BY id')
            for idx, (vid,) in enumerate(cursor.fetchall(), 1):
                cursor.execute('UPDATE vehicles SET "No." = ? WHERE id = ?', (str(idx), vid))

            conn.commit()
            conn.close()

            self.send_json_response({'success': True, 'message': 'Kendaraan dihapus'})

        except json.JSONDecodeError:
            self.send_json_response({'success': False, 'error': 'Invalid JSON'}, 400)
        except Exception as e:
            logger.error(f"Error in handle_api_delete: {e}")
            self.send_json_response({'success': False, 'error': str(e)}, 500)

    def handle_api_edit(self):
        """Edit vehicle data"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            edit_data = json.loads(post_data.decode('utf-8'))

            vehicle_id = edit_data.get('id')
            if not vehicle_id:
                self.send_json_response({'success': False, 'error': 'ID required'}, 400)
                return

            conn = get_db_connection()
            cursor = conn.cursor()

            updates = []
            params = []
            field_map = {'merk': 'MERK', 'no_polisi': '"No.Polisi"', 'jenis': 'Jenis',
                        'stnk': 'STNK', 'pajak': 'PAJAK', 'ktp': 'KTP', 'catatan': 'Catatan'}
            for key, db_field in field_map.items():
                if key in edit_data:
                    updates.append(f'{db_field} = ?')
                    params.append(edit_data[key])

            if updates:
                params.append(vehicle_id)
                cursor.execute(f'UPDATE vehicles SET {", ".join(updates)} WHERE id = ?', params)

            conn.commit()
            conn.close()

            self.send_json_response({'success': True, 'message': 'Kendaraan diedit'})

        except json.JSONDecodeError:
            self.send_json_response({'success': False, 'error': 'Invalid JSON'}, 400)
        except Exception as e:
            logger.error(f"Error in handle_api_edit: {e}")
            self.send_json_response({'success': False, 'error': str(e)}, 500)

    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info("%s - %s" % (self.address_string(), format % args))


def main():
    """Main function to start the server"""
    os.makedirs(BACKUP_DIR, exist_ok=True)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    init_database()

    server_address = ('127.0.0.1', PORT)
    httpd = HTTPServer(server_address, ModernDashboardHandler)
    httpd.allow_reuse_address = True

    logger.info(f"🚀 STNK Dashboard starting on port {PORT}")
    logger.info(f"📊 Dashboard: http://localhost:{PORT}")
    logger.info(f"💾 Database: {os.path.abspath(DATABASE_FILE)}")
    logger.info("🔐 Login required")
    logger.info("👤 Default: admin/admin123 or demo/demo123")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("\n🛑 Server stopped")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
