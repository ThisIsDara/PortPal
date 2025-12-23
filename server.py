"""
Local hosting server for websites and files.
Created by <ThisIsDara> - <AlirezaJahangiri>
This credit is optional and may be removed.
"""


import http.server
import socketserver
import argparse
import os
import json
import socket
import threading
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse, parse_qs
from typing import Optional, Tuple
from collections import defaultdict


# Thread pool for background operations
background_executor = ThreadPoolExecutor(max_workers=2)

# Global password variable
SERVER_PASSWORD = None
SERVER_USERNAME = None

# Brute force protection
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 900  # 15 minutes in seconds
login_attempts = defaultdict(list)  # IP -> list of attempt timestamps
locked_ips = {}  # IP -> lockout timestamp

# Online users tracking
online_users = {}
online_lock = threading.Lock()
ONLINE_TIMEOUT = 30  # consider user offline after 30 seconds without ping

def device_from_ua(ua: str) -> str:
    ua = (ua or '').lower()
    if 'iphone' in ua or 'ipad' in ua or 'ipod' in ua:
        return 'iOS'
    if 'android' in ua:
        return 'Android'
    if 'windows phone' in ua:
        return 'Windows Phone'
    if 'windows' in ua:
        return 'Windows'
    if 'mac os' in ua or 'macintosh' in ua or 'darwin' in ua:
        return 'Mac'
    if 'linux' in ua:
        return 'Linux'
    if 'chrome' in ua:
        return 'Chrome'
    return 'Unknown'


class CustomHTTPHandler(http.server.SimpleHTTPRequestHandler):
    root_dir = os.getcwd()

    def _get_client_ip(self) -> str:
        """Get the client's IP address"""
        # Check for X-Forwarded-For header (if behind proxy)
        forwarded = self.headers.get('X-Forwarded-For')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return self.client_address[0]

    def _is_ip_locked(self, ip: str) -> bool:
        """Check if an IP is currently locked out"""
        global locked_ips
        if ip in locked_ips:
            lock_time = locked_ips[ip]
            if time.time() - lock_time < LOCKOUT_DURATION:
                return True
            else:
                # Lockout expired, remove it
                del locked_ips[ip]
                if ip in login_attempts:
                    login_attempts[ip].clear()
        return False

    def _record_failed_login(self, ip: str):
        """Record a failed login attempt"""
        global login_attempts, locked_ips
        current_time = time.time()
        
        # Remove attempts older than lockout duration
        login_attempts[ip] = [t for t in login_attempts[ip] if current_time - t < LOCKOUT_DURATION]
        
        # Add current attempt
        login_attempts[ip].append(current_time)
        
        # Check if we should lock this IP
        if len(login_attempts[ip]) >= MAX_LOGIN_ATTEMPTS:
            locked_ips[ip] = current_time
            print(f"⚠️  IP {ip} locked out after {MAX_LOGIN_ATTEMPTS} failed login attempts")

    def _clear_failed_logins(self, ip: str):
        """Clear failed login attempts for an IP after successful login"""
        global login_attempts, locked_ips
        if ip in login_attempts:
            login_attempts[ip].clear()
        if ip in locked_ips:
            del locked_ips[ip]

    def _is_authenticated(self) -> bool:
        """Check if the request has valid authentication"""
        global SERVER_PASSWORD, SERVER_USERNAME
        # If neither username nor password is set, allow all requests
        if (SERVER_USERNAME is None or SERVER_USERNAME == "") and (SERVER_PASSWORD is None or SERVER_PASSWORD == ""):
            return True
        # Check for valid session cookie
        cookies = self.headers.get('Cookie', '')
        return 'session=valid' in cookies

    def _set_cors_headers(self):
        """Set CORS headers for API responses"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Requested-With')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')

    def _safe_path(self, rel_path: str) -> Optional[str]:
        rel_path = rel_path.strip() if rel_path else ''
        rel_path = rel_path.lstrip('/\\')
        norm_rel = os.path.normpath(rel_path)
        abs_path = os.path.normpath(os.path.join(self.root_dir, norm_rel))
        if not abs_path.startswith(self.root_dir):
            return None
        return abs_path

    def _save_path(self, rel_dir: str, filename: str) -> Optional[str]:
        """Return absolute path to save filename inside rel_dir; ensure dir exists and is inside root."""
        target_dir = self._safe_path(rel_dir)
        if target_dir is None or not os.path.isdir(target_dir):
            return None
        safe_name = os.path.basename(filename)
        return os.path.join(target_dir, safe_name)

    def _list_dir(self, rel_path: str):
        abs_path = self._safe_path(rel_path)
        if abs_path is None or not os.path.isdir(abs_path):
            return None

        items = []
        try:
            for name in os.listdir(abs_path):
                if name == 'index.html':
                    continue
                full = os.path.join(abs_path, name)
                is_dir = os.path.isdir(full)
                size = os.path.getsize(full) if not is_dir else 0
                items.append({
                    'name': name,
                    'type': 'dir' if is_dir else 'file',
                    'size': size
                })
            items.sort(key=lambda x: (x['type'] != 'dir', x['name'].lower()))
        except Exception as e:
            print(f"Error listing path {rel_path}: {e}")
            return None

        # Normalize paths for client
        clean_path = rel_path.replace('\\', '/').strip('.') if rel_path else ''
        parent = ''
        if clean_path:
            parent = os.path.normpath(os.path.join(clean_path, '..')).replace('\\', '/')
            if parent == '.':
                parent = ''

        return {
            'path': clean_path,
            'parent': parent,
            'items': items
        }

    def _parse_multipart(self, content_type: str) -> Tuple[Optional[str], Optional[bytes]]:
        """Minimal multipart/form-data parser that returns (filename, file_bytes) for the 'file' part."""
        # Extract boundary
        parts = content_type.split('boundary=')
        if len(parts) < 2:
            return None, None
        boundary = parts[1].strip().strip('"')
        boundary_bytes = ('--' + boundary).encode()

        try:
            content_length = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            content_length = 0
        if content_length <= 0:
            return None, None

        raw_data = self.rfile.read(content_length)
        # Split parts ignoring the first preamble and last epilogue
        segments = raw_data.split(boundary_bytes)
        for segment in segments:
            if not segment or segment in (b'--', b'--\r\n'):
                continue
            # Each part: headers \r\n\r\n body
            if segment.startswith(b'\r\n'):
                segment = segment[2:]
            try:
                header_bytes, body = segment.split(b'\r\n\r\n', 1)
            except ValueError:
                continue
            headers_text = header_bytes.decode(errors='ignore')
            body = body.rstrip(b'\r\n')  # strip trailing newlines and boundary markers

            disposition = None
            for line in headers_text.split('\r\n'):
                if line.lower().startswith('content-disposition:'):
                    disposition = line
                    break
            if not disposition:
                continue

            # Parse filename from content-disposition
            filename = None
            for token in disposition.split(';'):
                token = token.strip()
                if token.startswith('filename='):
                    filename = token.split('=', 1)[1].strip('"')
                if token.startswith('name='):
                    field_name = token.split('=', 1)[1].strip('"')
            if field_name != 'file':
                continue
            if not filename:
                continue

            return filename, body
        return None, None

    def do_OPTIONS(self):
        if self.path in ['/api/upload', '/api/delete', '/api/storage']:
            self.send_response(204)
            self._set_cors_headers()
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
            self.end_headers()
            return
        super().do_OPTIONS()

    def do_GET(self):
        parsed = urlparse(self.path)
        # check if password is set
        if parsed.path == '/api/has_password':
            global SERVER_PASSWORD, SERVER_USERNAME
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self._set_cors_headers()
            self.end_headers()
            # Check if either username or password is set (authentication required)
            # Must match the logic in _is_authenticated() - both None or empty strings mean no auth
            has_auth = not ((SERVER_USERNAME is None or SERVER_USERNAME == "") and (SERVER_PASSWORD is None or SERVER_PASSWORD == ""))
            self.wfile.write(json.dumps({'has_password': has_auth}).encode())
            return
        # Handle API endpoint for file listing with optional path
        if parsed.path == '/api/files':
            # Check authentication for file listing
            if not self._is_authenticated():
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Unauthorized'}).encode())
                return
            
            query = parse_qs(parsed.query)
            rel_path = query.get('path', [''])[0]

            listing = self._list_dir(rel_path)
            if listing is None:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Invalid path'}).encode())
                return

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(listing).encode())
            return

        # Storage info endpoint
        if parsed.path == '/api/storage':
            # Check authentication for storage info
            if not self._is_authenticated():
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Unauthorized'}).encode())
                return
            
            try:
                total, used, free = shutil.disk_usage(self.root_dir)
                percent_used = (used / total * 100.0) if total else 0.0
                payload = {
                    'mount': os.path.abspath(self.root_dir).replace('\\', '/'),
                    'total': int(total),
                    'used': int(used),
                    'free': int(free),
                    'percent_used': round(percent_used, 1)
                }
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps(payload).encode())
            except Exception as e:
                print(f"Storage info error: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Unable to read storage info'}).encode())
            return

        # Online users listing
        if parsed.path == '/api/online_users':
            # Require authentication to view online users (keep consistent with files/storage)
            if not self._is_authenticated():
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Unauthorized'}).encode())
                return

            # purge stale entries
            current_time = time.time()
            with online_lock:
                stale = [ip for ip, info in online_users.items() if current_time - info.get('last_seen', 0) > ONLINE_TIMEOUT]
                for ip in stale:
                    del online_users[ip]

                payload = []
                for ip, info in online_users.items():
                    payload.append({
                        'ip': ip,
                        'device': info.get('device', ''),
                        'last_seen': int(info.get('last_seen', 0))
                    })

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'online': payload}).encode())
            return

        # Default behavior for other requests (file downloads)
        # Allow unauthenticated access to root path and index.html (contains login form)
        # but require authentication for everything else
        parsed_path = parsed.path.rstrip('/')
        is_index_page = parsed_path == '' or parsed_path == '/index.html'
        
        if not is_index_page and not self._is_authenticated():
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Unauthorized'}).encode())
            return
        
        try:
            super().do_GET()
        except (ConnectionResetError, BrokenPipeError):
            # Client closed connection
            pass
        except OSError as e:
            # khafe sho
            pass

    def do_POST(self):
        # endpoint: register/ping online user
        if self.path.startswith('/api/online_users'):
            # Require authentication to add new online user
            if not self._is_authenticated():
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Unauthorized'}).encode())
                return
            try:
                content_length = int(self.headers.get('Content-Length', 0))
            except ValueError:
                content_length = 0

            body = self.rfile.read(content_length) if content_length > 0 else b'{}'
            try:
                data = json.loads(body)
            except Exception:
                data = {}

            ua = data.get('userAgent') or self.headers.get('User-Agent', '')
            device = data.get('device') or device_from_ua(ua)
            client_ip = self._get_client_ip()
            now = time.time()
            with online_lock:
                online_users[client_ip] = {
                    'device': device,
                    'last_seen': now
                }

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'ok': True}).encode())
            return

        # logic for checking password
        if self.path == '/api/login':
            client_ip = self._get_client_ip()
            
            # Check if IP is locked out
            if self._is_ip_locked(client_ip):
                self.send_response(429)  # Too Many Requests
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Retry-After', str(LOCKOUT_DURATION))
                self.end_headers()
                remaining_time = int(LOCKOUT_DURATION - (time.time() - locked_ips.get(client_ip, 0)))
                self.wfile.write(json.dumps({
                    'success': False, 
                    'error': 'Too many failed attempts',
                    'retry_after': remaining_time
                }).encode())
                return
            
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)
            global SERVER_PASSWORD, SERVER_USERNAME
            
            username = data.get('username', '')
            password = data.get('password', '')
            
            # Check both username and password
            if username == SERVER_USERNAME and password == SERVER_PASSWORD:
                # Successful login - clear failed attempts
                self._clear_failed_logins(client_ip)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Credentials', 'true')
                self.send_header('Set-Cookie', 'session=valid; Path=/; SameSite=Lax')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode())
            else:
                # Failed login - record attempt
                self._record_failed_login(client_ip)
                
                # Add a small delay to slow down brute force attempts
                time.sleep(1)
                
                self.send_response(401)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False}).encode())
            return
        # logic for handling uploads
        if self.path.startswith('/api/upload'):
            # Check authentication for uploads
            if not self._is_authenticated():
                self.send_response(401)
                self._set_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Unauthorized'}).encode())
                return
            
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)
            rel_dir = query.get('path', [''])[0]

            content_type = self.headers.get('Content-Type', '')
            if not content_type.startswith('multipart/form-data'):
                self.send_response(400)
                self._set_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Invalid content type'}).encode())
                return

            try:
                filename, file_bytes = self._parse_multipart(content_type)
                if not filename or file_bytes is None:
                    raise ValueError('Invalid upload payload')

                save_path = self._save_path(rel_dir, filename)
                if save_path is None:
                    raise ValueError('Invalid target folder')

                with open(save_path, 'wb') as f:
                    f.write(file_bytes)

                self.send_response(201)
                self._set_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'message': 'Upload successful', 'filename': os.path.basename(save_path), 'path': rel_dir}).encode())
            except Exception as e:
                print(f"Upload error: {e}")
                self.send_response(500)
                self._set_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Upload failed'}).encode())
            return

        super().do_POST()

    def do_DELETE(self):
        """Handle file/folder deletion"""
        if self.path.startswith('/api/delete'):
            # Check authentication for deletion
            if not self._is_authenticated():
                self.send_response(401)
                self._set_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Unauthorized'}).encode())
                return
            
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)
            rel_path = query.get('path', [''])[0]
            item_name = query.get('name', [''])[0]

            if not item_name:
                self.send_response(400)
                self._set_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Missing name parameter'}).encode())
                return

            # Build safe path (empty rel_path means root directory)
            if rel_path:
                parent_dir = self._safe_path(rel_path)
                if parent_dir is None or not os.path.isdir(parent_dir):
                    self.send_response(400)
                    self._set_cors_headers()
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Invalid path'}).encode())
                    return
            else:
                parent_dir = self.root_dir

            # Only delete basenames to prevent path traversal
            safe_name = os.path.basename(item_name)
            target_path = os.path.join(parent_dir, safe_name)

            # Verify target is inside root_dir
            target_abs = os.path.normpath(os.path.abspath(target_path))
            root_abs = os.path.normpath(os.path.abspath(self.root_dir))
            if not target_abs.startswith(root_abs):
                self.send_response(403)
                self._set_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Access denied'}).encode())
                return

            # Check if target exists
            if not os.path.exists(target_path):
                self.send_response(404)
                self._set_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'File or folder not found'}).encode())
                return

            # Delete in background thread to avoid blocking
            def delete_async():
                try:
                    if os.path.isfile(target_path):
                        os.remove(target_path)
                        print(f"Deleted file: {target_path}")
                    elif os.path.isdir(target_path):
                        import shutil
                        shutil.rmtree(target_path)
                        print(f"Deleted folder: {target_path}")
                except Exception as e:
                    print(f"Delete error: {e}")

            # Submit deletion to background thread
            background_executor.submit(delete_async)

            # Return immediately with 202 Accepted
            self.send_response(202)
            self._set_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'message': 'Deletion started', 'name': safe_name}).encode())
            return

        super().do_DELETE() if hasattr(super(), 'do_DELETE') else None


def print_banner():
    """Print ASCII banner"""
    banner = r"""
██████╗  ██████╗ ██████╗ ████████╗    ██████╗  █████╗ ██╗     
██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝    ██╔══██╗██╔══██╗██║     
██████╔╝██║   ██║██████╔╝   ██║       ██████╔╝███████║██║     
██╔═══╝ ██║   ██║██╔══██╗   ██║       ██╔═══╝ ██╔══██║██║     
██║     ╚██████╔╝██║  ██║   ██║       ██║     ██║  ██║███████╗
╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝       ╚═╝     ╚═╝  ╚═╝╚══════╝
"""
    print(banner)
    print("PortPal - Simple Local File Hosting Server")
    print("=" * 60)


def get_ipv4():
    """Get device IPv4 address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def show_ipv4_menu():
    """Show device IPv4 address"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print_banner()
    print("\n Device IPv4 Address")
    print("-" * 60)
    ipv4 = get_ipv4()
    print(f"Your IPv4: {ipv4}")
    print("\nYou can access your files from other devices using:")
    print(f"http://{ipv4}:8000 (or the port you choose)")
    print("\n" + "=" * 60)
    input("Press Enter to return to menu...")


def show_help_menu():
    """Show help information"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print_banner()
    print("\n Help")
    print("-" * 60)
    print("PortPal allows you to easily host files on a local server.")
    print("\nHow to use:")
    print("1. Place files in the 'public' folder")
    print("2. Start the server from the menu")
    print("3. Access your files via http://localhost:PORT")
    print("4. Use 'Get Device IPv4' to access from other devices")
    print("\nSupported features:")
    print("- Automatic file listing")
    print("- Download files from browser")
    print("- Works on local network")
    print("=" * 60)
    input("Press Enter to return to menu...")


def start_server(port=None):
    """Start the HTTP server"""
    # Change to public directory if it exists
    public_dir = os.path.join(os.path.dirname(__file__), 'public')
    if os.path.exists(public_dir):
        os.chdir(public_dir)
        CustomHTTPHandler.root_dir = os.getcwd()
        print(f"Serving files from: {public_dir}")
    else:
        print("Warning: 'public' directory not found. Serving from current directory.")

    handler = CustomHTTPHandler

    # if the port is used ask for a different one
    while True:
        try:
            with socketserver.TCPServer(("0.0.0.0", port), handler) as httpd:
                ipv4 = get_ipv4()
                print(
                    f"Serving HTTP Server on {ipv4} port {port} (http://{ipv4}:{port}/) ..."
                )
                print("Press Ctrl+C to stop the server.")
                try:
                    httpd.serve_forever()
                except KeyboardInterrupt:
                    print("\nShutting down...")
                break
        except OSError as e:
            print(f"Cannot bind to port {port} — {e}")
            suggested = port + 1
            while True:
                try:
                    user_input = input(
                        f"Enter a different port to try [{suggested}]: "
                    ).strip()
                except EOFError:
                    user_input = ""

                if user_input == "":
                    port = suggested
                    break

                try:
                    p = int(user_input)
                except ValueError:
                    print("Please enter a valid port")
                    continue

                if 1 <= p <= 65535:
                    port = p
                    break
                else:
                    print("Port must be between 1 and 65535.")


def start_server_menu():
    """Show server startup options"""
    global SERVER_PASSWORD, SERVER_USERNAME
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_banner()
        print("\n Start Server")
        print("-" * 60)
        print("1. Start with default port (8000)")
        print("2. Set custom port")
        print("3. Go back")
        print("=" * 60)
        
        choice = input("Enter your choice (1-3): ").strip()
        
        if choice == "1":
            username = input("Enter username for server [optional]: ").strip()
            password = input("Enter password for server [optional]: ").strip()
            
            if username or password:
                SERVER_USERNAME = username if username else None
                SERVER_PASSWORD = password if password else None
            
            os.system('cls' if os.name == 'nt' else 'clear')
            print_banner()
            start_server(8000)
            break
        elif choice == "2":
            os.system('cls' if os.name == 'nt' else 'clear')
            print_banner()
            
            # Get credentials first
            username = input("Enter username for server [optional]: ").strip()
            password = input("Enter password for server [optional]: ").strip()
            
            if username or password:
                SERVER_USERNAME = username if username else None
                SERVER_PASSWORD = password if password else None
            
            while True:
                try:
                    port_input = input("Enter port number [8000] (or 'N' to return): ").strip().lower()
                    if port_input == "n":
                        break
                    if port_input == "":
                        port = 8000
                    else:
                        port = int(port_input)
                    
                    if 1 <= port <= 65535:
                        start_server(port)
                        break
                    else:
                        print("Port must be between 1 and 65535.")
                except ValueError:
                    print("Please enter a valid port number")
            break
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")
            input("Press Enter to continue...")


def main():
    """Main menu"""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_banner()
        print("\nMain Menu")
        print("-" * 60)
        print("1. Start Server")
        print("2. Get Device IPv4")
        print("3. Help")
        print("4. Exit")
        print("=" * 60)
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == "1":
            start_server_menu()
        elif choice == "2":
            show_ipv4_menu()
        elif choice == "3":
            show_help_menu()
        elif choice == "4":
            print("Thanks for using PortPal! Built by https://github.com/ThisIsDara")
            break
        else:
            print("Invalid choice. Please try again.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()
