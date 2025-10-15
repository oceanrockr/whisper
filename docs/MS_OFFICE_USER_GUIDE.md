# Veleron Dictation - MS Office User Guide

**Version:** 1.0
**Date:** October 14, 2025
**Author:** Veleron Dev Studios

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start Guide](#quick-start-guide)
4. [Using with Microsoft Office](#using-with-microsoft-office)
5. [Keyboard Shortcuts](#keyboard-shortcuts)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Features](#advanced-features)

---

## Overview

**Veleron Dictation** is a powerful voice-to-text system that allows you to dictate directly into Microsoft Word, PowerPoint, Excel, Outlook, and any other Windows application. It uses OpenAI's Whisper AI model for highly accurate transcription.

### Key Features

- **System-wide dictation** - Works in ANY Windows application
- **Push-to-talk hotkey** - Press Ctrl+Shift+Space to start/stop
- **High accuracy** - Powered by OpenAI Whisper AI
- **No internet required** - Runs completely offline
- **Multi-language support** - Supports 10+ languages
- **Real-time transcription** - Fast processing (typically under 2 seconds)
- **System tray integration** - Runs quietly in the background

---

## Installation

### Automatic Installation (Recommended)

1. **Open Veleron Voice Flow**
   - Launch `veleron_voice_flow.py` from your desktop or project folder

2. **Click "Install for MS Office" Button**
   - Located at the bottom of the main window

3. **Choose Installation Options**
   - ✓ Desktop Shortcut (recommended)
   - ✓ Start Menu Shortcut (recommended)
   - ✓ Quick Launch Batch File (recommended)
   - ✓ Silent Launcher (recommended)
   - ⚠ Windows Startup (optional - auto-start on boot)

4. **Click "Install"**
   - Shortcuts will be created automatically
   - Installation takes less than 5 seconds

5. **Launch Veleron Dictation**
   - Double-click the Desktop shortcut **OR**
   - Start Menu → Veleron Dev Studios → Veleron Dictation

### Manual Installation

If you prefer manual setup, you can run:

```powershell
python office_installer.py
```

To uninstall:

```powershell
python office_installer.py --uninstall
```

---

## Quick Start Guide

### Step 1: Launch Veleron Dictation

**Option A: Desktop Shortcut**
- Double-click "Veleron Dictation" on your desktop

**Option B: Batch File**
- Double-click `Launch_Veleron_Dictation.bat` in the project folder

**Option C: Silent Launch (No Console)**
- Double-click `Launch_Veleron_Dictation_Silent.vbs`

### Step 2: Verify It's Running

Look for the **microphone icon** in your system tray (bottom-right corner of Windows taskbar).

- **Red microphone** = Ready to record
- **Green microphone** = Currently recording

### Step 3: Open Microsoft Office

Open any Office application:
- Microsoft Word
- Microsoft PowerPoint
- Microsoft Excel
- Microsoft Outlook
- OneNote

**IMPORTANT:** Make sure Veleron Dictation is running BEFORE you start dictating.

### Step 4: Start Dictating

1. **Click in your document** where you want text to appear
2. **Press and HOLD Ctrl+Shift+Space**
3. **Speak clearly** into your microphone
4. **Release Ctrl+Shift+Space** when done speaking
5. **Wait 1-2 seconds** for transcription to appear

**That's it!** Your spoken words will be typed automatically into your document.

---

## Using with Microsoft Office

### Microsoft Word

**Best For:** Long-form documents, reports, letters, articles

**Tips:**
- Dictate one paragraph at a time (15-30 seconds per recording)
- Say punctuation: "comma", "period", "question mark", "exclamation point"
- Use manual formatting after dictation (bold, italics, etc.)
- Dictate headings separately for better formatting control

**Example Workflow:**
```
1. Open Word document
2. Click where you want to start typing
3. Press Ctrl+Shift+Space
4. "This is the introduction paragraph. It explains the main topic.
   We will cover three key points in this document."
5. Release Ctrl+Shift+Space
6. Text appears automatically!
```

### Microsoft PowerPoint

**Best For:** Slide content, speaker notes, bullet points

**Tips:**
- Dictate bullet points one at a time
- Use short, concise phrases (easier to format)
- Dictate speaker notes separately from slide content
- Great for rapid content generation during brainstorming

**Example Workflow:**
```
Slide Title Box:
  Ctrl+Shift+Space → "Benefits of Cloud Computing" → Release

Bullet Point 1:
  Ctrl+Shift+Space → "Scalability and flexibility" → Release

Bullet Point 2:
  Ctrl+Shift+Space → "Cost-effective infrastructure" → Release
```

### Microsoft Excel

**Best For:** Cell content, formulas (as text), notes

**Tips:**
- Click in a cell before dictating
- Dictate one cell at a time
- Use Tab or arrow keys to move between cells
- Better for text content than numbers

**Example Use Cases:**
- Product descriptions
- Customer notes
- Meeting notes in cells
- Comment fields

### Microsoft Outlook

**Best For:** Emails, calendar entries, contact notes

**Tips:**
- Compose emails faster with dictation
- Dictate subject lines, email bodies, meeting notes
- Great for hands-free email responses
- Perfect for quick voice memos

**Example Email Workflow:**
```
Subject Line:
  Ctrl+Shift+Space → "Follow-up from today's meeting" → Release

Email Body:
  Ctrl+Shift+Space → "Hi team, thank you for attending today's meeting.
  Here are the action items we discussed. Please review and let me know
  if you have any questions." → Release
```

---

## Keyboard Shortcuts

### Global Hotkeys (Work Anywhere)

| Shortcut | Action |
|----------|--------|
| **Ctrl+Shift+Space** | Start/Stop recording (push-to-talk) |
| **Right-click tray icon** | Open menu (Settings, Exit) |

### Status Indicators

| Icon Color | Status |
|------------|--------|
| 🔴 Red | Ready to record |
| 🟢 Green | Currently recording |
| ⚪ Gray | Processing/Transcribing |

---

## Best Practices

### For Best Accuracy

1. **Use a good microphone**
   - USB microphones work best
   - Webcam microphones work well (like Logitech C922)
   - Bluetooth headsets may have latency issues

2. **Speak clearly and naturally**
   - Don't shout or whisper
   - Natural conversational pace is best
   - Pause briefly between sentences

3. **Minimize background noise**
   - Close windows to reduce street noise
   - Turn off fans or air conditioning when recording
   - Quiet room = better accuracy

4. **Optimal recording length**
   - **Best:** 5-15 seconds per recording
   - **Good:** 15-30 seconds
   - **Avoid:** Over 60 seconds (split into multiple recordings)

### Punctuation and Formatting

**Whisper AI automatically adds:**
- Periods at end of sentences
- Commas in appropriate places
- Basic capitalization

**You may need to manually add:**
- Question marks (say "question mark" or add manually)
- Exclamation points (say "exclamation point" or add manually)
- Quotation marks
- Paragraph breaks
- Bold, italics, underline formatting

### Workflow Optimization

**Recommended Workflow:**
1. **Dictate content first** (don't worry about perfect formatting)
2. **Review and edit** (check for accuracy)
3. **Format second** (apply styles, bold, italics, etc.)
4. **Proofread final** (check spelling, grammar, flow)

**Don't try to:**
- Format while dictating
- Say punctuation for every mark
- Dictate very long passages (break into chunks)

---

## Troubleshooting

### "Veleron Dictation is not responding"

**Solution:**
1. Check system tray - is the icon still there?
2. If missing, restart Veleron Dictation
3. Test with Notepad first (simpler app)

### "No text appears when I dictate"

**Possible Causes:**

1. **Not holding hotkey**
   - Make sure you HOLD Ctrl+Shift+Space while speaking
   - Release AFTER you finish speaking

2. **Cursor not in text field**
   - Click in your document where you want text
   - Make sure the cursor is blinking

3. **Microphone not working**
   - Test your microphone in Windows Sound Settings
   - Try refreshing devices in Veleron Voice Flow

4. **Wrong window focused**
   - Click in your Office document to make it active
   - Dictation types into the ACTIVE window only

### "Text appears in wrong location"

**Solution:**
- Always click where you want text BEFORE dictating
- Veleron Dictation types at your cursor position
- It doesn't know where you want text - you must position the cursor

### "Accuracy is poor"

**Troubleshooting Steps:**

1. **Check microphone**
   - Test in Windows Sound Settings
   - Is input level too low or too high?
   - Try a different microphone

2. **Reduce background noise**
   - Close door/window
   - Turn off fans
   - Move away from noisy computers

3. **Check microphone position**
   - Position 6-12 inches from mouth
   - Point directly at your mouth
   - Not too close (causes distortion)

4. **Try larger Whisper model**
   - Open Veleron Voice Flow
   - Change Model from "base" → "small" or "medium"
   - Larger models = better accuracy (but slower)

### "Dictation is too slow"

**Solutions:**

1. **Use smaller Whisper model**
   - "tiny" = fastest (lower accuracy)
   - "base" = balanced (recommended)
   - "small" = slower but more accurate

2. **Close other applications**
   - Whisper requires CPU resources
   - Close Chrome, heavy apps

3. **Record shorter clips**
   - 5-10 second recordings process faster
   - Long recordings take more time

---

## Advanced Features

### Multi-Language Support

Veleron Dictation supports 10+ languages:

| Language | Code | Example |
|----------|------|---------|
| English | en | Default |
| Spanish | es | "Hola, ¿cómo estás?" |
| French | fr | "Bonjour, comment allez-vous?" |
| German | de | "Guten Tag, wie geht es Ihnen?" |
| Italian | it | "Ciao, come stai?" |
| Portuguese | pt | "Olá, como está?" |
| Dutch | nl | "Hallo, hoe gaat het?" |
| Japanese | ja | "こんにちは" |
| Korean | ko | "안녕하세요" |
| Chinese | zh | "你好" |

**To use:**
1. Speak in your target language
2. Whisper auto-detects language
3. Transcription appears in that language

### Custom Hotkey (Advanced)

**Default:** Ctrl+Shift+Space

To change the hotkey, edit `veleron_dictation.py`:

```python
# Line 52: Change the hotkey
HOTKEY = "ctrl+shift+space"  # Change this line
```

**Examples:**
- `"ctrl+shift+d"` = Ctrl+Shift+D
- `"ctrl+alt+v"` = Ctrl+Alt+V
- `"f12"` = F12 key

**Restart Veleron Dictation** after changing.

### Running at Startup

**Option 1: During Installation**
- Check "Add to Windows Startup" when installing

**Option 2: Manual**
1. Press Win+R
2. Type: `shell:startup`
3. Press Enter
4. Copy "Veleron Dictation" shortcut into this folder

### Using with Other Applications

Veleron Dictation works with **ANY Windows application** that accepts text input:

- Notepad, Notepad++
- Google Docs (in Chrome)
- Visual Studio Code
- Slack, Discord, Teams
- Email clients
- Web forms
- Any text editor

**Same hotkey:** Ctrl+Shift+Space works everywhere!

---

## Frequently Asked Questions

### Q: Does this require internet?

**A:** No! Veleron Dictation runs completely offline. Your voice data never leaves your computer.

### Q: How accurate is the transcription?

**A:** With a good microphone in a quiet environment:
- Base model: 95%+ accuracy for clear English
- Small model: 97%+ accuracy
- Medium model: 98%+ accuracy

### Q: Can I use this for medical/legal dictation?

**A:** Yes, but always proofread carefully. While accuracy is high, this is not certified for medical/legal use. Review all transcriptions before finalizing documents.

### Q: Does this work with Microsoft 365 (cloud)?

**A:** Yes! It works with both desktop Office and Office 365. The dictation happens on your local computer, regardless of where your documents are stored.

### Q: Can multiple people use this on the same computer?

**A:** Yes, but train each person to speak clearly. Whisper adapts to different voices automatically.

### Q: How do I uninstall?

**A:** Run: `python office_installer.py --uninstall`

This removes all shortcuts and startup entries.

---

## Support

### Getting Help

**Check logs:**
1. Open Veleron Voice Flow
2. Click "View Logs" button
3. Look for error messages

**Common issues:**
- See [Troubleshooting](#troubleshooting) section above

**Report bugs:**
- Contact Veleron Dev Studios support
- Include log files when reporting issues

### System Requirements

- **OS:** Windows 10/11 (64-bit)
- **Python:** 3.8 or higher
- **RAM:** 4GB minimum, 8GB recommended
- **CPU:** Multi-core processor recommended
- **Microphone:** Any USB or built-in microphone

---

## Version History

### Version 1.0 (October 14, 2025)
- Initial release
- MS Office integration
- DirectSound fallback for USB devices
- System tray integration
- Push-to-talk hotkey support

---

## License

**Internal Use Only**
© 2025 Veleron Dev Studios

---

**Need more help?** Contact Veleron Dev Studios support or check the project README for technical documentation.

**Happy Dictating!** 🎤✨
