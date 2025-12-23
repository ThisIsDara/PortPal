# Building PortPal GUI Server Binary

This guide explains how to build the GUI version of PortPal into a standalone executable.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements-gui.txt
```

### 2. Build the Binary (Windows)

Using PyInstaller:

```bash
pyinstaller --onefile --windowed --name "PortPal" --icon icon.ico gui_server.py
```

**Options explained:**
- `--onefile`: Creates a single executable file instead of a folder
- `--windowed`: Hides the console window (GUI only)
- `--name "PortPal"`: Names the executable "PortPal.exe"
- `--icon icon.ico`: (Optional) Adds a custom icon to the executable

### 3. Find Your Binary

The compiled executable will be located in:
```
dist/PortPal.exe
```

### Optional: Add Icon

To add a custom icon to your application:

1. Create or download a `.ico` file
2. Place it in the PortPal folder as `icon.ico`
3. Run the PyInstaller command with the `--icon icon.ico` option

## How to Use the GUI

1. **Launch** the executable: Double-click `PortPal.exe`

2. **Select Folder**: Click "Browse" to choose the folder to serve
   - The last selected folder is automatically remembered

3. **Configure Port**: Enter a port number (default: 8000)
   - The last used port is remembered

4. **Optional Authentication**: 
   - Add username and password for server protection
   - Leave blank for public access

5. **Start Server**: Click "▶ Start Server"
   - IPv4 address is automatically displayed
   - Access URL is shown for quick reference

6. **Stop Server**: Click "⏹ Stop Server" when done

## Features

✅ **Persistent Settings** - Remembers last folder, port, and username  
✅ **IPv4 Display** - Shows your network IP automatically  
✅ **Modern GUI** - Dark theme with 480x360 window  
✅ **Easy Folder Selection** - Browse button for quick folder choice  
✅ **Port Management** - Set any valid port (1-65535)  
✅ **Optional Auth** - Add username/password protection  
✅ **Status Display** - Shows server status in real-time  
✅ **Access URL** - Displays quick access link  

## Advanced PyInstaller Options

If you need more control, use an advanced command:

```bash
pyinstaller \
  --onefile \
  --windowed \
  --name PortPal \
  --icon icon.ico \
  --add-data "public:public" \
  --add-data "_templates:_templates" \
  --splash splash.png \
  gui_server.py
```

## Troubleshooting

**Binary won't start:**
- Ensure you installed all dependencies with `pip install -r requirements-gui.txt`
- Check that Python 3.8+ is installed
- Look for error messages in the build output

**Port already in use:**
- Try a different port number
- Close other applications using that port

**Permission denied errors:**
- Run the executable as Administrator
- Check folder permissions for the served directory

**GUI looks wrong:**
- Ensure PySimpleGUI 5.0.8.3 is correctly installed
- Update: `pip install --upgrade PySimpleGUI`

## Distribution

To share the binary:
1. Copy `dist/PortPal.exe` to any Windows system
2. No Python installation needed on the target system
3. Double-click to run - it's completely standalone!

## Clean Build

To rebuild from scratch:

```bash
rmdir /s build  # Remove build folder
rmdir /s dist   # Remove dist folder  
del PortPal.spec  # Remove spec file
pyinstaller --onefile --windowed --name "PortPal" gui_server.py
```

## Using the Web Interface

Once the server is running:

1. Open your web browser
2. Navigate to the URL shown in the GUI
3. Example: `http://192.168.1.100:8000`

The web interface provides:
- File browsing and downloading
- File uploading (drag & drop)
- Folder navigation
- Storage information
- Authentication (if enabled)
