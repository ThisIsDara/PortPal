# PortPal

PortPal is a lightweight local file server designed for sharing files over your local area network. Launch the server, select a port, and access your files from any device connected to the same network.

**Live Demo**: Check out the [interactive demo page](https://thisisdara.github.io/PortPal/) to see the interface in action.

## Features

- Interactive command-line menu for easy server management
- Start server on default port 8000 or specify a custom port
- **Optional username/password authentication** with login screen
- **Brute force protection** - automatic IP lockout after 5 failed login attempts (15-minute cooldown)
- **Session-based authentication** - secure cookie management for logged-in users
- Display your device's IPv4 address for network access
- **Upload files directly through the web interface** with drag-and-drop support
- Serves files from the `public` folder with an auto-generated file list
- **Folder navigation** - browse through subdirectories seamlessly
- RESTful JSON endpoint at `/api/files` for programmatic access
- Beautiful web interface with file statistics and type categorization
- **Dark mode toggle** - switch between light and dark themes with persistent preference
- **Image and video previews** - visual thumbnails for media files
- **Upload progress tracking** - real-time feedback during file uploads
- Zero external dependencies - uses only Python standard library

## Security Notice

PortPal is designed for **local network use only**. Security features:

- **Optional Authentication** - Set username and password when starting the server
- **Brute Force Protection** - Automatic IP lockout after 5 failed login attempts
  - 15-minute lockout period per IP address
  - Automatic cleanup of expired lockouts
  - 1-second delay after each failed attempt
- **Session Management** - Cookie-based authentication for logged-in users
- **Path Validation** - Prevents directory traversal attacks

**Important Security Guidelines:**
- Only place files you want to share in the `public/` folder
- Enable authentication if sharing sensitive files
- Do not expose this server to the public internet
- Use only on trusted networks


## Requirements

- Python 3.8 or higher
- Windows (tested), macOS, and Linux compatible

## Download (Windows Binary)

- Grab the latest prebuilt executable from the [GitHub Releases page](https://github.com/ThisIsDara/PortPal/releases)
- Run `PortPal.exe` on Windows
- No Python install needed for the binary; use the installation steps below if running from source

## Installation

Clone the repository:

```bash
git clone https://github.com/ThisIsDara/PortPal.git
cd PortPal
```

Optional: Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## Usage

### Interactive Menu (Recommended)

Launch the interactive menu:

```bash
python server.py
```

When you run the server, you'll see the PortPal ASCII banner and menu:

```
██████╗  ██████╗ ██████╗ ████████╗    ██████╗  █████╗ ██╗     
██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝    ██╔══██╗██╔══██╗██║     
██████╔╝██║   ██║██████╔╝   ██║       ██████╔╝███████║██║     
██╔═══╝ ██║   ██║██╔══██╗   ██║       ██╔═══╝ ██╔══██║██║     
██║     ╚██████╔╝██║  ██║   ██║       ██║     ██║  ██║███████╗
╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝       ╚═╝     ╚═╝  ╚═╝╚══════╝

PortPal - Simple Local File Hosting Server
============================================================

Main Menu
------------------------------------------------------------
1. Start Server
2. Get Device IPv4
3. Help
4. Exit
============================================================
Enter your choice (1-4):
```

Available menu options:
- **Start Server** - Choose default port 8000 or enter a custom port
  - You'll be prompted to enter a username (optional)
  - You'll be prompted to enter a password (optional)
  - Leave both empty for no authentication
- **Get Device IPv4** - Display your local network IP address for sharing
- **Help** - View usage instructions and tips
- **Exit** - Return to menu or quit the application

### Quick Start (Windows)

Use the included batch file for quick server startup:

```bash
start_server.bat
```

This launches `python server.py` directly and keeps the terminal window open when the server stops.

### Command Line Arguments

Start the server directly with optional port specification:

```bash
python server.py --port 8080
```

## Using the Server

1. Place files you want to share in the `public` folder
2. Start the server using one of the methods above
3. (Optional) Enter username and password for authentication
4. Note the printed URL (typically `http://<your-ip>:<port>/`)
5. Open the URL from any device on the same network
6. Log in with credentials if authentication is enabled
7. Browse and download files

The web interface provides:
- **Login screen** - username/password authentication (when enabled)
- **Upload files** - drag and drop or select files to upload to the server
- **Folder navigation** - browse through directories with breadcrumb navigation
- Clean file listing with type icons and previews
- **Image and video thumbnails** - visual previews for media files
- File statistics dashboard with type-based breakdown
- **Dark mode** - toggle between light and dark themes (preference saved)
- One-click downloads for all file types
- Real-time upload progress tracking
- **Delete functionality** - remove files and folders (when authenticated)

## Project Structure

```
PortPal/
├── public/              # Directory for files to be served
│   └── index.html       # Web interface
├── server.py            # Main server application with interactive menu
├── start_server.bat     # Windows quick launcher
├── requirements.txt     # Dependencies (currently none - stdlib only)
└── _templates/          # Backup templates (not served)
    ├── index.html
    └── style.css
```

## Technical Details

- Server binds to all available network interfaces (`0.0.0.0`)
- Automatically detects and displays your LAN IPv4 address
- Built on Python's `http.server` and `socketserver` modules
- Custom HTTP request handler for file listings and API endpoints
- **Authentication system** with session cookie management
- **Rate limiting** - tracks failed login attempts per IP address
- **Automatic lockout** - 15-minute cooldown after 5 failed attempts
- **File upload support** via POST requests to `/api/upload` endpoint
- **File deletion support** via DELETE requests to `/api/delete` endpoint (requires authentication)
- **Folder-aware operations** - uploads and listings respect current directory
- **Safe path handling** - prevents directory traversal attacks
- Cross-Origin Resource Sharing (CORS) enabled for API endpoints
- **CSS variables for theming** - smooth transitions between light and dark modes

## Notes

- Only files in the `public` folder are accessible via the web server
- **Authentication is optional** - leave username and password empty for open access
- **Brute force protection** automatically locks IPs after multiple failed login attempts
- **Upload functionality** allows adding files directly through the browser
- **Delete functionality** requires authentication (when enabled) to prevent unauthorized deletions
- Files upload to the currently viewed directory (supports nested folders)
- The `_templates` directory serves as a backup and is not served by the server
- **Theme preference** is saved in browser localStorage
- **Session cookies** maintain login state across page refreshes
- Server can be stopped at any time with Ctrl+C
- Port conflicts will be reported if the chosen port is already in use

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check the issues page or submit a pull request.

## License

MIT

## Author

Created by ThisIsDara

Android Client by https://github.com/AlirezaJahangiri
