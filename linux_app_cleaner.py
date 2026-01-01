#!/usr/bin/env python3
"""
Linux App Cleaner - PyQt5 Version
Vollständiger Programm-Deinstaller mit PyQt5 GUI
Läuft komplett in venv - keine System-Pakete nötig!
"""

import os
import subprocess
import shutil
import json
import sys
from pathlib import Path
from datetime import datetime
import threading

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QLabel,
    QComboBox, QTextEdit, QMessageBox, QTabWidget, QHeaderView,
    QFileDialog, QProgressDialog
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QColor, QFont


class PackageScanner(QThread):
    """Thread zum Scannen von Paketen im Hintergrund"""
    finished = pyqtSignal(list)
    progress = pyqtSignal(str)
    
    def __init__(self, cleaner):
        super().__init__()
        self.cleaner = cleaner
    
    def run(self):
        """Scannt alle Pakete"""
        packages = self.cleaner.get_all_packages(progress_callback=self.progress.emit)
        self.finished.emit(packages)


class LinuxAppCleaner:
    def __init__(self):
        self.home = Path.home()
        self.log_file = self.home / ".app_cleaner_log.txt"
        
        # Kritische Systempakete die NICHT gelöscht werden dürfen
        self.protected_packages = {
            'linux-image', 'linux-headers', 'systemd', 'bash', 'coreutils',
            'apt', 'dpkg', 'gnome-shell', 'kde-plasma', 'xorg', 'wayland',
            'grub', 'sudo', 'network-manager', 'pulseaudio', 'pipewire',
            'gdm3', 'lightdm', 'sddm', 'python3', 'glibc', 'libc6'
        }
    
    def log(self, message):
        """Log-Nachricht in Datei schreiben"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def run_command(self, command):
        """Sicheres Ausführen von Shell-Befehlen"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=30
            )
            return result.stdout, result.stderr, result.returncode
        except Exception as e:
            return "", str(e), 1
    
    def is_protected(self, package_name):
        """Prüft ob Paket geschützt ist"""
        package_lower = package_name.lower()
        return any(protected in package_lower for protected in self.protected_packages)
    
    def get_apt_packages(self, progress_callback=None):
        """Alle über apt/dpkg installierten Pakete"""
        if progress_callback:
            progress_callback("Scanne apt-Pakete...")
        
        packages = []
        stdout, _, returncode = self.run_command("dpkg -l | grep '^ii'")
        
        if returncode == 0:
            for line in stdout.split('\n'):
                parts = line.split()
                if len(parts) >= 3:
                    name = parts[1]
                    version = parts[2]
                    packages.append({
                        'name': name,
                        'version': version,
                        'source': 'apt',
                        'protected': self.is_protected(name)
                    })
        return packages
    
    def get_flatpak_packages(self, progress_callback=None):
        """Alle Flatpak-Programme"""
        if progress_callback:
            progress_callback("Scanne Flatpak-Apps...")
        
        packages = []
        stdout, _, returncode = self.run_command("flatpak list --app --columns=name,application,version")
        
        if returncode == 0:
            for line in stdout.split('\n')[1:]:
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        packages.append({
                            'name': parts[0],
                            'id': parts[1] if len(parts) > 1 else parts[0],
                            'version': parts[2] if len(parts) > 2 else 'unknown',
                            'source': 'flatpak',
                            'protected': False
                        })
        return packages
    
    def get_snap_packages(self, progress_callback=None):
        """Alle Snap-Programme"""
        if progress_callback:
            progress_callback("Scanne Snap-Apps...")
        
        packages = []
        stdout, _, returncode = self.run_command("snap list")
        
        if returncode == 0:
            for line in stdout.split('\n')[1:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        packages.append({
                            'name': parts[0],
                            'version': parts[1],
                            'source': 'snap',
                            'protected': False
                        })
        return packages
    
    def get_pip_packages(self, progress_callback=None):
        """Alle pip-installierten Python-Pakete"""
        if progress_callback:
            progress_callback("Scanne pip-Pakete...")
        
        packages = []
        stdout, _, returncode = self.run_command("pip list --format=json")
        
        if returncode == 0:
            try:
                pip_list = json.loads(stdout)
                for pkg in pip_list:
                    packages.append({
                        'name': pkg['name'],
                        'version': pkg['version'],
                        'source': 'pip',
                        'protected': False
                    })
            except:
                pass
        return packages
    
    def get_npm_packages(self, progress_callback=None):
        """Alle global installierten npm-Pakete"""
        if progress_callback:
            progress_callback("Scanne npm-Pakete...")
        
        packages = []
        stdout, _, returncode = self.run_command("npm list -g --depth=0 --json")
        
        if returncode == 0:
            try:
                npm_data = json.loads(stdout)
                if 'dependencies' in npm_data:
                    for name, info in npm_data['dependencies'].items():
                        packages.append({
                            'name': name,
                            'version': info.get('version', 'unknown'),
                            'source': 'npm',
                            'protected': False
                        })
            except:
                pass
        return packages
    
    def get_appimages(self, progress_callback=None):
        """Findet AppImage-Dateien"""
        if progress_callback:
            progress_callback("Scanne AppImages...")
        
        packages = []
        search_paths = [
            self.home / 'Applications',
            self.home / 'Downloads',
            Path('/opt'),
            self.home / '.local' / 'bin'
        ]
        
        for search_path in search_paths:
            if search_path.exists():
                for appimage in search_path.rglob('*.AppImage'):
                    packages.append({
                        'name': appimage.stem,
                        'path': str(appimage),
                        'version': 'AppImage',
                        'source': 'appimage',
                        'protected': False
                    })
        return packages
    
    def get_all_packages(self, progress_callback=None):
        """Sammelt alle installierten Programme"""
        all_packages = []
        
        all_packages.extend(self.get_apt_packages(progress_callback))
        all_packages.extend(self.get_flatpak_packages(progress_callback))
        all_packages.extend(self.get_snap_packages(progress_callback))
        all_packages.extend(self.get_pip_packages(progress_callback))
        all_packages.extend(self.get_npm_packages(progress_callback))
        all_packages.extend(self.get_appimages(progress_callback))
        
        return all_packages
    
    def find_package_files(self, package_name, package_source=None, package_id=None):
        """Findet alle Dateien die zu einem Programm gehören"""
        
        # Basis-Verzeichnisse für normale Programme
        config_dirs = [
            self.home / '.config' / package_name,
            self.home / '.config' / package_name.lower(),
            self.home / f'.{package_name}',
            self.home / f'.{package_name.lower()}'
        ]
        
        cache_dirs = [
            self.home / '.cache' / package_name,
            self.home / '.cache' / package_name.lower()
        ]
        
        data_dirs = [
            self.home / '.local' / 'share' / package_name,
            self.home / '.local' / 'share' / package_name.lower()
        ]
        
        # Spezielle Behandlung für Flatpak
        if package_source == 'flatpak' and package_id:
            # Flatpak speichert ALLES in ~/.var/app/APP-ID/
            flatpak_dir = self.home / '.var' / 'app' / package_id
            if flatpak_dir.exists():
                config_dirs.append(flatpak_dir / 'config')
                cache_dirs.append(flatpak_dir / 'cache')
                data_dirs.append(flatpak_dir / 'data')
                # Haupt-Flatpak-Ordner auch hinzufügen
                data_dirs.append(flatpak_dir)
        
        # Spezielle Behandlung für Snap
        if package_source == 'snap':
            # Snap speichert in ~/snap/PROGRAMM/
            snap_dir = self.home / 'snap' / package_name
            if snap_dir.exists():
                data_dirs.append(snap_dir)
        
        all_dirs = config_dirs + cache_dirs + data_dirs
        
        found_files = {}
        for dir_path in all_dirs:
            if dir_path.exists():
                try:
                    size = sum(f.stat().st_size for f in dir_path.rglob('*') if f.is_file())
                    # Nur hinzufügen wenn größer als 0
                    if size > 0:
                        found_files[str(dir_path)] = {
                            'type': 'directory',
                            'size': size
                        }
                except (PermissionError, OSError):
                    # Manche Dateien können nicht gelesen werden
                    pass
        
        return found_files
    
    def deep_search_files(self, package_name, package_source=None, package_id=None, progress_callback=None):
        """
        GRÜNDLICHE Suche: Durchsucht die GESAMTE Festplatte nach allen Spuren
        Dies kann mehrere Minuten dauern!
        """
        found_files = {}
        
        # Verschiedene Schreibweisen des Programmnamens
        search_terms = [
            package_name,
            package_name.lower(),
            package_name.upper(),
            package_name.replace('-', '_'),
            package_name.replace('_', '-'),
            package_name.replace('-', ''),
            package_name.replace('_', ''),
        ]
        
        # Bei Flatpak auch die APP-ID nutzen
        if package_source == 'flatpak' and package_id:
            search_terms.append(package_id)
            search_terms.append(package_id.split('.')[-1])  # Nur letzter Teil
        
        # Wichtige Suchpfade (sortiert nach Wichtigkeit)
        search_paths = [
            # Benutzer-Daten (am wichtigsten)
            (self.home / '.config', 'Config'),
            (self.home / '.cache', 'Cache'),
            (self.home / '.local' / 'share', 'Daten'),
            (self.home / '.local' / 'state', 'Status'),
            
            # Flatpak & Snap
            (self.home / '.var' / 'app', 'Flatpak'),
            (self.home / 'snap', 'Snap'),
            
            # Desktop-Integration
            (self.home / '.local' / 'share' / 'applications', 'Desktop-Dateien'),
            (self.home / '.local' / 'share' / 'icons', 'Icons'),
            (Path('/usr/share/applications'), 'System-Desktop-Dateien'),
            (Path('/usr/share/icons'), 'System-Icons'),
            
            # Autostart
            (self.home / '.config' / 'autostart', 'Autostart'),
            
            # Versteckte Dateien im Home
            (self.home, 'Home-Dotfiles'),
            
            # Temporäre Dateien
            (Path('/tmp'), 'Temp'),
            (Path('/var/tmp'), 'Var-Temp'),
            
            # System-Configs (nur lesbar mit sudo)
            (Path('/etc'), 'System-Config'),
            
            # Logs
            (self.home / '.local' / 'share' / 'systemd', 'User-Logs'),
            (Path('/var/log'), 'System-Logs'),
            
            # Weitere mögliche Orte
            (self.home / 'Applications', 'Applications'),
            (self.home / 'Downloads', 'Downloads'),
            (self.home / '.wine', 'Wine'),
            (Path('/opt'), 'Optional-Apps'),
        ]
        
        total_paths = len(search_paths)
        
        for idx, (base_path, category) in enumerate(search_paths):
            if progress_callback:
                progress_callback(f"Durchsuche {category} ({idx+1}/{total_paths})...")
            
            if not base_path.exists():
                continue
            
            try:
                # Durchsuche diesen Pfad nach allen Varianten des Programmnamens
                for search_term in search_terms:
                    search_lower = search_term.lower()
                    
                    # Spezial-Behandlung für verschiedene Pfade
                    if category == 'Home-Dotfiles':
                        # Nur versteckte Dateien/Ordner im Home
                        for item in base_path.glob(f'.{search_lower}*'):
                            if item.is_dir() and item != base_path:
                                try:
                                    size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                                    if size > 0:
                                        found_files[str(item)] = {
                                            'type': 'directory',
                                            'size': size,
                                            'category': category
                                        }
                                except (PermissionError, OSError):
                                    pass
                    
                    elif category == 'Desktop-Dateien' or category == 'System-Desktop-Dateien':
                        # .desktop Dateien
                        for item in base_path.glob(f'*{search_lower}*.desktop'):
                            if item.is_file():
                                try:
                                    found_files[str(item)] = {
                                        'type': 'file',
                                        'size': item.stat().st_size,
                                        'category': category
                                    }
                                except (PermissionError, OSError):
                                    pass
                    
                    elif category in ['Temp', 'Var-Temp', 'Downloads']:
                        # Nur erste Ebene durchsuchen (zu viele Dateien)
                        try:
                            for item in base_path.glob(f'*{search_lower}*'):
                                if item.is_file():
                                    found_files[str(item)] = {
                                        'type': 'file',
                                        'size': item.stat().st_size,
                                        'category': category
                                    }
                                elif item.is_dir():
                                    size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                                    if size > 0:
                                        found_files[str(item)] = {
                                            'type': 'directory',
                                            'size': size,
                                            'category': category
                                        }
                        except (PermissionError, OSError):
                            pass
                    
                    else:
                        # Normale Ordner rekursiv durchsuchen
                        try:
                            for item in base_path.rglob(f'*{search_lower}*'):
                                if item.is_file():
                                    found_files[str(item)] = {
                                        'type': 'file',
                                        'size': item.stat().st_size,
                                        'category': category
                                    }
                                elif item.is_dir() and str(item) not in found_files:
                                    try:
                                        size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                                        if size > 0:
                                            found_files[str(item)] = {
                                                'type': 'directory',
                                                'size': size,
                                                'category': category
                                            }
                                    except (PermissionError, OSError):
                                        pass
                        except (PermissionError, OSError):
                            # Kein Zugriff auf diesen Pfad
                            pass
            
            except Exception as e:
                # Fehler beim Durchsuchen dieses Pfads ignorieren
                pass
        
        if progress_callback:
            progress_callback(f"Suche abgeschlossen! {len(found_files)} Dateien/Ordner gefunden.")
        
        return found_files
    
    def uninstall_package(self, package, mode='safe'):
        """Deinstalliert ein Paket"""
        results = {
            'success': False,
            'removed_program': False,
            'removed_files': [],
            'errors': []
        }
        
        if package.get('protected', False):
            results['errors'].append(f"GESCHÜTZT: {package['name']} ist ein Systempaket!")
            return results
        
        source = package['source']
        name = package['name']
        
        try:
            if source == 'apt':
                cmd = f"sudo apt-get remove -y {name}"
                if mode == 'thorough':
                    cmd = f"sudo apt-get purge -y {name}"
                
                stdout, stderr, returncode = self.run_command(cmd)
                if returncode == 0:
                    results['removed_program'] = True
                    self.log(f"APT: Entfernt {name}")
                else:
                    results['errors'].append(f"APT-Fehler: {stderr}")
            
            elif source == 'flatpak':
                cmd = f"flatpak uninstall -y {package.get('id', name)}"
                stdout, stderr, returncode = self.run_command(cmd)
                if returncode == 0:
                    results['removed_program'] = True
                    self.log(f"Flatpak: Entfernt {name}")
                else:
                    results['errors'].append(f"Flatpak-Fehler: {stderr}")
            
            elif source == 'snap':
                cmd = f"sudo snap remove {name}"
                stdout, stderr, returncode = self.run_command(cmd)
                if returncode == 0:
                    results['removed_program'] = True
                    self.log(f"Snap: Entfernt {name}")
                else:
                    results['errors'].append(f"Snap-Fehler: {stderr}")
            
            elif source == 'pip':
                cmd = f"pip uninstall -y {name}"
                stdout, stderr, returncode = self.run_command(cmd)
                if returncode == 0:
                    results['removed_program'] = True
                    self.log(f"pip: Entfernt {name}")
                else:
                    results['errors'].append(f"pip-Fehler: {stderr}")
            
            elif source == 'npm':
                cmd = f"npm uninstall -g {name}"
                stdout, stderr, returncode = self.run_command(cmd)
                if returncode == 0:
                    results['removed_program'] = True
                    self.log(f"npm: Entfernt {name}")
                else:
                    results['errors'].append(f"npm-Fehler: {stderr}")
            
            elif source == 'appimage':
                appimage_path = Path(package.get('path', ''))
                if appimage_path.exists():
                    appimage_path.unlink()
                    results['removed_program'] = True
                    self.log(f"AppImage gelöscht: {appimage_path}")
        
        except Exception as e:
            results['errors'].append(f"Fehler bei Deinstallation: {str(e)}")
        
        if mode == 'thorough' and results['removed_program']:
            # Nutze deep search für wirklich ALLE Dateien
            package_files = self.deep_search_files(
                name, 
                package_source=source,
                package_id=package.get('id')
            )
            
            for file_path in package_files:
                try:
                    path = Path(file_path)
                    if path.exists():
                        if path.is_dir():
                            shutil.rmtree(path)
                        else:
                            path.unlink()
                        results['removed_files'].append(file_path)
                        self.log(f"Gelöscht: {file_path}")
                except Exception as e:
                    results['errors'].append(f"Fehler beim Löschen von {file_path}: {str(e)}")
        
        results['success'] = results['removed_program']
        return results


class DeepSearchThread(QThread):
    """Thread für Tiefensuche"""
    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)
    
    def __init__(self, cleaner, package):
        super().__init__()
        self.cleaner = cleaner
        self.package = package
    
    def run(self):
        """Führt Tiefensuche durch"""
        results = self.cleaner.deep_search_files(
            self.package['name'],
            package_source=self.package.get('source'),
            package_id=self.package.get('id'),
            progress_callback=self.progress.emit
        )
        self.finished.emit(results)


class AnalyzeDialog(QWidget):
    """Dialog für die Analyse-Ansicht"""
    
    def __init__(self, package, cleaner, parent=None):
        super().__init__(parent)
        self.package = package
        self.cleaner = cleaner
        self.setWindowTitle(f"🔍 Analyse: {package['name']}")
        self.setGeometry(100, 100, 900, 700)
        self.deep_search_results = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Suchoptionen
        search_options = QHBoxLayout()
        search_options.addWidget(QLabel("Suchmodus:"))
        
        self.quick_search_btn = QPushButton("⚡ Schnelle Suche")
        self.quick_search_btn.clicked.connect(lambda: self.load_analysis(deep=False))
        self.quick_search_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px;")
        search_options.addWidget(self.quick_search_btn)
        
        self.deep_search_btn = QPushButton("🔬 GRÜNDLICHE Suche (ganze Festplatte)")
        self.deep_search_btn.clicked.connect(self.start_deep_search)
        self.deep_search_btn.setStyleSheet("background-color: #FF9800; color: white; padding: 5px;")
        search_options.addWidget(self.deep_search_btn)
        
        search_options.addStretch()
        layout.addLayout(search_options)
        
        # Info-Label
        info_label = QLabel("💡 Schnell = normale Orte | Gründlich = GESAMTE Festplatte (kann Minuten dauern)")
        info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(info_label)
        
        # Tabs
        self.tabs = QTabWidget()
        
        # Tab 1: Dateien
        files_tab = QWidget()
        files_layout = QVBoxLayout()
        
        self.files_text = QTextEdit()
        self.files_text.setReadOnly(True)
        self.files_text.setFont(QFont("Monospace", 10))
        files_layout.addWidget(self.files_text)
        
        files_tab.setLayout(files_layout)
        self.tabs.addTab(files_tab, "📁 Dateien & Orte")
        
        # Tab 2: Befehle
        commands_tab = QWidget()
        commands_layout = QVBoxLayout()
        
        self.commands_text = QTextEdit()
        self.commands_text.setReadOnly(True)
        self.commands_text.setFont(QFont("Monospace", 10))
        commands_layout.addWidget(self.commands_text)
        
        commands_tab.setLayout(commands_layout)
        self.tabs.addTab(commands_tab, "💻 Befehle")
        
        layout.addWidget(self.tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        copy_btn = QPushButton("📋 Befehle kopieren")
        copy_btn.clicked.connect(self.copy_commands)
        button_layout.addWidget(copy_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("❌ Schließen")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Lade Daten (schnelle Suche als Standard)
        self.load_analysis(deep=False)
    
    def start_deep_search(self):
        """Startet gründliche Suche im Hintergrund"""
        # Progress Dialog
        self.progress_dialog = QProgressDialog(
            "Durchsuche Festplatte...",
            None,
            0,
            0,
            self
        )
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setWindowTitle("Gründliche Suche")
        self.progress_dialog.show()
        
        # Search Thread
        self.search_thread = DeepSearchThread(self.cleaner, self.package)
        self.search_thread.progress.connect(lambda msg: self.progress_dialog.setLabelText(msg))
        self.search_thread.finished.connect(self.on_deep_search_finished)
        self.search_thread.start()
    
    def on_deep_search_finished(self, results):
        """Wird aufgerufen wenn Tiefensuche fertig ist"""
        self.progress_dialog.close()
        self.deep_search_results = results
        self.load_analysis(deep=True)
        
        # Info
        QMessageBox.information(
            self,
            "Suche abgeschlossen",
            f"Gründliche Suche abgeschlossen!\n\n"
            f"Gefunden: {len(results)} Dateien/Ordner\n"
            f"Größe: {sum(r['size'] for r in results.values()) / (1024*1024):.2f} MB"
        )
    
    def load_analysis(self, deep=False):
        """Lädt Analyse-Daten"""
        pkg_name = self.package['name']
        
        if deep and self.deep_search_results:
            pkg_files = self.deep_search_results
        elif deep:
            # Deep search wurde angefordert aber noch nicht durchgeführt
            return
        else:
            # Schnelle Suche
            pkg_files = self.cleaner.find_package_files(
                pkg_name,
                package_source=self.package.get('source'),
                package_id=self.package.get('id')
            )
        
        # Dateien-Tab
        files_info = f"ANALYSE FÜR: {pkg_name}\n"
        files_info += "=" * 80 + "\n\n"
        files_info += f"SUCHMODUS: {'🔬 GRÜNDLICH (ganze Festplatte)' if deep else '⚡ SCHNELL (normale Orte)'}\n"
        files_info += f"QUELLE: {self.package['source']}\n"
        files_info += f"VERSION: {self.package.get('version', 'unknown')}\n"
        
        if self.package.get('protected', False):
            files_info += "\n⚠️  WARNUNG: SYSTEMPAKET - NICHT LÖSCHEN!\n"
        
        files_info += f"\n{'=' * 80}\n"
        files_info += "GEFUNDENE DATEIEN UND ORTE:\n"
        files_info += "=" * 80 + "\n\n"
        
        if pkg_files:
            total_size = 0
            
            # Gruppiere nach Kategorie wenn Deep Search
            if deep and 'category' in list(pkg_files.values())[0]:
                # Gruppiere nach Kategorie
                categories = {}
                for path, info in pkg_files.items():
                    cat = info.get('category', 'Unbekannt')
                    if cat not in categories:
                        categories[cat] = []
                    categories[cat].append((path, info))
                
                # Zeige pro Kategorie
                for category, items in sorted(categories.items()):
                    files_info += f"\n📍 {category}:\n"
                    files_info += "-" * 80 + "\n"
                    
                    for path, info in sorted(items):
                        size_mb = info['size'] / (1024 * 1024)
                        total_size += info['size']
                        
                        icon = "📂" if info['type'] == 'directory' else "📄"
                        files_info += f"{icon} {path}\n"
                        files_info += f"   Größe: {size_mb:.2f} MB\n"
                    
                    files_info += "\n"
            else:
                # Normale Anzeige
                for path, info in sorted(pkg_files.items()):
                    size_mb = info['size'] / (1024 * 1024)
                    total_size += info['size']
                    
                    files_info += f"📂 {path}\n"
                    files_info += f"   Größe: {size_mb:.2f} MB\n"
                    
                    try:
                        path_obj = Path(path)
                        if path_obj.exists() and path_obj.is_dir():
                            contents = list(path_obj.iterdir())[:5]
                            if contents:
                                files_info += "   Inhalt (Beispiel):\n"
                                for item in contents:
                                    files_info += f"      • {item.name}\n"
                                if len(list(path_obj.iterdir())) > 5:
                                    files_info += f"      ... und {len(list(path_obj.iterdir())) - 5} weitere\n"
                    except:
                        pass
                    
                    files_info += "\n"
            
            total_mb = total_size / (1024 * 1024)
            files_info += "=" * 80 + "\n"
            files_info += f"ZUSAMMENFASSUNG:\n"
            files_info += f"  Dateien/Ordner gefunden: {len(pkg_files)}\n"
            files_info += f"  Gesamtgröße: {total_mb:.2f} MB ({total_size / (1024*1024*1024):.2f} GB)\n"
            
            if deep:
                files_info += f"\n💡 TIP: Dies sind ALLE gefundenen Spuren auf der Festplatte!\n"
                files_info += f"    Prüfe genau was du löschen willst.\n"
        else:
            files_info += "ℹ️  Keine zusätzlichen Dateien gefunden.\n"
            if not deep:
                files_info += "\n💡 TIP: Versuche die 'GRÜNDLICHE Suche' für eine vollständige Suche!\n"
        
        self.files_text.setText(files_info)
        
        # Befehle-Tab
        commands_info = f"BEFEHLE ZUM LÖSCHEN VON: {pkg_name}\n"
        commands_info += "=" * 80 + "\n\n"
        
        source = self.package['source']
        
        commands_info += "🟢 SICHER LÖSCHEN:\n"
        commands_info += "-" * 80 + "\n"
        
        self.complete_cmd = ""
        
        if source == 'apt':
            self.complete_cmd = f"sudo apt-get remove {pkg_name}"
            commands_info += f"{self.complete_cmd}\n"
        elif source == 'flatpak':
            self.complete_cmd = f"flatpak uninstall {self.package.get('id', pkg_name)}"
            commands_info += f"{self.complete_cmd}\n"
        elif source == 'snap':
            self.complete_cmd = f"sudo snap remove {pkg_name}"
            commands_info += f"{self.complete_cmd}\n"
        elif source == 'pip':
            self.complete_cmd = f"pip uninstall {pkg_name}"
            commands_info += f"{self.complete_cmd}\n"
        elif source == 'npm':
            self.complete_cmd = f"npm uninstall -g {pkg_name}"
            commands_info += f"{self.complete_cmd}\n"
        elif source == 'appimage':
            self.complete_cmd = f"rm '{self.package.get('path', '')}'"
            commands_info += f"{self.complete_cmd}\n"
        
        commands_info += "\n🔴 GRÜNDLICH LÖSCHEN:\n"
        commands_info += "-" * 80 + "\n"
        
        if source == 'apt':
            commands_info += f"sudo apt-get purge {pkg_name}\n"
        else:
            commands_info += f"{self.complete_cmd}\n"
        
        if pkg_files:
            for path in sorted(pkg_files.keys()):
                commands_info += f"rm -rf '{path}'\n"
        
        self.commands_text.setText(commands_info)
    
    def copy_commands(self):
        """Kopiert Befehle in Zwischenablage"""
        clipboard = QApplication.clipboard()
        
        cmd_text = self.complete_cmd + "\n"
        pkg_files = self.cleaner.find_package_files(
            self.package['name'],
            package_source=self.package.get('source'),
            package_id=self.package.get('id')
        )
        
        for path in sorted(pkg_files.keys()):
            cmd_text += f"rm -rf '{path}'\n"
        
        clipboard.setText(cmd_text)
        QMessageBox.information(self, "Kopiert", "Befehle in Zwischenablage kopiert!")


class AppCleanerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.cleaner = LinuxAppCleaner()
        self.packages = []
        self.filtered_packages = []
        self.init_ui()
        self.refresh_packages()
    
    def init_ui(self):
        self.setWindowTitle("Linux App Cleaner - PyQt5")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main Layout
        layout = QVBoxLayout()
        
        # Top Bar - Suche und Filter
        top_layout = QHBoxLayout()
        
        top_layout.addWidget(QLabel("Suche:"))
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Programmname eingeben...")
        self.search_box.textChanged.connect(self.filter_packages)
        top_layout.addWidget(self.search_box)
        
        refresh_btn = QPushButton("🔄 Aktualisieren")
        refresh_btn.clicked.connect(self.refresh_packages)
        top_layout.addWidget(refresh_btn)
        
        top_layout.addWidget(QLabel("Quelle:"))
        
        self.source_filter = QComboBox()
        self.source_filter.addItems(['Alle', 'apt', 'flatpak', 'snap', 'pip', 'npm', 'appimage'])
        self.source_filter.currentTextChanged.connect(self.filter_packages)
        top_layout.addWidget(self.source_filter)
        
        layout.addLayout(top_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Name', 'Version', 'Quelle', 'Status'])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        layout.addWidget(self.table)
        
        # Info Box
        info_label = QLabel("Details:")
        layout.addWidget(info_label)
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        layout.addWidget(self.info_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        analyze_btn = QPushButton("🔍 Nur Anzeigen")
        analyze_btn.clicked.connect(self.analyze_package)
        analyze_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px;")
        button_layout.addWidget(analyze_btn)
        
        safe_btn = QPushButton("🟢 Sicher Löschen")
        safe_btn.clicked.connect(lambda: self.uninstall_selected('safe'))
        safe_btn.setStyleSheet("background-color: #2196F3; color: white; padding: 10px;")
        button_layout.addWidget(safe_btn)
        
        thorough_btn = QPushButton("🔴 Gründlich Löschen")
        thorough_btn.clicked.connect(lambda: self.uninstall_selected('thorough'))
        thorough_btn.setStyleSheet("background-color: #f44336; color: white; padding: 10px;")
        button_layout.addWidget(thorough_btn)
        
        export_btn = QPushButton("💾 Export Liste")
        export_btn.clicked.connect(self.export_analysis)
        button_layout.addWidget(export_btn)
        
        layout.addLayout(button_layout)
        
        # Status Bar
        self.status_label = QLabel("Bereit")
        layout.addWidget(self.status_label)
        
        central_widget.setLayout(layout)
    
    def refresh_packages(self):
        """Lädt alle Pakete neu"""
        self.status_label.setText("Lade Programme...")
        
        # Progress Dialog
        progress = QProgressDialog("Scanne installierte Programme...", None, 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        
        # Scanner Thread
        self.scanner = PackageScanner(self.cleaner)
        self.scanner.progress.connect(lambda msg: progress.setLabelText(msg))
        self.scanner.finished.connect(lambda pkgs: self.on_packages_loaded(pkgs, progress))
        self.scanner.start()
    
    def on_packages_loaded(self, packages, progress):
        """Wird aufgerufen wenn Pakete geladen wurden"""
        self.packages = packages
        self.filtered_packages = packages
        self.display_packages()
        progress.close()
        self.status_label.setText(f"{len(packages)} Programme gefunden")
    
    def filter_packages(self):
        """Filtert Paketliste"""
        search_term = self.search_box.text().lower()
        source_filter = self.source_filter.currentText()
        
        self.filtered_packages = []
        for pkg in self.packages:
            if source_filter != 'Alle' and pkg['source'] != source_filter:
                continue
            
            if search_term and search_term not in pkg['name'].lower():
                continue
            
            self.filtered_packages.append(pkg)
        
        self.display_packages()
    
    def display_packages(self):
        """Zeigt Pakete in der Tabelle an"""
        self.table.setRowCount(0)
        
        for pkg in self.filtered_packages:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(pkg['name']))
            self.table.setItem(row, 1, QTableWidgetItem(pkg.get('version', 'unknown')))
            self.table.setItem(row, 2, QTableWidgetItem(pkg['source']))
            
            status = "🔒 GESCHÜTZT" if pkg.get('protected', False) else "✓"
            status_item = QTableWidgetItem(status)
            
            if pkg.get('protected', False):
                status_item.setBackground(QColor(255, 200, 200))
            
            self.table.setItem(row, 3, status_item)
        
        self.status_label.setText(f"{len(self.filtered_packages)} Programme gefunden")
    
    def on_selection_changed(self):
        """Wird aufgerufen wenn Auswahl geändert wird"""
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            pkg_name = self.table.item(row, 0).text()
            
            for pkg in self.filtered_packages:
                if pkg['name'] == pkg_name:
                    info = f"Programm: {pkg['name']}\n"
                    info += f"Version: {pkg.get('version', 'unknown')}\n"
                    info += f"Quelle: {pkg['source']}\n"
                    
                    if pkg.get('protected', False):
                        info += "\n⚠️ WARNUNG: Dies ist ein SYSTEMPAKET!\n"
                        info += "Das Löschen kann Linux beschädigen!\n"
                    
                    self.info_text.setText(info)
                    break
    
    def get_selected_package(self):
        """Gibt aktuell ausgewähltes Paket zurück"""
        selected = self.table.selectedItems()
        if not selected:
            return None
        
        row = selected[0].row()
        pkg_name = self.table.item(row, 0).text()
        
        for pkg in self.filtered_packages:
            if pkg['name'] == pkg_name:
                return pkg
        
        return None
    
    def analyze_package(self):
        """Öffnet Analyse-Dialog"""
        pkg = self.get_selected_package()
        if not pkg:
            QMessageBox.information(self, "Info", "Bitte wähle zuerst ein Programm aus!")
            return
        
        dialog = AnalyzeDialog(pkg, self.cleaner, self)
        dialog.show()
    
    def uninstall_selected(self, mode):
        """Deinstalliert ausgewähltes Paket"""
        pkg = self.get_selected_package()
        if not pkg:
            QMessageBox.information(self, "Info", "Bitte wähle zuerst ein Programm aus!")
            return
        
        # Geschützte Pakete
        if pkg.get('protected', False):
            QMessageBox.critical(
                self,
                "Geschütztes Paket",
                f"⛔ {pkg['name']} ist ein SYSTEMPAKET!\n\n"
                "Das Löschen würde Linux beschädigen.\n"
                "Deinstallation abgebrochen."
            )
            return
        
        # Bestätigung
        mode_text = "SICHER" if mode == 'safe' else "GRÜNDLICH"
        
        if mode == 'safe':
            msg = f"🟢 SICHER LÖSCHEN\n\n"
            msg += f"Programm: {pkg['name']}\n"
            msg += f"Quelle: {pkg['source']}\n\n"
            msg += "Was wird gelöscht:\n"
            msg += "• Das Programm selbst\n\n"
            msg += "Was bleibt:\n"
            msg += "• Config-Dateien\n"
            msg += "• Cache und Daten\n"
        else:
            files = self.cleaner.find_package_files(
                pkg['name'],
                package_source=pkg.get('source'),
                package_id=pkg.get('id')
            )
            total_size = sum(info['size'] for info in files.values())
            size_mb = total_size / (1024 * 1024)
            
            msg = f"🔴 GRÜNDLICH LÖSCHEN\n\n"
            msg += f"Programm: {pkg['name']}\n"
            msg += f"Quelle: {pkg['source']}\n\n"
            msg += "Was wird gelöscht:\n"
            msg += "• Das Programm\n"
            msg += "• Alle Config-Dateien\n"
            msg += "• Alle Cache-Daten\n"
            msg += "• Alle Programm-Daten\n\n"
            msg += f"Dateien: {len(files)}\n"
            msg += f"Größe: {size_mb:.2f} MB\n"
        
        msg += "\nMöchtest du fortfahren?"
        
        reply = QMessageBox.question(
            self,
            f"{mode_text} Löschen",
            msg,
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Deinstallation
        self.status_label.setText(f"Deinstalliere {pkg['name']}...")
        QApplication.processEvents()
        
        results = self.cleaner.uninstall_package(pkg, mode)
        
        # Ergebnis
        if results['success']:
            msg = f"✅ {pkg['name']} erfolgreich deinstalliert!\n\n"
            
            if results['removed_program']:
                msg += "✓ Programm entfernt\n"
            
            if results['removed_files']:
                msg += f"✓ {len(results['removed_files'])} Dateien gelöscht\n"
            
            if results['errors']:
                msg += "\n⚠️ Warnungen:\n"
                for error in results['errors']:
                    msg += f"  • {error}\n"
            
            QMessageBox.information(self, "Erfolg", msg)
            self.refresh_packages()
        else:
            msg = f"❌ Fehler beim Deinstallieren von {pkg['name']}\n\n"
            for error in results['errors']:
                msg += f"• {error}\n"
            
            QMessageBox.critical(self, "Fehler", msg)
        
        self.status_label.setText("Bereit")
    
    def export_analysis(self):
        """Exportiert Analyse"""
        pkg = self.get_selected_package()
        if not pkg:
            QMessageBox.information(self, "Info", "Bitte wähle zuerst ein Programm aus!")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export speichern",
            str(self.cleaner.home / f"app_cleaner_{pkg['name']}.txt"),
            "Text Files (*.txt)"
        )
        
        if not filename:
            return
        
        pkg_files = self.cleaner.find_package_files(
            pkg['name'],
            package_source=pkg.get('source'),
            package_id=pkg.get('id')
        )
        
        with open(filename, 'w') as f:
            f.write(f"LINUX APP CLEANER - EXPORT\n")
            f.write(f"Erstellt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"PROGRAMM: {pkg['name']}\n")
            f.write("-" * 80 + "\n")
            f.write(f"Quelle: {pkg['source']}\n")
            f.write(f"Version: {pkg.get('version', 'unknown')}\n\n")
            
            if pkg_files:
                f.write("Gefundene Dateien:\n")
                total_size = 0
                for path, info in sorted(pkg_files.items()):
                    size_mb = info['size'] / (1024 * 1024)
                    total_size += info['size']
                    f.write(f"  • {path} ({size_mb:.2f} MB)\n")
                
                total_mb = total_size / (1024 * 1024)
                f.write(f"\nGesamtgröße: {total_mb:.2f} MB\n")
            
            f.write("\nLösch-Befehle:\n")
            source = pkg['source']
            if source == 'apt':
                f.write(f"  sudo apt-get purge -y {pkg['name']}\n")
            elif source == 'flatpak':
                f.write(f"  flatpak uninstall -y {pkg.get('id', pkg['name'])}\n")
            elif source == 'snap':
                f.write(f"  sudo snap remove {pkg['name']}\n")
            elif source == 'pip':
                f.write(f"  pip uninstall -y {pkg['name']}\n")
            elif source == 'npm':
                f.write(f"  npm uninstall -g {pkg['name']}\n")
            
            if pkg_files:
                f.write("\nDateien löschen:\n")
                for path in sorted(pkg_files.keys()):
                    f.write(f"  rm -rf '{path}'\n")
        
        QMessageBox.information(self, "Export", f"Analyse exportiert nach:\n{filename}")


def main():
    app = QApplication(sys.argv)
    
    # Dark Mode Support
    app.setStyle('Fusion')
    
    window = AppCleanerGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
