# PortPal GUI Server - Features & Usage Guide

## 🎨 GUI Layout (480x360 window)

```
┌─────────────────────────────────────────┐
│  PortPal Server                         │  
│  Desktop File Sharing                   │
├─────────────────────────────────────────┤
│                                         │
│  📁 Folder to Share:                   │
│  [/path/to/folder]          [Browse]   │
│                                         │
│  🔌 Port: [8000]  Username: [user    ]│
│  Password (optional): [••••••]          │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  [▶ Start Server]  [⏹ Stop Server]     │
│                                         │
├─────────────────────────────────────────┤
│  📍 IPv4: 192.168.1.100                │
│  Status: Running ✓                      │
│  Access: http://192.168.1.100:8000     │
│                                         │
└─────────────────────────────────────────┘
```

## ✨ Features

### 1. **📁 Folder Selection**
- Click "Browse" button to select folder
- Last selected folder is automatically remembered
- No need to navigate every time you restart

### 2. **🔌 Port Configuration**
- Default: 8000
- Change to any valid port (1-65535)
- Last used port is remembered
- Auto-increments if port is in use

### 3. **📍 IPv4 Address Display**
- Automatically detects your device's network IP
- Shows in the GUI for easy reference
- Click "Refresh IPv4" to update (if needed)

### 4. **💾 Remember Last Settings**
Configuration stored in: `~/.portpal_gui_config.json`

Saved settings:
- Last folder path
- Last port number
- Last username (optional)

### 5. **🔐 Optional Authentication**
- Add username for basic security
- Add password for access protection
- Both optional - leave blank for public access
- Last username is remembered (password is NOT saved)

### 6. **Real-time Status**
- Shows "Running ✓" when server is active
- Shows "Idle" when server is stopped
- Live access URL for quick copying

### 7. **Easy Start/Stop**
- Click "▶ Start Server" to begin
- Click "⏹ Stop Server" to halt
- Buttons enable/disable automatically

## 🚀 Quick Start

### Windows Executable (No Python Needed)

1. **Download or Build:**
   - Get `PortPal.exe` from releases or
   - Run `build_gui.bat` to build from source

2. **Launch:**
   - Double-click `PortPal.exe`

3. **Configure:**
   - Click Browse to select folder
   - Set port (or keep default 8000)
   - (Optional) Add username/password

4. **Start:**
   - Click "▶ Start Server"

5. **Access:**
   - Copy the URL shown
   - Open in browser on any device on your network

### Python Users

```bash
# Install dependencies
pip install -r requirements-gui.txt

# Run directly
python gui_server.py
```

## 🎯 Use Cases

### Share Files with Friends on LAN
- No internet needed
- No cloud uploads
- Fast local network speed
- Full control of files

### Portable Web Server
- Easy setup via GUI
- No command-line needed
- Settings persist between sessions
- Works on any Windows PC

### Home Media Server
- Stream files to smart TV
- Access from multiple devices
- Password protect if needed
- Monitor status in real-time

### Backup Server
- Quick file sharing for backups
- Direct folder serving
- One-click deployment
- No installation required

## 🔧 Configuration File

Settings are automatically saved to:
```
Windows: C:\Users\YourName\.portpal_gui_config.json
```

Example content:
```json
{
  "last_folder": "C:\\Users\\John\\Documents\\Shared",
  "last_port": 8080,
  "last_username": "admin"
}
```

To reset settings, delete this file (it will be recreated with defaults).

## 📋 Keyboard Shortcuts

- **Tab** - Navigate between fields
- **Enter** - Activate focused button
- **Alt+F4** - Close application

## 🌐 Web Interface Access

Once server is running, access via:

**Local machine:**
- `http://localhost:8000`

**From other devices on network:**
- `http://192.168.1.100:8000` (your actual IPv4)
- Replace IP with value shown in GUI

**With authentication:**
- Login screen appears automatically
- Use username/password set in GUI

## 📊 Server Capabilities

| Feature | Supported |
|---------|-----------|
| File Download | ✅ Yes |
| File Upload | ✅ Yes |
| Folder Browsing | ✅ Yes |
| Authentication | ✅ Yes |
| Brute Force Protection | ✅ Yes |
| Disk Usage Info | ✅ Yes |
| JSON API | ✅ Yes |
| CORS Support | ✅ Yes |
| Dark Mode | ✅ Yes |
| Mobile Responsive | ✅ Yes |

## ⚙️ Building Your Own Binary

```bash
# Install build tools
pip install -r requirements-gui.txt

# Build the executable
pyinstaller --onefile --windowed --name "PortPal" gui_server.py

# Find your binary at:
# dist/PortPal.exe
```

## 🐛 Troubleshooting

**GUI doesn't start**
- Ensure PySimpleGUI is installed: `pip install PySimpleGUI`
- Check Python version: `python --version` (need 3.8+)

**Port is already in use**
- Select a different port number
- Close other applications using that port
- Common conflict: ports 80, 443, 8080, 8000

**Can't access from other devices**
- Verify correct IPv4 shown in GUI
- Check firewall isn't blocking the port
- Ensure devices are on same network

**Files not appearing**
- Refresh browser (F5)
- Check folder path is correct
- Verify files are not in subfolders

**Password protection not working**
- Leave BOTH username AND password blank for no auth
- Both fields must have values for auth to activate

## 📝 Notes

- Server runs until you click "Stop" or close the window
- Closing window automatically shuts down server
- No background service - only runs when GUI is open
- All files must be in selected folder (no parent directory access)
- Max file upload size depends on available disk space

## 🔒 Security

- **For LAN use only** - don't expose to internet
- **Optional password** - recommended for sensitive files
- **Brute force protection** - 5 attempt lockout
- **Path validation** - prevents directory traversal
- **Session cookies** - secure after login

---

**PortPal GUI Server** - Simple, fast, secure local file sharing.
