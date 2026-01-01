# FAQ - Häufig gestellte Fragen

## ❓ Allgemeine Fragen

### Was ist System Cleaner?

Ein Programm für Linux das Programme zu 100% löscht - nicht nur das Programm selbst, sondern auch ALLE Config-Dateien, Cache-Daten, Desktop-Dateien, Icons, etc.

---

### Ist es kostenlos?

Ja! 100% kostenlos und Open Source. Für immer!

---

### Ist es sicher?

Ja! Der komplette Code ist auf GitHub einsehbar. System-Pakete werden automatisch geschützt. Du siehst VOR dem Löschen was alles entfernt wird.

---

### Für welche Linux-Distributionen funktioniert es?

**ALLE!** Ubuntu, Debian, Fedora, Arch, openSUSE, Manjaro, Pop!_OS, Elementary, Linux Mint - und alle anderen!

---

## 🖥️ Windows & macOS

### Gibt es eine Windows-Version?

**Nein!** Und wird es auch nicht geben.

**Warum?**
- Registry löschen würde Windows kaputt machen (Blue Screen, bootet nicht mehr)
- Microsoft verbietet solche Programme in ihrer Lizenz
- Zu gefährlich - wir wollen nicht verantwortlich sein wenn Systeme kaputt gehen

**Aber:** Wenn genug Leute eine Windows-Version wollen, können wir eine STARK EINGESCHRÄNKTE Version machen (ohne Registry-Zugriff). Diese kann dann aber NICHT alles löschen.

---

### Gibt es eine macOS-Version?

**Nein!**

**Warum?**
- macOS hat bereits einen eingebauten Deinstaller
- Wenn man ihn richtig benutzt, löscht er bereits alle Daten
- Technisch unnötig

---

## 🔧 Installation & Nutzung

### Wie installiere ich System Cleaner?

**Einfach:**
```bash
git clone https://github.com/cali72mero/System-Cleaner.git
cd System-Cleaner
chmod +x setup.sh
./setup.sh
```

Fertig! Starten mit: `app-cleaner`

---

### Brauche ich Python-Kenntnisse?

Nein! Das Programm hat eine GUI (grafische Oberfläche). Einfach starten und klicken!

---

### Welche Python-Version brauche ich?

Python 3.8 oder höher.

Prüfen mit: `python3 --version`

---

### Muss ich sudo benutzen?

**Kommt drauf an:**
- **Flatpak, pip, npm, AppImage:** KEIN sudo nötig
- **apt, snap:** Ja, sudo nötig

Das Programm sagt dir wenn sudo nötig ist!

---

## 🔍 Funktionen

### Was ist der Unterschied zwischen "Schnelle Suche" und "Gründliche Suche"?

**Schnelle Suche:**
- Durchsucht nur übliche Orte (~/.config, ~/.cache, etc.)
- Fertig in Sekunden
- Findet 90% der Dateien

**Gründliche Suche:**
- Durchsucht die KOMPLETTE Festplatte
- Dauert 2-10 Minuten
- Findet 100% der Dateien (ALLES!)

---

### Was ist der Unterschied zwischen "Sicher" und "Gründlich" Löschen?

**🟢 Sicher Löschen:**
- Löscht nur das Programm
- Config-Dateien bleiben
- Du kannst später wieder installieren und hast deine Einstellungen

**🔴 Gründlich Löschen:**
- Löscht ALLES (Programm + Config + Cache + Daten)
- 0 Bytes bleiben übrig
- Wie eine komplette Neuinstallation

---

### Was macht "🔍 Nur Anzeigen"?

Zeigt dir alle Dateien die gefunden wurden, ohne sie zu löschen. Perfekt um zu prüfen was gelöscht würde!

---

## 💾 Speicherplatz

### Wie viel Speicher spare ich?

**Kommt drauf an!**

Ein Programm: 50-500 MB (je nach Programm)
100 Programme: 5-20 GB!

Beispiel Spotify (Flatpak): ~230 MB Datenmüll bleibt normalerweise übrig.

---

### Warum ist meine Festplatte immer noch voll?

1. Hast du "Schnelle Suche" benutzt? → Nutze "Gründliche Suche"!
2. Leere den Papierkorb: `rm -rf ~/.local/share/Trash/*`
3. Prüfe große Dateien: `du -sh ~/* | sort -h`

---

## 📦 Unterstützte Programme

### Welche Programmtypen werden unterstützt?

- ✅ apt/dpkg (Ubuntu, Debian)
- ✅ Flatpak
- ✅ Snap
- ✅ pip (Python)
- ✅ npm (Node.js)
- ✅ AppImage

---

### Kann ich auch manuell installierte Programme löschen?

Ja! Wenn sie in einem der üblichen Orte liegen:
- ~/Applications
- ~/Downloads
- /opt
- ~/.local/bin

---

### Funktioniert es mit Wine-Programmen?

Teilweise! Wine-Programme in ~/.wine werden gefunden.

---

## 🛡️ Sicherheit

### Kann ich aus Versehen wichtige System-Pakete löschen?

**Nein!** System-Pakete werden automatisch geschützt:
- linux-image (Kernel)
- systemd
- bash
- apt
- etc.

Wenn du versuchst ein System-Paket zu löschen, kommt eine Fehlermeldung.

---

### Sammelt das Programm Daten über mich?

**Nein!** Absolut KEINE Datensammlung. Kein Tracking, keine Telemetrie, keine Werbung.

Der komplette Code ist Open Source - du kannst alles überprüfen!

---

### Kann mein System kaputt gehen?

Sehr unwahrscheinlich! System-Pakete sind geschützt. Aber:
- ⚠️ Prüfe immer was gelöscht wird bevor du bestätigst
- ⚠️ Mache Backups wichtiger Daten

---

## 🐛 Probleme

### Das Programm startet nicht!

Siehe [TROUBLESHOOTING.md](TROUBLESHOOTING.md) für Lösungen!

---

### Ich habe einen Bug gefunden!

Super! Bitte melden:
- GitHub Issues: https://github.com/cali72mero/System-Cleaner/issues
- Email: support@cali72mero.de

---

### Ich habe eine Feature-Idee!

Toll! Öffne ein Issue auf GitHub oder schreib eine Email!

---

## 📧 Support

### Wie bekomme ich Hilfe?

**Email:** support@cali72mero.de

**GitHub Issues:** https://github.com/cali72mero/System-Cleaner/issues

**Dokumentation:**
- [Installation](README.md)
- [PyQt5 Version](README_PYQT5.md)
- [Gründliche Suche](GRUENDLICHE_SUCHE.md)
- [Probleme lösen](TROUBLESHOOTING.md)

---

### Wie lange dauert es bis ich eine Antwort bekomme?

Email: 24-48 Stunden
GitHub Issues: So schnell wie möglich!

---

## 🚀 Entwicklung

### Kann ich mithelfen?

Ja! Siehe [CONTRIBUTING.md](CONTRIBUTING.md)

Du kannst:
- Bugs melden
- Features vorschlagen
- Auf anderen Distros testen
- Dokumentation verbessern
- Übersetzungen machen

**Aber:** Code ändern ist nicht erlaubt (siehe Lizenz).

---

### Warum darf ich den Code nicht ändern?

Wegen der Custom License. Du darfst:
- ✅ Das Programm nutzen
- ✅ Es teilen
- ✅ Bugs melden

Aber nicht:
- ❌ Code ändern
- ❌ Forks erstellen
- ❌ Als eigenes Projekt ausgeben

---

### Wird das Programm weiterentwickelt?

Ja! Aktive Entwicklung. Schau auf GitHub für Updates!

---

## 📊 Technische Details

### Mit was ist es programmiert?

Python 3.8+ mit PyQt5 für die GUI.

---

### Wie funktioniert die Deep-Search?

Rekursives Durchsuchen aller Ordner auf der Festplatte nach Dateien die den Programmnamen enthalten.

Durchsucht: ~/.config, ~/.cache, ~/.local, ~/.var/app, ~/snap, /tmp, /etc, und mehr!

---

### Warum dauert Deep-Search so lange?

Weil es die KOMPLETTE Festplatte durchsucht! Auf großen HDDs kann das 5-10 Minuten dauern.

**Tipp:** Auf SSDs geht's viel schneller (2-3 Minuten)!

---

## 💡 Tipps & Tricks

### Soll ich immer "Gründlich Löschen" nutzen?

Kommt drauf an:
- **Gründlich:** Wenn du das Programm NIE WIEDER brauchst
- **Sicher:** Wenn du es vielleicht nochmal installieren willst (Einstellungen bleiben)

---

### Wie finde ich heraus wie viel Speicher frei wird?

Nutze "🔍 Nur Anzeigen" - zeigt dir die Größe BEVOR du löschst!

---

### Kann ich mehrere Programme auf einmal löschen?

Aktuell nicht. Kommt vielleicht in einer späteren Version!

---

**Noch Fragen? Schreib uns!** 📧 support@cali72mero.de
