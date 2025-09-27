# 🎤 Voice Typing - Push-to-Talk Speech Recognition

A fast, secure, and elegant voice typing solution with push-to-talk functionality. Perfect for hands-free text input with real-time transcription.

![Voice Typing Demo](https://img.shields.io/badge/Status-Ready-green) ![Platform](https://img.shields.io/badge/Platform-Linux-blue) ![Debian](https://img.shields.io/badge/Tested-Debian%20Bookworm-red) ![License](https://img.shields.io/badge/License-Apache%202.0-orange)

## ✨ Features

### 🎯 **Push-to-Talk Interface**
- **Hotkey**: Hold `Left Shift + Left Alt` to record
- **Instant Transcription**: Fast, local processing with whisper.cpp
- **Smart Filtering**: Automatic removal of false positives and noise
- **Real-time Feedback**: Beautiful status indicators

### 🖥️ **System Tray Integration**
- **Beautiful Icons**: Microphone icons that change color by status
- **One-Click Control**: Simple start/pause toggle
- **Auto-startup**: Launches automatically on login
- **KDE Compatible**: Optimized for KDE Plasma desktop

### 🛡️ **Security & Privacy**
- **Local Processing**: All transcription happens locally
- **Input Sanitization**: Secure text filtering and validation
- **Configurable Endpoints**: No hardcoded server addresses
- **Minimal Permissions**: Runs with standard user privileges

### ⚡ **Performance**
- **Lightning Fast**: Types almost immediately after speaking
- **High Quality Audio**: 44.1kHz WAV recording for best accuracy
- **Resource Efficient**: Minimal CPU and memory usage
- **Reliable**: Comprehensive error handling and recovery

## 🚀 Quick Start

### Prerequisites

**Tested on Debian 12 (Bookworm)** - Should work on most modern Linux distributions.

```bash
# Install system dependencies
sudo apt install sox xinput python3-venv

# Install ydotool for typing simulation
sudo apt install ydotool

# Start ydotool daemon
sudo systemctl enable --now ydotoold
```

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd voice_typing
   ```

2. **Set up Python environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure your setup**
   ```bash
   cp config.env.example config.env
   # Edit config.env with your whisper server details
   ```

4. **Install system tray (optional)**
   ```bash
   cp voice-typing-tray.desktop ~/.config/autostart/
   cp voice-typing-tray.desktop ~/.local/share/applications/
   ```

### Whisper Server Setup

You need a running whisper.cpp server. Quick setup:

```bash
# Clone and build whisper.cpp
git clone https://github.com/ggerganov/whisper.cpp.git
cd whisper.cpp
make server

# Download a model
./models/download-ggml-model.sh base.en

# Start the server
./server -m models/ggml-base.en.bin -p 8080
```

## 🎮 Usage

### Command Line
```bash
./voice_client_ptt
```

### System Tray
```bash
./voice_tray_qt.py
```
- Right-click the tray icon to start/pause
- **Green**: Ready for input
- **Red**: Recording in progress
- **Blue**: Processing transcription
- **Gray**: Service stopped

### Recording Voice
1. Hold `Left Shift + Left Alt`
2. Speak clearly
3. Release keys to transcribe
4. Text appears instantly where your cursor is

## ⚙️ Configuration

Edit `config.env` to customize:

```bash
# Server Configuration
WHISPER_SERVER=http://localhost:8080

# Audio Settings
AUDIO_SAMPLE_RATE=44100
AUDIO_FORMAT=wav

# Keyboard Settings
KEYBOARD_NAME="Dell KB216 Wired Keyboard"
HOTKEY_1=50  # Left Shift
HOTKEY_2=64  # Left Alt

# Filtering
MIN_WORD_COUNT=2
MIN_CHAR_COUNT=6
```

## 📁 Project Structure

```
voice_typing/
├── voice_client_ptt          # Main push-to-talk script
├── voice_tray_qt.py          # System tray application
├── voice-typing-tray.desktop # Desktop entry for auto-start
├── config.env.example        # Configuration template
├── icons/                    # System tray icons
│   ├── tray_icon_ready.png
│   ├── tray_icon_recording.png
│   ├── tray_icon_processing.png
│   └── tray_icon_stopped.png
├── utils/                    # Utility scripts
└── Old/                      # Legacy versions
```

## 🔧 Troubleshooting

### Common Issues

**"No keyboard device found"**
- Update `KEYBOARD_NAME` in config.env
- List available keyboards: `xinput list | grep -i keyboard`

**"Connection refused"**
- Ensure whisper.cpp server is running
- Check `WHISPER_SERVER` URL in config.env
- Test with: `curl http://localhost:8080/health`

**"ydotool not working"**
- Start the daemon: `sudo systemctl start ydotoold`
- Add user to input group: `sudo usermod -a -G input $USER`

**"System tray not showing"**
- KDE: Enable system tray in panel settings
- Install Qt5: `sudo apt install python3-pyqt5`

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## 📄 License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## 🙏 Acknowledgments

- **whisper.cpp** - Fast local speech recognition
- **ydotool** - Wayland-compatible input simulation
- **PyQt5** - Cross-platform GUI toolkit
- **sox** - Audio processing utilities

---

**Made with ❤️ for the open source community**

*Fast • Secure • Private • Open Source*
