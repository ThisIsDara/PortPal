# PortPal GUI - Quick Reference Card

## 🚀 Getting Started (30 seconds)

1. **Download:** Get `PortPal.exe` or run `python gui_server.py`
2. **Select:** Click Browse → Choose folder
3. **Start:** Click "▶ Start Server"
4. **Access:** Copy URL from "Access URL:" field

---

## 📋 GUI Fields Explained

| Field | What to Do | Example |
|-------|-----------|---------|
| **Folder to Share** | Click Browse, pick folder | `C:\Users\John\Documents` |
| **Port** | Keep 8000 or change it | `8000`, `8080`, `3000` |
| **Username** | Optional - leave blank if no auth | `admin` |
| **Password** | Optional - leave blank if no auth | `mypassword123` |

---

## 🎮 Button Guide

| Button | What Happens |
|--------|-------------|
| **Browse** | Opens folder picker |
| **▶ Start Server** | Launches server, shows status/URL |
| **⏹ Stop Server** | Shuts down server |

---

## 📊 Status Indicators

| Status | Meaning |
|--------|---------|
| **Idle** (Yellow) | Server is stopped |
| **Running ✓** (Green) | Server is active |
| **IPv4: 192.168...** | Your network address |
| **Access: http://...** | URL to access files |

---

## 🔑 Authentication

### No Password Needed
- Leave **Username** blank
- Leave **Password** blank
- Anyone can access files

### Password Protection
- Enter **Username** (any text)
- Enter **Password** (any text)
- Login screen appears for visitors

---

## 🌐 Access URLs

### From Your Computer
```
http://localhost:8000
```

### From Other Devices
```
http://[IPv4 shown in GUI]:8000
```

Example:
```
http://192.168.1.100:8000
```

---

## 💾 What Gets Remembered?

✅ Last folder selected  
✅ Last port used  
✅ Last username  
❌ Password (NOT saved for security)

Location: `~/.portpal_gui_config.json`

---

## 🛠️ Building Executable

```bash
# One-step build (Windows)
build_gui.bat

# Or manually
pyinstaller --onefile --windowed --name "PortPal" gui_server.py
```

Result: `dist/PortPal.exe`

---

## ⚙️ Port Selection Guide

| Port | Use | Note |
|------|-----|------|
| **8000** | Default | Usually free |
| **8080** | Alternative | Also common |
| **3000** | Development | Node.js default |
| **5000** | Development | Flask default |
| **80** | HTTP | Requires admin |
| **443** | HTTPS | Requires admin |

**Pick any 1-65535** that isn't in use.

---

## 🔒 Security Checklist

- ✅ For **sensitive files** → Add password
- ✅ Use on **trusted networks** only
- ✅ **Don't expose** to internet
- ✅ Check **IPv4 address** is private (192.168.x.x, 10.x.x.x)
- ✅ **Disable auth** when not needed

---

## 🐛 Quick Fixes

**"Port already in use"**
→ Enter different port (8001, 8080)

**"Can't access from other device"**
→ Use IPv4 address shown, not localhost

**"Password not working"**
→ Make sure BOTH username AND password have values

**"GUI won't start"**
→ Run `pip install PySimpleGUI`

**"Files not showing"**
→ Refresh browser (Ctrl+F5)

---

## 📝 Settings File

File: `C:\Users\YourName\.portpal_gui_config.json`

```json
{
  "last_folder": "C:\\path\\to\\folder",
  "last_port": 8000,
  "last_username": "user"
}
```

**To reset:** Delete the file (it recreates with defaults)

---

## 🎯 Features at a Glance

| Feature | GUI | CLI |
|---------|-----|-----|
| Easy folder selection | ✅ | ❌ |
| Visual status display | ✅ | ❌ |
| Remember settings | ✅ | ❌ |
| IPv4 auto-detect | ✅ | ✅ |
| File hosting | ✅ | ✅ |
| Authentication | ✅ | ✅ |
| Upload/Download | ✅ | ✅ |
| Command-line | ❌ | ✅ |

---

## 📞 Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **Tab** | Move to next field |
| **Enter** | Click active button |
| **Alt+F4** | Close application |

---

## 📦 File Sizes

| Item | Size |
|------|------|
| `gui_server.py` | ~25 KB |
| `PortPal.exe` | ~45-50 MB |
| Installed requirements | ~100 MB |

---

## 🌍 Network Addressing

**Your Computer:**
```
IPv4: 192.168.1.100 (example)
Access: http://192.168.1.100:8000
```

**Other Devices (same network):**
```
Access: http://192.168.1.100:8000
```

**NOT from Internet:**
```
Access: BLOCKED (by design - local only)
```

---

## 🎓 Pro Tips

1. **Set custom port** to run multiple servers
2. **Use authentication** with a strong password
3. **Bookmark access URL** for quick return
4. **Refresh browser** if files don't update
5. **Check firewall** if can't access from other devices
6. **Use port 8000** if unsure (standard)

---

## ✅ Checklist Before Sharing

- [ ] Correct folder selected
- [ ] Port available (not in use)
- [ ] Server shows "Running ✓"
- [ ] Access URL is displayed
- [ ] Can open URL in browser
- [ ] Files visible in browser
- [ ] Password set (if needed)
- [ ] Only intended files in folder

---

## 🎉 You're Ready!

**Start serving files in seconds.**

Questions? Check:
- `README_GUI.md` - Full documentation
- `GUI_FEATURES.md` - Detailed features
- `BUILD_GUI_BINARY.md` - Build instructions

**Happy sharing!** 🚀
