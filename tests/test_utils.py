"""
Test Utilities for Veleron Whisper Applications
Provides common testing functions, fixtures, and helpers.
"""

import os
import sys
import tempfile
import shutil
import json
import wave
import numpy as np
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, Dict, Any


# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "test_data"


def get_test_audio_path(filename: str) -> str:
    """Get absolute path to test audio file"""
    path = TEST_DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Test audio file not found: {path}")
    return str(path)


def get_test_data_dir() -> str:
    """Get absolute path to test data directory"""
    return str(TEST_DATA_DIR)


@contextmanager
def temporary_directory():
    """Context manager for temporary directory"""
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@contextmanager
def temporary_file(suffix=".txt", delete=True):
    """Context manager for temporary file"""
    temp_file = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
    temp_file.close()
    try:
        yield temp_file.name
    finally:
        if delete and os.path.exists(temp_file.name):
            os.unlink(temp_file.name)


def create_test_wav(duration: float = 1.0, frequency: float = 440.0,
                    sample_rate: int = 16000, output_path: Optional[str] = None) -> str:
    """
    Create a test WAV file with a sine wave.

    Args:
        duration: Duration in seconds
        frequency: Frequency in Hz
        sample_rate: Sample rate in Hz
        output_path: Output file path (optional, creates temp file if not provided)

    Returns:
        Path to created WAV file
    """
    # Generate sine wave
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = 0.3 * np.sin(2 * np.pi * frequency * t)
    audio_int16 = (audio * 32767).astype(np.int16)

    # Create output path if not provided
    if output_path is None:
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        output_path = temp_file.name
        temp_file.close()

    # Write WAV file
    with wave.open(output_path, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_int16.tobytes())

    return output_path


def read_wav_info(file_path: str) -> Dict[str, Any]:
    """
    Read WAV file information.

    Returns:
        Dict with channels, sample_width, frame_rate, n_frames, duration
    """
    with wave.open(file_path, 'r') as wav_file:
        info = {
            'channels': wav_file.getnchannels(),
            'sample_width': wav_file.getsampwidth(),
            'frame_rate': wav_file.getframerate(),
            'n_frames': wav_file.getnframes(),
            'duration': wav_file.getnframes() / wav_file.getframerate()
        }
    return info


def validate_json_file(file_path: str) -> Dict[str, Any]:
    """
    Validate and load JSON file.

    Returns:
        Parsed JSON data

    Raises:
        json.JSONDecodeError: If file is not valid JSON
        FileNotFoundError: If file doesn't exist
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_text_file(file_path: str, min_length: int = 0) -> str:
    """
    Validate and read text file.

    Args:
        file_path: Path to text file
        min_length: Minimum expected content length

    Returns:
        File content as string

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If content is too short
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if len(content) < min_length:
        raise ValueError(f"File content too short: {len(content)} < {min_length}")

    return content


def file_contains_text(file_path: str, search_text: str, case_sensitive: bool = False) -> bool:
    """
    Check if file contains specific text.

    Args:
        file_path: Path to file
        search_text: Text to search for
        case_sensitive: Whether search is case-sensitive

    Returns:
        True if text found, False otherwise
    """
    try:
        content = validate_text_file(file_path)
        if not case_sensitive:
            content = content.lower()
            search_text = search_text.lower()
        return search_text in content
    except (FileNotFoundError, ValueError):
        return False


def count_lines_in_file(file_path: str) -> int:
    """Count number of lines in file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return sum(1 for _ in f)


def get_file_size_mb(file_path: str) -> float:
    """Get file size in megabytes"""
    return os.path.getsize(file_path) / (1024 * 1024)


class MockWhisperResult:
    """Mock Whisper transcription result for testing"""

    def __init__(self, text: str = "Test transcription", language: str = "en",
                 segments: Optional[list] = None):
        self.text = text
        self.language = language
        if segments is None:
            self.segments = [
                {
                    "start": 0.0,
                    "end": 2.0,
                    "text": " Test transcription"
                }
            ]
        else:
            self.segments = segments

    def __getitem__(self, key):
        """Allow dict-like access"""
        if key == "text":
            return self.text
        elif key == "language":
            return self.language
        elif key == "segments":
            return self.segments
        else:
            raise KeyError(key)


class TestAudioRecorder:
    """Mock audio recorder for testing"""

    def __init__(self, duration: float = 1.0):
        self.duration = duration
        self.is_recording = False
        self.audio_data = []

    def start_recording(self):
        """Start mock recording"""
        self.is_recording = True
        self.audio_data = []

    def stop_recording(self):
        """Stop mock recording and return audio data"""
        self.is_recording = False
        # Generate mock audio data
        sample_rate = 16000
        t = np.linspace(0, self.duration, int(sample_rate * self.duration))
        audio = 0.3 * np.sin(2 * np.pi * 440 * t)
        self.audio_data = [audio.astype(np.float32)]
        return self.audio_data

    def get_audio_data(self):
        """Get recorded audio data"""
        if self.audio_data:
            return np.concatenate(self.audio_data)
        return np.array([], dtype=np.float32)


def assert_file_exists(file_path: str, message: Optional[str] = None):
    """Assert that file exists"""
    if not os.path.exists(file_path):
        msg = message or f"File does not exist: {file_path}"
        raise AssertionError(msg)


def assert_file_not_empty(file_path: str, message: Optional[str] = None):
    """Assert that file exists and is not empty"""
    assert_file_exists(file_path, message)
    if os.path.getsize(file_path) == 0:
        msg = message or f"File is empty: {file_path}"
        raise AssertionError(msg)


def assert_valid_timestamp(timestamp_str: str):
    """
    Assert that string is a valid timestamp format.
    Accepts: MM:SS or HH:MM:SS
    """
    parts = timestamp_str.split(':')
    if len(parts) not in [2, 3]:
        raise AssertionError(f"Invalid timestamp format: {timestamp_str}")

    for part in parts:
        if not part.isdigit():
            raise AssertionError(f"Invalid timestamp format: {timestamp_str}")


def cleanup_temp_files(*file_paths):
    """Clean up temporary files (safe, doesn't raise errors)"""
    for file_path in file_paths:
        if file_path and os.path.exists(file_path):
            try:
                os.unlink(file_path)
            except Exception:
                pass  # Ignore cleanup errors


# Test audio file listing
def list_test_audio_files():
    """List all available test audio files"""
    if not TEST_DATA_DIR.exists():
        return []

    audio_extensions = ['.wav', '.mp3', '.m4a', '.flac', '.ogg']
    files = []
    for ext in audio_extensions:
        files.extend(TEST_DATA_DIR.glob(f"*{ext}"))

    return [f.name for f in files]


def print_test_audio_inventory():
    """Print inventory of available test audio files"""
    files = list_test_audio_files()
    if not files:
        print("No test audio files found in:", TEST_DATA_DIR)
        return

    print(f"\nAvailable test audio files ({len(files)}):")
    print("-" * 60)
    for filename in sorted(files):
        file_path = TEST_DATA_DIR / filename
        size_mb = get_file_size_mb(str(file_path))
        print(f"  - {filename:30} ({size_mb:.2f} MB)")
    print()


# Whisper model helpers
def get_small_test_model():
    """Get smallest Whisper model name for fast testing"""
    return "tiny"


def get_default_test_model():
    """Get default model for testing"""
    return "base"


# Performance tracking
class PerformanceTimer:
    """Simple timer for performance measurements"""

    def __init__(self):
        self.start_time = None
        self.end_time = None

    def start(self):
        """Start the timer"""
        import time
        self.start_time = time.time()

    def stop(self):
        """Stop the timer"""
        import time
        self.end_time = time.time()

    def elapsed(self):
        """Get elapsed time in seconds"""
        if self.start_time is None:
            return 0
        if self.end_time is None:
            import time
            return time.time() - self.start_time
        return self.end_time - self.start_time

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()


# Test markers
def requires_model(model_name: str = "base"):
    """Decorator to mark tests that require a specific model"""
    def decorator(func):
        func.requires_model = model_name
        return func
    return decorator


def requires_microphone(func):
    """Decorator to mark tests that require microphone"""
    func.requires_microphone = True
    return func


def requires_admin(func):
    """Decorator to mark tests that require administrator privileges"""
    func.requires_admin = True
    return func


if __name__ == "__main__":
    # Print test utility information
    print("="*60)
    print("Veleron Whisper Test Utilities")
    print("="*60)
    print(f"\nProject Root: {PROJECT_ROOT}")
    print(f"Test Data Directory: {TEST_DATA_DIR}")
    print(f"Test Data Exists: {TEST_DATA_DIR.exists()}")

    print_test_audio_inventory()

    # Test creating a sample WAV file
    print("\nTesting WAV file creation...")
    temp_wav = create_test_wav(duration=0.5)
    info = read_wav_info(temp_wav)
    print(f"Created test WAV: {temp_wav}")
    print(f"Info: {info}")
    cleanup_temp_files(temp_wav)
    print("Cleanup complete.")
