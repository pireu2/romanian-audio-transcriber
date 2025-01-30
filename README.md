# Romanian Audio Transcriber 🎙️➡️📝

A desktop application for transcribing Romanian audio files to text using whisper.cpp and FFmpeg. Works **100% offline** .

![App Screenshot](media/screenshot.png)

## 📑 Table of Contents

- [Project Structure](#-project-structure)
- [Key Features](#-key-features)
- [Prerequisites](#-prerequisites)
- [Installation & Build](#-installation--build)
- [Model Management](#-model-management)
- [Usage Guide](#-usage-guide)
- [Deployment](#-deployment)
- [TODO](#-todo)
- [License](#-license)

## 📂 Project Structure

`romanian-audio-transcriber`

- `main.py` - Main entry point of the application
- `transcriber.py` - Core transcription logic (Transcriber class) and tkinter GUI
- `vendor/ffmpeg/ffmpeg` - FFmpeg binaries for audio processing
- `whisper.cpp` - C++ implementation of OpenAi's whisper model
- `package.spec` - PyInstaller configuration file
- `requrements.txt` - Python dependencies list

## 🎯 Key Features

- Romanian Language Focus 🇷🇴 -
  Optimized for Romanian speech patterns and diacritics

- Offline Operation 🔒 -
  No internet connection required post-installation

- Long Audio Support ⏳ -
  Handles files up to 3+ hours efficiently

- Custom Model Support 🧠 -
  Easily swap between different whisper.cpp models

- Audio Preprocessing 🔊 -
  Built-in noise reduction and audio normalization

## 🛠️ Prerequisites

- **CMake 3.25+** (Required for building whisper.cpp)
- Python 3.12+
- Ffmpeg (if on Linux)
- C++ Compiler:
  - Windows: Visual Studio Build Tools
  - Linux: gcc/g++
  - macOS: Xcode Command Line Tools

## 🚀 Installation & Build

```bash
# 1. Clone with submodules
git clone --recurse-submodules https://github.com/pireu2/romanian-audio-transcriber.git
cd romanian-audio-transcriber

# 3. Install Python dependencies if you want to deploy the application
pip install -r requirements.txt

# 4. Run application
# If whisper is not built or the model is not downloaded you will be prompted to build/download
python main.py
```

## 🔧 Model Management

Default Model Configuration

```python
#transcriber.py
MODEL_CONFIG = {
    "name": "base",
    "language": "ro",
}
```

The model can be changed to one of the following:

- tiny.en
- tiny
- base.en
- base
- small.en
- small
- medium.en
- medium
- large-v1
- large-v2
- large-v3
- large-v3-turbo

Bigger models have more accuracity but they are slower at transcribing, the base one has a nice ballance.

## 📝 Usage Guide

- Select audio file (.mp3, .wav, .ogg)
- Choose output path (default: same as input)
- Click "Transcribe"
- Review/edit text in your default editor

## 📦 Deployment

Create standalone executable:

```bash

pyinstaller package.spec
```

Output executable located in /dist with:

- Complete Romanian language support
- Embedded FFmpeg binaries
- Selected whisper.cpp model

## ✅ TODO

- <input disabled="" type="checkbox"> Add more unit tests for the transcription logic
- <input disabled="" type="checkbox"> Implement performance testing for long audio files
- <input disabled="" type="checkbox"> Explore GPU implementation for faster transcription
- <input disabled="" type="checkbox"> Improve error handling and user feedback
- <input disabled="" type="checkbox"> Add a progress bar for the transcription process
- <input disabled="" type="checkbox"> Create a detailed user manual

## 📜 License

MIT License - See [LICENSE](LICENSE)
