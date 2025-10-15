"""
Generate synthetic test audio files for automated testing.

This script creates various test audio files using text-to-speech
or simple tone generation for testing the Veleron Whisper applications.
"""

import numpy as np
import wave
import os
from datetime import datetime


def generate_sine_wave(frequency=440, duration=1.0, sample_rate=16000, amplitude=0.3):
    """Generate a sine wave audio signal"""
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = amplitude * np.sin(2 * np.pi * frequency * t)
    return audio.astype(np.float32)


def generate_silence(duration=1.0, sample_rate=16000):
    """Generate silent audio"""
    return np.zeros(int(sample_rate * duration), dtype=np.float32)


def generate_white_noise(duration=1.0, sample_rate=16000, amplitude=0.1):
    """Generate white noise"""
    return (amplitude * np.random.randn(int(sample_rate * duration))).astype(np.float32)


def save_wav(filename, audio, sample_rate=16000):
    """Save audio as WAV file"""
    # Convert float32 to int16
    audio_int16 = (audio * 32767).astype(np.int16)

    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes = 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_int16.tobytes())

    print(f"Created: {filename}")


def create_test_audio_files():
    """Create all test audio files"""

    # Ensure output directory exists
    output_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(output_dir, exist_ok=True)

    print("Generating test audio files...")
    print(f"Output directory: {output_dir}")
    print()

    # 1. Silent audio (5 seconds)
    print("1. Creating silent audio...")
    silence = generate_silence(duration=5.0)
    save_wav(os.path.join(output_dir, "test_silent.wav"), silence)

    # 2. Very short audio (0.2 seconds) - for testing "too short" handling
    print("2. Creating very short audio...")
    short_audio = generate_sine_wave(frequency=440, duration=0.2)
    save_wav(os.path.join(output_dir, "test_very_short.wav"), short_audio)

    # 3. Short tone (5 seconds) - for basic testing
    print("3. Creating short tone audio...")
    short_tone = generate_sine_wave(frequency=440, duration=5.0)
    save_wav(os.path.join(output_dir, "test_short_tone.wav"), short_tone)

    # 4. Medium tone (30 seconds)
    print("4. Creating medium tone audio...")
    medium_tone = generate_sine_wave(frequency=523, duration=30.0)
    save_wav(os.path.join(output_dir, "test_medium_tone.wav"), medium_tone)

    # 5. Long tone (5 minutes) - for performance testing
    print("5. Creating long tone audio (this may take a moment)...")
    long_tone = generate_sine_wave(frequency=440, duration=300.0)
    save_wav(os.path.join(output_dir, "test_long_tone.wav"), long_tone)

    # 6. White noise (10 seconds) - for noise testing
    print("6. Creating white noise audio...")
    noise = generate_white_noise(duration=10.0)
    save_wav(os.path.join(output_dir, "test_noise.wav"), noise)

    # 7. Very quiet audio (low amplitude)
    print("7. Creating quiet audio...")
    quiet = generate_sine_wave(frequency=440, duration=5.0, amplitude=0.01)
    save_wav(os.path.join(output_dir, "test_quiet.wav"), quiet)

    # 8. Multi-tone audio (simulates speech-like patterns)
    print("8. Creating multi-tone audio...")
    multi_tone = np.concatenate([
        generate_sine_wave(440, 0.5),  # A4
        generate_sine_wave(494, 0.5),  # B4
        generate_sine_wave(523, 0.5),  # C5
        generate_sine_wave(587, 0.5),  # D5
        generate_sine_wave(659, 0.5),  # E5
        generate_sine_wave(698, 0.5),  # F5
        generate_sine_wave(784, 0.5),  # G5
        generate_sine_wave(880, 0.5),  # A5
    ])
    save_wav(os.path.join(output_dir, "test_multi_tone.wav"), multi_tone)

    # 9. Tone with silence (for segment testing)
    print("9. Creating tone with silence...")
    tone_with_silence = np.concatenate([
        generate_sine_wave(440, 2.0),
        generate_silence(1.0),
        generate_sine_wave(523, 2.0),
        generate_silence(1.0),
        generate_sine_wave(659, 2.0),
    ])
    save_wav(os.path.join(output_dir, "test_segmented.wav"), tone_with_silence)

    # 10. Create a README explaining the test files
    readme_content = f"""# Test Audio Files

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

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
"""

    readme_path = os.path.join(output_dir, "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"\nCreated: {readme_path}")

    print("\n" + "="*60)
    print("Test audio generation complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Add real speech audio files for accuracy testing")
    print("2. Convert some files to MP3, M4A, FLAC formats")
    print("3. Run the automated tests")
    print()


if __name__ == "__main__":
    create_test_audio_files()
