# 💻 Befehls-Referenz

Hier sind die Befehle, die der Linux App Cleaner im Hintergrund ausführt:

| Quelle | Befehl (Sicher) | Befehl (Gründlich) |
| :--- | :--- | :--- |
| **APT** | `apt-get remove` | `apt-get purge` |
| **Flatpak** | `flatpak uninstall` | `flatpak uninstall --delete-data` |
| **Snap** | `snap remove` | `snap remove --purge` |
| **pip** | `pip uninstall` | `pip uninstall -y` |
| **AppImage** | Datei löschen | Datei + Desktop-Integration löschen |

Das Tool nutzt `subprocess.run`, um diese Befehle sicher auszuführen.
