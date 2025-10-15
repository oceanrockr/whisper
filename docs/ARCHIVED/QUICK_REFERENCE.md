# Quick Reference Card - Veleron Whisper Voice-to-Text

**One-page summary for fast access**

---

## 🚨 CRITICAL: First Thing to Do

**ffmpeg is NOT in PATH - You must restart your terminal!**

```bash
# After restarting, test:
ffmpeg -version

# If that fails, manually add to PATH:
# 1. Press Win+R, type: sysdm.cpl
# 2. Advanced → Environment Variables
# 3. System Variables → Path → Edit
# 4. Add: C:\Program Files\ffmpeg\bin
# 5. OK all dialogs → Restart terminal
```

---

## 🎯 What You Have

### **Three Applications**

| App | Purpose | How to Launch |
|-----|---------|---------------|
| **Veleron Dictation v2** | Real-time voice typing | `py veleron_dictation_v2.py` |
| Veleron Voice Flow | GUI file transcription | `py veleron_voice_flow.py` |
| Whisper to Office | CLI document creator | `py whisper_to_office.py file.mp3 --format word` |

---

## 🚀 Quick Start (After Fixing PATH)

### **Test Voice Dictation**

```bash
# 1. Open PowerShell in project folder
cd "c:\Users\noelj\Projects\Veleron Dev Studios\Applications\whisper"

# 2. Launch app
py veleron_dictation_v2.py

# 3. GUI window appears:
#    - Click "Test Microphone"
#    - Click and HOLD green button
#    - Speak: "This is a test"
#    - Release button
#    - Check log for transcription

# 4. Test typing:
#    - Open Notepad
#    - Click in Notepad
#    - Switch to Veleron Dictation window
#    - Hold green button
#    - Speak: "Hello World"
#    - Release
#    - Switch to Notepad
#    - Text should appear!
```

---

## 📋 Commands Reference

### **Launch Applications**
```bash
# Voice dictation (best UX)
py veleron_dictation_v2.py

# GUI transcription
py veleron_voice_flow.py

# Office integration
py whisper_to_office.py meeting.mp3 --format word
py whisper_to_office.py audio.mp3 --format powerpoint
py whisper_to_office.py recording.mp3 --format meeting
```

### **Testing**
```bash
# Test ffmpeg
ffmpeg -version

# Test Python
py --version

# Test Whisper installation
py -c "import whisper; print(whisper.__version__)"

# List audio devices
py -c "import sounddevice as sd; print(sd.query_devices())"
```

---

## 🔧 Dependencies Installed

```
✅ openai-whisper==20250625
✅ torch==2.8.0
✅ sounddevice==0.5.2
✅ soundfile==0.13.1
✅ pyautogui==0.9.54
✅ keyboard==0.13.5
✅ pystray==0.19.5
✅ Pillow==11.3.0
⚠️  ffmpeg (needs PATH restart)
```

---

## 📁 Project Structure

```
whisper/
├── veleron_dictation_v2.py    ⭐ Real-time dictation (START HERE)
├── veleron_voice_flow.py       📱 GUI app
├── whisper_to_office.py        📄 Office tool
├── docs/
│   ├── HANDOFF_PROMPT.md       📖 Next session guide
│   ├── DAILY_DEV_NOTES.md      📝 Development notes
│   ├── SESSION_SUMMARY.md      📊 Today's summary
│   └── QUICK_REFERENCE.md      ⚡ This file
├── DICTATION_README.md         📚 User guide
├── COMPARISON.md               📊 Feature comparison
└── START_DICTATION.bat         🚀 Quick launcher
```

---

## 🐛 Common Issues

### **"FileNotFoundError: ffmpeg"**
→ ffmpeg not in PATH. Restart terminal or manually add.

### **"No audio recorded"**
→ Click and HOLD button while speaking. Don't just click.

### **"Audio too short"**
→ Hold button for at least 0.5 seconds. Speak immediately.

### **Text doesn't appear in target app**
→ Make sure target window is active/focused after releasing button.

### **"Model not loaded"**
→ Wait for model to download (first time only, 139MB for base).

---

## 📊 Model Guide

| Model | Speed | Accuracy | Use Case |
|-------|-------|----------|----------|
| tiny | ⚡⚡⚡⚡⚡ | ⭐⭐ | Quick notes |
| base | ⚡⚡⚡⚡ | ⭐⭐⭐ | **Default** |
| small | ⚡⚡⚡ | ⭐⭐⭐⭐ | Better accuracy |
| medium | ⚡⚡ | ⭐⭐⭐⭐⭐ | Professional |
| turbo | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ | Best balance |

---

## ✅ Next Session Checklist

```
Day 2 (Tomorrow):
[ ] Fix ffmpeg PATH (5 min)
[ ] Test Veleron Dictation v2
    [ ] Test Microphone
    [ ] Record and transcribe
    [ ] Test typing into Notepad
    [ ] Test typing into Word
[ ] Test Veleron Voice Flow
    [ ] Record audio
    [ ] Transcribe file
    [ ] Export to TXT/JSON
[ ] Test Whisper to Office
    [ ] Word format
    [ ] PowerPoint format
    [ ] Meeting format
[ ] Document bugs in TEST_RESULTS.md
[ ] Fix critical bugs
[ ] Polish UI

Day 3:
[ ] Bug fixes based on testing
[ ] Performance optimization
[ ] Documentation updates

Day 4:
[ ] Internal beta release
[ ] Gather feedback

Day 5:
[ ] Final polish
[ ] Production release
```

---

## 📞 Getting Help

**Read Documentation:**
- Start: `docs/HANDOFF_PROMPT.md`
- Details: `DICTATION_README.md`
- Compare: `COMPARISON.md`

**Test Commands:**
- See "Commands Reference" above
- All commands are copy-paste ready

**Critical Issue:**
- ffmpeg PATH - restart terminal!

---

## 🎯 Success = MVP Complete

**Current Status**: 85% → Blocked by ffmpeg PATH

**After PATH Fix**: Ready for comprehensive testing!

**Timeline**:
- Fix PATH: 5 min
- Testing: 4-5 hours
- Bug fixes: 2-4 hours
- **Beta ready**: Tomorrow!

---

## 💡 Pro Tips

1. **Always restart terminal after PATH changes**
2. **Test Microphone button first** (verifies mic works)
3. **Start with base model** (fast enough, accurate enough)
4. **Hold button entire time** while speaking
5. **Click target window before recording** for best results

---

## 🚀 The Goal

**Replace typing with voice in:**
- Microsoft Word ✅
- Microsoft PowerPoint ✅
- Gmail / Outlook ✅
- Slack / Teams ✅
- VS Code ✅
- **ANY Windows application** ✅

**Status**: Code complete, needs testing!

---

**Last Updated**: 2025-10-12
**Version**: 1.0.0 (MVP)
**Status**: Ready for PATH fix → Testing → Beta

---

**Quick Start After PATH Fix:**
```bash
cd "c:\Users\noelj\Projects\Veleron Dev Studios\Applications\whisper"
py veleron_dictation_v2.py
# Click "Test Microphone"
# Hold green button and speak
# Magic happens! ✨
```
