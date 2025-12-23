# PortPal GUI - Visual Guides

## GUI Layout Diagram

```
╔════════════════════════════════════════════╗
║         PortPal Server                     ║
║       Desktop File Sharing                 ║
╠════════════════════════════════════════════╣
║                                            ║
║  📁 Folder to Share:                       ║
║  ┌──────────────────────────────────────┐  ║
║  │ C:\Users\John\Documents\Files      │  ║
║  └──────────────────────────────────────┘  ║
║                            [Browse]        ║
║                                            ║
║  🔌 Port: ┌─────────┐  Username: ┌─────┐  ║
║           │  8000   │             │admin│  ║
║           └─────────┘             └─────┘  ║
║                                            ║
║  Password (optional): ┌─────────────────┐  ║
║                       │ • • • • •        │  ║
║                       └─────────────────┘  ║
║                                            ║
╠════════════════════════════════════════════╣
║                                            ║
║    [▶ Start Server]   [⏹ Stop Server]     ║
║                                            ║
╠════════════════════════════════════════════╣
║                                            ║
║  📍 IPv4: 192.168.1.100                   ║
║  Status: Running ✓                         ║
║  Access: http://192.168.1.100:8000        ║
║                                            ║
╚════════════════════════════════════════════╝
        480 × 360 pixels, Dark Theme
```

---

## How It Works - Flow Diagram

```
User Launches App
        ↓
GUI Appears (480x360)
        ↓
User Clicks Browse Button
        ↓
Folder Dialog Opens
        ↓
User Selects Folder
        ↓
Path Stored in Text Field
        ↓
User Enters Port & Auth
        ↓
User Clicks "▶ Start Server"
        ↓
Server Thread Starts
        ↓
Configuration Saved to ~/.portpal_gui_config.json
        ↓
Status Changes to "Running ✓"
        ↓
IPv4 Auto-Detected
        ↓
Access URL Displayed
        ↓
User Opens URL in Browser
        ↓
Browser Connects to HTTP Server
        ↓
Server Authenticates (if password set)
        ↓
Web Interface Loads
        ↓
User Uploads/Downloads/Browses Files
        ↓
User Clicks "⏹ Stop Server"
        ↓
Server Shuts Down
        ↓
Status Returns to "Idle"
```

---

## Network Architecture

```
┌─────────────────────────────────────┐
│  PortPal GUI Application            │
│  (GUI Thread)                       │
│                                     │
│  • Folder selection                 │
│  • Port configuration               │
│  • Status display                   │
│  • Settings management              │
└──────────────┬──────────────────────┘
               │
               │ Starts
               ↓
┌─────────────────────────────────────┐
│  HTTP Server Thread                 │
│  (Background)                       │
│                                     │
│  Listening on 0.0.0.0:PORT          │
│  • Handles GET/POST/DELETE          │
│  • Manages authentication           │
│  • Validates paths                  │
│  • Serves files                     │
│  • Returns JSON API responses       │
└──────────────┬──────────────────────┘
               │
        ┌──────┴──────┬──────────┐
        ↓             ↓          ↓
   Web Browser   Other Device  Mobile Device
   localhost:    192.168.1.x:   192.168.1.y:
   8000          8000           8000
```

---

## Authentication Flow

```
User Visits Server (No Auth Set)
        ↓
Allowed ✓
Access Granted


User Visits Server (Auth Set)
        ↓
Authentication Required
        ↓
Display Login Screen
        ↓
User Enters Username & Password
        ↓
Server Validates Credentials
        ├─ Correct: Set Session Cookie, Redirect to Files
        └─ Wrong: Record Failed Attempt
              ├─ 1-4 attempts: Deny + Show Error
              └─ 5th attempt: Lock IP for 15 minutes
                     ↓
                 User Locked Out (429 Response)
                 Show "Too Many Attempts" Message
                 Wait 15 minutes
                     ↓
                 Can Try Again
```

---

## File Server Architecture

```
┌────────────────────────────────────────┐
│  HTTP Request Comes In                 │
└─────────────┬──────────────────────────┘
              │
              ↓
┌────────────────────────────────────────┐
│  Get Client IP Address                 │
│  Check if IP is Locked                 │
└─────────────┬──────────────────────────┘
              │
     ┌────────┴────────┐
     ↓                 ↓
  Locked           Not Locked
     │                 │
     ↓                 ↓
429 Response    Check Authentication
Too Many        ├─ No Auth Set → Allowed
Attempts        └─ Auth Set → Check Cookie/Login
                        │
                   ┌────┴────┐
                   ↓         ↓
              Valid      Invalid
              Session    Session
                │           │
                ↓           ↓
             Allowed      Deny 401
             Process      Return Error
             Request
                │
     ┌──────────┼──────────┐
     ↓          ↓          ↓
  GET        POST       DELETE
  Files      Upload     Delete
     │          │          │
     ↓          ↓          ↓
  List      Multipart   Path
  Files     Parser      Validate
     │          │          │
     ↓          ↓          ↓
  Return    Save to    Background
  JSON      Disk       Thread
     │          │          │
     ↓          ↓          ↓
Response    201      202
JSON       Created   Accepted
```

---

## Configuration Persistence

```
First Launch:
    ↓
No Config File
    ↓
Use Defaults:
  • Folder: Home directory
  • Port: 8000
  • Username: (empty)
    ↓
User Sets Values
    ↓
Clicks "Start Server"
    ↓
Save to ~/.portpal_gui_config.json:
{
  "last_folder": "...",
  "last_port": 8000,
  "last_username": "..."
}
    ↓
Next Launch:
    ↓
Load from Config File
    ↓
Pre-fill GUI Fields
    ↓
User Ready to Use Same Settings
```

---

## Security Layers

```
┌──────────────────────────────────────┐
│     Incoming Request                 │
└──────────────┬───────────────────────┘
               │
               ↓
    ┌──────────────────────────────┐
    │  Layer 1: IP Lockout         │
    │  - Track failed attempts     │
    │  - Lock IPs at 5 attempts    │
    │  - 15 min lockout period     │
    └──────────┬───────────────────┘
               │
               ↓
    ┌──────────────────────────────┐
    │  Layer 2: Authentication     │
    │  - Check credentials         │
    │  - Session cookie validation │
    │  - Login endpoint            │
    └──────────┬───────────────────┘
               │
               ↓
    ┌──────────────────────────────┐
    │  Layer 3: Path Validation    │
    │  - Normalize paths           │
    │  - Check bounds (within root)│
    │  - Prevent traversal attacks │
    └──────────┬───────────────────┘
               │
               ↓
    ┌──────────────────────────────┐
    │  Layer 4: Operation          │
    │  - Serve files               │
    │  - Process uploads           │
    │  - Delete files safely       │
    └──────────┬───────────────────┘
               │
               ↓
    ┌──────────────────────────────┐
    │  Response Sent to Client     │
    └──────────────────────────────┘
```

---

## Setting Persistence Model

```
RAM (During Execution)
┌──────────────────────────────┐
│  Configuration Variables     │
│                              │
│  SERVER_USERNAME = "admin"   │
│  SERVER_PASSWORD = "pass123" │
│  CURRENT_SERVER = HTTPServer │
│  login_attempts = {}         │
│  locked_ips = {}             │
└──────────────────────────────┘
         ↑ ↓
  Save/Load (JSON)
         ↑ ↓
Disk (Persistent)
┌──────────────────────────────┐
│  ~/.portpal_gui_config.json  │
│                              │
│  {                           │
│    "last_folder": "...",     │
│    "last_port": 8000,        │
│    "last_username": "admin"  │
│  }                           │
└──────────────────────────────┘
```

---

## UI Theme Colors

```
┌─────────────────────────────────────┐
│  Background: #1A202C (Dark Blue)    │
│  ████████████████████████████████   │
│                                     │
│  Accent: #667eea (Purple)           │
│  ████████████████ (Headers, Links)  │
│                                     │
│  Status Running: #48BB78 (Green)    │
│  ████████████ (Success indicator)   │
│                                     │
│  Status Idle: #FFD700 (Yellow)      │
│  ████████████ (Waiting indicator)   │
│                                     │
│  Error: #F56565 (Red)               │
│  ████████████ (Stop button)         │
│                                     │
│  Text: #E2E8F0 (Light Gray)         │
│  ████████████████████ (Readable)    │
│                                     │
│  Input: #2D3748 (Darker Blue)       │
│  ████████████████████ (Text field)  │
└─────────────────────────────────────┘
```

---

## Feature Implementation Map

```
┌──────────────────────────────────────┐
│      PortPal GUI Server              │
│         (gui_server.py)              │
├──────────────────────────────────────┤
│                                      │
│  ┌─ PySimpleGUI (GUI Framework)     │
│  │  ├─ Window Management           │
│  │  ├─ Button Callbacks            │
│  │  └─ Theme & Styling             │
│  │                                  │
│  ├─ Configuration Module            │
│  │  ├─ Save Settings to JSON       │
│  │  ├─ Load Settings from JSON     │
│  │  └─ Persistent Storage          │
│  │                                  │
│  ├─ Server Module                   │
│  │  ├─ CustomHTTPHandler           │
│  │  ├─ GET/POST/DELETE Methods     │
│  │  ├─ Authentication              │
│  │  ├─ Brute Force Protection      │
│  │  └─ JSON API Endpoints          │
│  │                                  │
│  ├─ Networking Module               │
│  │  ├─ IPv4 Detection              │
│  │  ├─ Port Configuration          │
│  │  └─ socketserver.TCPServer      │
│  │                                  │
│  └─ Threading Module                │
│     ├─ Background Server Thread    │
│     ├─ File Operations Thread      │
│     └─ ThreadPoolExecutor          │
│                                      │
└──────────────────────────────────────┘
```

---

## Deployment Options Diagram

```
Source Code
├── gui_server.py (633 lines)
├── requirements-gui.txt
├── build_gui.bat
└── check_gui_dependencies.py

         ↓ Distribute

┌────────┴────────────────────────┐
│                                 │
↓                                 ↓

Windows User          Developer
(No Python)           (Has Python)

    │                     │
    ↓                     ↓
    
PortPal.exe          pip install
(Download/            requirements-gui.txt
Build)                    │
    │                     ↓
    ↓              python gui_server.py
    │                     │
    ↓                     ↓
    └──────┬──────────────┘
           ↓
    Server Running
    (Ready to Use)
```

---

## File Organization After Implementation

```
PortPal/
│
├── 📄 Application Files
│   ├── gui_server.py (NEW - Main GUI app)
│   ├── server.py (Original - CLI server)
│   └── start_server.bat (Original launcher)
│
├── 🛠️ Build & Setup
│   ├── build_gui.bat (NEW - Automated builder)
│   ├── check_gui_dependencies.py (NEW - Verifier)
│   ├── requirements.txt (Original - empty)
│   └── requirements-gui.txt (NEW - dependencies)
│
├── 📚 Documentation (NEW)
│   ├── README_GUI.md (Comprehensive guide)
│   ├── GUI_FEATURES.md (Features explained)
│   ├── BUILD_GUI_BINARY.md (Build instructions)
│   ├── QUICK_REFERENCE.md (Quick lookup)
│   ├── GETTING_STARTED.md (Getting started)
│   └── IMPLEMENTATION_SUMMARY.md (Technical)
│
├── 🗂️ Server Files
│   ├── public/ (Files to serve)
│   ├── _templates/ (Template files)
│   └── docs/ (Documentation site)
│
└── 📖 Original
    └── README.md (Original project README)
```

---

These diagrams show the complete visual architecture of PortPal GUI!
