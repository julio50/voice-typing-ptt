#!/home/julio/Development/voice_typing/venv/bin/python
"""
Voice Typing System Tray Icon - Qt Version
Better compatibility with KDE Plasma
"""

import sys
import os
import subprocess
import signal
import time
from pathlib import Path
import threading
import queue

from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QTimer, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont

class VoiceTypingMonitor(QThread):
    status_changed = pyqtSignal(str)
    transcription_ready = pyqtSignal(str)

    def __init__(self, process, log_path):
        super().__init__()
        self.process = process
        self.log_path = log_path
        self.running = True

    def run(self):
        """Monitor the process output for status changes"""
        if not self.process:
            return

        try:
            while self.running and self.process and self.process.poll() is None:
                line = self.process.stdout.readline()
                if not line:
                    break

                line = line.strip()

                # Log all output
                with open(self.log_path, 'a') as f:
                    f.write(f"{time.strftime('%H:%M:%S')} {line}\n")

                # Parse status from output
                if "🔴 Recording..." in line:
                    self.status_changed.emit("recording")
                elif "⏳ Processing..." in line or "🧠 Transcribing..." in line:
                    self.status_changed.emit("processing")
                elif "💬" in line:
                    # Extract transcription
                    if '"' in line:
                        start = line.find('"') + 1
                        end = line.rfind('"')
                        if start < end:
                            self.transcription_ready.emit(line[start:end])
                    self.status_changed.emit("ready")
                elif "🟢 Ready" in line:
                    self.status_changed.emit("ready")

        except Exception as e:
            with open(self.log_path, 'a') as f:
                f.write(f"Monitor error: {e}\n")

    def stop(self):
        self.running = False

class VoiceTypingTray(QObject):
    def __init__(self):
        super().__init__()

        self.script_dir = Path(__file__).parent
        self.script_path = self.script_dir / "voice_client_ptt"
        self.log_path = self.script_dir / "voice_typing.log"

        self.process = None
        self.monitor_thread = None
        self.status = "stopped"
        self.last_transcription = ""

        # Create system tray icon
        self.tray_icon = QSystemTrayIcon()

        # Create icons
        self.create_icons()

        # Set initial icon
        self.tray_icon.setIcon(self.icons["stopped"])
        self.tray_icon.setToolTip("Voice Typing - Stopped")

        # Create context menu
        self.create_menu()

        # Connect signals
        self.tray_icon.activated.connect(self.icon_activated)

        # Show the tray icon
        self.tray_icon.show()

        print("Qt System Tray Icon created successfully")

    def create_icons(self):
        """Load PNG microphone icons for different states"""
        self.icons = {}

        try:
            # Try to load the tray icon files first
            for state in ["stopped", "ready", "recording", "processing"]:
                icon_file = self.script_dir / f"tray_icon_{state}.png"
                if icon_file.exists():
                    self.icons[state] = QIcon(str(icon_file))
                    print(f"Loaded tray icon: {icon_file}")
                else:
                    print(f"Tray icon not found: {icon_file}")

            # If we have all microphone icons, we're done
            if len(self.icons) == 4:
                return

        except Exception as e:
            print(f"Error loading PNG icons: {e}")

        # Fallback: create simple colored icons
        size = 22

        def create_colored_icon(color_hex):
            pixmap = QPixmap(size, size)
            pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)

            # Draw colored circle
            color = QColor(color_hex)
            painter.setBrush(color)
            painter.setPen(QColor("white"))
            painter.drawEllipse(3, 3, size-6, size-6)

            # Add center dot
            painter.setBrush(QColor("white"))
            center = size // 2
            painter.drawEllipse(center-2, center-2, 4, 4)

            painter.end()
            return QIcon(pixmap)

        # Create fallback icons
        self.icons["stopped"] = create_colored_icon("#808080")    # Gray
        self.icons["ready"] = create_colored_icon("#00AA00")      # Green
        self.icons["recording"] = create_colored_icon("#DD0000")  # Red
        self.icons["processing"] = create_colored_icon("#0066CC") # Blue

        print(f"Using fallback icons ({len(self.icons)} created)")

    def create_menu(self):
        """Create the simplified context menu"""
        self.menu = QMenu()

        # Status info
        self.status_action = QAction("Voice Typing - Stopped", self.menu)
        self.status_action.setEnabled(False)
        self.menu.addAction(self.status_action)

        self.last_action = QAction("Last: None", self.menu)
        self.last_action.setEnabled(False)
        self.menu.addAction(self.last_action)

        self.menu.addSeparator()

        # Main toggle action (starts stopped, so first action is "Start")
        self.toggle_action = QAction("▶️ Start Voice Typing", self.menu)
        self.toggle_action.triggered.connect(self.toggle_service)
        self.menu.addAction(self.toggle_action)

        self.menu.addSeparator()

        # Utility actions
        show_log_action = QAction("📋 Show Log", self.menu)
        show_log_action.triggered.connect(self.show_log)
        self.menu.addAction(show_log_action)

        settings_action = QAction("⚙️ Settings", self.menu)
        settings_action.triggered.connect(self.show_settings)
        self.menu.addAction(settings_action)

        self.menu.addSeparator()

        # Exit action
        exit_action = QAction("❌ Exit", self.menu)
        exit_action.triggered.connect(self.quit_app)
        self.menu.addAction(exit_action)

        self.tray_icon.setContextMenu(self.menu)

    def update_status(self, new_status):
        """Update the tray icon status"""
        self.status = new_status

        # Update icon
        self.tray_icon.setIcon(self.icons[self.status])

        # Update tooltip and menu
        status_text = {
            "stopped": "Stopped",
            "ready": "Ready - Hold Left Shift + Left Alt",
            "recording": "Recording...",
            "processing": "Processing..."
        }.get(self.status, "Unknown")

        self.tray_icon.setToolTip(f"Voice Typing - {status_text}")
        self.status_action.setText(f"Voice Typing - {status_text}")

        # Update toggle button text
        if self.status == "stopped":
            self.toggle_action.setText("▶️ Start Voice Typing")
        else:
            self.toggle_action.setText("⏸️ Pause Voice Typing")

        # No automatic notifications for transcriptions

    def update_transcription(self, text):
        """Update the last transcription"""
        self.last_transcription = text
        last_text = text[:30] + "..." if len(text) > 30 else text
        self.last_action.setText(f"Last: {last_text}")

    def toggle_service(self):
        """Toggle the voice typing service on/off"""
        if self.status == "stopped":
            self.start_service()
        else:
            self.stop_service()

    def start_service(self):
        """Start the voice typing service"""
        if self.process and self.process.poll() is None:
            return  # Already running

        try:
            # Clear log
            with open(self.log_path, 'w') as f:
                f.write(f"Voice Typing started at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

            # Start process
            self.process = subprocess.Popen(
                [str(self.script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=str(self.script_dir)
            )

            # Start monitoring thread
            self.monitor_thread = VoiceTypingMonitor(self.process, self.log_path)
            self.monitor_thread.status_changed.connect(self.update_status)
            self.monitor_thread.transcription_ready.connect(self.update_transcription)
            self.monitor_thread.start()

            self.update_status("ready")

            self.tray_icon.showMessage(
                "Voice Typing",
                "Service started! Use Left Shift + Left Alt to record.",
                QSystemTrayIcon.Information,
                3000
            )

        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to start service: {e}")

    def stop_service(self):
        """Stop the voice typing service"""
        if self.monitor_thread:
            self.monitor_thread.stop()
            self.monitor_thread.wait()

        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
            except:
                pass

        self.process = None
        self.monitor_thread = None
        self.update_status("stopped")

        # Log stop
        with open(self.log_path, 'a') as f:
            f.write(f"Voice Typing stopped at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")


    def show_log(self):
        """Show the log file"""
        try:
            subprocess.run(["xdg-open", str(self.log_path)])
        except:
            try:
                subprocess.run(["kate", str(self.log_path)])
            except:
                QMessageBox.information(None, "Log Location", f"Log file: {self.log_path}")

    def show_settings(self):
        """Show settings dialog"""
        dialog = QDialog()
        dialog.setWindowTitle("Voice Typing Settings")
        dialog.setFixedSize(350, 200)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("🎤 Voice Typing Settings"))
        layout.addWidget(QLabel(f"Script: {self.script_path.name}"))
        layout.addWidget(QLabel(f"Hotkey: Left Shift + Left Alt"))
        layout.addWidget(QLabel(f"Status: {self.status.title()}"))
        layout.addWidget(QLabel(f"Log: {self.log_path}"))

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.setLayout(layout)
        dialog.exec_()

    def icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_settings()

    def quit_app(self):
        """Quit the application"""
        self.stop_service()
        QApplication.quit()

def main():
    app = QApplication(sys.argv)

    # Check if system tray is available
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "System Tray", "System tray is not available on this desktop.")
        return 1

    # Check if script exists
    script_path = Path(__file__).parent / "voice_client_ptt"
    if not script_path.exists():
        QMessageBox.critical(None, "Error", f"Voice typing script not found: {script_path}")
        return 1

    # Create tray application
    tray = VoiceTypingTray()

    print("Voice Typing Tray (Qt) started successfully")
    print("Right-click the tray icon to access controls")

    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())