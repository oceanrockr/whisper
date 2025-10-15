# Veleron Dictation - Real-Time Voice-to-Text System

**System-wide voice dictation that replaces typing with speech**

Transform your voice into text in **any application** - Word, PowerPoint, Notepad, email, chat, code editors, and more!

---

## 🎯 What It Does

**Veleron Dictation** is a **push-to-talk** voice typing system that works like this:

1. Press and hold `Ctrl+Shift+Space` (configurable)
2. Speak naturally
3. Release the hotkey
4. Text appears instantly in your active window!

Works in:
- ✅ Microsoft Word
- ✅ Microsoft PowerPoint
- ✅ Microsoft Outlook
- ✅ Notepad / Notepad++
- ✅ VS Code
- ✅ Chrome / Edge (Gmail, Google Docs, etc.)
- ✅ Slack, Teams, Discord
- ✅ **Any application with a text field!**

---

## 🚀 Key Features

### Real-Time Dictation
- **Push-to-talk**: Press hotkey, speak, release = instant text
- **System-wide**: Works in ANY Windows application
- **Low latency**: Types text within 1-2 seconds
- **100% local**: No cloud, all processing on your machine

### Smart Features
- **Auto-punctuation**: Whisper adds periods, commas, etc.
- **Multi-language**: Supports 100+ languages
- **Model selection**: Choose speed vs accuracy
- **Always available**: Runs in system tray

### Privacy & Control
- **Offline**: Works without internet (after model download)
- **Private**: Audio never leaves your computer
- **Customizable**: Change models, languages, hotkeys

---

## 📦 Installation

### Step 1: Install Dependencies

```bash
cd "c:\Users\noelj\Projects\Veleron Dev Studios\Applications\whisper"
py -m pip install -r dictation_requirements.txt
```

### Step 2: Verify Installation

Check that these are installed:
- ✅ openai-whisper
- ✅ pyautogui (keyboard typing)
- ✅ keyboard (hotkey detection)
- ✅ sounddevice (audio recording)
- ✅ pystray (system tray icon)

### Step 3: Run Administrator (Important!)

The `keyboard` library requires **administrator privileges** to capture global hotkeys:

**Windows:**
1. Right-click on Command Prompt or PowerShell
2. Select "Run as Administrator"
3. Navigate to the whisper directory
4. Run: `py veleron_dictation.py`

---

## 🎮 How to Use

### Basic Usage

1. **Start the application**:
   ```bash
   py veleron_dictation.py
   ```

2. **Wait for model to load**:
   - First time: Downloads model (139MB for base)
   - Status window shows "Ready"

3. **Click in any text field** (Word, email, etc.)

4. **Press and HOLD `Ctrl+Shift+Space`**

5. **Speak clearly**: "Hello, this is a test of voice dictation."

6. **Release the hotkey**

7. **Watch the text appear!** ✨

### Advanced Usage

**Change Model (Speed vs Accuracy):**
1. Click "Settings" in status window
2. Select model:
   - `tiny` / `tiny.en`: Fastest (1-2 sec)
   - `base` / `base.en`: Good balance (2-3 sec) ⭐ **Default**
   - `small` / `small.en`: Better accuracy (3-5 sec)
   - `medium`: Professional quality (5-8 sec)
   - `turbo`: Best quality (3-4 sec)

**Change Language:**
1. Click "Settings"
2. Select language or keep "auto" for detection

**Minimize to System Tray:**
- Close status window → runs in background
- Click tray icon → show status window

---

## ⌨️ Hotkey Guide

### Default Hotkey
- **`Ctrl+Shift+Space`**: Start/stop recording

### How It Works
- **Press and hold**: Starts recording (red status)
- **Release**: Stops recording and transcribes
- **Push-to-talk**: Like a walkie-talkie!

### Tips
- Hold hotkey for entire sentence/paragraph
- Don't release until you're done speaking
- Pause briefly before releasing for better accuracy

---

## 💡 Usage Tips

### For Best Results

**Speaking:**
- ✅ Speak naturally at normal pace
- ✅ Use complete sentences
- ✅ Pause briefly between sentences
- ❌ Don't speak too fast
- ❌ Don't whisper or shout

**Environment:**
- ✅ Use in quiet environment
- ✅ Good quality microphone helps
- ❌ Minimize background noise

**Model Selection:**
- `tiny/base`: Quick notes, casual use
- `small`: Regular documents
- `medium/turbo`: Important documents, presentations
- `.en` models: Use for English-only (more accurate)

### Punctuation

Whisper adds punctuation automatically! You don't need to say "comma" or "period".

**Example:**
- Say: "Hello world this is amazing"
- Types: "Hello world, this is amazing."

### Common Use Cases

**Email Writing:**
1. Open Gmail/Outlook
2. Click in compose box
3. Hold hotkey and dictate email
4. Edit as needed

**Document Creation:**
1. Open Word
2. Hold hotkey and dictate paragraphs
3. Release between paragraphs
4. Quick editing with keyboard

**Code Comments:**
1. Open VS Code
2. Position cursor in comment
3. Dictate comment text
4. Works great for documentation!

**Meeting Notes:**
1. Open Notepad/Word
2. During meeting, hold hotkey
3. Speak key points
4. Instant notes!

---

## 🔧 Configuration

### Settings Window

Access via:
- Status window → "Settings" button
- System tray → "Settings"

**Available Settings:**

| Setting | Options | Recommended |
|---------|---------|-------------|
| Model | tiny, base, small, medium, turbo | base |
| Language | auto, en, es, fr, de, etc. | auto |
| Hotkey | Currently: Ctrl+Shift+Space | - |

### Model Comparison

| Model | Speed | Accuracy | RAM | Best For |
|-------|-------|----------|-----|----------|
| tiny | ⚡⚡⚡⚡⚡ | ⭐⭐ | 1GB | Quick notes |
| tiny.en | ⚡⚡⚡⚡⚡ | ⭐⭐⭐ | 1GB | English notes |
| base | ⚡⚡⚡⚡ | ⭐⭐⭐ | 1GB | General use |
| base.en | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ | 1GB | English docs |
| small | ⚡⚡⚡ | ⭐⭐⭐⭐ | 2GB | Documents |
| medium | ⚡⚡ | ⭐⭐⭐⭐⭐ | 5GB | Professional |
| turbo | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | 6GB | Best balance |

---

## 🆚 Comparison with Commercial Products

### vs. Wispr Flow

| Feature | Wispr Flow | Veleron Dictation |
|---------|-----------|-------------------|
| **Price** | $12-24/month | FREE |
| **Privacy** | Cloud-based | 100% Local |
| **Offline** | ❌ No | ✅ Yes |
| **Model Choice** | Fixed | 6+ options |
| **Customizable** | ❌ No | ✅ Full source |
| **Real-time Typing** | ✅ Yes | ✅ Yes |
| **System-wide** | ✅ Yes | ✅ Yes |
| **Multi-language** | ✅ Yes | ✅ Yes |

### vs. Windows Speech Recognition

| Feature | Windows Speech | Veleron Dictation |
|---------|---------------|-------------------|
| **Accuracy** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Languages** | Limited | 100+ |
| **Training Required** | ✅ Yes | ❌ No |
| **Offline** | ✅ Yes | ✅ Yes |
| **Push-to-talk** | ❌ No | ✅ Yes |
| **Modern AI** | ❌ No | ✅ Yes |

### vs. Dragon NaturallySpeaking

| Feature | Dragon | Veleron Dictation |
|---------|--------|-------------------|
| **Price** | $300+ | FREE |
| **Setup** | Complex | Simple |
| **Accuracy** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Training** | Required | None |
| **Speed** | Fast | Fast |

---

## 🛠️ Troubleshooting

### Hotkey Not Working

**Problem**: Pressing Ctrl+Shift+Space doesn't record

**Solutions:**
1. ✅ Run as Administrator (required!)
2. ✅ Check if another app uses same hotkey
3. ✅ Verify status window shows "Ready"
4. ✅ Restart application

### Text Not Appearing

**Problem**: Text doesn't type into application

**Solutions:**
1. ✅ Click in text field BEFORE pressing hotkey
2. ✅ Ensure application window is focused
3. ✅ Try in Notepad first (test if it works)
4. ✅ Some apps may block automation (rare)

### Poor Transcription Quality

**Problem**: Text is inaccurate

**Solutions:**
1. ✅ Use larger model (medium/turbo)
2. ✅ Speak more clearly
3. ✅ Reduce background noise
4. ✅ Use `.en` model for English
5. ✅ Check microphone quality

### "Audio too short" Error

**Problem**: Gets "Audio too short" message

**Solutions:**
1. ✅ Hold hotkey longer (at least 0.5 seconds)
2. ✅ Speak immediately after pressing
3. ✅ Check microphone is working

### Application Crashes

**Problem**: Application closes unexpectedly

**Solutions:**
1. ✅ Ensure all dependencies installed
2. ✅ Check Python version (3.8+)
3. ✅ Verify ffmpeg is in PATH
4. ✅ Run from terminal to see errors

### High CPU/RAM Usage

**Problem**: Computer slows down

**Solutions:**
1. ✅ Use smaller model (tiny/base)
2. ✅ Close other applications
3. ✅ Ensure adequate RAM (4GB+ recommended)

---

## 📋 System Requirements

### Minimum Requirements
- **OS**: Windows 10/11 (with admin rights)
- **CPU**: Dual-core processor
- **RAM**: 4GB (for tiny/base models)
- **Storage**: 2GB free
- **Microphone**: Any USB or built-in mic

### Recommended Requirements
- **OS**: Windows 11
- **CPU**: Quad-core processor
- **RAM**: 8GB+ (for medium/turbo models)
- **Storage**: 10GB free
- **Microphone**: USB microphone or headset
- **GPU**: NVIDIA GPU with CUDA (optional, for faster processing)

---

## 🔐 Privacy & Security

### Data Privacy
- ✅ **100% Local**: All processing on your machine
- ✅ **No Network**: Audio never uploaded anywhere
- ✅ **No Logging**: No transcripts saved unless you export
- ✅ **No Telemetry**: No usage data collected

### Security
- ⚠️ **Admin Rights**: Required for global hotkeys
- ✅ **Open Source**: Full source code available
- ✅ **Auditable**: Review all code
- ✅ **No External Dependencies**: No cloud APIs

---

## 🚀 Future Enhancements

### Planned Features (v2.0)
- [ ] Custom hotkey configuration
- [ ] Multiple hotkey profiles
- [ ] Voice commands (undo, delete, format)
- [ ] Real-time streaming (type as you speak)
- [ ] Custom vocabulary/names
- [ ] Context-aware formatting
- [ ] Integration with popular apps
- [ ] Auto-capitalization rules
- [ ] Speaker diarization
- [ ] Macro support

### Potential Improvements
- [ ] GPU acceleration for faster transcription
- [ ] Smaller model sizes (compressed)
- [ ] Background noise reduction
- [ ] Echo cancellation
- [ ] Multiple language detection
- [ ] Emoji insertion by voice

---

## 🤝 Support

**Internal Support**: Contact Veleron Dev Studios

**Common Issues**: See Troubleshooting section above

**Feature Requests**: Submit to development team

---

## 📄 License

**Internal Use Only** - Veleron Dev Studios

Built with:
- OpenAI Whisper (MIT License)
- Python open-source libraries

---

## 📚 Additional Resources

### Related Files
- `veleron_dictation.py` - Main application
- `dictation_requirements.txt` - Dependencies
- `veleron_voice_flow.py` - Alternative GUI version
- `whisper_to_office.py` - Office integration tool

### Documentation
- [Whisper Official Docs](https://github.com/openai/whisper)
- [PyAutoGUI Docs](https://pyautogui.readthedocs.io/)

---

**Version**: 1.0.0
**Last Updated**: 2025-10-12
**Author**: Veleron Dev Studios

---

## Quick Start Summary

```bash
# 1. Install dependencies
py -m pip install -r dictation_requirements.txt

# 2. Run as administrator
# Right-click PowerShell → "Run as Administrator"

# 3. Start application
cd "c:\Users\noelj\Projects\Veleron Dev Studios\Applications\whisper"
py veleron_dictation.py

# 4. Wait for "Ready" message

# 5. Click in any text field

# 6. Hold Ctrl+Shift+Space, speak, release

# 7. Enjoy voice typing! 🎉
```
