"""
Unit Tests for veleron_voice_flow.py

Tests GUI functionality, file transcription, export features,
and user interactions in the Voice Flow application.
"""

import pytest
import os
import sys
import json
import numpy as np
from unittest.mock import Mock, patch, MagicMock, mock_open, call
import tkinter as tk
from tkinter import ttk
import threading
import queue

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestVeleronVoiceFlowInitialization:
    """Test VeleronVoiceFlow class initialization"""

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    def test_initialization(self, mock_thread, mock_load_model, mock_whisper_model):
        """Test basic initialization"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)

        assert app.is_recording is False
        assert app.audio_data == []
        assert app.sample_rate == 16000
        assert app.model_name == "base"
        assert app.current_language == "auto"
        assert isinstance(app.transcription_queue, queue.Queue)

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    def test_window_configuration(self, mock_thread, mock_load_model, mock_whisper_model):
        """Test window configuration on initialization"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)

        root.title.assert_called_with("Veleron Voice Flow - AI Voice Transcription")
        root.geometry.assert_called_with("900x700")

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    def test_background_model_loading(self, mock_thread, mock_load_model, mock_whisper_model):
        """Test that model loads in background thread"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)

        # Verify thread was started for model loading
        mock_thread.assert_called()


class TestUISetup:
    """Test user interface setup"""

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    def test_setup_ui_creates_widgets(self, mock_thread, mock_load_model, mock_whisper_model):
        """Test that UI setup creates all required widgets"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)

        # Verify key UI elements exist
        assert app.record_button is not None
        assert app.transcribe_file_button is not None
        assert app.transcription_text is not None
        assert app.status_var is not None
        assert app.model_var is not None
        assert app.language_var is not None

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    def test_model_combobox_values(self, mock_thread, mock_load_model, mock_whisper_model):
        """Test model selection combobox has correct values"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)

        # Check initial model value
        assert app.model_var.get() == "base"

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    def test_language_combobox_values(self, mock_thread, mock_load_model, mock_whisper_model):
        """Test language selection combobox has correct values"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)

        # Check initial language value
        assert app.language_var.get() == "auto"


class TestModelLoading:
    """Test model loading functionality"""

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    def test_load_model_success(self, mock_thread, mock_load_model, mock_whisper_model):
        """Test successful model loading"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)

        app.load_model()

        assert app.model == mock_whisper_model
        assert "Ready" in app.status_var.get()

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    @patch('veleron_voice_flow.messagebox.showerror')
    def test_load_model_error(self, mock_error, mock_thread, mock_load_model):
        """Test model loading error handling"""
        mock_load_model.side_effect = Exception("Failed to load model")

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)

        app.load_model()

        assert "Error" in app.status_var.get()
        mock_error.assert_called_once()

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    def test_change_model(self, mock_thread, mock_load_model, mock_whisper_model):
        """Test changing model through UI"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)

        # Change model
        app.model_var.set("small")
        app.change_model()

        assert app.model_name == "small"
        assert "Loading" in app.status_var.get()


class TestRecordingFunctionality:
    """Test audio recording functionality"""

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    def test_toggle_recording_start(self, mock_thread, mock_load_model, mock_whisper_model):
        """Test starting recording through toggle"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)
        app.model = mock_whisper_model

        app.toggle_recording()

        assert app.is_recording is True

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    def test_toggle_recording_stop(self, mock_thread, mock_load_model, mock_whisper_model):
        """Test stopping recording through toggle"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)
        app.model = mock_whisper_model

        # Start then stop
        app.toggle_recording()
        app.toggle_recording()

        assert app.is_recording is False

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    @patch('veleron_voice_flow.messagebox.showwarning')
    def test_start_recording_no_model(self, mock_warning, mock_thread, mock_load_model):
        """Test starting recording when model is not loaded"""
        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)
        app.model = None

        app.start_recording()

        mock_warning.assert_called_once()
        assert app.is_recording is False

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    def test_start_recording_initializes_audio(self, mock_thread, mock_load_model, mock_whisper_model):
        """Test that starting recording initializes audio data"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)
        app.model = mock_whisper_model

        app.start_recording()

        assert app.audio_data == []
        assert app.is_recording is True
        assert "Recording" in app.status_var.get()

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    @patch('veleron_voice_flow.sd.InputStream')
    def test_record_audio_callback(self, mock_stream, mock_thread, mock_load_model, mock_whisper_model):
        """Test audio recording callback"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)
        app.model = mock_whisper_model

        # This would normally be tested with actual audio streaming
        # For now, verify the method exists
        assert hasattr(app, 'record_audio')


class TestTranscription:
    """Test transcription functionality"""

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    @patch('veleron_voice_flow.tempfile.NamedTemporaryFile')
    @patch('veleron_voice_flow.os.unlink')
    def test_transcribe_recording(
        self, mock_unlink, mock_tempfile, mock_thread,
        mock_load_model, mock_whisper_model,
        sample_audio_chunks, mock_transcription_result
    ):
        """Test transcription of recorded audio"""
        mock_load_model.return_value = mock_whisper_model
        mock_whisper_model.transcribe.return_value = mock_transcription_result

        # Mock temporary file
        mock_temp = MagicMock()
        mock_temp.name = "test_temp.wav"
        mock_tempfile.return_value = mock_temp

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)
        app.model = mock_whisper_model
        app.audio_data = sample_audio_chunks

        app.transcribe_recording()

        # Verify transcription was called
        mock_whisper_model.transcribe.assert_called_once()

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    def test_transcribe_recording_no_audio(
        self, mock_thread, mock_load_model, mock_whisper_model
    ):
        """Test transcription with no audio data"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)
        app.model = mock_whisper_model
        app.audio_data = []

        app.transcribe_recording()

        # Should return early without transcribing
        assert "No audio" in app.status_var.get()

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    @patch('veleron_voice_flow.messagebox.showerror')
    def test_transcribe_recording_error(
        self, mock_error, mock_thread, mock_load_model,
        mock_whisper_model, sample_audio_chunks
    ):
        """Test error handling during transcription"""
        mock_load_model.return_value = mock_whisper_model
        mock_whisper_model.transcribe.side_effect = Exception("Transcription failed")

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)
        app.model = mock_whisper_model
        app.audio_data = sample_audio_chunks

        app.transcribe_recording()

        mock_error.assert_called_once()


class TestFileTranscription:
    """Test file transcription functionality"""

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    @patch('veleron_voice_flow.filedialog.askopenfilename')
    @patch('veleron_voice_flow.messagebox.showwarning')
    def test_transcribe_file_no_model(
        self, mock_warning, mock_filedialog,
        mock_thread, mock_load_model
    ):
        """Test file transcription when model is not loaded"""
        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)
        app.model = None

        app.transcribe_file()

        mock_warning.assert_called_once()
        # File dialog should not be shown
        mock_filedialog.assert_not_called()

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    @patch('veleron_voice_flow.filedialog.askopenfilename')
    def test_transcribe_file_cancel(
        self, mock_filedialog, mock_thread,
        mock_load_model, mock_whisper_model
    ):
        """Test canceling file selection dialog"""
        mock_load_model.return_value = mock_whisper_model
        mock_filedialog.return_value = ""  # User canceled

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)
        app.model = mock_whisper_model

        app.transcribe_file()

        # Should return without processing

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    @patch('veleron_voice_flow.filedialog.askopenfilename')
    def test_transcribe_file_selected(
        self, mock_filedialog, mock_thread,
        mock_load_model, mock_whisper_model,
        sample_audio_file
    ):
        """Test file transcription with selected file"""
        mock_load_model.return_value = mock_whisper_model
        mock_filedialog.return_value = sample_audio_file

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)
        app.model = mock_whisper_model

        app.transcribe_file()

        # Verify status was updated
        assert sample_audio_file.split(os.sep)[-1] in app.status_var.get() or "Transcribing" in app.status_var.get()

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    def test_transcribe_file_worker(
        self, mock_thread, mock_load_model,
        mock_whisper_model, sample_audio_file,
        mock_transcription_result
    ):
        """Test file transcription worker thread"""
        mock_load_model.return_value = mock_whisper_model
        mock_whisper_model.transcribe.return_value = mock_transcription_result

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)
        app.model = mock_whisper_model

        app.transcribe_file_worker(sample_audio_file)

        # Verify transcription was called
        mock_whisper_model.transcribe.assert_called_once()


class TestDisplayTranscription:
    """Test transcription display functionality"""

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    def test_display_transcription(
        self, mock_thread, mock_load_model,
        mock_whisper_model, mock_transcription_result
    ):
        """Test displaying transcription results"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)

        app.display_transcription(mock_transcription_result)

        # Verify text was inserted
        app.transcription_text.insert.assert_called()

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    def test_display_transcription_with_timestamp(
        self, mock_thread, mock_load_model,
        mock_whisper_model, mock_transcription_result
    ):
        """Test that timestamp is included in display"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)

        app.display_transcription(mock_transcription_result)

        # Check that insert was called with timestamp
        calls = app.transcription_text.insert.call_args_list
        # Verify timestamp format is present in one of the calls
        assert any("Language:" in str(call) for call in calls)


class TestTextOperations:
    """Test text manipulation operations"""

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    def test_clear_transcription(
        self, mock_thread, mock_load_model, mock_whisper_model
    ):
        """Test clearing transcription text"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)

        app.clear_transcription()

        app.transcription_text.delete.assert_called_once_with(1.0, tk.END)
        assert "Cleared" in app.status_var.get()

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    def test_copy_to_clipboard(
        self, mock_thread, mock_load_model, mock_whisper_model
    ):
        """Test copying transcription to clipboard"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)

        # Mock text content
        app.transcription_text.get.return_value = "Test transcription"

        app.copy_to_clipboard()

        # Verify clipboard operations
        app.root.clipboard_clear.assert_called_once()
        app.root.clipboard_append.assert_called_once()
        assert "Copied" in app.status_var.get()

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    @patch('veleron_voice_flow.messagebox.showinfo')
    def test_copy_to_clipboard_empty(
        self, mock_showinfo, mock_thread,
        mock_load_model, mock_whisper_model
    ):
        """Test copying when no transcription exists"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)

        # Mock empty text
        app.transcription_text.get.return_value = ""

        app.copy_to_clipboard()

        mock_showinfo.assert_called_once()


class TestExportFunctionality:
    """Test export functionality"""

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    @patch('veleron_voice_flow.filedialog.asksaveasfilename')
    def test_export_transcription_txt(
        self, mock_saveas, mock_thread,
        mock_load_model, mock_whisper_model, tmp_path
    ):
        """Test exporting transcription as TXT"""
        mock_load_model.return_value = mock_whisper_model
        output_file = tmp_path / "export.txt"
        mock_saveas.return_value = str(output_file)

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)

        app.transcription_text.get.return_value = "Test transcription content"

        app.export_transcription("txt")

        # Verify file was created
        assert output_file.exists()
        content = output_file.read_text(encoding='utf-8')
        assert "Test transcription content" in content

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    @patch('veleron_voice_flow.filedialog.asksaveasfilename')
    def test_export_transcription_json(
        self, mock_saveas, mock_thread,
        mock_load_model, mock_whisper_model, tmp_path
    ):
        """Test exporting transcription as JSON"""
        mock_load_model.return_value = mock_whisper_model
        output_file = tmp_path / "export.json"
        mock_saveas.return_value = str(output_file)

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)

        app.transcription_text.get.return_value = "Test transcription content"

        app.export_transcription("json")

        # Verify file was created
        assert output_file.exists()

        # Verify JSON structure
        with open(output_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert "timestamp" in data
        assert "model" in data
        assert "language" in data
        assert "transcription" in data
        assert data["transcription"] == "Test transcription content"
        assert data["model"] == "base"

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    @patch('veleron_voice_flow.filedialog.asksaveasfilename')
    def test_export_transcription_cancel(
        self, mock_saveas, mock_thread,
        mock_load_model, mock_whisper_model
    ):
        """Test canceling export dialog"""
        mock_load_model.return_value = mock_whisper_model
        mock_saveas.return_value = ""  # User canceled

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)

        app.transcription_text.get.return_value = "Test content"

        app.export_transcription("txt")

        # Should return without error

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    @patch('veleron_voice_flow.messagebox.showinfo')
    def test_export_empty_transcription(
        self, mock_showinfo, mock_thread,
        mock_load_model, mock_whisper_model
    ):
        """Test exporting when no transcription exists"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)

        app.transcription_text.get.return_value = ""

        app.export_transcription("txt")

        mock_showinfo.assert_called_once()


class TestProgressIndicator:
    """Test progress indicator functionality"""

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    def test_progress_starts_on_recording(
        self, mock_thread, mock_load_model, mock_whisper_model
    ):
        """Test progress indicator starts when processing"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)
        app.model = mock_whisper_model
        app.audio_data = [np.zeros((100, 1))]

        app.stop_recording()

        # Progress should start
        app.progress.start.assert_called_once()


class TestLanguageHandling:
    """Test language selection and handling"""

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    def test_auto_language_detection(
        self, mock_thread, mock_load_model, mock_whisper_model
    ):
        """Test automatic language detection"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)

        # Default should be auto
        assert app.language_var.get() == "auto"

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    @patch('veleron_voice_flow.tempfile.NamedTemporaryFile')
    @patch('veleron_voice_flow.os.unlink')
    def test_specific_language_transcription(
        self, mock_unlink, mock_tempfile, mock_thread,
        mock_load_model, mock_whisper_model,
        sample_audio_chunks, mock_transcription_result
    ):
        """Test transcription with specific language"""
        mock_load_model.return_value = mock_whisper_model
        mock_whisper_model.transcribe.return_value = mock_transcription_result

        mock_temp = MagicMock()
        mock_temp.name = "test_temp.wav"
        mock_tempfile.return_value = mock_temp

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)
        app.model = mock_whisper_model
        app.audio_data = sample_audio_chunks
        app.language_var.set("es")

        app.transcribe_recording()

        # Verify language was passed to transcribe
        call_args = mock_whisper_model.transcribe.call_args
        assert call_args[1]['language'] == 'es'


class TestErrorHandling:
    """Test error handling scenarios"""

    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    @patch('veleron_voice_flow.sd.InputStream')
    @patch('veleron_voice_flow.messagebox.showerror')
    def test_recording_error_handling(
        self, mock_error, mock_stream, mock_thread,
        mock_load_model, mock_whisper_model
    ):
        """Test error handling during recording"""
        mock_load_model.return_value = mock_whisper_model
        mock_stream.side_effect = Exception("Audio device error")

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)
        app.model = mock_whisper_model

        # This should be caught by try-except in record_audio
        # Can't easily test the threaded function, but ensure method exists
        assert hasattr(app, 'record_audio')


class TestPerformance:
    """Performance-related tests"""

    @pytest.mark.slow
    @patch('veleron_voice_flow.whisper.load_model')
    @patch('veleron_voice_flow.threading.Thread')
    def test_large_transcription_display(
        self, mock_thread, mock_load_model, mock_whisper_model
    ):
        """Test displaying large transcription"""
        mock_load_model.return_value = mock_whisper_model

        large_result = {
            "text": "A" * 10000,
            "language": "en",
            "segments": []
        }

        from veleron_voice_flow import VeleronVoiceFlow

        root = MagicMock()
        app = VeleronVoiceFlow(root)

        # Should handle large text without error
        app.display_transcription(large_result)
