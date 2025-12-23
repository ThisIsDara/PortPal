# PortPal GUI Server

**A beautiful, easy-to-use desktop application for sharing files on your local network.**

![GUI Preview](gui_preview.txt)

## 🎯 What is PortPal GUI?

PortPal GUI is a Windows desktop application that makes it simple to:
- Select any folder on your computer to share
- Start a local file server with one click
- Access files from any device on your network
- Remember your settings for next time

**No command-line needed. No technical knowledge required.**

## ⚡ Quick Start

### Option 1: Download Executable (Easiest)
1. Download `PortPal.exe` from Releases
2. Double-click to run
3. Select folder → Click "Start Server"
4. Share the URL with others

### Option 2: Build from Source
```bash
# Clone and navigate to project
cd PortPal

# Install dependencies
pip install -r requirements-gui.txt

# Run the GUI
python gui_server.py
```

### Option 3: Create Your Own Binary
```bash
# Install build tools
pip install -r requirements-gui.txt

# Run builder (Windows)
build_gui.bat

# Or use PyInstaller directly
pyinstaller --onefile --windowed --name "PortPal" gui_server.py

# Find executable at: dist/PortPal.exe
```

## ✨ Features

### Core Features
- ✅ **Modern GUI** - Dark theme, clean 480x360 interface
- ✅ **Folder Selection** - Browse and select any folder
- ✅ **Port Configuration** - Use port 8000 or any other
- ✅ **IPv4 Display** - Shows your network address
- ✅ **Persistent Settings** - Remembers last folder and port
- ✅ **One-Click Deploy** - Start/Stop with single click
- ✅ **Status Monitoring** - Real-time server status
- ✅ **Access URL** - Quick link display

### Server Features
- ✅ **File Hosting** - Share entire folder via HTTP
- ✅ **File Upload** - Upload files directly through browser
- ✅ **File Download** - Download files from web interface
- ✅ **Folder Navigation** - Browse subfolders
- ✅ **Authentication** - Optional username/password
- ✅ **Brute Force Protection** - IP lockout after failed logins
- ✅ **CORS Support** - API access from anywhere
- ✅ **JSON API** - Programmatic access to files

## 🎨 UI Overview

```
┌─────────────────────────────────────────┐
│  PortPal Server                         │
│  Desktop File Sharing                   │
├─────────────────────────────────────────┤
│                                         │
│  📁 Folder to Share:                    │
│  [/path/to/folder]          [Browse]    │
│                                         │
│  🔌 Port: [8000]                        │
│  Username (optional): [user]            │
│  Password (optional): [••••]            │
│                                         │
│  [▶ Start Server]  [⏹ Stop Server]     │
│                                         │
│  📍 IPv4: 192.168.1.100                │
│  Status: Running ✓                      │
│  Access: http://192.168.1.100:8000     │
│                                         │
└─────────────────────────────────────────┘
```

**Window Size:** 480x360 pixels  
**Theme:** Dark Blue (professional, easy on eyes)  
**Font:** Segoe UI (Windows system font)

## 🚀 Usage Guide

### Basic Setup

1. **Launch Application**
   - Double-click `PortPal.exe` (or run `python gui_server.py`)

2. **Select Folder**
   - Click "Browse" button
   - Choose folder to share
   - Folder path appears in text field

3. **Configure Server**
   - **Port:** Keep 8000 or enter custom port (1-65535)
   - **Username:** (Optional) Enter username for protection
   - **Password:** (Optional) Enter password for protection

4. **Start Server**
   - Click "▶ Start Server" button
   - Status changes to "Running ✓"
   - Access URL is displayed

5. **Access Files**
   - On **same computer:** Open browser → `http://localhost:8000`
   - On **other devices:** Open browser → `http://[IPv4 shown]:8000`
   - Use username/password if set

6. **Stop Server**
   - Click "⏹ Stop Server" when done
   - Status returns to "Idle"

### Advanced Features

**Remember Settings**
- Last folder automatically saved
- Last port automatically saved
- Last username automatically saved (password is NOT saved for security)
- Settings stored in: `~/.portpal_gui_config.json`

**Authentication (Optional)**
- Leave both username AND password blank = No authentication
- Fill in username and/or password = Authentication enabled
- Protects files with login screen

**Port Management**
- Valid range: 1 to 65535
- Common ports: 8000, 8080, 3000, 5000
- Avoid: 80, 443 (need admin), 22, 21 (system services)

## 🔐 Security

PortPal GUI includes built-in security features:

| Feature | Details |
|---------|---------|
| **Authentication** | Optional username/password protection |
| **Brute Force Protection** | 5 attempt limit, 15-minute IP lockout |
| **Session Management** | Secure cookie-based sessions |
| **Path Validation** | Prevents directory traversal attacks |
| **Local Network Only** | Designed for trusted networks |

**Security Best Practices:**
- Enable authentication for sensitive files
- Only use on trusted networks
- Don't expose to public internet
- Disable password when done sharing

## 📋 System Requirements

| Requirement | Details |
|-------------|---------|
| **OS** | Windows 10+ |
| **Python** | 3.8 or higher (if running from source) |
| **RAM** | 50 MB minimum |
| **Disk** | 10 MB for GUI application |
| **Network** | Local network connection required |

## 🛠️ Building the Binary

### Prerequisites
- Python 3.8+
- pip (comes with Python)

### Windows Batch Script (Easiest)
```bash
build_gui.bat
```
This will:
1. Install dependencies
2. Clean previous builds
3. Build new executable
4. Show location of finished binary

### Manual PyInstaller
```bash
# Install PyInstaller
pip install pyinstaller

# Build the executable
pyinstaller --onefile --windowed --name "PortPal" gui_server.py

# Find executable at: dist/PortPal.exe
```

### Advanced Build Options
```bash
# With custom icon
pyinstaller --onefile --windowed --icon icon.ico --name "PortPal" gui_server.py

# With splash screen
pyinstaller --onefile --windowed --splash splash.png --name "PortPal" gui_server.py

# Smaller file size
pyinstaller --onefile --windowed --noupx --name "PortPal" gui_server.py
```

## 📁 Project Structure

```
PortPal/
├── gui_server.py              # Main GUI application
├── server.py                  # Original CLI server
├── requirements-gui.txt       # GUI dependencies
├── build_gui.bat              # Windows builder script
├── check_gui_dependencies.py  # Dependency checker
├── GUI_FEATURES.md            # Feature documentation
├── BUILD_GUI_BINARY.md        # Binary build guide
├── README_GUI.md              # This file
└── public/                    # Files to serve
```

## 🧪 Testing

Before building a binary, test the GUI works:

```bash
# Check dependencies
python check_gui_dependencies.py

# Run the GUI
python gui_server.py
```

If all checks pass ✅, you're ready to build!

## 🐛 Troubleshooting

### GUI won't start
**Error:** "ModuleNotFoundError: No module named 'PySimpleGUI'"

**Solution:**
```bash
pip install PySimpleGUI
```

### Port already in use
**Error:** "Cannot bind to port 8000"

**Solution:**
- Try a different port (8001, 8080, etc.)
- Or close other applications using that port
- Use `netstat -ano` to find what's using the port

### Can't access from other devices
**Problem:** Browser shows "connection refused" on other computers

**Solutions:**
1. Check IPv4 address shown in GUI
2. Use that IP instead of localhost
3. Make sure both devices are on same Wi-Fi network
4. Check Windows Firewall isn't blocking port

### Files not showing in browser
**Problem:** Folder is empty or files don't appear

**Solutions:**
1. Check correct folder was selected
2. Refresh browser (Ctrl+F5)
3. Check files have correct permissions
4. Verify files aren't in subfolders

### Authentication issues
**Problem:** Login not working

**Solutions:**
- Leave BOTH username AND password blank for no auth
- Both must have values for auth to activate
- Password IS case-sensitive
- Clear browser cookies and try again

## 📊 Performance

PortPal GUI is lightweight:
- **Memory:** ~20-50 MB when idle
- **Network:** Handles multiple concurrent connections
- **File Size:** Executable ~40-50 MB (includes Python runtime)
- **Startup:** < 2 seconds

## 🔗 Integration

### Use as a Service
Create Windows shortcut with startup folder for auto-run.

### Share Folder Quickly
1. Right-click folder → Properties
2. Note the path
3. Open PortPal GUI
4. Select that folder
5. Click Start

### API Access
Once server is running, access via JSON API:

```
GET /api/files?path=          # List files
GET /api/storage              # Get disk usage
GET /api/has_password         # Check auth
POST /api/login               # Login
POST /api/upload?path=        # Upload file
DELETE /api/delete?path=&name= # Delete file
```

## 📝 Configuration File

Settings are saved to: `~/.portpal_gui_config.json`

Example:
```json
{
  "last_folder": "C:\\Users\\John\\Documents",
  "last_port": 8000,
  "last_username": "admin"
}
```

To reset to defaults, delete this file.

## 🎯 Use Cases

### 📤 Quick File Sharing
Share documents, photos, or videos with friends/family on your home network.

### 💼 Team File Distribution
Share project files, presentations, or documents with colleagues.

### 🎮 Media Server
Stream videos, music, or photos to devices on your network.

### 📱 Device Integration
Access files from phones, tablets, and computers on same network.

### 🔄 Backup Sharing
Quickly share backup files for distribution or verification.

## 📞 Support

### Common Questions

**Q: Is PortPal safe?**  
A: Yes! It's designed for local networks only. Enable authentication for added security.

**Q: Can I access from the internet?**  
A: Not recommended. PortPal is for local network use. For internet access, use proper web hosting.

**Q: Do I need Python installed?**  
A: Only if running from source. The `.exe` binary includes everything needed.

**Q: Can I use it on Mac/Linux?**  
A: Run `python gui_server.py` with the same requirements installed.

**Q: What's the file size limit?**  
A: Limited by your disk space. PortPal handles large files efficiently.

**Q: Can multiple people access at once?**  
A: Yes! The server supports concurrent connections.

## 🤝 Contributing

Found a bug? Have a feature request?
- Report issues on GitHub
- Suggest improvements
- Share feedback

## 📄 License

PortPal is open source and free to use.

## 🎉 Credits

Built with:
- **PySimpleGUI** - Modern Python GUI
- **Python stdlib** - Core server functionality
- **PyInstaller** - Binary packaging

---

**PortPal GUI Server** - Making file sharing simple, fast, and beautiful.

**Ready to get started?** Download the executable or run `python gui_server.py` now!
