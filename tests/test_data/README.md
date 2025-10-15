# Test Audio Files

Generated: 2025-10-12 14:13:06

## Synthetic Test Audio Files

These files are generated programmatically for automated testing.
They do not contain real speech, but can be used to test:
- File loading and processing
- Error handling
- Performance benchmarks
- Audio pipeline functionality

### Files:

1. **test_silent.wav** (5s)
   - Purpose: Test silence detection
   - Expected: No transcription or "no speech detected"

2. **test_very_short.wav** (0.2s)
   - Purpose: Test "audio too short" handling
   - Expected: Rejection with appropriate message

3. **test_short_tone.wav** (5s)
   - Purpose: Basic functionality testing
   - Expected: Processes without error (may produce gibberish transcription)

4. **test_medium_tone.wav** (30s)
   - Purpose: Medium-length audio testing
   - Expected: Processes successfully

5. **test_long_tone.wav** (5 minutes)
   - Purpose: Performance and memory testing
   - Expected: Processes successfully, monitor memory usage

6. **test_noise.wav** (10s)
   - Purpose: Test noise handling
   - Expected: May detect noise as speech or reject

7. **test_quiet.wav** (5s)
   - Purpose: Test low-volume audio handling
   - Expected: May warn about low volume

8. **test_multi_tone.wav** (4s)
   - Purpose: Test varying frequency input
   - Expected: Processes successfully

9. **test_segmented.wav** (8s)
   - Purpose: Test segment detection with pauses
   - Expected: Should detect 3 segments

## Real Audio Files (Add Manually)

For full testing, you should add real speech audio files:

- **test_speech_short.wav** - 5-10s of clear speech
- **test_speech_medium.wav** - 30-60s of clear speech
- **test_speech_long.wav** - 5-15 minutes of speech
- **test_speech_noisy.wav** - Speech with background noise
- **test_speech_accented.wav** - Non-native English speaker
- **test_speech_fast.wav** - Rapid speech
- **test_speech_spanish.mp3** - Spanish language audio
- **test_speech_french.mp3** - French language audio

## Audio Formats to Test

Convert some real speech files to:
- MP3 (128kbps, 256kbps)
- M4A
- FLAC
- OGG

## Notes

- All generated files are mono, 16kHz, 16-bit WAV
- File sizes vary from ~32KB to ~9.6MB
- These are synthetic; accuracy testing requires real speech
- Use these for automation, supplement with manual real-audio tests
