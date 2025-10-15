# Hardware Testing Guide - Veleron Whisper Voice-to-Text
**DirectSound Fallback Verification**

**Version:** 1.0
**Date:** October 14, 2025
**Status:** Ready for Testing
**Purpose:** Verify DirectSound fallback works with real hardware

---

## Overview

This guide provides step-by-step instructions for testing the DirectSound fallback mechanism with actual USB audio devices. The goal is to verify that the automatic API switching works correctly with real hardware, not just mocked devices.

**What We're Testing:**
- DirectSound fallback activates automatically with USB devices
- Console logs show "SWITCHING TO DIRECTSOUND" message
- Recording works without WDM-KS errors
- Audio quality is acceptable
- All three recording applications function correctly

---

## Prerequisites

### Hardware Required

**Minimum (Must Have):**
- ✅ 1 USB webcam with microphone (e.g., Logitech C922 Pro Stream Webcam)
  - This is the primary test case as it previously failed with WDM-KS errors

**Recommended (Should Have):**
- ✅ 1 Bluetooth headset (e.g., Samsung Galaxy Buds3 Pro, AirPods, etc.)
- ✅ 1 USB headset (gaming or conference headset)
- ⚠️ 1 USB microphone (Blue Yeti, Rode NT-USB, etc.)

**Optional (Nice to Have):**
- ⚠️ USB audio interface (Focusrite Scarlett, etc.)
- ⚠️ Multiple USB webcams (to test device switching)

### Software Required

- ✅ Python 3.13.7 (installed)
- ✅ All dependencies installed (openai-whisper, sounddevice, etc.)
- ✅ Applications patched with DirectSound fallback (Oct 14, 2025)
- ✅ Console window access (to view logs)

---

## Testing Checklist

Use this checklist to track testing progress:

```
📋 HARDWARE TESTING CHECKLIST

[ ] Test 1: veleron_voice_flow.py with USB webcam
[ ] Test 2: veleron_dictation.py with USB webcam
[ ] Test 3: veleron_dictation_v2.py with USB webcam
[ ] Test 4: veleron_voice_flow.py with Bluetooth headset
[ ] Test 5: veleron_dictation.py with Bluetooth headset
[ ] Test 6: veleron_dictation_v2.py with Bluetooth headset
[ ] Test 7: Device hot-swap (connect device mid-session)
[ ] Test 8: Multiple devices (switch between devices)
[ ] Test 9: Built-in microphone (verify no regression)
[ ] Test 10: Audio quality verification
```

---

## Test 1: veleron_voice_flow.py with USB Webcam

### Setup
1. **Connect USB webcam** (e.g., C922)
2. **Wait 10 seconds** for Windows to recognize device
3. **Open Command Prompt** (not PowerShell)

### Execution
```bash
cd "c:\Users\noelj\Projects\Veleron Dev Studios\Applications\whisper"
py veleron_voice_flow.py
```

### Expected Behavior

**On Application Launch:**
```
[2025-10-14 HH:MM:SS] [INFO] Checking ffmpeg availability...
[2025-10-14 HH:MM:SS] [INFO] Found ffmpeg at: C:\Program Files\ffmpeg\bin
[2025-10-14 HH:MM:SS] [INFO] Scanning for audio input devices...
[2025-10-14 HH:MM:SS] [INFO] Found input device 12: Microphone (C922 Pro Stream Webcam) (Windows WASAPI, 2 channels)
```

**When You Start Recording:**
1. Select "Microphone (C922 Pro Stream Web... (WASAPI)" from dropdown
2. Click "Start Recording" button
3. **Watch console for this log:**

```
[2025-10-14 HH:MM:SS] [INFO] Starting recording...
[2025-10-14 HH:MM:SS] [INFO] Recording from device 12: Microphone (C922 Pro Stream Webcam)
[2025-10-14 HH:MM:SS] [INFO] Device has 2 input channels
[2025-10-14 HH:MM:SS] [INFO] Current selection: Microphone (C922 Pro Stream Webcam) (ID: 12, API: Windows WASAPI)
[2025-10-14 HH:MM:SS] [INFO] SWITCHING TO DIRECTSOUND: Using device ID 6 (Microphone (C922 Pro Stream Webcam)) instead of 12
```

**Key Indicator:** Look for **"SWITCHING TO DIRECTSOUND"** message!

4. Speak for 5-10 seconds: "This is a test of the DirectSound fallback mechanism."
5. Click "Stop Recording"
6. Wait for transcription to complete

### Success Criteria

✅ **PASS** if:
- Console shows "SWITCHING TO DIRECTSOUND" message
- No error messages appear
- Transcription completes successfully
- Transcribed text is accurate
- Webcam LED lights up during recording (physical verification)

❌ **FAIL** if:
- No "SWITCHING TO DIRECTSOUND" message (fallback not working)
- Error: "PaErrorCode -9999" (WDM-KS error - fallback failed)
- Error: "Invalid number of channels" (channel detection failed)
- No transcription output (recording failed)
- Webcam LED doesn't light up (device not activated)

### Troubleshooting

**If "SWITCHING TO DIRECTSOUND" doesn't appear:**
- Check that you selected a WASAPI device from dropdown
- DirectSound may not be available for this device
- Try a different USB device

**If WDM-KS error occurs:**
- DirectSound fallback failed
- Report this as a critical bug
- Include device name and error message

**If no audio captured:**
- Check Windows Sound Settings (microphone not muted)
- Verify device is default input device
- Try "Refresh" button to rescan devices

---

## Test 2: veleron_dictation.py with USB Webcam

### Setup
1. **Ensure USB webcam still connected**
2. **Close veleron_voice_flow.py** (if running)
3. **Open new Command Prompt**

### Execution
```bash
cd "c:\Users\noelj\Projects\Veleron Dev Studios\Applications\whisper"
py veleron_dictation.py
```

### Expected Behavior

**On Application Launch:**
```
========================================
Veleron Dictation - System-wide Voice Input
========================================
Loading Whisper model: base...
Model loaded successfully!

Default input device: Microphone (C922 Pro Stream Webcam) (ID: 12)
Device channels: 2
SWITCHING TO DIRECTSOUND: Using device ID 6 (Microphone (C922 Pro Stream Webcam)) instead of 12

Dictation ready! Press Ctrl+Shift+Space to record.
Press Ctrl+C to exit.
```

**Key Indicator:** Look for **"SWITCHING TO DIRECTSOUND"** during startup!

### Testing Steps

1. **Verify startup logs** show DirectSound switch
2. **Press `Ctrl+Shift+Space`** to start recording
3. **Speak for 5 seconds:** "Testing dictation with USB webcam"
4. **Release keys** to stop recording
5. **Wait for transcription**
6. **Verify text typed** into active window (Notepad recommended)

### Success Criteria

✅ **PASS** if:
- "SWITCHING TO DIRECTSOUND" appears during startup
- Hotkey activates recording (visual feedback appears)
- Transcribed text appears in active window
- Text is accurate
- No errors in console

❌ **FAIL** if:
- No DirectSound switch message
- Recording doesn't start (no visual feedback)
- No text typed after recording
- WDM-KS error appears
- Application crashes

### Testing Hotkey

**Important:** This app uses global hotkey `Ctrl+Shift+Space`

**To test:**
1. Open Notepad
2. Place cursor in Notepad window
3. Press and hold `Ctrl+Shift+Space`
4. Speak
5. Release keys
6. Wait for text to appear in Notepad

---

## Test 3: veleron_dictation_v2.py with USB Webcam

### Setup
1. **Ensure USB webcam still connected**
2. **Close veleron_dictation.py** (if running)
3. **Open new Command Prompt**

### Execution
```bash
cd "c:\Users\noelj\Projects\Veleron Dev Studios\Applications\whisper"
py veleron_dictation_v2.py
```

### Expected Behavior

**On Application Launch:**
```
Loading Whisper model: base...
Model loaded successfully!
```

**GUI Window Appears:**
- Dropdown showing available microphones
- "Start Dictation" button
- Status display

**When You Click "Start Dictation":**
```
Selected device: Microphone (C922 Pro Stream Webcam) (ID: 12)
Device channels: 2
SWITCHING TO DIRECTSOUND: Using device ID 6 (Microphone (C922 Pro Stream Webcam)) instead of 12
```

### Testing Steps

1. **Select USB webcam** from device dropdown
2. **Open Notepad** (or any text editor)
3. **Click in Notepad** to focus it
4. **Click "Start Dictation"** button in veleron_dictation_v2
5. **Speak for 5 seconds:** "Testing GUI dictation with DirectSound fallback"
6. **Click "Stop Dictation"** button
7. **Verify text appears** in Notepad

### Success Criteria

✅ **PASS** if:
- Console shows "SWITCHING TO DIRECTSOUND" after clicking Start
- Button changes to "Stop Dictation" (state change)
- Text appears in Notepad window
- Text is accurate
- No errors

❌ **FAIL** if:
- No DirectSound switch in console
- Button doesn't change state
- No text typed
- Application freezes
- WDM-KS error

---

## Test 4-6: Bluetooth Headset Tests

Repeat Tests 1-3 with a **Bluetooth headset** instead of USB webcam.

### Additional Setup Steps

1. **Pair Bluetooth headset** with computer
2. **Set as default input** in Windows Sound Settings
3. **Wait 15 seconds** for full connection
4. **Verify in Sound Settings** (green bars when speaking)

### Expected Behavior

**DirectSound Fallback:**
- May or may not switch to DirectSound (depends on device)
- Bluetooth devices often work with WASAPI directly
- If no DirectSound version exists, should use WASAPI
- Should NOT show WDM-KS errors

**Possible Console Output (Bluetooth):**
```
# Scenario 1: DirectSound available
Selected device: Headset (Josh's Buds3 Pro) (ID: 18)
SWITCHING TO DIRECTSOUND: Using device ID 9 (Headset (Josh's Buds3 Pro)) instead of 18

# Scenario 2: No DirectSound (acceptable)
Selected device: Headset (Josh's Buds3 Pro) (ID: 18)
Using selected device (no DirectSound version found)
```

**Both scenarios are PASS** - the key is NO WDM-KS ERRORS.

---

## Test 7: Device Hot-Swap

### Purpose
Verify applications handle devices being connected mid-session.

### Test Procedure

**For veleron_voice_flow.py:**
1. Launch application with built-in microphone selected
2. **While application running**, connect USB webcam
3. Click "🔄 Refresh" button
4. **Verify webcam appears** in dropdown
5. **Select webcam** from dropdown
6. **Start recording** and verify DirectSound switch

**For veleron_dictation_v2.py:**
1. Launch application with built-in microphone
2. **While application running**, connect USB webcam
3. Click "Refresh Devices" button (if available)
4. **Select webcam** from dropdown
5. **Start dictation** and verify DirectSound switch

**For veleron_dictation.py:**
- Not applicable (uses system default, no device selection)

### Success Criteria

✅ **PASS** if:
- New device appears after refresh
- Can select and use new device
- DirectSound switch works with new device
- No application restart required

---

## Test 8: Multiple Device Switching

### Purpose
Verify switching between devices works correctly.

### Test Procedure

**Setup:** Have 3 devices available:
1. Built-in microphone
2. USB webcam
3. Bluetooth headset (or USB headset)

**Test Steps:**
1. Launch veleron_voice_flow.py
2. **Record with Device 1** (built-in mic)
   - Verify transcription works
3. **Switch to Device 2** (USB webcam)
   - Verify "SWITCHING TO DIRECTSOUND" appears
   - Record and verify transcription
4. **Switch to Device 3** (Bluetooth headset)
   - Verify DirectSound or WASAPI works
   - Record and verify transcription
5. **Switch back to Device 1**
   - Verify still works

### Success Criteria

✅ **PASS** if:
- All 3 devices work
- No errors when switching
- DirectSound activates for USB devices
- Transcriptions are accurate

---

## Test 9: Built-in Microphone (Regression Test)

### Purpose
Verify DirectSound fallback doesn't break built-in microphones.

### Test Procedure

1. **Disconnect all USB/Bluetooth devices**
2. **Use only built-in laptop microphone** (or desktop mic)
3. **Run Test 1 procedure** with built-in mic
4. **Verify recording works**

### Expected Behavior

**Console Output:**
```
Selected device: Microphone (Realtek High Definition Audio) (ID: 2)
Device channels: 2
Using selected device (no DirectSound version found)
# OR
SWITCHING TO DIRECTSOUND: Using device ID X...
```

**Either output is acceptable** - the key is: NO ERRORS.

### Success Criteria

✅ **PASS** if:
- Recording works
- Transcription accurate
- No errors
- (DirectSound switch optional for built-in devices)

❌ **FAIL** if:
- Built-in microphone no longer works (regression)
- New errors appear
- Transcription fails

---

## Test 10: Audio Quality Verification

### Purpose
Verify DirectSound doesn't degrade audio quality.

### Test Procedure

1. **Prepare test script:**
   ```
   "The quick brown fox jumps over the lazy dog.
   This sentence contains all letters of the alphabet.
   Testing audio quality with DirectSound fallback mechanism.
   Numbers: one, two, three, four, five.
   Special characters: period, comma, question mark?"
   ```

2. **Record with USB webcam** using veleron_voice_flow.py
3. **Check transcription accuracy:**
   - Count word errors
   - Check punctuation
   - Verify numbers transcribed correctly

### Success Criteria

✅ **PASS** if:
- <5% word error rate (e.g., 2-3 words wrong out of 50)
- Punctuation mostly correct
- Numbers transcribed accurately
- No audio artifacts (clipping, distortion)

⚠️ **ACCEPTABLE** if:
- 5-10% word error rate (Whisper base model limitation)
- Some punctuation errors (expected)
- Minor transcription quirks

❌ **FAIL** if:
- >10% word error rate (audio quality issue)
- Transcription is garbled
- Audio artifacts present
- Significantly worse than WASAPI quality

### Comparison Test (Optional)

**Compare WASAPI vs DirectSound quality:**

1. Record same script with **WASAPI device** (if available)
2. Record same script with **DirectSound device**
3. Compare transcriptions
4. Verify quality is similar

---

## Test Results Template

Use this template to document test results:

```markdown
# Hardware Test Results - [Date]

## Test Environment
- **Date:** [YYYY-MM-DD]
- **Tester:** [Name]
- **Windows Version:** [e.g., Windows 11 23H2]
- **Python Version:** [py --version output]

## Devices Tested

### Device 1: USB Webcam
- **Model:** Logitech C922 Pro Stream Webcam
- **Connection:** USB 2.0 / USB 3.0
- **Device ID:** 12 (WASAPI) → 6 (DirectSound)

### Device 2: Bluetooth Headset
- **Model:** [Model name]
- **Connection:** Bluetooth
- **Device ID:** [ID]

### Device 3: [Other device]
- **Model:** [Model]
- **Connection:** [Type]
- **Device ID:** [ID]

## Test Results

| Test | Device | Application | Result | Notes |
|------|--------|-------------|--------|-------|
| 1 | USB Webcam | veleron_voice_flow.py | ✅ PASS | DirectSound switch confirmed |
| 2 | USB Webcam | veleron_dictation.py | ✅ PASS | Hotkey works, text appears |
| 3 | USB Webcam | veleron_dictation_v2.py | ✅ PASS | GUI button works |
| 4 | Bluetooth | veleron_voice_flow.py | ✅ PASS | WASAPI used (no DirectSound) |
| 5 | Bluetooth | veleron_dictation.py | ✅ PASS | |
| 6 | Bluetooth | veleron_dictation_v2.py | ✅ PASS | |
| 7 | Hot-swap | veleron_voice_flow.py | ✅ PASS | Refresh button works |
| 8 | Multi-device | veleron_voice_flow.py | ✅ PASS | Switching works |
| 9 | Built-in | All apps | ✅ PASS | No regression |
| 10 | Quality | USB Webcam | ✅ PASS | <5% WER |

## DirectSound Switch Logs

### veleron_voice_flow.py (USB Webcam)
```
[2025-10-14 15:30:00] [INFO] Current selection: Microphone (C922 Pro Stream Webcam) (ID: 12, API: Windows WASAPI)
[2025-10-14 15:30:00] [INFO] SWITCHING TO DIRECTSOUND: Using device ID 6 (Microphone (C922 Pro Stream Webcam)) instead of 12
```

### veleron_dictation.py (USB Webcam)
```
Default input device: Microphone (C922 Pro Stream Webcam) (ID: 12)
SWITCHING TO DIRECTSOUND: Using device ID 6 (Microphone (C922 Pro Stream Webcam)) instead of 12
```

## Issues Found

### Issue 1: [Title]
- **Severity:** Critical / High / Medium / Low
- **Description:** [Detailed description]
- **Steps to Reproduce:** [Steps]
- **Expected:** [What should happen]
- **Actual:** [What actually happened]
- **Workaround:** [If any]

### Issue 2: [Title]
...

## Audio Quality Samples

### Test Script
"The quick brown fox jumps over the lazy dog..."

### Transcription (WASAPI)
"[Transcribed text]"
Word Error Rate: X%

### Transcription (DirectSound)
"[Transcribed text]"
Word Error Rate: Y%

## Recommendations

1. [Recommendation 1]
2. [Recommendation 2]
...

## Sign-off

- **Tester:** [Name]
- **Date:** [YYYY-MM-DD]
- **Overall Status:** ✅ PASS / ⚠️ PASS WITH ISSUES / ❌ FAIL
```

---

## Common Issues and Solutions

### Issue: "SWITCHING TO DIRECTSOUND" never appears

**Possible Causes:**
1. Device doesn't have DirectSound version (check Windows Sound Settings)
2. DirectSound driver not installed
3. Fallback code not running

**Solution:**
1. Check if device appears in Windows Sound Settings with "Windows DirectSound" suffix
2. Verify fallback code is present (check line numbers in report)
3. Try a different USB device

---

### Issue: WDM-KS Error Still Occurs

**Error Message:**
```
Error starting stream: Unexpected host error [PaErrorCode -9999]:
'WdmSyncIoctl: DeviceIoControl GLE = 0x00000490'
```

**This is a CRITICAL BUG** - DirectSound fallback failed!

**Immediate Actions:**
1. **Document everything:**
   - Device model
   - Device ID
   - Console logs
   - Screenshot of error
2. **Check fallback code:**
   - Verify lines 580-618 present in veleron_voice_flow.py
   - Verify lines 394-464 present in veleron_dictation.py
   - Verify lines 338-415 present in veleron_dictation_v2.py
3. **Report bug** with documentation

---

### Issue: No Audio Captured (Silent Recording)

**Possible Causes:**
1. Microphone muted in Windows
2. Wrong device selected
3. Permission denied

**Solution:**
1. **Check Windows Sound Settings:**
   - Speak and watch input level meter
   - Ensure microphone not muted
   - Set microphone as default device
2. **Check Windows Privacy Settings:**
   - Settings → Privacy & Security → Microphone
   - Enable "Microphone access"
   - Enable for Python
3. **Try Refresh button** to rescan devices
4. **Restart application**

---

### Issue: Application Crashes During Recording

**If this happens:**
1. **Note exactly when crash occurred** (during start, during recording, during transcription)
2. **Check console for error messages** before crash
3. **Try with different device**
4. **Check Windows Event Viewer** for crash logs

**Report with:**
- Full console output before crash
- Device being used
- Steps to reproduce

---

## Performance Benchmarks

Track these metrics during testing:

### Startup Time
- **Measurement:** Time from launch to "Ready" state
- **Target:** <5 seconds
- **Your Result:** ______ seconds

### DirectSound Search Time
- **Measurement:** Time from "Current selection" log to "SWITCHING TO DIRECTSOUND" log
- **Target:** <500ms
- **Your Result:** ______ ms

### Recording Latency
- **Measurement:** Time from "Start Recording" click to recording actually starting
- **Target:** <200ms
- **Your Result:** ______ ms

### Transcription Time (10-second audio)
- **Measurement:** Time from "Stop Recording" to transcription appearing
- **Target:** <3 seconds (base model)
- **Your Result:** ______ seconds

---

## Beta Testing Feedback Form

After completing hardware tests, prepare a beta testing package with this feedback form:

```markdown
# Veleron Whisper Voice-to-Text - Beta Tester Feedback

## Your Information
- **Name:** [Optional]
- **Date:** [YYYY-MM-DD]
- **Windows Version:** [e.g., Windows 11]

## Hardware Configuration
- **Microphone 1:** [Built-in / USB Webcam / USB Mic / Bluetooth / Other]
  - Model: [Model name]
- **Microphone 2:** [Type]
  - Model: [Model name]

## Application Tested
- [ ] Veleron Voice Flow (GUI, file transcription)
- [ ] Veleron Dictation (hotkey, global)
- [ ] Veleron Dictation v2 (GUI, button)

## Overall Experience
- **Ease of Use:** ⭐⭐⭐⭐⭐ (1-5 stars)
- **Audio Quality:** ⭐⭐⭐⭐⭐ (1-5 stars)
- **Transcription Accuracy:** ⭐⭐⭐⭐⭐ (1-5 stars)
- **Reliability:** ⭐⭐⭐⭐⭐ (1-5 stars)

## Did It Work?
- **USB Device Detected:** ✅ Yes / ❌ No
- **Recording Successful:** ✅ Yes / ❌ No
- **Transcription Accurate:** ✅ Yes / ❌ No
- **DirectSound Switch (check console):** ✅ Yes / ❌ No / ⚠️ Not Sure

## Issues Encountered
[Describe any issues, errors, or unexpected behavior]

## What You Liked
[What worked well?]

## What Could Be Improved
[Suggestions for improvement]

## Would You Use This Product?
- ✅ Yes, regularly
- ⚠️ Yes, occasionally
- ❌ No

## Additional Comments
[Any other feedback]
```

---

## Next Steps After Testing

### If All Tests Pass ✅

1. **Document results** using test results template
2. **Create beta package:**
   - Installer or ZIP file
   - README with setup instructions
   - Feedback form
   - Bug report template
3. **Distribute to beta testers** (5-10 people)
4. **Monitor feedback** for 1 week
5. **Fix critical bugs** as reported
6. **Prepare for production release**

### If Tests Fail ❌

1. **Document failures** thoroughly
2. **Prioritize by severity:**
   - CRITICAL: WDM-KS errors, crashes
   - HIGH: Transcription failures, quality issues
   - MEDIUM: UI bugs, minor errors
   - LOW: Cosmetic issues
3. **Fix critical issues** immediately
4. **Re-test** with same devices
5. **Don't proceed to beta** until all critical issues fixed

### If Tests Are Inconclusive ⚠️

1. **Try more devices** (different brands, models)
2. **Test on different computer** (different Windows version)
3. **Check for environmental issues:**
   - Windows updates pending
   - Antivirus interference
   - Driver issues
4. **Consult documentation** (AUDIO_API_TROUBLESHOOTING.md)
5. **Re-test** after addressing issues

---

## Hardware Compatibility Matrix

Track which devices work:

| Device Type | Model | WASAPI | DirectSound | MME | WDM-KS | Notes |
|-------------|-------|--------|-------------|-----|--------|-------|
| USB Webcam | C922 Pro Stream | ❌ | ✅ | ✅ | ❌ | Switch to DirectSound |
| USB Webcam | C920 HD Pro | ❌ | ✅ | ✅ | ❌ | Switch to DirectSound |
| Bluetooth | Buds3 Pro | ✅ | ✅ | ✅ | ❌ | WASAPI works |
| Built-in | Realtek HD Audio | ✅ | ✅ | ✅ | ⚠️ | All APIs work |
| USB Mic | Blue Yeti | ❌ | ✅ | ✅ | ❌ | Switch to DirectSound |
| USB Headset | HyperX Cloud | ❌ | ✅ | ✅ | ❌ | Switch to DirectSound |

**Legend:**
- ✅ Works reliably
- ❌ Fails (WDM-KS error or no audio)
- ⚠️ Works but with caveats

---

## Conclusion

This hardware testing guide provides comprehensive procedures for verifying the DirectSound fallback mechanism. Follow each test systematically, document results thoroughly, and report any issues discovered.

**Key Success Indicators:**
1. "SWITCHING TO DIRECTSOUND" logs appear for USB devices
2. No WDM-KS errors (-9999)
3. Transcriptions are accurate
4. All three applications work reliably
5. Audio quality is acceptable

**If all tests pass:** Proceed to beta testing
**If tests fail:** Fix issues and re-test before beta

---

**Document Version:** 1.0
**Created:** October 14, 2025
**Next Review:** After initial hardware testing
**Status:** Ready for Use

**Happy Testing! 🎤🎧🎙️**
