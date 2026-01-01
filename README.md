# Linux App Cleaner 🧹

[![License](https://img.shields.io/badge/License-Custom-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20Only-orange.svg)]()
[![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)]()
[![PyQt5](https://img.shields.io/badge/GUI-PyQt5-brightgreen.svg)]()

> **A powerful uninstaller for Linux that finds and removes ALL traces of applications**

[🇩🇪 Deutsche Version](README_DE.md)

---

## ⚠️ Platform Notice

**This software is ONLY for Linux distributions.**  
There will be **NO Windows or macOS versions** - ever.

Supported Linux distributions:
- Ubuntu / Debian / Linux Mint
- Fedora / RHEL / Nobara
- Arch Linux / Manjaro
- openSUSE
- And most other Linux distributions

---

## 🎯 What is this?

Linux App Cleaner is a comprehensive application uninstaller that goes beyond your system's package manager. It finds and removes **ALL traces** of applications, including:

- ✅ Applications from **apt, flatpak, snap, pip, npm, AppImage**
- ✅ Configuration files in `~/.config/`
- ✅ Cache files in `~/.cache/`
- ✅ Application data in `~/.local/share/`
- ✅ Desktop integration files (`.desktop`, icons)
- ✅ Autostart entries
- ✅ Hidden config files
- ✅ Temporary files
- ✅ Log files
- ✅ And much more!

**Problem:** When you uninstall an app on Linux, it often leaves behind configs, cache, and data.  
**Solution:** Linux App Cleaner finds and removes EVERYTHING!

---

## ✨ Features

### 🔍 Three Search Modes

1. **⚡ Quick Search** - Fast scan of common locations (seconds)
2. **🔬 Deep Search** - Scans the ENTIRE filesystem (2-10 minutes)
3. **🎯 Custom Search** - Select what you want to search

### 🗑️ Three Deletion Modes

1. **🟢 Safe Delete** - Removes only the application
2. **🔴 Thorough Delete** - Removes application + ALL data (uses deep search)
3. **🔍 Analyze Only** - Shows what would be deleted (without deleting)

### 📦 Supports All Package Types

- **apt/dpkg** - System packages
- **Flatpak** - Sandboxed applications  
- **Snap** - Snap packages
- **pip** - Python packages
- **npm** - Node.js packages
- **AppImage** - Portable applications

### 🛡️ Safety Features

- ✅ Protects critical system packages
- ✅ Shows exactly what will be deleted
- ✅ Confirmation dialogs before deletion
- ✅ Live progress indicator
- ✅ Detailed logging
- ✅ Export analysis to text file

### 🎨 Two GUI Versions

- **PyQt5 Version** - Modern, runs 100% in virtualenv (recommended)
- **tkinter Version** - Classic, requires system package

---

## 📥 Installation

### Quick Setup (PyQt5 - Recommended)

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/linux-app-cleaner.git
cd linux-app-cleaner

# 2. Run automatic setup
chmod +x setup.sh
./setup.sh

# 3. Done! Start with:
app-cleaner
```

### Manual Setup (PyQt5)

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install PyQt5

# 3. Run
python linux_app_cleaner_pyqt.py
```

### tkinter Version

```bash
# Install system package
sudo apt install python3-tk  # Ubuntu/Debian
sudo dnf install python3-tkinter  # Fedora
sudo pacman -S tk  # Arch

# Run
python linux_app_cleaner.py
```

---

## 🚀 Usage

### Basic Usage

```bash
# Start the program
cd ~/AppCleaner
source venv/bin/activate
python linux_app_cleaner_pyqt.py
```

### Example: Remove Spotify (Flatpak)

1. **Search** - Type "spotify" in search box
2. **Select** - Click on Spotify in the list
3. **Analyze** - Click "🔍 Analyze Only"
4. **Choose search depth:**
   - ⚡ Quick Search → Shows common locations
   - 🔬 Deep Search → Scans entire system
5. **Review** - See all files that will be deleted
6. **Delete:**
   - 🟢 Safe Delete → Only app
   - 🔴 Thorough Delete → App + all data

### What You'll See

```
📍 Flatpak:
📂 ~/.var/app/com.spotify.Client/           (234 MB)
📂 ~/.var/app/com.spotify.Client/config/    (45 MB)
📂 ~/.var/app/com.spotify.Client/cache/     (123 MB)

📍 Desktop Files:
📄 ~/.local/share/applications/spotify.desktop

📍 Icons:
📄 ~/.local/share/icons/hicolor/256x256/apps/spotify.png

📍 Autostart:
📄 ~/.config/autostart/spotify-autostart.desktop

SUMMARY:
  Files/Folders: 15
  Total Size: 402 MB
```

---

## 📖 Documentation

- [Installation Guide](README_PYQT5.md)
- [Deep Search Explained](GRUENDLICHE_SUCHE.md)
- [Command Reference](BEFEHLE_ERKLAERUNG.md)
- [Update Notes](UPDATE_FORTSCHRITT.md)

---

## 🔬 Deep Search Feature

The **Deep Search** scans these locations:

```
📁 User Data:
  ~/.config/, ~/.cache/, ~/.local/share/
  ~/.var/app/ (Flatpak), ~/snap/ (Snap)

📁 Desktop Integration:
  ~/.local/share/applications/ (.desktop files)
  ~/.local/share/icons/ (Icons)
  /usr/share/applications/, /usr/share/icons/

📁 Autostart:
  ~/.config/autostart/

📁 Hidden Files:
  ~/.*programm*/ (Hidden configs)

📁 Temporary Files:
  /tmp/, /var/tmp/

📁 System Configs:
  /etc/ (System configurations)

📁 Logs:
  ~/.local/share/systemd/, /var/log/

📁 Other:
  ~/Applications/, ~/Downloads/, /opt/
```

**Performance:** 2-10 minutes depending on disk size and file count.

---

## ⚙️ Requirements

- **OS:** Linux (any distribution)
- **Python:** 3.8 or higher
- **Dependencies:** PyQt5 (installed via pip)
- **Disk Space:** ~50 MB
- **Permissions:** sudo access for system packages

---

## 🤝 Contributing

### How to Help

✅ **Report bugs** - Open an issue  
✅ **Test on your distribution** - Share results  
✅ **Translate** - Help with other languages  
✅ **Documentation** - Improve docs  
✅ **Share** - Tell your friends!

### What's NOT Allowed

❌ Modifying the source code  
❌ Creating forks or derivative works  
❌ Selling this software

See [LICENSE](LICENSE) for details.

---

## 🐛 Known Issues

- Deep search can take 5-10 minutes on HDDs
- Some system paths require sudo access
- Progress updates may pause during sudo prompts

---

## 📊 Comparison

| Feature | apt remove | flatpak uninstall | Linux App Cleaner |
|---------|-----------|------------------|-------------------|
| Remove app | ✅ | ✅ | ✅ |
| Remove configs | ❌ | ❌ | ✅ |
| Remove cache | ❌ | ❌ | ✅ |
| Remove desktop files | ❌ | ❌ | ✅ |
| Remove autostart | ❌ | ❌ | ✅ |
| Find hidden files | ❌ | ❌ | ✅ |
| Search entire disk | ❌ | ❌ | ✅ |
| Works for all types | ❌ | ❌ | ✅ |

---

## 🎯 Use Cases

### Perfect for:
- 🧹 Cleaning up after uninstalling apps
- 💾 Freeing disk space
- 🔍 Finding leftover files from old installations
- 🎮 Completely removing games and their data
- 🧪 Testing software without leaving traces
- 📱 Preparing a clean system

### Examples:
- **Remove Flatpak completely:** Finds data in `~/.var/app/`
- **Clean up AppImages:** Finds desktop integration files
- **Delete old configs:** Finds hidden `.programm` folders
- **Free disk space:** Shows exact size of all files

---

## 📝 License

This project uses a **Custom License** that allows:
- ✅ Personal and commercial use
- ✅ Distribution and sharing
- ✅ Bug reporting and support

But does NOT allow:
- ❌ Modifications or derivative works
- ❌ Claiming as your own
- ❌ Selling

See [LICENSE](LICENSE) for full details.

---

## ⚠️ Disclaimer

**USE AT YOUR OWN RISK**

This software deletes files from your system. While it has safety measures:
- Always review what will be deleted before confirming
- Make backups of important data
- Test on non-critical systems first
- The author is not responsible for any data loss

---

## 💬 Support

- 📖 Read the [documentation](README_PYQT5.md)
- 🐛 Report bugs via [Issues](https://github.com/YOUR_USERNAME/linux-app-cleaner/issues)
- 💡 Suggest features via [Issues](https://github.com/YOUR_USERNAME/linux-app-cleaner/issues)
- ⭐ Star this project if you find it useful!

---

## 🙏 Acknowledgments

Made with ❤️ for the Linux community

Special thanks to:
- PyQt5 team for the excellent GUI framework
- All Linux distributions for making this tool necessary 😄
- Everyone who reports bugs and suggests improvements

---

## 📌 Version

**Current Version:** 2.1  
**Release Date:** 2026-01-01  
**Platform:** Linux only  
**Status:** Active development

---

**Remember:** This tool is Linux-only by design. Don't ask for Windows or macOS versions - they will never happen! 🐧
