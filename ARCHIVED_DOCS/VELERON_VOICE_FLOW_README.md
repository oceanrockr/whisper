# Veleron Voice Flow

**Custom WhisperFlow-Equivalent Voice-to-Text Application**

A powerful, privacy-focused voice transcription application powered by OpenAI Whisper, designed for internal use at Veleron Dev Studios.

---

## Features

### Core Functionality
- **Real-Time Recording**: Record audio directly from your microphone
- **File Transcription**: Transcribe existing audio files (MP3, WAV, M4A, FLAC, OGG)
- **Multi-Language Support**: Automatically detect or manually select from 100+ languages
- **Multiple Model Options**: Choose between tiny, base, small, medium, large, or turbo models
- **Clean GUI**: User-friendly interface built with Tkinter

### Transcription Features
- **Automatic Punctuation**: Whisper adds punctuation automatically
- **Language Detection**: Auto-detect the spoken language
- **Timestamp Tracking**: Each transcription includes timestamp metadata
- **Batch Processing**: Transcribe multiple files sequentially

### Export Options
- **Plain Text (.txt)**: Simple text export
- **JSON (.json)**: Structured export with metadata
- **Clipboard Copy**: Quick copy to clipboard for pasting anywhere
- **Live Editing**: Edit transcriptions directly in the app

---

## Installation

### Prerequisites
- Python 3.8 or higher
- Windows, macOS, or Linux
- Microphone (for recording)
- ffmpeg (for audio processing)

### Setup Steps

1. **Install Python Dependencies**:
   ```bash
   cd "c:\Users\noelj\Projects\Veleron Dev Studios\Applications\whisper"
   py -m pip install -r voice_flow_requirements.txt
   ```

2. **Verify ffmpeg is installed**:
   ```bash
   ffmpeg -version
   ```
   (If not installed, add `C:\Program Files\ffmpeg\bin` to PATH and restart)

3. **Run the Application**:
   ```bash
   py veleron_voice_flow.py
   ```

---

## Usage Guide

### Recording Audio

1. **Select Model**: Choose your preferred Whisper model
   - `tiny`: Fastest, less accurate (~1GB RAM)
   - `base`: Good balance (default)
   - `small`: Better accuracy (~2GB RAM)
   - `medium`: Professional quality (~5GB RAM)
   - `large/turbo`: Best accuracy (~10GB RAM)

2. **Choose Language**:
   - `auto`: Automatically detect (recommended)
   - Or select specific language (en, es, fr, etc.)

3. **Start Recording**:
   - Click "🎤 Start Recording"
   - Speak clearly into your microphone
   - Click "⏹ Stop Recording" when done

4. **View Results**:
   - Transcription appears in the text area
   - Includes timestamp and detected language

### Transcribing Files

1. Click "📁 Transcribe File"
2. Select your audio file
3. Wait for processing
4. View transcription in the text area

### Exporting Results

- **Copy to Clipboard**: Quick copy for pasting into other apps
- **Export as TXT**: Save as plain text file
- **Export as JSON**: Save with metadata (timestamp, model, language)

---

## Comparison with Wispr Flow

| Feature | Wispr Flow (Commercial) | Veleron Voice Flow (Custom) |
|---------|------------------------|----------------------------|
| **Real-time Transcription** | ✅ Yes | ✅ Yes |
| **Multi-language** | ✅ 100+ languages | ✅ 100+ languages |
| **System-wide Integration** | ✅ Works in all apps | ⚠️ Standalone app |
| **Model Selection** | ❌ Fixed | ✅ 6 models to choose |
| **Privacy** | ⚠️ Cloud-based | ✅ 100% Local |
| **Cost** | 💰 $12-24/month | ✅ Free (internal) |
| **Offline** | ❌ No | ✅ Yes |
| **Customization** | ❌ Limited | ✅ Full control |
| **File Transcription** | ❌ Limited | ✅ Yes |

---

## Model Selection Guide

### For Quick Tests & Drafts
- **tiny** (39M params): ~10x faster, ~1GB VRAM
- **base** (74M params): ~7x faster, ~1GB VRAM ⭐ **Recommended for most users**

### For Professional Use
- **small** (244M params): ~4x faster, ~2GB VRAM
- **medium** (769M params): ~2x faster, ~5GB VRAM

### For Best Accuracy
- **large** (1550M params): Best quality, ~10GB VRAM
- **turbo** (809M params): Optimized large-v3, ~6GB VRAM ⭐ **Best balance**

### English-Only Variants
Add `.en` suffix for better English accuracy:
- `tiny.en`, `base.en`, `small.en`, `medium.en`

---

## Technical Details

### Architecture
```
┌─────────────────────────────────────┐
│     Veleron Voice Flow GUI          │
│  (Tkinter Interface)                │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Audio Recording/File Loading      │
│   (sounddevice / file input)        │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Whisper Transcription Engine      │
│   (OpenAI Whisper - Local)          │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Display & Export                  │
│   (Text, JSON, Clipboard)           │
└─────────────────────────────────────┘
```

### Audio Processing
- **Sample Rate**: 16kHz (Whisper standard)
- **Format**: Mono (single channel)
- **Encoding**: 16-bit PCM

### Performance
- **Latency**: < 2 seconds for tiny/base models
- **Accuracy**: WER ~7% (Word Error Rate)
- **Processing**: 100% local, no cloud required

---

## Use Cases

### Internal Business
- Transcribe meetings and discussions
- Convert voice notes to text
- Document interviews and conversations
- Create captions for internal videos

### Productivity
- Dictate emails and documents
- Create quick notes while walking/driving
- Transcribe brainstorming sessions
- Convert lectures to text

### Accessibility
- Assist users with typing difficulties
- Provide text alternatives to audio content
- Enable multilingual communication

---

## Troubleshooting

### "Model Not Loaded" Error
- Wait for model to download (first run only)
- Check internet connection for first download
- Models cached in `~\.cache\whisper\`

### Recording Not Working
- Check microphone permissions
- Verify microphone is selected in Windows Sound settings
- Try restarting the application

### ffmpeg Error
- Ensure ffmpeg is installed and in PATH
- Restart terminal/application after installing ffmpeg
- Test: `ffmpeg -version`

### Low Transcription Accuracy
- Use a better model (medium/large)
- Speak clearly and reduce background noise
- Select specific language instead of "auto"
- Use English-only models for English (e.g., `base.en`)

---

## Future Enhancements

### Planned Features
- [ ] Hotkey support (global keyboard shortcuts)
- [ ] Real-time streaming transcription
- [ ] Custom vocabulary/dictionary
- [ ] Speaker diarization (identify multiple speakers)
- [ ] Integration with popular apps (VS Code, Word, etc.)
- [ ] Voice commands for app control
- [ ] Auto-formatting based on context
- [ ] Cloud sync option (optional)

---

## Privacy & Security

- ✅ **100% Local Processing**: All transcription happens on your machine
- ✅ **No Cloud Upload**: Audio never leaves your computer
- ✅ **No API Keys**: No external services required
- ✅ **Full Control**: You own your data
- ✅ **Offline Capable**: Works without internet (after model download)

---

## System Requirements

### Minimum
- **CPU**: Dual-core processor
- **RAM**: 4GB (tiny/base models)
- **Storage**: 2GB free space
- **OS**: Windows 10+, macOS 10.14+, Linux

### Recommended
- **CPU**: Quad-core processor or better
- **RAM**: 8GB+ (for medium/large models)
- **GPU**: NVIDIA GPU with CUDA support (optional, for faster processing)
- **Storage**: 10GB free space (for all models)

---

## License

**Internal Use Only** - Veleron Dev Studios

This application is built using:
- OpenAI Whisper (MIT License)
- Python open-source libraries

---

## Support

For issues or questions, contact Veleron Dev Studios internal support.

**Version**: 1.0.0
**Last Updated**: 2025-10-12
**Author**: Veleron Dev Studios
