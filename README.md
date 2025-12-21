# PortPal

PortPal is a lightweight local file server designed for sharing files over your local area network. Launch the server, select a port, and access your files from any device connected to the same network.

**Live Demo**: Check out the [interactive demo page](https://thisisdara.github.io/PortPal/) to see the interface in action.

## Features

- Interactive command-line menu for easy server management
- Start server on default port 8000 or specify a custom port
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

PortPal is designed for **local network use only**. Please be aware:

- Only place files you want to share in the `public/` folder
- Do not expose this server to the public internet
- Use only on trusted networks


## Requirements

- Python 3.8 or higher
- Windows (tested), macOS, and Linux compatible

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
3. Note the printed URL (typically `http://<your-ip>:<port>/`)
4. Open the URL from any device on the same network to browse and download files

The web interface provides:
- **Upload files** - drag and drop or select files to upload to the server
- **Folder navigation** - browse through directories with breadcrumb navigation
- Clean file listing with type icons and previews
- **Image and video thumbnails** - visual previews for media files
- File statistics dashboard with type-based breakdown
- **Dark mode** - toggle between light and dark themes (preference saved)
- One-click downloads for all file types
- Real-time upload progress tracking

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
- **File upload support** via POST requests to `/api/upload` endpoint
- **Folder-aware operations** - uploads and listings respect current directory
- **Safe path handling** - prevents directory traversal attacks
- Cross-Origin Resource Sharing (CORS) enabled for API endpoints
- **CSS variables for theming** - smooth transitions between light and dark modes

## Notes

- Only files in the `public` folder are accessible via the web server
- **Upload functionality** allows adding files directly through the browser
- Files upload to the currently viewed directory (supports nested folders)
- The `_templates` directory serves as a backup and is not served by the server
- **Theme preference** is saved in browser localStorage
- Server can be stopped at any time with Ctrl+C
- Port conflicts will be reported if the chosen port is already in use

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check the issues page or submit a pull request.

## License

MIT

## Author

Created by ThisIsDara

Android Client by https://github.com/AlirezaJahangiri
