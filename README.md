# 🐾 EchoPaw: AI-Powered Therapeutic Companion for Dementia Care

**EchoPaw** is an AI companion system designed to help elderly dementia patients through natural conversation. Built for privacy and empathy, it runs entirely on your local computer without sending any data to the cloud.

## 🎯 What Does EchoPaw Do?

- **Natural Conversations**: Talk to EchoPaw like you would with a friend
- **Remembers Everything**: Stores personal memories and stories locally on your device
- **Completely Private**: No data ever leaves your computer - perfect for healthcare settings
- **Voice-Enabled**: Speaks back to you with realistic AI-generated voice
- **Therapeutic Focus**: Designed specifically for dementia care and cognitive support

## 🏥 The Problem We're Solving

In NHS hospitals, dementia patients occupy 25% of acute beds and stay 30-60 days (vs 16 days in Japan). EchoPaw aims to prevent cognitive decline during hospital stays, potentially reducing costs and improving patient outcomes.

## 🛠️ How It Works

EchoPaw combines four AI technologies:

1. **Speech-to-Text** (Whisper) - Understands what you say
2. **Memory System** (RAG) - Remembers your conversations and personal details
3. **Language Model** (Llama 3.2) - Generates caring, therapeutic responses
4. **Text-to-Speech** (Voice Cloning) - Speaks back with a warm, human-like voice

Everything runs locally on your computer for complete privacy.

## 🚀 Quick Start

### Prerequisites

- **Python 3.13+** 
- **32GB RAM** recommended (minimum 16GB)
- **GPU** optional but recommended (NVIDIA, Apple Silicon, or CPU fallback)
- **Microphone** for voice input

### Installation

1. **Clone the repository**
   ```bash
   git clone git@github.com:Shreyas8612/EchoPaw.git
   ```

2. **Install dependencies**
   ```bash
   # Using uv (recommended)
   uv sync

   # Or using pip
   pip install -r requirements.txt
   ```

3. **Test the system**
   ```bash
   python EchoPaw.py
   ```

### Running the Web Interface

For the best experience, use the web interface:

```bash
python Web.py
```

Then open your browser and go to: **http://localhost:5000**

The web interface provides:
- 🎤 Easy voice recording
- 💬 Clean chat interface  
- 📊 Memory statistics
- 🔊 Audio playback

## 💻 Usage Options

### Option 1: Web Interface (Recommended)
```bash
python Web.py
```
- Open http://localhost:5000 in your browser
- Click "Speak Now" to record audio
- EchoPaw will respond with both text and voice

### Option 2: Command Line
```bash
python EchoPaw.py
```
- Press Enter to record audio
- Type 'good-bye' to exit
- Say 'demo' to see memory system in action

### Option 3: Memory Demo
```bash
python RAG_demo.py
```
- See how EchoPaw stores and recalls memories
- Perfect for understanding the system capabilities

## 🧠 Memory System

EchoPaw automatically remembers:
- **Personal details** (family, pets, hobbies)
- **Important events** and stories
- **Preferences** and interests
- **Medical information** (if shared)

All memories are stored locally in the `memory/` folder and never leave your computer.

## 🎛️ Configuration

### Performance Optimization

**For NVIDIA GPUs:**
- CUDA acceleration enabled automatically
- Faster processing for real-time conversations

**For Apple Silicon (M1/M2/M3):**
- MPS acceleration for optimal performance
- Native ARM64 support

**For CPU-only systems:**
- Optimized for Intel/AMD processors
- Slightly slower but fully functional

### Voice Customization

The system uses Naomi Scott's voice by default. To use a different voice:

1. Replace `Naomi Scott.mp3` with your audio file
2. Update the text in `TTS.py` to match your audio content
3. Restart the system

## 📁 Project Structure

```
echopaw/
├── EchoPaw.py          # Main command-line interface
├── Web.py              # Web server and interface
├── Web.html            # Web UI (served automatically)
├── STT.py              # Speech-to-text (Whisper)
├── LLM.py              # Language model (Llama 3.2)
├── RAG.py              # Memory system
├── TTS.py              # Text-to-speech with voice cloning
├── RAG_demo.py         # Memory system demonstration
├── memory/             # Local memory storage (created automatically)
├── requirements.txt    # Python dependencies
└── README.md           # This file
```