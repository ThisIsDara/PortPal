# Getting Started with PortPal GUI Server

## 🎯 Choose Your Path

### 👤 End Users (No Technical Background)

**I just want to use the app:**

1. **Download** `PortPal.exe` from Releases (or ask developer to build it)
2. **Double-click** `PortPal.exe`
3. **Click "Browse"** and select a folder
4. **Click "▶ Start Server"**
5. **Copy the URL** and share it
6. Done! 🎉

**No Python needed. No installation. Just download and run.**

---

### 👨‍💻 Developers (Have Python Installed)

**I want to run from source:**

```bash
# Step 1: Install dependencies (one time only)
pip install -r requirements-gui.txt

# Step 2: Verify setup
python check_gui_dependencies.py

# Step 3: Run the application
python gui_server.py
```

Done! The GUI appears immediately.

---

### 🏗️ Builders (Want to Create Executable)

**I want to build the binary:**

```bash
# Fastest way on Windows:
build_gui.bat

# Manually (if needed):
pip install -r requirements-gui.txt
pyinstaller --onefile --windowed --name "PortPal" gui_server.py

# Result: dist/PortPal.exe
```

The executable is ready to share!

---

## 📖 Using the GUI

### Step-by-Step

**1. Launch**
- Double-click `PortPal.exe` or run `python gui_server.py`

**2. Select Folder**
- Click the **Browse** button
- Choose the folder you want to share
- Path appears in the text field

**3. Configure (Optional)**
- **Port:** Leave as 8000 or enter custom port
- **Username:** Enter if you want password protection
- **Password:** Enter if you want password protection

**4. Start Server**
- Click **"▶ Start Server"** button
- Wait 1-2 seconds for startup
- Status changes to "Running ✓"
- Access URL appears below

**5. Access Files**
- **On your computer:** Open browser, go to `http://localhost:8000`
- **On other devices:** Open browser, go to `http://[IPv4 shown]:8000`

**6. Stop**
- Click **"⏹ Stop Server"** when done

---

## 🔑 Key Concepts

### Port
A "port" is like a channel for network communication.
- **Default:** 8000
- **Common:** 8000, 8080, 3000, 5000
- **Valid range:** 1 to 65535

If port 8000 is in use, just pick a different number (8001, 8080, etc.)

### IPv4 Address
Your computer's address on the network.
- **Format:** `192.168.1.100` (example)
- **Auto-detected** by PortPal
- **Use this** to access from other devices

### Authentication
Optional password protection for files.
- **No auth:** Leave both username and password blank
- **With auth:** Fill in both username and password
- **Note:** Password is NOT remembered (only username)

---

## 🎯 Common Tasks

### Share Files with Family
1. Put files in a folder
2. Select that folder in PortPal
3. Click Start
4. Send the URL to family members
5. They open the URL in browser

### Quick File Transfer
1. Create a new folder
2. Put files to transfer in it
3. Select folder in PortPal
4. Share URL with recipient
5. They download files

### Team File Distribution
1. Create shared folder with documents
2. Start PortPal server
3. Give team the URL
4. Everyone can access and download

### Streaming Media
1. Put videos/music in folder
2. Start PortPal server
3. Access from any device (phone, TV, computer)
4. Play files directly in browser

---

## 🔐 Security

### Basic Security
- ✅ Only share on trusted networks
- ✅ Only share files you want to share
- ✅ Delete files from folder when done sharing

### Enhanced Security
- ✅ Add username and password
- ✅ Change default port to something less obvious
- ✅ Close server when not needed

### Maximum Security
- ✅ Use strong password (mix of letters, numbers, symbols)
- ✅ Only allow needed people access
- ✅ Monitor access logs if available
- ✅ Never expose to public internet

---

## 🆘 If Something Goes Wrong

### "Port already in use"
→ Use a different port number (8001, 8080, etc.)

### "Can't access from other device"
→ Use the IPv4 address shown in GUI, not localhost
→ Make sure both devices are on same Wi-Fi

### "Can't find folder"
→ Make sure to click Browse and select folder
→ Can't just type the path

### "Password not working"
→ Make sure BOTH username and password have values
→ Password is case-sensitive (P ≠ p)
→ Close browser and try again

### "Files not appearing"
→ Refresh browser (Ctrl+F5)
→ Make sure files are in selected folder
→ Try a different folder

### GUI won't start
→ Run: `pip install PySimpleGUI`
→ Make sure Python 3.8+ is installed

---

## 📚 More Information

| Want to Know | Read This |
|--------------|-----------|
| How to use the GUI | **GUI_FEATURES.md** |
| How to build executable | **BUILD_GUI_BINARY.md** |
| Complete documentation | **README_GUI.md** |
| Quick reference | **QUICK_REFERENCE.md** |
| Technical details | **IMPLEMENTATION_SUMMARY.md** |

---

## ⚡ Quick Reference

| Task | Steps |
|------|-------|
| **Run app** | Double-click PortPal.exe |
| **Select folder** | Click Browse → Pick folder |
| **Start server** | Click "▶ Start Server" |
| **Access files** | Go to URL shown in GUI |
| **Stop server** | Click "⏹ Stop Server" |
| **Add password** | Fill username + password fields |
| **Change port** | Edit port field before starting |

---

## 🎓 Pro Tips

1. **Keep port consistent** - Use same port every time so bookmarks work
2. **Add to favorites** - Bookmark the access URL for quick return
3. **Test before sharing** - Open URL yourself before sending to others
4. **Use strong password** - Mix letters, numbers, and symbols
5. **Check IPv4 first** - Verify it starts with 192.168 or 10. (private)
6. **Close when done** - Always stop the server when finished

---

## ✅ Verify Everything Works

Before sharing, test:

1. [ ] GUI opens without errors
2. [ ] Can select folder
3. [ ] Server starts ("Running ✓" shows)
4. [ ] IPv4 address displays
5. [ ] Access URL is shown
6. [ ] URL works in browser
7. [ ] Files appear in browser
8. [ ] Can download a file

If all checks pass ✅, you're ready to share!

---

## 🚀 Now You're Ready!

You have everything you need to:
- ✅ Share files with others
- ✅ Host a local web server
- ✅ Transfer large files easily
- ✅ Stream media to other devices
- ✅ Distribute team documents

**Questions?** Check the documentation files.  
**Problems?** See the troubleshooting section above.  
**Ready?** Launch PortPal and start sharing! 🎉

---

## 📞 Where to Go for Help

1. **GUI won't run?** → See check_gui_dependencies.py
2. **Can't access files?** → See QUICK_REFERENCE.md
3. **Want more features?** → See GUI_FEATURES.md
4. **Building executable?** → See BUILD_GUI_BINARY.md
5. **Deep dive?** → See README_GUI.md

---

**PortPal GUI Server** - Making file sharing simple. 🌟

Enjoy your fast, easy, secure local file sharing! 🚀
