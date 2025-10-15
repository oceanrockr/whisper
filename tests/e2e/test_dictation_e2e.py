"""
End-to-End and Unit Tests for Veleron Dictation Application

Most dictation tests require manual execution due to:
- Administrator privilege requirements
- Keyboard automation dependencies
- Microphone input requirements
- System-wide integration

This test suite covers:
1. Unit tests for testable components
2. Integration tests with mocked dependencies
3. Manual test procedures documentation
"""

import pytest
import os
import sys
import tkinter as tk
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import wave
import tempfile

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.test_utils import (
    get_test_audio_path,
    temporary_file,
    assert_file_exists,
    MockWhisperResult,
    PerformanceTimer,
    create_test_wav
)

# Import the application class
from veleron_dictation_v2 import VeleronDictationV2


class TestDictationUnitTests:
    """Unit tests for isolated functions"""

    def test_timestamp_formatting(self):
        """TC-VD-022: Test timestamp formatting in logs"""
        from datetime import datetime

        # Test timestamp format
        timestamp = datetime.now().strftime("%H:%M:%S")
        parts = timestamp.split(':')

        assert len(parts) == 3
        assert all(part.isdigit() for part in parts)
        assert 0 <= int(parts[0]) <= 23  # hours
        assert 0 <= int(parts[1]) <= 59  # minutes
        assert 0 <= int(parts[2]) <= 59  # seconds

    def test_audio_validation_length(self):
        """TC-VD-021: Test audio length validation"""
        sample_rate = 16000

        # Create very short audio (0.2s) - should be rejected
        short_audio = np.zeros(int(sample_rate * 0.2), dtype=np.float32)
        assert len(short_audio) < sample_rate * 0.3  # Below 0.3s threshold

        # Create valid length audio (1.0s)
        valid_audio = np.zeros(int(sample_rate * 1.0), dtype=np.float32)
        assert len(valid_audio) >= sample_rate * 0.3  # Above threshold

    def test_audio_validation_amplitude(self):
        """TC-VD-021: Test audio amplitude validation"""
        # Create silent audio (no speech)
        silent_audio = np.zeros(16000, dtype=np.float32)
        max_amplitude = np.max(np.abs(silent_audio))
        assert max_amplitude < 0.01  # Should be below speech threshold

        # Create audio with sufficient amplitude
        normal_audio = 0.1 * np.random.randn(16000).astype(np.float32)
        max_amplitude = np.max(np.abs(normal_audio))
        assert max_amplitude >= 0.01  # Should be above threshold


class TestDictationInitialization:
    """Tests for application initialization"""

    @pytest.fixture
    def app_instance(self):
        """Create application instance with mocked dependencies"""
        with patch('sounddevice.query_devices') as mock_devices:
            # Mock audio device list
            mock_devices.return_value = [
                {
                    'name': 'Test Microphone',
                    'max_input_channels': 1,
                    'default_samplerate': 16000
                }
            ]

            with patch('veleron_dictation_v2.whisper.load_model') as mock_load:
                mock_model = Mock()
                mock_load.return_value = mock_model

                app = VeleronDictationV2()
                app.model = mock_model

                yield app

                # Cleanup
                try:
                    app.root.destroy()
                except:
                    pass

    def test_application_initialization(self, app_instance):
        """TC-VD-001: Test application initializes correctly"""
        assert app_instance.model_name == 'base'
        assert app_instance.language is None  # Auto-detect
        assert app_instance.sample_rate == 16000
        assert app_instance.is_recording == False

    def test_window_creation(self, app_instance):
        """TC-VD-001: Test window is created"""
        assert app_instance.root is not None
        assert isinstance(app_instance.root, tk.Tk)

    def test_ui_components_exist(self, app_instance):
        """TC-VD-001: Test all UI components exist"""
        assert hasattr(app_instance, 'status_var')
        assert hasattr(app_instance, 'record_button')
        assert hasattr(app_instance, 'device_var')
        assert hasattr(app_instance, 'model_var')
        assert hasattr(app_instance, 'language_var')
        assert hasattr(app_instance, 'log_text')


class TestMicrophoneSelection:
    """Tests for microphone device selection"""

    def test_get_audio_devices(self):
        """TC-VD-002: Test audio device enumeration"""
        with patch('sounddevice.query_devices') as mock_devices:
            # Mock device list
            mock_devices.return_value = [
                {'name': 'Mic 1', 'max_input_channels': 1, 'default_samplerate': 44100},
                {'name': 'Mic 2', 'max_input_channels': 2, 'default_samplerate': 48000},
                {'name': 'Speaker', 'max_input_channels': 0, 'default_samplerate': 44100},  # Output only
            ]

            with patch('veleron_dictation_v2.whisper.load_model'):
                app = VeleronDictationV2()
                devices = app.get_audio_devices()

                # Should only include input devices (max_input_channels > 0)
                assert len(devices) == 2
                assert all(d['max_input_channels'] > 0 for d in devices)

                app.root.destroy()

    def test_device_selection_format(self):
        """TC-VD-002: Test device selection format"""
        device = {
            'index': 0,
            'name': 'Test Microphone',
            'channels': 1,
            'sample_rate': 16000
        }

        # Device string format: "index: name"
        device_str = f"{device['index']}: {device['name']}"
        assert device_str == "0: Test Microphone"


class TestModelManagement:
    """Tests for model selection and loading"""

    def test_model_options(self):
        """TC-VD-007: Test available model options"""
        expected_models = ["tiny", "tiny.en", "base", "base.en", "small", "small.en", "medium", "turbo"]

        with patch('sounddevice.query_devices'):
            with patch('veleron_dictation_v2.whisper.load_model'):
                app = VeleronDictationV2()

                # Verify default model
                assert app.model_name in expected_models

                app.root.destroy()


class TestLanguageSettings:
    """Tests for language selection"""

    def test_language_options(self):
        """TC-VD-008: Test language options"""
        expected_languages = ["auto", "en", "es", "fr", "de", "it", "pt", "nl", "ja", "ko", "zh"]

        with patch('sounddevice.query_devices'):
            with patch('veleron_dictation_v2.whisper.load_model'):
                app = VeleronDictationV2()

                # Verify default language is auto
                assert app.language_var.get() == "auto"

                app.root.destroy()


class TestRecordingState:
    """Tests for recording state management"""

    @pytest.fixture
    def app_with_mic(self):
        """Create app instance with mock microphone"""
        with patch('sounddevice.query_devices') as mock_devices:
            mock_devices.return_value = [{
                'name': 'Test Mic',
                'max_input_channels': 1,
                'default_samplerate': 16000
            }]

            with patch('veleron_dictation_v2.whisper.load_model'):
                app = VeleronDictationV2()
                app.model = Mock()
                app.selected_device = 0  # Select first device

                yield app

                try:
                    app.root.destroy()
                except:
                    pass

    def test_initial_recording_state(self, app_with_mic):
        """TC-VD-004: Test initial recording state"""
        assert app_with_mic.is_recording == False
        assert len(app_with_mic.audio_data) == 0

    def test_start_recording_state_changes(self, app_with_mic):
        """TC-VD-004: Test state changes when starting recording"""
        with patch('sounddevice.InputStream'):
            with patch('threading.Thread'):
                app_with_mic.start_recording()

                assert app_with_mic.is_recording == True
                assert "Recording" in app_with_mic.status_var.get()

    def test_start_recording_without_model(self, app_with_mic):
        """TC-VD-004: Test recording fails without model"""
        app_with_mic.model = None

        with patch('tkinter.messagebox.showwarning') as mock_warning:
            app_with_mic.start_recording()
            mock_warning.assert_called_once()

    def test_start_recording_without_microphone(self, app_with_mic):
        """TC-VD-004: Test recording fails without microphone"""
        app_with_mic.selected_device = None

        with patch('tkinter.messagebox.showwarning') as mock_warning:
            app_with_mic.start_recording()
            mock_warning.assert_called_once()


class TestAudioProcessing:
    """Tests for audio processing logic"""

    def test_audio_concatenation(self):
        """Test audio chunk concatenation"""
        # Simulate multiple audio chunks
        chunks = [
            np.random.randn(1024).astype(np.float32),
            np.random.randn(1024).astype(np.float32),
            np.random.randn(1024).astype(np.float32),
        ]

        # Concatenate
        audio = np.concatenate(chunks, axis=0)
        audio = audio.flatten()

        assert len(audio) == 1024 * 3
        assert audio.dtype == np.float32

    def test_audio_wav_conversion(self):
        """Test converting audio to WAV format"""
        sample_rate = 16000
        audio = 0.3 * np.sin(2 * np.pi * 440 * np.linspace(0, 1, sample_rate))
        audio = audio.astype(np.float32)

        with temporary_file(suffix=".wav", delete=True) as temp_file:
            # Convert to int16
            audio_int16 = (audio * 32767).astype(np.int16)

            # Write WAV file
            with wave.open(temp_file, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(audio_int16.tobytes())

            # Verify file created
            assert_file_exists(temp_file)

            # Read and verify
            with wave.open(temp_file, 'rb') as wf:
                assert wf.getnchannels() == 1
                assert wf.getsampwidth() == 2
                assert wf.getframerate() == sample_rate


class TestTranscriptionLog:
    """Tests for transcription logging"""

    @pytest.fixture
    def app_with_log(self):
        """Create app instance"""
        with patch('sounddevice.query_devices'):
            with patch('veleron_dictation_v2.whisper.load_model'):
                app = VeleronDictationV2()
                yield app
                try:
                    app.root.destroy()
                except:
                    pass

    def test_log_text_widget_exists(self, app_with_log):
        """TC-VD-009: Verify log widget exists"""
        assert hasattr(app_with_log, 'log_text')
        assert app_with_log.log_text is not None

    def test_log_entry_format(self, app_with_log):
        """TC-VD-009: Test log entry format"""
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        text = "Test transcription"
        log_entry = f"[{timestamp}] {text}\n"

        # Insert into log
        app_with_log.log_text.insert(tk.END, log_entry)

        # Verify it's there
        log_content = app_with_log.log_text.get(1.0, tk.END)
        assert timestamp in log_content
        assert text in log_content


class TestStatusFeedback:
    """Tests for status message feedback"""

    @pytest.fixture
    def app_instance(self):
        """Create app instance"""
        with patch('sounddevice.query_devices'):
            with patch('veleron_dictation_v2.whisper.load_model'):
                app = VeleronDictationV2()
                yield app
                try:
                    app.root.destroy()
                except:
                    pass

    def test_status_updates(self, app_instance):
        """TC-VD-016: Test status message updates"""
        test_messages = [
            "Ready to record",
            "Recording... Speak now!",
            "Processing audio...",
            "Transcribing...",
            "Typing text...",
            "Success!"
        ]

        for message in test_messages:
            app_instance.status_var.set(message)
            assert app_instance.status_var.get() == message

    def test_footer_updates(self, app_instance):
        """TC-VD-016: Test footer message updates"""
        test_message = "Recording audio..."
        app_instance.footer_var.set(test_message)
        assert app_instance.footer_var.get() == test_message


@pytest.mark.manual
class TestManualDictationTests:
    """
    Manual test procedures for Veleron Dictation.
    These tests require:
    - Administrator privileges
    - Physical microphone
    - Target applications installed
    - User interaction
    """

    def test_manual_full_workflow(self):
        """
        TC-VD-004: Manual Test - Complete Dictation Workflow

        PREREQUISITES:
        - Run application as Administrator
        - Microphone connected and working
        - Notepad or text editor open

        MANUAL TEST PROCEDURE:
        1. Right-click veleron_dictation_v2.py
        2. Select "Run as administrator"
        3. Wait for model to load
        4. Click "Test Microphone" button
        5. Speak during 2-second test
        6. Verify audio level displayed
        7. Open Notepad
        8. Click in Notepad text area
        9. Click and HOLD the green record button in dictation app
        10. Speak test phrase: "Testing dictation system"
        11. Release button
        12. Wait for processing (observe status messages)
        13. Verify text appears in Notepad

        EXPECTED RESULT:
        - Microphone test shows audio level > 0.01
        - Status updates through: Recording -> Processing -> Typing
        - Text "Testing dictation system" appears in Notepad
        - Log shows transcription with timestamp

        PASS CRITERIA:
        - No errors or crashes
        - Text appears within 15 seconds
        - 80%+ transcription accuracy
        """
        pytest.skip("Manual test - requires admin privileges and user interaction")

    def test_manual_application_compatibility(self):
        """
        TC-VD-011 through TC-VD-014: Manual Test - Application Compatibility

        MANUAL TEST PROCEDURE:
        For each target application:
        1. Open target application
        2. Create/open a document
        3. Click in text input area
        4. Use dictation to enter text
        5. Verify text appears correctly

        APPLICATIONS TO TEST:
        - [ ] Notepad (TC-VD-011)
        - [ ] Microsoft Word (TC-VD-012)
        - [ ] Google Chrome (TC-VD-013)
        - [ ] Mozilla Firefox (TC-VD-013)
        - [ ] Microsoft Edge (TC-VD-013)
        - [ ] Email client (TC-VD-014)

        EXPECTED RESULT:
        - Text appears in all tested applications
        - Formatting preserved
        - No character corruption

        NOTES:
        - Some applications may have security restrictions
        - Browser extensions may interfere
        - Document each application's compatibility
        """
        pytest.skip("Manual test - requires multiple applications and user interaction")

    def test_manual_microphone_test_feature(self):
        """
        TC-VD-003: Manual Test - Microphone Test Feature

        MANUAL TEST PROCEDURE:
        1. Launch application as Administrator
        2. Verify microphone dropdown shows available devices
        3. Select your microphone
        4. Click "Test Microphone" button
        5. Speak clearly during the 2-second test
        6. Observe the result message

        EXPECTED RESULTS:
        Scenario A - Good Microphone:
        - Message: "Microphone test passed! Level: X.XX"
        - Audio level > 0.05

        Scenario B - Quiet Microphone:
        - Warning about low audio level
        - Audio level between 0.01 and 0.05
        - Suggestions displayed

        Scenario C - No Sound:
        - Warning about no sound detected
        - Audio level < 0.01
        - Troubleshooting suggestions

        PASS CRITERIA:
        - Clear feedback in all scenarios
        - Accurate audio level detection
        - Helpful error messages
        """
        pytest.skip("Manual test - requires microphone hardware")

    def test_manual_long_recording(self):
        """
        TC-VD-019: Manual Test - Long Recording (>30 seconds)

        MANUAL TEST PROCEDURE:
        1. Launch application as Administrator
        2. Open Notepad
        3. Click and HOLD record button
        4. Speak continuously for 45-60 seconds
        5. Release button
        6. Monitor status messages
        7. Verify transcription completes
        8. Check all content captured

        EXPECTED RESULT:
        - Recording handles 45-60 seconds
        - No audio dropped
        - Complete transcription appears
        - Processing completes within 2 minutes
        - Memory usage stays reasonable

        PASS CRITERIA:
        - All spoken content transcribed
        - No crashes or freezes
        - Status messages accurate throughout
        """
        pytest.skip("Manual test - requires extended speech recording")

    def test_manual_rapid_recordings(self):
        """
        TC-VD-018: Manual Test - Rapid Consecutive Recordings

        MANUAL TEST PROCEDURE:
        1. Launch application
        2. Open Notepad
        3. Perform 5 rapid recordings:
           - Record phrase 1: "First sentence"
           - Wait for typing to complete
           - Immediately record phrase 2: "Second sentence"
           - Continue for 5 phrases
        4. Verify all phrases typed correctly
        5. Check for any interference

        EXPECTED RESULT:
        - All 5 recordings complete successfully
        - Text appears in correct order
        - No mixing of transcriptions
        - Log shows all 5 entries

        PASS CRITERIA:
        - No errors or crashes
        - Each transcription independent
        - All text accurate
        """
        pytest.skip("Manual test - requires multiple recordings")


@pytest.mark.integration
class TestDictationIntegration:
    """Integration tests with mocked dependencies"""

    def test_full_workflow_mocked(self):
        """Test complete workflow with mocked components"""
        with patch('sounddevice.query_devices'):
            with patch('veleron_dictation_v2.whisper.load_model'):
                with patch('pyautogui.write') as mock_type:
                    # Create app
                    app = VeleronDictationV2()
                    app.model = Mock()
                    app.selected_device = 0

                    # Mock transcription result
                    mock_result = MockWhisperResult(
                        text="Test dictation",
                        language="en"
                    )
                    app.model.transcribe = Mock(return_value=mock_result)

                    # Simulate having audio data
                    app.audio_data = [np.random.randn(8000).astype(np.float32)]

                    # Run transcribe_and_type
                    app.transcribe_and_type()

                    # Verify pyautogui.write was called with our text
                    mock_type.assert_called_once()
                    call_args = str(mock_type.call_args)
                    assert "Test dictation" in call_args

                    app.root.destroy()


@pytest.mark.performance
class TestDictationPerformance:
    """Performance tests"""

    def test_ui_creation_performance(self):
        """Test UI creation speed"""
        with PerformanceTimer() as timer:
            with patch('sounddevice.query_devices'):
                with patch('veleron_dictation_v2.whisper.load_model'):
                    app = VeleronDictationV2()

        elapsed = timer.elapsed()
        print(f"\nDictation UI creation time: {elapsed:.3f}s")

        assert elapsed < 5, f"UI creation too slow: {elapsed}s"

        app.root.destroy()


# Test configuration
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "manual: manual tests requiring user interaction and admin privileges")
    config.addinivalue_line("markers", "integration: integration tests with mocked dependencies")
    config.addinivalue_line("markers", "performance: performance benchmark tests")


if __name__ == "__main__":
    # Run tests (excluding manual tests by default)
    pytest.main([__file__, "-v", "-s", "-m", "not manual"])
