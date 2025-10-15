"""
Pytest Configuration and Shared Fixtures for Veleron Whisper Tests

This module provides shared fixtures and mock objects for testing the
Veleron Whisper Voice-to-Text applications.
"""

import random as rand
import numpy
import numpy as np
import pytest
import tempfile
import os
from unittest.mock import Mock, MagicMock
import wave


def pytest_configure(config):
    config.addinivalue_line("markers", "requires_cuda")
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")


@pytest.fixture
def random():
    rand.seed(42)
    numpy.random.seed(42)


@pytest.fixture
def mock_whisper_model():
    """
    Create a mock Whisper model for testing without loading real models.

    Returns:
        Mock: A mock Whisper model with transcribe method
    """
    model = Mock()
    model.transcribe = Mock(return_value={
        "text": "This is a test transcription.",
        "language": "en",
        "segments": [
            {
                "id": 0,
                "start": 0.0,
                "end": 2.5,
                "text": "This is a test"
            },
            {
                "id": 1,
                "start": 2.5,
                "end": 5.0,
                "text": "transcription."
            }
        ]
    })
    return model


@pytest.fixture
def mock_whisper_load_model(monkeypatch, mock_whisper_model):
    """
    Mock whisper.load_model to return a mock model instead of loading real model.

    Args:
        monkeypatch: Pytest monkeypatch fixture
        mock_whisper_model: Mock model fixture

    Returns:
        Mock: The mocked load_model function
    """
    def mock_load(*args, **kwargs):
        return mock_whisper_model

    import whisper
    monkeypatch.setattr(whisper, 'load_model', mock_load)
    return Mock(side_effect=mock_load)


@pytest.fixture
def sample_audio_data():
    """
    Generate sample audio data for testing.

    Returns:
        np.ndarray: Sample audio data as float32 array
    """
    # Generate 1 second of 440Hz sine wave at 16kHz
    sample_rate = 16000
    duration = 1.0
    frequency = 440.0

    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.sin(2 * np.pi * frequency * t).astype(np.float32)

    return audio


@pytest.fixture
def sample_audio_file(sample_audio_data, tmp_path):
    """
    Create a temporary WAV file with sample audio data.

    Args:
        sample_audio_data: Sample audio data fixture
        tmp_path: Pytest temporary directory

    Returns:
        str: Path to temporary audio file
    """
    audio_file = tmp_path / "test_audio.wav"

    with wave.open(str(audio_file), 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        audio_int16 = (sample_audio_data * 32767).astype(np.int16)
        wf.writeframes(audio_int16.tobytes())

    return str(audio_file)


@pytest.fixture
def sample_audio_chunks():
    """
    Generate a list of audio chunks simulating streaming recording.

    Returns:
        list: List of numpy arrays representing audio chunks
    """
    chunks = []
    for i in range(10):
        # Each chunk is 0.1 seconds at 16kHz
        chunk = np.random.randn(1600, 1).astype(np.float32) * 0.1
        chunks.append(chunk)
    return chunks


@pytest.fixture
def mock_sounddevice(monkeypatch):
    """
    Mock sounddevice module for testing audio I/O without hardware.

    Args:
        monkeypatch: Pytest monkeypatch fixture

    Returns:
        Mock: Mocked sounddevice module
    """
    mock_sd = MagicMock()
    mock_sd.InputStream = MagicMock()
    mock_sd.sleep = Mock()

    # Create a context manager for InputStream
    mock_stream = MagicMock()
    mock_stream.__enter__ = Mock(return_value=mock_stream)
    mock_stream.__exit__ = Mock(return_value=False)
    mock_sd.InputStream.return_value = mock_stream

    import sys
    sys.modules['sounddevice'] = mock_sd

    return mock_sd


@pytest.fixture
def mock_keyboard(monkeypatch):
    """
    Mock keyboard module for testing hotkey functionality.

    Args:
        monkeypatch: Pytest monkeypatch fixture

    Returns:
        Mock: Mocked keyboard module
    """
    mock_kb = MagicMock()
    mock_kb.add_hotkey = Mock()
    mock_kb.on_release_key = Mock()

    import sys
    sys.modules['keyboard'] = mock_kb

    return mock_kb


@pytest.fixture
def mock_pyautogui(monkeypatch):
    """
    Mock pyautogui module for testing typing functionality.

    Args:
        monkeypatch: Pytest monkeypatch fixture

    Returns:
        Mock: Mocked pyautogui module
    """
    mock_pag = MagicMock()
    mock_pag.write = Mock()

    import sys
    sys.modules['pyautogui'] = mock_pag

    return mock_pag


@pytest.fixture
def mock_pystray(monkeypatch):
    """
    Mock pystray module for testing system tray functionality.

    Args:
        monkeypatch: Pytest monkeypatch fixture

    Returns:
        Mock: Mocked pystray module
    """
    mock_tray = MagicMock()
    mock_icon = MagicMock()
    mock_menu = MagicMock()
    mock_menu_item = MagicMock()

    mock_tray.Icon = Mock(return_value=mock_icon)
    mock_tray.Menu = Mock(return_value=mock_menu)
    mock_tray.MenuItem = Mock(return_value=mock_menu_item)

    import sys
    sys.modules['pystray'] = mock_tray

    return mock_tray


@pytest.fixture
def mock_tkinter():
    """
    Mock tkinter for GUI testing without display.

    Returns:
        Mock: Mocked tkinter root window
    """
    root = MagicMock()
    root.title = Mock()
    root.geometry = Mock()
    root.mainloop = Mock()
    root.quit = Mock()
    root.clipboard_clear = Mock()
    root.clipboard_append = Mock()
    root.after = Mock(side_effect=lambda delay, func, *args: func(*args))

    return root


@pytest.fixture
def temp_output_dir(tmp_path):
    """
    Create a temporary directory for output files.

    Args:
        tmp_path: Pytest temporary directory

    Returns:
        str: Path to temporary output directory
    """
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return str(output_dir)


@pytest.fixture
def mock_transcription_result():
    """
    Create a mock transcription result with realistic data.

    Returns:
        dict: Mock transcription result
    """
    return {
        "text": "Hello, this is a test transcription. It contains multiple sentences. "
                "This helps test formatting and processing of longer text.",
        "language": "en",
        "segments": [
            {
                "id": 0,
                "start": 0.0,
                "end": 3.2,
                "text": "Hello, this is a test transcription."
            },
            {
                "id": 1,
                "start": 3.2,
                "end": 6.5,
                "text": "It contains multiple sentences."
            },
            {
                "id": 2,
                "start": 6.5,
                "end": 10.8,
                "text": "This helps test formatting and processing of longer text."
            }
        ]
    }


@pytest.fixture
def cleanup_temp_files():
    """
    Fixture to track and cleanup temporary files created during tests.

    Yields:
        list: List to track temporary files
    """
    temp_files = []
    yield temp_files

    # Cleanup after test
    for file_path in temp_files:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Warning: Could not delete {file_path}: {e}")


# Test data constants
SAMPLE_MODELS = ["tiny", "base", "small", "medium", "large", "turbo"]
SAMPLE_LANGUAGES = ["en", "es", "fr", "de", "it", "pt", "nl", "ja", "ko", "zh"]
SAMPLE_HOTKEYS = ["ctrl+shift+space", "ctrl+alt+r", "alt+space"]
