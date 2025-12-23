"""
PortPal GUI Server - Desktop application for easy file sharing
Features: Folder selection, IPv4 display, port configuration, persistent settings
"""

import PySimpleGUI as sg
# Fallback UI
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
except Exception:
    tk = None
    filedialog = None
    messagebox = None
import os
import json
import socket
import threading
import time
from pathlib import Path
import functools
import sys
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import shutil

# Configuration file
CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".portpal_gui_config.json")

# Resolve fallback landing page (works in frozen exe via _MEIPASS)
def fallback_index_path() -> Path:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base / "public" / "index.html"

# Thread pool for background operations
background_executor = ThreadPoolExecutor(max_workers=2)

# Global password variables
SERVER_PASSWORD = None
SERVER_USERNAME = None
CURRENT_SERVER = None

# Brute force protection
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 900
login_attempts = defaultdict(list)
locked_ips = {}


class CustomHTTPHandler(http.server.SimpleHTTPRequestHandler):
    root_dir = os.getcwd()

    def _get_client_ip(self) -> str:
        forwarded = self.headers.get('X-Forwarded-For')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return self.client_address[0]

    def _is_ip_locked(self, ip: str) -> bool:
        global locked_ips
        if ip in locked_ips:
            lock_time = locked_ips[ip]
            if time.time() - lock_time < LOCKOUT_DURATION:
                return True
            else:
                del locked_ips[ip]
                if ip in login_attempts:
                    login_attempts[ip].clear()
        return False

    def _record_failed_login(self, ip: str):
        global login_attempts, locked_ips
        current_time = time.time()
        login_attempts[ip] = [t for t in login_attempts[ip] if current_time - t < LOCKOUT_DURATION]
        login_attempts[ip].append(current_time)
        if len(login_attempts[ip]) >= MAX_LOGIN_ATTEMPTS:
            locked_ips[ip] = current_time

    def _clear_failed_logins(self, ip: str):
        global login_attempts, locked_ips
        if ip in login_attempts:
            login_attempts[ip].clear()
        if ip in locked_ips:
            del locked_ips[ip]

    def _is_authenticated(self) -> bool:
        global SERVER_PASSWORD, SERVER_USERNAME
        if (SERVER_USERNAME is None or SERVER_USERNAME == "") and (SERVER_PASSWORD is None or SERVER_PASSWORD == ""):
            return True
        cookies = self.headers.get('Cookie', '')
        return 'session=valid' in cookies

    def _set_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Requested-With')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')

    def _safe_path(self, rel_path: str):
        rel_path = rel_path.strip() if rel_path else ''
        rel_path = rel_path.lstrip('/\\')
        norm_rel = os.path.normpath(rel_path)
        abs_path = os.path.normpath(os.path.join(self.root_dir, norm_rel))
        if not abs_path.startswith(self.root_dir):
            return None
        return abs_path

    def _save_path(self, rel_dir: str, filename: str):
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
            return None

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

    def _parse_multipart(self, content_type: str):
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
        segments = raw_data.split(boundary_bytes)
        for segment in segments:
            if not segment or segment in (b'--', b'--\r\n'):
                continue
            if segment.startswith(b'\r\n'):
                segment = segment[2:]
            try:
                header_bytes, body = segment.split(b'\r\n\r\n', 1)
            except ValueError:
                continue
            headers_text = header_bytes.decode(errors='ignore')
            body = body.rstrip(b'\r\n')

            disposition = None
            for line in headers_text.split('\r\n'):
                if line.lower().startswith('content-disposition:'):
                    disposition = line
                    break
            if not disposition:
                continue

            filename = None
            field_name = None
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
        if parsed.path == '/api/has_password':
            global SERVER_PASSWORD, SERVER_USERNAME
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self._set_cors_headers()
            self.end_headers()
            has_auth = not ((SERVER_USERNAME is None or SERVER_USERNAME == "") and (SERVER_PASSWORD is None or SERVER_PASSWORD == ""))
            self.wfile.write(json.dumps({'has_password': has_auth}).encode())
            return
        if parsed.path == '/api/files':
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

        if parsed.path == '/api/storage':
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
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Unable to read storage info'}).encode())
            return

        parsed_path = parsed.path.rstrip('/')
        is_index_page = parsed_path == '' or parsed_path == '/index.html'

        if not is_index_page and not self._is_authenticated():
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Unauthorized'}).encode())
            return

        # Always serve bundled landing page for root/index requests
        if parsed.path in ('', '/', '/index', '/index.html'):
            fallback_index = fallback_index_path()
            if fallback_index.exists():
                try:
                    with open(fallback_index, 'rb') as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self._set_cors_headers()
                    self.end_headers()
                    self.wfile.write(content)
                    return
                except Exception:
                    self.send_error(404, "File not found")
                    return
            else:
                self.send_error(404, "File not found")
                return
        
        try:
            super().do_GET()
        except (ConnectionResetError, BrokenPipeError):
            pass
        except OSError:
            pass

    def do_POST(self):
        if self.path == '/api/login':
            client_ip = self._get_client_ip()
            
            if self._is_ip_locked(client_ip):
                self.send_response(429)
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
            
            if username == SERVER_USERNAME and password == SERVER_PASSWORD:
                self._clear_failed_logins(client_ip)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Credentials', 'true')
                self.send_header('Set-Cookie', 'session=valid; Path=/; SameSite=Lax')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True}).encode())
            else:
                self._record_failed_login(client_ip)
                time.sleep(1)
                self.send_response(401)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False}).encode())
            return

        if self.path.startswith('/api/upload'):
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
                self.send_response(500)
                self._set_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Upload failed'}).encode())
            return

        super().do_POST()

    def do_DELETE(self):
        if self.path.startswith('/api/delete'):
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

            safe_name = os.path.basename(item_name)
            target_path = os.path.join(parent_dir, safe_name)

            target_abs = os.path.normpath(os.path.abspath(target_path))
            root_abs = os.path.normpath(os.path.abspath(self.root_dir))
            if not target_abs.startswith(root_abs):
                self.send_response(403)
                self._set_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Access denied'}).encode())
                return

            if not os.path.exists(target_path):
                self.send_response(404)
                self._set_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'File or folder not found'}).encode())
                return

            def delete_async():
                try:
                    if os.path.isfile(target_path):
                        os.remove(target_path)
                    elif os.path.isdir(target_path):
                        shutil.rmtree(target_path)
                except Exception as e:
                    pass

            background_executor.submit(delete_async)

            self.send_response(202)
            self._set_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'message': 'Deletion started', 'name': safe_name}).encode())
            return

        super().do_DELETE() if hasattr(super(), 'do_DELETE') else None

    def log_message(self, format, *args):
        pass  # Suppress logs


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


def load_config():
    """Load configuration from file"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_config(config):
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except:
        pass


def start_server_thread(folder, port, username, password):
    """Start server in background thread"""
    global SERVER_PASSWORD, SERVER_USERNAME, CURRENT_SERVER
    
    # Normalize folder to an absolute path for consistent serving
    canonical_folder = os.path.abspath(folder)

    SERVER_USERNAME = username if username else None
    SERVER_PASSWORD = password if password else None
    CustomHTTPHandler.root_dir = canonical_folder
    CustomHTTPHandler.directory = canonical_folder
    handler_cls = functools.partial(CustomHTTPHandler, directory=canonical_folder)
    
    try:
        with socketserver.TCPServer(("0.0.0.0", port), handler_cls) as httpd:
            CURRENT_SERVER = httpd
            httpd.serve_forever()
    except Exception as e:
        CURRENT_SERVER = None


def _set_theme_safe(name: str = 'DarkBlue3'):
    """Set theme in a version-safe way across PySimpleGUI variants."""
    for meth in ("theme", "set_theme", "theme_global", "set_global_theme"):
        fn = getattr(sg, meth, None)
        if callable(fn):
            try:
                fn(name)
                return
            except Exception:
                pass

def _set_options_safe(**kwargs):
    """Set global options using whichever API is available (v4/v5)."""
    for meth in ("set_options", "SetOptions"):
        fn = getattr(sg, meth, None)
        if callable(fn):
            try:
                fn(**kwargs)
                return True
            except Exception:
                pass
    return False


def _pysimplegui_available() -> bool:
    """Check if core PySimpleGUI APIs used by this app exist."""
    required = ("Text", "Window", "Button", "Input", "FolderBrowse")
    return all(hasattr(sg, name) for name in required)


def create_gui_tk():
    """Tkinter fallback GUI for environments where PySimpleGUI v5 API differs."""
    if tk is None:
        print("Tkinter is unavailable; cannot launch fallback GUI.")
        return

    # Load config
    config = load_config()
    last_folder = config.get('last_folder', str(Path.home()))
    last_port = int(config.get('last_port', 8000))
    last_username = config.get('last_username', '')

    root = tk.Tk()
    root.title('PortPal GUI Server')
    root.geometry('480x420')
    root.resizable(False, False)

    # Set window icon
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    icon_path = base_path / "server.ico"
    if icon_path.exists():
        try:
            root.iconbitmap(str(icon_path))
        except Exception:
            pass

    bg = '#1A202C'
    fg = '#E2E8F0'
    accent = '#667eea'
    success = '#48BB78'
    warn = '#FFD700'
    danger = '#F56565'

    root.configure(bg=bg)

    # Variables
    folder_var = tk.StringVar(value=last_folder)
    port_var = tk.StringVar(value=str(last_port))
    user_var = tk.StringVar(value=last_username)
    pass_var = tk.StringVar(value='')
    ipv4_var = tk.StringVar(value=get_ipv4())
    status_var = tk.StringVar(value='Idle')
    url_var = tk.StringVar(value='N/A')

    # Helpers
    def pick_folder():
        sel = filedialog.askdirectory(initialdir=folder_var.get() or str(Path.home()))
        if sel:
            folder_var.set(sel)

    server_running = {"value": False}

    def start_server_gui():
        folder = folder_var.get()
        try:
            port = int(port_var.get())
        except ValueError:
            messagebox.showerror('Error', 'Please enter a valid port (1-65535)')
            return
        if not folder or not os.path.isdir(folder):
            messagebox.showerror('Error', 'Please select a valid folder')
            return
        if not (1 <= port <= 65535):
            messagebox.showerror('Error', 'Port must be between 1 and 65535')
            return

        # Save config
        config['last_folder'] = folder
        config['last_port'] = port
        config['last_username'] = user_var.get()
        save_config(config)

        # Start server thread
        th = threading.Thread(
            target=start_server_thread,
            args=(folder, port, user_var.get(), pass_var.get()),
            daemon=True
        )
        th.start()
        server_running["value"] = True
        status_var.set('Running ✓')
        ipv4_var.set(get_ipv4())
        url_var.set(f'http://{ipv4_var.get()}:{port}')
        start_btn.configure(state=tk.DISABLED, bg=success)
        stop_btn.configure(state=tk.NORMAL, bg=danger)
        open_btn.configure(state=tk.NORMAL, bg='#667eea')

    def stop_server_gui():
        if CURRENT_SERVER:
            try:
                CURRENT_SERVER.shutdown()
            except Exception:
                pass
        server_running["value"] = False
        status_var.set('Idle')
        url_var.set('N/A')
        start_btn.configure(state=tk.NORMAL, bg=success)
        stop_btn.configure(state=tk.DISABLED, bg=danger)
        open_btn.configure(state=tk.DISABLED, bg='#667eea')

    def open_server():
        """Open server URL in default browser"""
        url = url_var.get()
        if url and url != 'N/A':
            import webbrowser
            webbrowser.open(url)

    def on_close():
        if server_running["value"] and CURRENT_SERVER:
            try:
                CURRENT_SERVER.shutdown()
            except Exception:
                pass
        root.destroy()

    # Layout
    def mk_label(text, size=10, color=fg):
        return tk.Label(root, text=text, fg=color, bg=bg, font=('Segoe UI', size))

    title = tk.Label(root, text='PortPal Server', fg=accent, bg=bg, font=('Segoe UI', 18, 'bold'))
    subtitle = mk_label('Desktop File Sharing', 10, '#A0AEC0')
    title.place(x=20, y=14)
    subtitle.place(x=20, y=42)

    mk_label('📁 Folder to Share:', 10).place(x=20, y=76)
    folder_entry = tk.Entry(root, textvariable=folder_var, width=42, fg=fg, bg='#2D3748', insertbackground=fg)
    folder_entry.place(x=20, y=98)
    browse_btn = tk.Button(root, text='Browse', command=pick_folder, width=8, bg=accent, fg='white', relief=tk.FLAT)
    browse_btn.place(x=376, y=96)

    mk_label('🔌 Port:', 10).place(x=20, y=132)
    port_entry = tk.Entry(root, textvariable=port_var, width=10, fg=fg, bg='#2D3748', insertbackground=fg)
    port_entry.place(x=78, y=132)

    mk_label('Username (optional):', 10).place(x=170, y=132)
    user_entry = tk.Entry(root, textvariable=user_var, width=14, fg=fg, bg='#2D3748', insertbackground=fg)
    user_entry.place(x=318, y=132)

    mk_label('Password (optional):', 10).place(x=20, y=164)
    pass_entry = tk.Entry(root, textvariable=pass_var, width=20, show='*', fg=fg, bg='#2D3748', insertbackground=fg)
    pass_entry.place(x=176, y=164)

    # Buttons
    start_btn = tk.Button(root, text='▶ Start Server', command=start_server_gui, bg=success, fg='black', font=('Segoe UI', 10, 'bold'), relief=tk.RAISED, bd=2, padx=10, pady=8)
    stop_btn = tk.Button(root, text='⏹ Stop Server', command=stop_server_gui, bg=danger, fg='black', font=('Segoe UI', 10, 'bold'), relief=tk.RAISED, bd=2, padx=10, pady=8, state=tk.DISABLED)
    open_btn = tk.Button(root, text='🌐 Open Server', command=open_server, bg='#667eea', fg='black', font=('Segoe UI', 10, 'bold'), relief=tk.RAISED, bd=2, padx=10, pady=8, state=tk.DISABLED)
    start_btn.place(x=20, y=200, width=440, height=38)
    stop_btn.place(x=20, y=244, width=440, height=38)
    open_btn.place(x=20, y=288, width=440, height=38)

    # Status
    mk_label('📍 IPv4 Address:', 10).place(x=20, y=336)
    ipv4_lbl = mk_label('', 10, '#90EE90')
    ipv4_lbl.configure(textvariable=ipv4_var)
    ipv4_lbl.place(x=150, y=336)

    mk_label('Status:', 10).place(x=20, y=360)
    status_lbl = mk_label('', 10, warn)
    status_lbl.configure(textvariable=status_var)
    status_lbl.place(x=78, y=360)

    # Footer with credit
    def open_github(event=None):
        import webbrowser
        webbrowser.open('https://github.com/thisisdara')

    footer = tk.Label(root, text='Made by ThisIsDara', fg='#A0AEC0', bg=bg, font=('Segoe UI', 8), cursor='hand2')
    footer.place(x=360, y=398)
    footer.bind('<Button-1>', open_github)

    root.protocol('WM_DELETE_WINDOW', on_close)
    root.mainloop()


def create_gui():
    """Create and run the GUI"""
    # If PySimpleGUI essential APIs are missing, use Tkinter fallback
    if not _pysimplegui_available():
        return create_gui_tk()

    # Set theme (handles PySimpleGUI v4/v5 API differences)
    _set_theme_safe('DarkBlue3')
    _set_options_safe(
        font=('Segoe UI', 10),
        margins=(20, 20),
        border_width=0
    )
    
    # Load config
    config = load_config()
    last_folder = config.get('last_folder', str(Path.home()))
    last_port = config.get('last_port', 8000)
    last_username = config.get('last_username', '')
    
    # Layout
    layout = [
        [sg.Text('PortPal Server', font=('Segoe UI', 18, 'bold'), text_color='#667eea')],
        [sg.Text('Desktop File Sharing', text_color='#A0AEC0', font=('Segoe UI', 10))],
        [sg.Text('_' * 50)],
        
        [sg.Text('📁 Folder to Share:', font=('Segoe UI', 10, 'bold'))],
        [sg.Input(last_folder, key='-FOLDER-', size=(35, 1), disabled=True, background_color='#2D3748'),
         sg.FolderBrowse(button_color=('#FFFFFF', '#667eea'), size=(8, 1))],
        
        [sg.Text('🔌 Port:', font=('Segoe UI', 10, 'bold')), 
         sg.Input(last_port, key='-PORT-', size=(15, 1), background_color='#2D3748', text_color='#FFFFFF'),
         sg.Text('Username (optional):'),
         sg.Input(last_username, key='-USERNAME-', size=(12, 1), background_color='#2D3748', text_color='#FFFFFF')],
        
        [sg.Text('Password (optional):', font=('Segoe UI', 10, 'bold')), 
         sg.Input('', key='-PASSWORD-', size=(20, 1), password_char='*', background_color='#2D3748', text_color='#FFFFFF')],
        
        [sg.Text('_' * 50)],
        
        [sg.Button('▶ Start Server', button_color=('#000000', '#48BB78'), size=(14, 1), key='-START-'),
         sg.Button('⏹ Stop Server', button_color=('#000000', '#F56565'), size=(14, 1), key='-STOP-', disabled=True),
         sg.Button('🌐 Open', button_color=('#000000', '#667eea'), size=(8, 1), key='-OPEN-', disabled=True)],
        
        [sg.Text('_' * 50)],
        
        [sg.Text('📍 IPv4 Address:', font=('Segoe UI', 10, 'bold')),
         sg.Text(get_ipv4(), text_color='#90EE90', font=('Segoe UI', 10, 'bold'), key='-IPV4-')],
        
        [sg.Text('Status:', font=('Segoe UI', 10, 'bold')),
         sg.Text('Idle', text_color='#FFD700', font=('Segoe UI', 10, 'bold'), key='-STATUS-')],
        
        [sg.Text('Access URL:', font=('Segoe UI', 10, 'bold')),
         sg.Text('N/A', text_color='#87CEEB', font=('Segoe UI', 9), key='-URL-')],

        [sg.Text('Made by ', text_color='#A0AEC0', font=('Segoe UI', 8)),
         sg.Text('ThisIsDara', text_color='#87CEEB', font=('Segoe UI', 8, 'underline'), key='-CREDIT-', enable_events=True)],
    ]
    
    window = sg.Window(
        'PortPal GUI Server',
        layout,
        size=(480, 360),
        finalize=True,
        keep_on_top=False,
        background_color='#1A202C',
        text_color='#E2E8F0'
    )
    
    server_thread = None
    server_running = False
    
    while True:
        event, values = window.read(timeout=100)
        
        if event == sg.WIN_CLOSED:
            if server_running:
                CURRENT_SERVER.shutdown()
            break
        
        if event == '-START-':
            folder = values['-FOLDER-']
            port_str = values['-PORT-']
            username = values['-USERNAME-']
            password = values['-PASSWORD-']
            
            if not folder or not os.path.isdir(folder):
                sg.popup_error('Please select a valid folder', title='Error')
                continue
            
            try:
                port = int(port_str)
                if not (1 <= port <= 65535):
                    raise ValueError()
            except:
                sg.popup_error('Please enter a valid port (1-65535)', title='Error')
                continue
            
            # Save config
            config['last_folder'] = folder
            config['last_port'] = port
            config['last_username'] = username
            save_config(config)
            
            # Start server
            server_thread = threading.Thread(
                target=start_server_thread,
                args=(folder, port, username, password),
                daemon=True
            )
            server_thread.start()
            server_running = True
            
            window['-START-'].update(disabled=True)
            window['-STOP-'].update(disabled=False)
            window['-OPEN-'].update(disabled=False)
            window['-STATUS-'].update('Running ✓', text_color='#48BB78')
            
            ipv4 = get_ipv4()
            window['-IPV4-'].update(ipv4)
            window['-URL-'].update(f'http://{ipv4}:{port}')
        
        if event == '-STOP-':
            if CURRENT_SERVER:
                CURRENT_SERVER.shutdown()
            server_running = False
            
            window['-START-'].update(disabled=False)
            window['-STOP-'].update(disabled=True)
            window['-OPEN-'].update(disabled=True)
            window['-STATUS-'].update('Idle', text_color='#FFD700')
            window['-URL-'].update('N/A')
        
        if event == '-OPEN-':
            url = values['-URL-']
            if url and url != 'N/A':
                import webbrowser
                webbrowser.open(url)
        
        if event == '-CREDIT-':
            import webbrowser
            webbrowser.open('https://github.com/thisisdara')
    
    window.close()


if __name__ == '__main__':
    create_gui()
