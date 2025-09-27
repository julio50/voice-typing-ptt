#!/home/julio/Development/voice_typing/venv/bin/python
"""
Voice Typing System Tray Icon
Provides visual status and control for voice typing service
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path
import threading
import queue
import tkinter as tk
from tkinter import messagebox

try:
    import pystray
    from pystray import MenuItem as item
    from PIL import Image, ImageDraw
except ImportError:
    print("Missing dependencies. Install with:")
    print("pip install pystray pillow")
    sys.exit(1)

class VoiceTypingTray:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.script_path = self.script_dir / "voice_client_ptt"
        self.log_path = self.script_dir / "voice_typing.log"

        self.process = None
        self.status = "stopped"  # stopped, ready, recording, processing
        self.last_transcription = ""

        # Message queue for status updates
        self.status_queue = queue.Queue()

        # Create icons
        self.icons = self.create_icons()

        # Create tray
        self.tray = pystray.Icon(
            "voice_typing",
            icon=self.icons["stopped"],
            title="Voice Typing - Stopped",
            menu=pystray.Menu(
                item("Status: Stopped", lambda: None, enabled=False),
                item("Last: None", lambda: None, enabled=False),
                pystray.Menu.SEPARATOR,
                item("Start Service", self.start_service),
                item("Stop Service", self.stop_service, enabled=False),
                item("Restart Service", self.restart_service, enabled=False),
                pystray.Menu.SEPARATOR,
                item("Show Log", self.show_log),
                item("Settings", self.show_settings),
                pystray.Menu.SEPARATOR,
                item("Exit", self.quit_app)
            )
        )

    def create_icons(self):
        """Load different colored microphone icons for different states"""
        icons = {}

        try:
            # Try to load PNG icon files
            for state in ["stopped", "ready", "recording", "processing"]:
                icon_file = self.script_dir / f"icon_{state}.png"
                if icon_file.exists():
                    icons[state] = Image.open(icon_file)
                    print(f"Loaded icon: {icon_file}")
                else:
                    print(f"Icon file not found: {icon_file}")

            # If no icons loaded, create fallback
            if not icons:
                raise Exception("No icon files found")

        except Exception as e:
            print(f"Error loading icons: {e}")
            # Fallback: create simple colored circles
            size = 22

            def create_simple_icon(color):
                img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                margin = 4
                draw.ellipse([margin, margin, size-margin, size-margin],
                           fill=color, outline="white", width=2)
                return img

            icons = {
                "stopped": create_simple_icon("#808080"),    # Gray
                "ready": create_simple_icon("#00AA00"),      # Green
                "recording": create_simple_icon("#DD0000"),  # Red
                "processing": create_simple_icon("#0066CC") # Blue
            }
            print("Using fallback icons")

        return icons

    def update_tray(self):
        """Update tray icon and menu based on current status"""
        icon = self.icons.get(self.status, self.icons["stopped"])

        # Status text
        status_text = {
            "stopped": "Stopped",
            "ready": "Ready",
            "recording": "Recording...",
            "processing": "Processing..."
        }.get(self.status, "Unknown")

        # Last transcription (truncated)
        last_text = self.last_transcription[:30] + "..." if len(self.last_transcription) > 30 else self.last_transcription
        if not last_text:
            last_text = "None"

        # Update menu
        self.tray.menu = pystray.Menu(
            item(f"Status: {status_text}", lambda: None, enabled=False),
            item(f"Last: {last_text}", lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            item("Start Service", self.start_service, enabled=(self.status == "stopped")),
            item("Stop Service", self.stop_service, enabled=(self.status != "stopped")),
            item("Restart Service", self.restart_service, enabled=(self.status != "stopped")),
            pystray.Menu.SEPARATOR,
            item("Show Log", self.show_log),
            item("Settings", self.show_settings),
            pystray.Menu.SEPARATOR,
            item("Exit", self.quit_app)
        )

        # Update icon and title
        self.tray.icon = icon
        self.tray.title = f"Voice Typing - {status_text}"

    def start_service(self, icon=None, item=None):
        """Start the voice typing service"""
        if self.process and self.process.poll() is None:
            return  # Already running

        try:
            # Clear log
            with open(self.log_path, 'w') as f:
                f.write(f"Voice Typing started at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

            # Start process with output redirected to log
            self.process = subprocess.Popen(
                [str(self.script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=str(self.script_dir)
            )

            # Start monitoring thread
            self.monitor_thread = threading.Thread(target=self.monitor_process, daemon=True)
            self.monitor_thread.start()

            self.status = "ready"
            self.update_tray()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to start service: {e}")

    def stop_service(self, icon=None, item=None):
        """Stop the voice typing service"""
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
        self.status = "stopped"
        self.update_tray()

        # Log stop
        with open(self.log_path, 'a') as f:
            f.write(f"Voice Typing stopped at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    def restart_service(self, icon=None, item=None):
        """Restart the voice typing service"""
        self.stop_service()
        time.sleep(1)
        self.start_service()

    def monitor_process(self):
        """Monitor the process output for status changes"""
        if not self.process:
            return

        try:
            while self.process and self.process.poll() is None:
                line = self.process.stdout.readline()
                if not line:
                    break

                line = line.strip()

                # Log all output
                with open(self.log_path, 'a') as f:
                    f.write(f"{time.strftime('%H:%M:%S')} {line}\n")

                # Parse status from output
                if "🔴 Recording..." in line:
                    self.status = "recording"
                    self.update_tray()
                elif "⏳ Processing..." in line or "🧠 Transcribing..." in line:
                    self.status = "processing"
                    self.update_tray()
                elif "💬" in line:
                    # Extract transcription
                    if '"' in line:
                        start = line.find('"') + 1
                        end = line.rfind('"')
                        if start < end:
                            self.last_transcription = line[start:end]
                    self.status = "ready"
                    self.update_tray()
                elif "🟢 Ready" in line:
                    self.status = "ready"
                    self.update_tray()

        except Exception as e:
            with open(self.log_path, 'a') as f:
                f.write(f"Monitor error: {e}\n")
        finally:
            if self.status != "stopped":
                self.status = "stopped"
                self.update_tray()

    def show_log(self, icon=None, item=None):
        """Show the log file"""
        try:
            subprocess.run(["xdg-open", str(self.log_path)])
        except:
            # Fallback
            try:
                subprocess.run(["gedit", str(self.log_path)])
            except:
                messagebox.showinfo("Log Location", f"Log file: {self.log_path}")

    def show_settings(self, icon=None, item=None):
        """Show settings dialog"""
        root = tk.Tk()
        root.title("Voice Typing Settings")
        root.geometry("300x200")
        root.resizable(False, False)

        tk.Label(root, text="Voice Typing Settings", font=("Arial", 12, "bold")).pack(pady=10)

        tk.Label(root, text=f"Script: {self.script_path.name}").pack(pady=5)
        tk.Label(root, text=f"Hotkey: Left Shift + Left Alt").pack(pady=5)
        tk.Label(root, text=f"Status: {self.status.title()}").pack(pady=5)

        button_frame = tk.Frame(root)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Show Log", command=lambda: self.show_log()).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Close", command=root.destroy).pack(side=tk.LEFT, padx=5)

        root.mainloop()

    def quit_app(self, icon=None, item=None):
        """Quit the application"""
        self.stop_service()
        self.tray.stop()

    def run(self):
        """Run the tray application"""
        print("Voice Typing Tray started")
        print("Use Left Shift + Left Alt to record when service is running")
        print(f"Script path: {self.script_path}")
        print(f"Icons created: {list(self.icons.keys())}")
        try:
            self.tray.run()
        except Exception as e:
            print(f"Tray error: {e}")
            import traceback
            traceback.print_exc()

def main():
    # Check if script exists
    script_path = Path(__file__).parent / "voice_client_ptt"
    if not script_path.exists():
        messagebox.showerror("Error", f"Voice typing script not found: {script_path}")
        return

    # Create and run tray
    tray = VoiceTypingTray()
    tray.run()

if __name__ == "__main__":
    main()