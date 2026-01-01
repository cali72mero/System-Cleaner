# Linux App Cleaner 🧹

[![Lizenz](https://img.shields.io/badge/Lizenz-Custom-blue.svg)](LICENSE)
[![Plattform](https://img.shields.io/badge/Plattform-Nur%20Linux-orange.svg)]()
[![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)]()
[![PyQt5](https://img.shields.io/badge/GUI-PyQt5-brightgreen.svg)]()

> **Ein mächtiger Deinstaller für Linux, der ALLE Spuren von Programmen findet und entfernt**

[🇬🇧 English Version](README.md)

---

## ⚠️ Plattform-Hinweis

**Diese Software ist NUR für Linux-Distributionen.**  
Es wird **NIEMALS Windows- oder macOS-Versionen** geben.

Unterstützte Linux-Distributionen:
- Ubuntu / Debian / Linux Mint
- Fedora / RHEL / Nobara
- Arch Linux / Manjaro
- openSUSE
- Und die meisten anderen Linux-Distributionen

---

## 🎯 Was ist das?

Linux App Cleaner ist ein umfassender Programm-Deinstaller, der über den System-Paketmanager hinausgeht. Er findet und entfernt **ALLE Spuren** von Programmen, einschließlich:

- ✅ Programme aus **apt, flatpak, snap, pip, npm, AppImage**
- ✅ Konfigurationsdateien in `~/.config/`
- ✅ Cache-Dateien in `~/.cache/`
- ✅ Programmdaten in `~/.local/share/`
- ✅ Desktop-Integrationsdateien (`.desktop`, Icons)
- ✅ Autostart-Einträge
- ✅ Versteckte Konfigurationsdateien
- ✅ Temporäre Dateien
- ✅ Log-Dateien
- ✅ Und vieles mehr!

**Problem:** Wenn du eine App unter Linux deinstallierst, bleiben oft Configs, Cache und Daten zurück.  
**Lösung:** Linux App Cleaner findet und entfernt ALLES!

---

## ✨ Funktionen

### 🔍 Drei Such-Modi

1. **⚡ Schnelle Suche** - Schneller Scan der üblichen Orte (Sekunden)
2. **🔬 Gründliche Suche** - Durchsucht das GESAMTE Dateisystem (2-10 Minuten)
3. **🎯 Benutzerdefinierte Suche** - Wähle aus was durchsucht werden soll

### 🗑️ Drei Lösch-Modi

1. **🟢 Sicher Löschen** - Entfernt nur die Anwendung
2. **🔴 Gründlich Löschen** - Entfernt Anwendung + ALLE Daten (nutzt gründliche Suche)
3. **🔍 Nur Anzeigen** - Zeigt was gelöscht würde (ohne zu löschen)

### 📦 Unterstützt Alle Paket-Typen

- **apt/dpkg** - System-Pakete
- **Flatpak** - Sandboxed-Anwendungen  
- **Snap** - Snap-Pakete
- **pip** - Python-Pakete
- **npm** - Node.js-Pakete
- **AppImage** - Portable Anwendungen

### 🛡️ Sicherheitsfunktionen

- ✅ Schützt kritische Systempakete
- ✅ Zeigt genau was gelöscht wird
- ✅ Bestätigungsdialoge vor dem Löschen
- ✅ Live-Fortschrittsanzeige
- ✅ Detailliertes Logging
- ✅ Export der Analyse in Textdatei

### 🎨 Zwei GUI-Versionen

- **PyQt5-Version** - Modern, läuft 100% in virtualenv (empfohlen)
- **tkinter-Version** - Klassisch, benötigt System-Paket

---

## 📥 Installation

### Schnell-Setup (PyQt5 - Empfohlen)

```bash
# 1. Repository klonen
git clone https://github.com/YOUR_USERNAME/linux-app-cleaner.git
cd linux-app-cleaner

# 2. Automatisches Setup ausführen
chmod +x setup.sh
./setup.sh

# 3. Fertig! Starten mit:
app-cleaner
```

### Manuelles Setup (PyQt5)

```bash
# 1. Virtuelle Umgebung erstellen
python3 -m venv venv
source venv/bin/activate

# 2. Abhängigkeiten installieren
pip install PyQt5

# 3. Ausführen
python linux_app_cleaner_pyqt.py
```

### tkinter-Version

```bash
# System-Paket installieren
sudo apt install python3-tk  # Ubuntu/Debian
sudo dnf install python3-tkinter  # Fedora
sudo pacman -S tk  # Arch

# Ausführen
python linux_app_cleaner.py
```

---

## 🚀 Benutzung

### Grundlegende Verwendung

```bash
# Programm starten
cd ~/AppCleaner
source venv/bin/activate
python linux_app_cleaner_pyqt.py
```

### Beispiel: Spotify entfernen (Flatpak)

1. **Suchen** - "spotify" in Suchfeld eingeben
2. **Auswählen** - Auf Spotify in der Liste klicken
3. **Analysieren** - Auf "🔍 Nur Anzeigen" klicken
4. **Suchtiefe wählen:**
   - ⚡ Schnelle Suche → Zeigt übliche Orte
   - 🔬 Gründliche Suche → Durchsucht gesamtes System
5. **Prüfen** - Alle Dateien ansehen die gelöscht würden
6. **Löschen:**
   - 🟢 Sicher Löschen → Nur App
   - 🔴 Gründlich Löschen → App + alle Daten

### Was du sehen wirst

```
📍 Flatpak:
📂 ~/.var/app/com.spotify.Client/           (234 MB)
📂 ~/.var/app/com.spotify.Client/config/    (45 MB)
📂 ~/.var/app/com.spotify.Client/cache/     (123 MB)

📍 Desktop-Dateien:
📄 ~/.local/share/applications/spotify.desktop

📍 Icons:
📄 ~/.local/share/icons/hicolor/256x256/apps/spotify.png

📍 Autostart:
📄 ~/.config/autostart/spotify-autostart.desktop

ZUSAMMENFASSUNG:
  Dateien/Ordner: 15
  Gesamtgröße: 402 MB
```

---

## 📖 Dokumentation

- [Installationsanleitung](README_PYQT5.md)
- [Gründliche Suche erklärt](GRUENDLICHE_SUCHE.md)
- [Befehls-Referenz](BEFEHLE_ERKLAERUNG.md)
- [Update-Notizen](UPDATE_FORTSCHRITT.md)

---

## 🔬 Gründliche Suche Feature

Die **Gründliche Suche** durchsucht diese Orte:

```
📁 Benutzerdaten:
  ~/.config/, ~/.cache/, ~/.local/share/
  ~/.var/app/ (Flatpak), ~/snap/ (Snap)

📁 Desktop-Integration:
  ~/.local/share/applications/ (.desktop Dateien)
  ~/.local/share/icons/ (Icons)
  /usr/share/applications/, /usr/share/icons/

📁 Autostart:
  ~/.config/autostart/

📁 Versteckte Dateien:
  ~/.*programm*/ (Versteckte Configs)

📁 Temporäre Dateien:
  /tmp/, /var/tmp/

📁 System-Configs:
  /etc/ (System-Konfigurationen)

📁 Logs:
  ~/.local/share/systemd/, /var/log/

📁 Sonstiges:
  ~/Applications/, ~/Downloads/, /opt/
```

**Performance:** 2-10 Minuten je nach Festplattengröße und Dateianzahl.

---

## ⚙️ Anforderungen

- **OS:** Linux (jede Distribution)
- **Python:** 3.8 oder höher
- **Abhängigkeiten:** PyQt5 (via pip installiert)
- **Festplattenspeicher:** ~50 MB
- **Berechtigungen:** sudo-Zugriff für Systempakete

---

## 🤝 Mitmachen

### Wie du helfen kannst

✅ **Fehler melden** - Issue öffnen  
✅ **Auf deiner Distribution testen** - Ergebnisse teilen  
✅ **Übersetzen** - Bei anderen Sprachen helfen  
✅ **Dokumentation** - Docs verbessern  
✅ **Teilen** - Erzähle deinen Freunden davon!

### Was NICHT erlaubt ist

❌ Quellcode modifizieren  
❌ Forks oder abgeleitete Werke erstellen  
❌ Diese Software verkaufen

Siehe [LICENSE](LICENSE) für Details.

---

## 🐛 Bekannte Probleme

- Gründliche Suche kann auf HDDs 5-10 Minuten dauern
- Einige System-Pfade benötigen sudo-Zugriff
- Fortschritts-Updates können bei sudo-Abfragen pausieren

---

## 📊 Vergleich

| Feature | apt remove | flatpak uninstall | Linux App Cleaner |
|---------|-----------|------------------|-------------------|
| App entfernen | ✅ | ✅ | ✅ |
| Configs entfernen | ❌ | ❌ | ✅ |
| Cache entfernen | ❌ | ❌ | ✅ |
| Desktop-Dateien entfernen | ❌ | ❌ | ✅ |
| Autostart entfernen | ❌ | ❌ | ✅ |
| Versteckte Dateien finden | ❌ | ❌ | ✅ |
| Gesamte Festplatte durchsuchen | ❌ | ❌ | ✅ |
| Funktioniert für alle Typen | ❌ | ❌ | ✅ |

---

## 🎯 Anwendungsfälle

### Perfekt für:
- 🧹 Aufräumen nach App-Deinstallation
- 💾 Festplattenspeicher freigeben
- 🔍 Übriggebliebene Dateien von alten Installationen finden
- 🎮 Spiele und deren Daten komplett entfernen
- 🧪 Software testen ohne Spuren zu hinterlassen
- 📱 Sauberes System vorbereiten

### Beispiele:
- **Flatpak komplett entfernen:** Findet Daten in `~/.var/app/`
- **AppImages aufräumen:** Findet Desktop-Integrationsdateien
- **Alte Configs löschen:** Findet versteckte `.programm` Ordner
- **Speicherplatz freigeben:** Zeigt exakte Größe aller Dateien

---

## 📝 Lizenz

Dieses Projekt verwendet eine **Benutzerdefinierte Lizenz** die erlaubt:
- ✅ Persönliche und kommerzielle Nutzung
- ✅ Verbreitung und Teilen
- ✅ Fehler melden und Support

Aber NICHT erlaubt:
- ❌ Modifikationen oder abgeleitete Werke
- ❌ Als eigenes ausgeben
- ❌ Verkaufen

Siehe [LICENSE](LICENSE) für vollständige Details.

---

## ⚠️ Haftungsausschluss

**NUTZUNG AUF EIGENE GEFAHR**

Diese Software löscht Dateien von deinem System. Obwohl Sicherheitsmaßnahmen vorhanden sind:
- Prüfe immer was gelöscht wird vor der Bestätigung
- Erstelle Backups wichtiger Daten
- Teste erst auf unkritischen Systemen
- Der Autor ist nicht verantwortlich für Datenverlust

---

## 💬 Support

- 📖 Lies die [Dokumentation](README_PYQT5.md)
- 🐛 Melde Fehler via [Issues](https://github.com/YOUR_USERNAME/linux-app-cleaner/issues)
- 💡 Schlage Features vor via [Issues](https://github.com/YOUR_USERNAME/linux-app-cleaner/issues)
- ⭐ Gib diesem Projekt einen Stern wenn du es nützlich findest!

---

## 🙏 Danksagungen

Gemacht mit ❤️ für die Linux-Community

Besonderer Dank an:
- Das PyQt5-Team für das exzellente GUI-Framework
- Alle Linux-Distributionen dafür, dass sie dieses Tool notwendig gemacht haben 😄
- Alle die Fehler melden und Verbesserungen vorschlagen

---

## 📌 Version

**Aktuelle Version:** 2.1  
**Veröffentlichungsdatum:** 2026-01-01  
**Plattform:** Nur Linux  
**Status:** Aktive Entwicklung

---

**Denk dran:** Dieses Tool ist absichtlich nur für Linux. Frag nicht nach Windows- oder macOS-Versionen - die wird es nie geben! 🐧
