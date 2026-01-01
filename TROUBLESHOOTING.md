# Troubleshooting / Problemlösung

## 🔧 Häufige Probleme & Lösungen

### Problem 1: "Programm startet nicht"

**Symptom:** Beim Ausführen von `python linux_app_cleaner_pyqt.py` passiert nichts oder es kommt ein Fehler.

**Lösung:**

1. **Prüfe Python-Version:**
   ```bash
   python3 --version
   ```
   Muss mindestens 3.8 sein!

2. **Prüfe ob PyQt5 installiert ist:**
   ```bash
   pip list | grep PyQt5
   ```
   
3. **Installiere PyQt5 neu:**
   ```bash
   pip install --upgrade PyQt5
   ```

4. **Nutze das setup.sh Script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

---

### Problem 2: "ModuleNotFoundError: No module named 'PyQt5'"

**Symptom:** Fehler beim Starten: `ModuleNotFoundError: No module named 'PyQt5'`

**Lösung:**

```bash
# In der virtuellen Umgebung:
source venv/bin/activate
pip install PyQt5

# Oder system-weit:
pip install PyQt5 --break-system-packages
```

---

### Problem 3: "Permission denied" beim Löschen

**Symptom:** Beim Löschen kommt "Permission denied"

**Lösung:**

Systemweite Programme brauchen sudo:
```bash
# Für apt-Pakete:
sudo app-cleaner

# Oder direkt:
sudo python linux_app_cleaner_pyqt.py
```

---

### Problem 4: "Deep Search dauert ewig"

**Symptom:** Gründliche Suche läuft über 15 Minuten

**Lösung:**

Das ist normal wenn:
- ✅ Große Festplatte (1 TB+)
- ✅ Viele Dateien auf der Platte
- ✅ Langsame HDD (statt SSD)

**Tipp:** Nutze die "Schnelle Suche" für die meisten Programme!

---

### Problem 5: "Programm wird nicht gefunden"

**Symptom:** Dein installiertes Programm wird nicht in der Liste angezeigt

**Lösung:**

1. **Aktualisiere die Liste:**
   - Klicke auf "🔄 Aktualisieren"

2. **Prüfe ob wirklich installiert:**
   ```bash
   # Für apt:
   dpkg -l | grep programmname
   
   # Für flatpak:
   flatpak list
   
   # Für snap:
   snap list
   ```

3. **Manuell installierte Programme:**
   - AppImages müssen in ~/Applications, ~/Downloads, /opt oder ~/.local/bin liegen

---

### Problem 6: "System-Paket kann nicht gelöscht werden"

**Symptom:** Fehlermeldung "⛔ SYSTEMPAKET - NICHT LÖSCHEN!"

**Lösung:**

Das ist **RICHTIG SO**! 🛡️

System-Pakete wie:
- linux-image (Kernel)
- systemd
- bash
- apt
- etc.

dürfen NICHT gelöscht werden, sonst geht dein System kaputt!

**Das ist eine Sicherheitsfunktion!**

---

### Problem 7: "tkinter Version funktioniert nicht"

**Symptom:** `linux_app_cleaner.py` startet nicht

**Lösung:**

tkinter braucht System-Paket:

```bash
# Ubuntu/Debian:
sudo apt install python3-tk

# Fedora:
sudo dnf install python3-tkinter

# Arch:
sudo pacman -S tk
```

**Tipp:** Nutze lieber die PyQt5-Version! Die funktioniert in venv.

---

### Problem 8: "Keine sudo-Rechte"

**Symptom:** "sudo: command not found" oder keine sudo-Rechte

**Lösung:**

Für User-Programme (flatpak, pip, npm, AppImage) brauchst du kein sudo!

Für System-Pakete (apt, snap) bist du Administrator:
```bash
# Als root einloggen
su -

# Oder Nutzer zu sudo-Gruppe hinzufügen
usermod -aG sudo deinusername
```

---

### Problem 9: "Festplatte immer noch voll"

**Symptom:** Nach dem Löschen ist die Festplatte immer noch voll

**Lösung:**

1. **Nutze Deep Search statt Quick Search:**
   - Quick Search findet nur die üblichen Orte
   - Deep Search durchsucht die KOMPLETTE Platte

2. **Prüfe andere große Dateien:**
   ```bash
   # Größte Ordner finden:
   du -sh ~/* | sort -h
   ```

3. **Leere den Papierkorb:**
   ```bash
   rm -rf ~/.local/share/Trash/*
   ```

---

### Problem 10: "Programm friert ein"

**Symptom:** GUI reagiert nicht mehr während Deep Search

**Lösung:**

Das ist ein bekannter Bug in Version 2.0 und früher!

**Update auf Version 2.1+:**
```bash
cd System-Cleaner
git pull
```

Version 2.1 hat Live-Fortschrittsanzeige und friert nicht mehr ein!

---

### Problem 11: "Flatpak-Daten werden nicht gefunden"

**Symptom:** Flatpak-App zeigt "Keine Dateien gefunden"

**Lösung:**

Update auf Version 2.0+! Ältere Versionen fanden Flatpak-Daten in `~/.var/app/` nicht.

```bash
cd System-Cleaner
git pull
```

---

### Problem 12: "Error beim Installieren mit setup.sh"

**Symptom:** setup.sh schlägt fehl

**Lösung:**

```bash
# 1. Python3 und venv installiert?
sudo apt install python3 python3-venv python3-pip

# 2. setup.sh ausführbar machen
chmod +x setup.sh

# 3. Neu starten
./setup.sh
```

---

## 🆘 Immer noch Probleme?

**Schreib uns eine Email:**

📧 **support@cali72mero.de**

**Oder öffne ein Issue auf GitHub:**

👉 https://github.com/cali72mero/System-Cleaner/issues

---

## 📋 Checkliste für Bug Reports

Wenn du ein Problem meldest, gib bitte an:

```
[ ] Linux-Distribution und Version
[ ] Python-Version (python3 --version)
[ ] PyQt5-Version (pip show PyQt5)
[ ] Was du gemacht hast (Schritte)
[ ] Was passiert ist (Fehler)
[ ] Fehlermeldungen (komplett kopieren)
[ ] Screenshots (falls hilfreich)
```

---

**Wir helfen gerne! 🚀**
