# 🚀 Veleron Voice Flow - Launcher Guide
**Date:** October 12, 2025

---

## ✅ Application Launched!

The Veleron Voice Flow application is now running! You should see the application window with the new **Microphone selection dropdown**.

---

## 🎯 Quick Actions

### To Use the App Right Now:

1. **Look for the Microphone dropdown** (second row of Controls panel)
2. **Select:** `12: Microphone (C922 Pro Stream Webcam)`
3. **Click:** "🎤 Start Recording"
4. **Watch:** Your webcam LED should turn ON! 💡
5. **Speak:** Clearly for 5-10 seconds
6. **Click:** "⏹ Stop Recording"
7. **Check:** Transcription appears!

---

## 📁 Shortcuts Created

I've created **3 ways** to launch Veleron Voice Flow:

### 1. Desktop Shortcut ⭐ (Easiest!)

**Location:** Your Desktop
**Name:** "Veleron Voice Flow.lnk"
**Icon:** Microphone icon 🎤

**How to use:**
- Just **double-click** the shortcut on your desktop!
- That's it! The app launches with console window.

✅ **Already created and ready to use!**

### 2. Batch File Launcher (In Project Folder)

**Location:** `c:\Users\noelj\Projects\Veleron Dev Studios\Applications\whisper\`
**Name:** `Launch_Voice_Flow.bat`

**How to use:**
- Navigate to the project folder
- Double-click `Launch_Voice_Flow.bat`
- Shows console window with logs (useful for debugging)

**Features:**
- Shows console output (device detection, logs, errors)
- Good for troubleshooting
- Automatically uses `py` or `python` command

### 3. Silent Launcher (No Console)

**Location:** `c:\Users\noelj\Projects\Veleron Dev Studios\Applications\whisper\`
**Name:** `Launch_Voice_Flow_Silent.vbs`

**How to use:**
- Double-click `Launch_Voice_Flow_Silent.vbs`
- Launches app **without console window** (cleaner)

**Features:**
- No console window (cleaner desktop)
- Silent launch
- Good for regular use when you don't need logs

---

## 🔧 Recreating Desktop Shortcut

If you need to recreate the desktop shortcut (or create one on another computer):

### Option 1: Run PowerShell Script

```powershell
cd "c:\Users\noelj\Projects\Veleron Dev Studios\Applications\whisper"
powershell -ExecutionPolicy Bypass -File Create_Desktop_Shortcut.ps1
```

✅ Shortcut will be created on your desktop!

### Option 2: Manual Method

1. Right-click on `Launch_Voice_Flow.bat`
2. Select "Create shortcut"
3. Drag the shortcut to your Desktop
4. Right-click shortcut → Properties
5. Click "Change Icon"
6. Browse to: `C:\Windows\System32\imageres.dll`
7. Select microphone icon (around icon #190)
8. Click OK

---

## 📂 All Launcher Files

| File | Type | Purpose | Shows Console? |
|------|------|---------|----------------|
| **Desktop: "Veleron Voice Flow"** | Shortcut | Quick desktop access | ✅ Yes |
| `Launch_Voice_Flow.bat` | Batch | Launch with console | ✅ Yes |
| `Launch_Voice_Flow_Silent.vbs` | VBScript | Launch without console | ❌ No |
| `Create_Desktop_Shortcut.ps1` | PowerShell | Creates desktop shortcut | N/A |
| `veleron_voice_flow.py` | Python | Main application | ✅ Yes (if run directly) |

---

## 💡 Which Launcher to Use?

### Use the Desktop Shortcut 🏆 (Recommended)
**When:** Most of the time
**Why:** Quick access, shows console for debugging

### Use Launch_Voice_Flow.bat
**When:** You're in the project folder
**Why:** Convenient if you're already there

### Use Launch_Voice_Flow_Silent.vbs
**When:** You don't want to see the console
**Why:** Cleaner, no extra window

### Run Python Directly
**When:** Developing or debugging
**Command:** `py veleron_voice_flow.py`
**Why:** Full control, can see all output

---

## 🎯 Testing Your Shortcuts

### Test Desktop Shortcut:

1. Go to your Desktop
2. Find "Veleron Voice Flow" shortcut (microphone icon)
3. Double-click it
4. Console window opens with logs
5. Application window appears
6. ✅ Success!

### Test Batch Launcher:

```powershell
cd "c:\Users\noelj\Projects\Veleron Dev Studios\Applications\whisper"
.\Launch_Voice_Flow.bat
```

### Test Silent Launcher:

1. Navigate to project folder
2. Double-click `Launch_Voice_Flow_Silent.vbs`
3. No console window
4. Application appears
5. ✅ Success!

---

## 🐛 Troubleshooting

### Issue: Desktop Shortcut Not Working

**Solution 1:** Recreate it
```powershell
cd "c:\Users\noelj\Projects\Veleron Dev Studios\Applications\whisper"
powershell -ExecutionPolicy Bypass -File Create_Desktop_Shortcut.ps1
```

**Solution 2:** Check target
- Right-click shortcut → Properties
- Target should be: `...\Launch_Voice_Flow.bat`
- Start in should be: `...\whisper\`

### Issue: "Python not found"

**Check Python installation:**
```powershell
py --version
python --version
```

**If not found:** Python isn't in PATH or not installed

### Issue: App Opens But No Microphone Dropdown

**Solution:** Make sure you're running the updated version
```powershell
cd "c:\Users\noelj\Projects\Veleron Dev Studios\Applications\whisper"
py veleron_voice_flow.py
```

Check the console for: `[INFO] Scanning for audio input devices...`

### Issue: Multiple Instances Running

**Check running instances:**
```powershell
tasklist | findstr python
```

**Kill all Python processes:**
```powershell
taskkill /F /IM python.exe
taskkill /F /IM pythonw.exe
```

---

## 📋 Startup Checklist

When you launch the app, you should see:

**In Console:**
```
============================================================
Veleron Voice Flow - Starting Application
============================================================
Python version: 3.13.7 ...
Current directory: ...
Temp directory: ...
============================================================
[INFO] Checking ffmpeg availability...
[INFO] Found ffmpeg at: C:\Program Files\ffmpeg\bin
[INFO] Added C:\Program Files\ffmpeg\bin to PATH
[INFO] Scanning for audio input devices...
[INFO] Found input device 1: Microphone (C922 Pro Stream Web
[INFO] Found input device 12: Microphone (C922 Pro Stream Webcam)
[INFO] Default input device: ... (ID: X)
[INFO] Found 7 input devices total
[INFO] Loading Whisper model: base
[INFO] Model base loaded successfully
```

**In Application Window:**
- ✅ Title: "Veleron Voice Flow - AI Voice Transcription"
- ✅ Microphone dropdown visible (second row)
- ✅ Status bar: "Ready - Model: base"
- ✅ All buttons visible

---

## 🎨 Customizing Your Shortcut

### Change Icon:

1. Right-click desktop shortcut
2. Properties → Change Icon
3. Browse for icon file or use system icons
4. Suggestions:
   - `imageres.dll,190` - Microphone 🎤
   - `imageres.dll,73` - Sound wave
   - `shell32.dll,165` - Speaker

### Change Name:

1. Right-click desktop shortcut
2. Rename
3. Type new name
4. Press Enter

### Pin to Taskbar:

1. Right-click desktop shortcut
2. Select "Pin to taskbar"
3. ✅ Now in taskbar for quick access!

### Pin to Start Menu:

1. Right-click desktop shortcut
2. Select "Pin to Start"
3. ✅ Now in Start menu!

---

## 📊 Comparison of Launch Methods

| Method | Speed | Console | Clean | Best For |
|--------|-------|---------|-------|----------|
| **Desktop Shortcut** | ⚡⚡⚡ | ✅ | ⭐⭐ | Daily use |
| **Batch File** | ⚡⚡ | ✅ | ⭐⭐ | Development |
| **Silent VBS** | ⚡⚡⚡ | ❌ | ⭐⭐⭐ | Clean desktop |
| **Python Direct** | ⚡ | ✅ | ⭐ | Debugging |

---

## 🚀 Quick Start from Desktop

**New workflow:**

1. **Double-click** "Veleron Voice Flow" on desktop
2. **Wait** for app to load (5-10 seconds)
3. **Select** your C922 microphone from dropdown
4. **Click** "🎤 Start Recording"
5. **Speak** and transcribe!

**That's it!** 🎉

---

## 📁 File Locations Summary

```
Your Desktop:
  └─ Veleron Voice Flow.lnk ← Double-click here!

Project Folder (c:\Users\noelj\Projects\Veleron Dev Studios\Applications\whisper\):
  ├─ veleron_voice_flow.py          (Main app)
  ├─ Launch_Voice_Flow.bat          (Launcher with console)
  ├─ Launch_Voice_Flow_Silent.vbs   (Launcher without console)
  ├─ Create_Desktop_Shortcut.ps1    (Shortcut creator)
  └─ LAUNCHER_GUIDE.md              (This guide)
```

---

## ✅ Success Indicators

After launching via any method:

- ✅ Console shows device detection (if console visible)
- ✅ Application window appears
- ✅ Microphone dropdown is populated
- ✅ Status shows "Ready - Model: base"
- ✅ All buttons are enabled
- ✅ You can select microphones from dropdown

---

## 🎯 Next Steps

1. **Try the desktop shortcut** - Double-click it!
2. **Select your C922 webcam** from Microphone dropdown
3. **Test recording** - Watch for LED light!
4. **Enjoy transcription!** 🎉

**Optional:**
5. Pin shortcut to taskbar for even quicker access
6. Create shortcuts for other apps (Dictation, Whisper to Office)

---

## 📞 Need More Shortcuts?

Want shortcuts for the other applications?

**Veleron Dictation:**
```powershell
# Edit Launch_Voice_Flow.bat
# Change: py veleron_voice_flow.py
# To: py veleron_dictation.py
```

**Whisper to Office:**
(This is CLI-based, so shortcut would need to open terminal)

---

**Created:** October 12, 2025
**Status:** ✅ All Launchers Ready
**Location:** Project folder and Desktop

🚀 **You can now launch Veleron Voice Flow from your desktop!** 🚀
