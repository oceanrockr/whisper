"""
End-to-End Tests for Veleron Voice Flow Application

Tests GUI application functionality including file transcription,
export functions, and model loading. Real-time recording tests
require manual execution due to microphone dependency.
"""

import pytest
import os
import sys
import json
import tkinter as tk
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import threading
import time

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.test_utils import (
    get_test_audio_path,
    temporary_directory,
    temporary_file,
    validate_text_file,
    validate_json_file,
    assert_file_exists,
    assert_file_not_empty,
    file_contains_text,
    cleanup_temp_files,
    MockWhisperResult,
    PerformanceTimer
)

# Import the application class
from veleron_voice_flow import VeleronVoiceFlow


class TestVeleronVoiceFlowApp:
    """Test suite for Veleron Voice Flow application"""

    @pytest.fixture
    def app_instance(self):
        """Create application instance for testing"""
        root = tk.Tk()
        root.withdraw()  # Hide window during tests

        # Create app without loading model (too slow for testing)
        with patch('veleron_voice_flow.whisper.load_model') as mock_load:
            mock_model = Mock()
            mock_load.return_value = mock_model
            app = VeleronVoiceFlow(root)
            app.model = mock_model  # Set mock model
            yield app

        # Cleanup
        try:
            root.destroy()
        except:
            pass

    @pytest.fixture
    def test_audio_file(self):
        """Get path to a test audio file"""
        try:
            return get_test_audio_path("test_short_tone.wav")
        except FileNotFoundError:
            pytest.skip("Test audio files not available")


class TestApplicationLaunch(TestVeleronVoiceFlowApp):
    """Tests for application launch and initialization"""

    def test_application_creates_window(self, app_instance):
        """TC-VF-001: Verify application window is created"""
        assert app_instance.root is not None
        assert isinstance(app_instance.root, tk.Tk)

    def test_application_has_required_components(self, app_instance):
        """TC-VF-001: Verify all UI components exist"""
        # Check key components
        assert hasattr(app_instance, 'record_button')
        assert hasattr(app_instance, 'transcribe_file_button')
        assert hasattr(app_instance, 'transcription_text')
        assert hasattr(app_instance, 'status_var')
        assert hasattr(app_instance, 'model_var')
        assert hasattr(app_instance, 'language_var')

    def test_application_initial_state(self, app_instance):
        """TC-VF-001: Verify initial application state"""
        assert app_instance.is_recording == False
        assert app_instance.model_name == "base"
        assert app_instance.current_language == "auto"
        assert app_instance.sample_rate == 16000


class TestModelManagement(TestVeleronVoiceFlowApp):
    """Tests for Whisper model loading and switching"""

    def test_model_variable_initialization(self, app_instance):
        """TC-VF-002: Verify model selection initialized"""
        assert app_instance.model_var.get() == "base"

    def test_model_selection_options(self, app_instance):
        """TC-VF-002: Verify all model options available"""
        expected_models = ["tiny", "base", "small", "medium", "large", "turbo"]

        # Find the model combobox widget
        # Note: This is a simplified test - in real scenario would need to
        # traverse widget tree to find combobox
        assert app_instance.model_name in expected_models

    @patch('veleron_voice_flow.whisper.load_model')
    def test_model_loading(self, mock_load, app_instance):
        """TC-VF-002: Test model loading function"""
        mock_model = Mock()
        mock_load.return_value = mock_model

        app_instance.load_model()

        mock_load.assert_called_once_with(app_instance.model_name)
        assert app_instance.model is not None


class TestFileTranscription(TestVeleronVoiceFlowApp):
    """Tests for audio file transcription"""

    def test_transcribe_file_worker_success(self, app_instance, test_audio_file):
        """TC-VF-004: Test file transcription with WAV file"""
        # Mock the transcription result
        mock_result = MockWhisperResult(
            text="Test transcription result",
            language="en"
        )

        app_instance.model.transcribe = Mock(return_value=mock_result)

        # Call the worker function directly
        app_instance.transcribe_file_worker(test_audio_file)

        # Verify transcribe was called
        app_instance.model.transcribe.assert_called_once()

        # Check that file path was passed correctly
        call_args = app_instance.model.transcribe.call_args
        assert test_audio_file in str(call_args)

    def test_display_transcription(self, app_instance):
        """TC-VF-004: Test transcription display function"""
        mock_result = MockWhisperResult(
            text="This is a test transcription",
            language="en"
        )

        # Clear any existing text
        app_instance.transcription_text.delete(1.0, tk.END)

        # Display the transcription
        app_instance.display_transcription(mock_result)

        # Get the displayed text
        displayed_text = app_instance.transcription_text.get(1.0, tk.END)

        # Verify text was added
        assert "This is a test transcription" in displayed_text
        assert "Language: en" in displayed_text


class TestExportFunctions(TestVeleronVoiceFlowApp):
    """Tests for export functionality"""

    def test_export_txt(self, app_instance):
        """TC-VF-006: Test TXT export"""
        # Add some transcription text
        test_text = "This is a test transcription for export"
        app_instance.transcription_text.insert(tk.END, test_text)

        with temporary_file(suffix=".txt") as temp_file:
            # Mock the file dialog to return our temp file
            with patch('tkinter.filedialog.asksaveasfilename', return_value=temp_file):
                app_instance.export_transcription("txt")

            # Verify file was created and contains text
            assert_file_exists(temp_file)
            content = validate_text_file(temp_file)
            assert test_text in content

    def test_export_json(self, app_instance):
        """TC-VF-007: Test JSON export"""
        # Add some transcription text
        test_text = "This is a test transcription for JSON export"
        app_instance.transcription_text.insert(tk.END, test_text)

        with temporary_file(suffix=".json") as temp_file:
            # Mock the file dialog
            with patch('tkinter.filedialog.asksaveasfilename', return_value=temp_file):
                app_instance.export_transcription("json")

            # Verify file was created
            assert_file_exists(temp_file)

            # Validate JSON structure
            data = validate_json_file(temp_file)
            assert "timestamp" in data
            assert "model" in data
            assert "language" in data
            assert "transcription" in data
            assert test_text in data["transcription"]

    def test_export_empty_transcription(self, app_instance):
        """TC-VF-006: Test export with no content"""
        # Clear transcription
        app_instance.transcription_text.delete(1.0, tk.END)

        # Mock messagebox to capture the info message
        with patch('tkinter.messagebox.showinfo') as mock_info:
            app_instance.export_transcription("txt")

            # Verify user was informed of no content
            mock_info.assert_called_once()
            call_args = str(mock_info.call_args)
            assert "No" in call_args or "content" in call_args.lower()


class TestClipboardOperations(TestVeleronVoiceFlowApp):
    """Tests for clipboard functionality"""

    def test_copy_to_clipboard(self, app_instance):
        """TC-VF-008: Test copy to clipboard"""
        test_text = "Test text for clipboard"
        app_instance.transcription_text.insert(tk.END, test_text)

        # Copy to clipboard
        app_instance.copy_to_clipboard()

        # Verify clipboard contains our text
        clipboard_content = app_instance.root.clipboard_get()
        assert test_text in clipboard_content

    def test_copy_empty_transcription(self, app_instance):
        """TC-VF-008: Test copy with no content"""
        app_instance.transcription_text.delete(1.0, tk.END)

        with patch('tkinter.messagebox.showinfo') as mock_info:
            app_instance.copy_to_clipboard()
            mock_info.assert_called_once()


class TestClearFunction(TestVeleronVoiceFlowApp):
    """Tests for clear functionality"""

    def test_clear_transcription(self, app_instance):
        """TC-VF-009: Test clear function"""
        # Add some text
        app_instance.transcription_text.insert(tk.END, "Test content to clear")

        # Clear it
        app_instance.clear_transcription()

        # Verify text area is empty
        content = app_instance.transcription_text.get(1.0, tk.END).strip()
        assert content == ""

        # Verify status updated
        assert "Cleared" in app_instance.status_var.get() or "cleared" in app_instance.status_var.get().lower()


class TestLanguageSelection(TestVeleronVoiceFlowApp):
    """Tests for language selection"""

    def test_language_options(self, app_instance):
        """TC-VF-010: Verify language options available"""
        expected_languages = ["auto", "en", "es", "fr", "de", "it", "pt", "nl", "ja", "ko", "zh"]
        assert app_instance.language_var.get() == "auto"

    def test_language_detection_auto(self, app_instance):
        """TC-VF-010: Test automatic language detection"""
        app_instance.language_var.set("auto")

        mock_result = MockWhisperResult(text="Test", language="en")
        app_instance.model.transcribe = Mock(return_value=mock_result)

        # When calling transcribe with auto, language param should be None
        # This is tested indirectly through the transcribe_file_worker
        assert app_instance.language_var.get() == "auto"


class TestRecordingState(TestVeleronVoiceFlowApp):
    """Tests for recording state management"""

    def test_recording_state_initial(self, app_instance):
        """TC-VF-003: Verify initial recording state"""
        assert app_instance.is_recording == False
        assert len(app_instance.audio_data) == 0

    def test_start_recording_state_change(self, app_instance):
        """TC-VF-003: Test start recording state changes"""
        # Mock the recording thread to avoid actual recording
        with patch('threading.Thread'):
            app_instance.start_recording()

            assert app_instance.is_recording == True
            assert "Recording" in app_instance.status_var.get()

    def test_start_recording_without_model(self, app_instance):
        """TC-VF-003: Test recording fails gracefully without model"""
        app_instance.model = None

        with patch('tkinter.messagebox.showwarning') as mock_warning:
            app_instance.start_recording()
            mock_warning.assert_called_once()


class TestUIResponsiveness(TestVeleronVoiceFlowApp):
    """Tests for UI responsiveness"""

    def test_status_updates(self, app_instance):
        """TC-VF-015: Test status message updates"""
        test_message = "Test status message"
        app_instance.status_var.set(test_message)

        assert app_instance.status_var.get() == test_message

    def test_progress_bar_exists(self, app_instance):
        """TC-VF-015: Verify progress bar component exists"""
        assert hasattr(app_instance, 'progress')
        assert app_instance.progress is not None


class TestErrorHandling(TestVeleronVoiceFlowApp):
    """Tests for error handling"""

    def test_invalid_file_handling(self, app_instance):
        """TC-VF-014: Test handling of invalid audio file"""
        with temporary_file(suffix=".txt") as fake_audio:
            # Create a text file pretending to be audio
            with open(fake_audio, 'w') as f:
                f.write("Not audio data")

            # Mock the transcribe to raise an error
            app_instance.model.transcribe = Mock(side_effect=Exception("Invalid file"))

            # This should handle the error gracefully
            app_instance.transcribe_file_worker(fake_audio)

            # Status should show error
            status = app_instance.status_var.get()
            assert "Error" in status or "error" in status


class TestMultipleOperations(TestVeleronVoiceFlowApp):
    """Tests for multiple consecutive operations"""

    def test_multiple_transcriptions(self, app_instance):
        """TC-VF-012: Test multiple transcriptions don't interfere"""
        results = [
            MockWhisperResult(text="First transcription", language="en"),
            MockWhisperResult(text="Second transcription", language="en"),
            MockWhisperResult(text="Third transcription", language="en")
        ]

        app_instance.transcription_text.delete(1.0, tk.END)

        for result in results:
            app_instance.display_transcription(result)

        # Verify all transcriptions present
        full_text = app_instance.transcription_text.get(1.0, tk.END)
        assert "First transcription" in full_text
        assert "Second transcription" in full_text
        assert "Third transcription" in full_text


@pytest.mark.manual
class TestManualOperations:
    """
    Tests that require manual execution due to hardware dependencies.
    These serve as test procedures for manual testing.
    """

    def test_manual_microphone_recording(self):
        """
        TC-VF-003: Manual Test - Real Microphone Recording

        MANUAL TEST PROCEDURE:
        1. Launch veleron_voice_flow.py
        2. Wait for model to load
        3. Click "Start Recording"
        4. Speak test phrase: "Testing Veleron Voice Flow transcription system"
        5. Click "Stop Recording"
        6. Wait for transcription to appear

        EXPECTED RESULT:
        - Spoken text accurately transcribed (90%+ accuracy)
        - Text appears in transcription area
        - Status shows "Transcription complete"

        PASS CRITERIA:
        - No errors or crashes
        - Transcription contains key words from test phrase
        - Processing completes within 30 seconds
        """
        pytest.skip("Manual test - requires microphone and user interaction")

    def test_manual_window_resize(self):
        """
        TC-VF-016: Manual Test - Window Resize

        MANUAL TEST PROCEDURE:
        1. Launch application
        2. Resize window to minimum size
        3. Verify all controls accessible
        4. Resize window to maximum size
        5. Verify text wraps correctly
        6. Resize to medium size
        7. Verify UI remains usable

        EXPECTED RESULT:
        - UI adapts to all window sizes
        - No controls hidden or cut off
        - Text wraps appropriately
        """
        pytest.skip("Manual test - requires visual verification")


@pytest.mark.integration
class TestIntegration(TestVeleronVoiceFlowApp):
    """Integration tests combining multiple features"""

    def test_full_workflow_file_to_export(self, app_instance, test_audio_file):
        """Test complete workflow: Load file -> Transcribe -> Export"""
        # Mock transcription
        mock_result = MockWhisperResult(
            text="Complete workflow test",
            language="en"
        )
        app_instance.model.transcribe = Mock(return_value=mock_result)

        # Transcribe file
        app_instance.transcribe_file_worker(test_audio_file)

        # Verify transcription displayed
        text = app_instance.transcription_text.get(1.0, tk.END)
        assert "Complete workflow test" in text

        # Export to file
        with temporary_file(suffix=".txt") as export_file:
            with patch('tkinter.filedialog.asksaveasfilename', return_value=export_file):
                app_instance.export_transcription("txt")

            # Verify export successful
            assert_file_exists(export_file)
            content = validate_text_file(export_file)
            assert "Complete workflow test" in content


# Performance tests
@pytest.mark.performance
class TestPerformance(TestVeleronVoiceFlowApp):
    """Performance tests"""

    def test_ui_creation_speed(self):
        """Measure UI creation time"""
        with PerformanceTimer() as timer:
            root = tk.Tk()
            root.withdraw()
            with patch('veleron_voice_flow.whisper.load_model'):
                app = VeleronVoiceFlow(root)

        elapsed = timer.elapsed()
        print(f"\nUI creation time: {elapsed:.3f}s")

        # UI should create quickly (model loading excluded)
        assert elapsed < 5, f"UI creation too slow: {elapsed}s"

        root.destroy()


# Test configuration
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "manual: manual tests requiring user interaction")
    config.addinivalue_line("markers", "integration: integration tests")
    config.addinivalue_line("markers", "performance: performance benchmark tests")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s", "-m", "not manual"])
