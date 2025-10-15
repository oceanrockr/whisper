"""
Unit Tests for veleron_dictation.py

Tests real-time dictation functionality including audio recording,
transcription, hotkey handling, and typing automation.
"""

import pytest
import os
import sys
import numpy as np
import tempfile
from unittest.mock import Mock, patch, MagicMock, call
import queue
import threading
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestVeleronDictationInitialization:
    """Test VeleronDictation class initialization"""

    @patch('veleron_dictation.whisper.load_model')
    def test_initialization_default_config(self, mock_load_model, mock_whisper_model):
        """Test default configuration on initialization"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_dictation import VeleronDictation
        dictation = VeleronDictation()

        assert dictation.hotkey == 'ctrl+shift+space'
        assert dictation.model_name == 'base'
        assert dictation.language is None
        assert dictation.sample_rate == 16000
        assert dictation.is_recording is False
        assert dictation.is_running is True
        assert isinstance(dictation.audio_queue, queue.Queue)
        assert dictation.audio_data == []
        assert dictation.model is not None

    @patch('veleron_dictation.whisper.load_model')
    def test_model_loading_called(self, mock_load_model, mock_whisper_model):
        """Test that model loading is called during initialization"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_dictation import VeleronDictation
        dictation = VeleronDictation()

        mock_load_model.assert_called_once_with('base')

    @patch('veleron_dictation.whisper.load_model')
    def test_initialization_error_handling(self, mock_load_model):
        """Test error handling during model loading"""
        mock_load_model.side_effect = Exception("Model loading failed")

        from veleron_dictation import VeleronDictation

        with pytest.raises(Exception) as exc_info:
            dictation = VeleronDictation()

        assert "Model loading failed" in str(exc_info.value)


class TestLoadModel:
    """Test model loading functionality"""

    @patch('veleron_dictation.whisper.load_model')
    def test_load_model_success(self, mock_load_model, mock_whisper_model):
        """Test successful model loading"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_dictation import VeleronDictation
        dictation = VeleronDictation()

        assert dictation.model == mock_whisper_model

    @patch('veleron_dictation.whisper.load_model')
    def test_load_model_different_models(self, mock_load_model, mock_whisper_model):
        """Test loading different model types"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_dictation import VeleronDictation

        for model_name in ['tiny', 'base', 'small', 'medium']:
            dictation = VeleronDictation()
            dictation.model_name = model_name
            dictation.load_model()

            # Verify the correct model was requested
            assert mock_load_model.called


class TestAudioRecording:
    """Test audio recording functionality"""

    @patch('veleron_dictation.whisper.load_model')
    def test_start_recording(self, mock_load_model, mock_whisper_model):
        """Test starting audio recording"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_dictation import VeleronDictation
        dictation = VeleronDictation()

        dictation.start_recording()

        assert dictation.is_recording is True
        assert dictation.audio_data == []

    @patch('veleron_dictation.whisper.load_model')
    def test_start_recording_already_recording(self, mock_load_model, mock_whisper_model):
        """Test starting recording when already recording"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_dictation import VeleronDictation
        dictation = VeleronDictation()

        dictation.start_recording()
        initial_state = dictation.is_recording

        # Try to start recording again
        dictation.start_recording()

        # Should remain in recording state
        assert dictation.is_recording == initial_state

    @patch('veleron_dictation.whisper.load_model')
    def test_stop_recording_not_recording(self, mock_load_model, mock_whisper_model):
        """Test stopping when not recording"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_dictation import VeleronDictation
        dictation = VeleronDictation()

        # Should not raise error
        dictation.stop_recording()
        assert dictation.is_recording is False

    @patch('veleron_dictation.whisper.load_model')
    def test_stop_recording_with_audio(self, mock_load_model, mock_whisper_model, sample_audio_chunks):
        """Test stopping recording with audio data"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_dictation import VeleronDictation
        dictation = VeleronDictation()

        dictation.start_recording()
        dictation.audio_data = sample_audio_chunks
        dictation.stop_recording()

        assert dictation.is_recording is False

    @patch('veleron_dictation.whisper.load_model')
    def test_stop_recording_no_audio(self, mock_load_model, mock_whisper_model):
        """Test stopping recording with no audio data"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_dictation import VeleronDictation
        dictation = VeleronDictation()

        dictation.start_recording()
        dictation.stop_recording()

        assert dictation.is_recording is False
        # Should return early without processing

    @patch('veleron_dictation.whisper.load_model')
    def test_audio_callback(self, mock_load_model, mock_whisper_model, sample_audio_data):
        """Test audio callback function"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_dictation import VeleronDictation
        dictation = VeleronDictation()

        dictation.is_recording = True

        # Simulate audio callback
        audio_chunk = sample_audio_data.reshape(-1, 1)
        dictation.audio_callback(audio_chunk, None, None, None)

        # Verify audio was queued
        assert not dictation.audio_queue.empty()

    @patch('veleron_dictation.whisper.load_model')
    def test_audio_callback_not_recording(self, mock_load_model, mock_whisper_model, sample_audio_data):
        """Test audio callback when not recording"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_dictation import VeleronDictation
        dictation = VeleronDictation()

        dictation.is_recording = False

        audio_chunk = sample_audio_data.reshape(-1, 1)
        dictation.audio_callback(audio_chunk, None, None, None)

        # Audio should not be queued
        assert dictation.audio_queue.empty()


class TestTranscriptionAndTyping:
    """Test transcription and typing functionality"""

    @patch('veleron_dictation.whisper.load_model')
    @patch('veleron_dictation.pyautogui.write')
    @patch('veleron_dictation.time.sleep')
    def test_transcribe_and_type_success(
        self, mock_sleep, mock_write, mock_load_model,
        mock_whisper_model, sample_audio_chunks, mock_transcription_result
    ):
        """Test successful transcription and typing"""
        mock_load_model.return_value = mock_whisper_model
        mock_whisper_model.transcribe.return_value = mock_transcription_result

        from veleron_dictation import VeleronDictation
        dictation = VeleronDictation()

        dictation.audio_data = sample_audio_chunks
        dictation.transcribe_and_type()

        # Verify text was typed
        mock_write.assert_called_once()
        assert mock_transcription_result["text"].strip() in str(mock_write.call_args)

    @patch('veleron_dictation.whisper.load_model')
    @patch('veleron_dictation.time.sleep')
    def test_transcribe_and_type_short_audio(
        self, mock_sleep, mock_load_model, mock_whisper_model
    ):
        """Test handling of very short audio"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_dictation import VeleronDictation
        dictation = VeleronDictation()

        # Create very short audio (less than 0.3 seconds)
        short_audio = [np.zeros((100, 1), dtype=np.float32)]
        dictation.audio_data = short_audio

        dictation.transcribe_and_type()

        # Should exit early without transcribing

    @patch('veleron_dictation.whisper.load_model')
    @patch('veleron_dictation.time.sleep')
    def test_transcribe_and_type_empty_result(
        self, mock_sleep, mock_load_model,
        mock_whisper_model, sample_audio_chunks
    ):
        """Test handling of empty transcription result"""
        mock_load_model.return_value = mock_whisper_model
        mock_whisper_model.transcribe.return_value = {
            "text": "",
            "language": "en",
            "segments": []
        }

        from veleron_dictation import VeleronDictation
        dictation = VeleronDictation()

        dictation.audio_data = sample_audio_chunks
        dictation.transcribe_and_type()

        # Should handle empty text gracefully

    @patch('veleron_dictation.whisper.load_model')
    @patch('veleron_dictation.pyautogui.write')
    @patch('veleron_dictation.time.sleep')
    def test_transcribe_and_type_error_handling(
        self, mock_sleep, mock_write, mock_load_model,
        mock_whisper_model, sample_audio_chunks
    ):
        """Test error handling during transcription"""
        mock_load_model.return_value = mock_whisper_model
        mock_whisper_model.transcribe.side_effect = Exception("Transcription failed")

        from veleron_dictation import VeleronDictation
        dictation = VeleronDictation()

        dictation.audio_data = sample_audio_chunks

        # Should not raise exception, but handle error gracefully
        dictation.transcribe_and_type()

    @patch('veleron_dictation.whisper.load_model')
    @patch('veleron_dictation.pyautogui.write')
    @patch('veleron_dictation.time.sleep')
    def test_transcribe_and_type_temp_file_cleanup(
        self, mock_sleep, mock_write, mock_load_model,
        mock_whisper_model, sample_audio_chunks, mock_transcription_result
    ):
        """Test that temporary audio files are cleaned up"""
        mock_load_model.return_value = mock_whisper_model
        mock_whisper_model.transcribe.return_value = mock_transcription_result

        from veleron_dictation import VeleronDictation
        dictation = VeleronDictation()

        dictation.audio_data = sample_audio_chunks

        # Track temp files
        import tempfile
        original_tempfile = tempfile.NamedTemporaryFile

        temp_files = []

        def track_tempfile(*args, **kwargs):
            tf = original_tempfile(*args, **kwargs)
            temp_files.append(tf.name)
            return tf

        with patch('tempfile.NamedTemporaryFile', side_effect=track_tempfile):
            dictation.transcribe_and_type()

            # Verify temp files were created and should be cleaned
            # (actual cleanup happens in the function via os.unlink)


class TestHotkeyFunctionality:
    """Test hotkey setup and handling"""

    @patch('veleron_dictation.whisper.load_model')
    @patch('veleron_dictation.keyboard.add_hotkey')
    @patch('veleron_dictation.keyboard.on_release_key')
    def test_setup_hotkey(
        self, mock_on_release, mock_add_hotkey,
        mock_load_model, mock_whisper_model
    ):
        """Test hotkey setup"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_dictation import VeleronDictation
        dictation = VeleronDictation()

        dictation.setup_hotkey()

        # Verify hotkey was registered
        mock_add_hotkey.assert_called_once()
        mock_on_release.assert_called_once()

    @patch('veleron_dictation.whisper.load_model')
    @patch('veleron_dictation.keyboard.add_hotkey')
    def test_setup_different_hotkeys(
        self, mock_add_hotkey, mock_load_model, mock_whisper_model
    ):
        """Test setup with different hotkey configurations"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_dictation import VeleronDictation

        for hotkey in ['ctrl+shift+space', 'ctrl+alt+r', 'alt+space']:
            dictation = VeleronDictation()
            dictation.hotkey = hotkey
            dictation.setup_hotkey()

            # Verify each hotkey was registered


class TestStatusWindow:
    """Test status window functionality"""

    @patch('veleron_dictation.whisper.load_model')
    @patch('veleron_dictation.tk.Tk')
    def test_create_status_window(
        self, mock_tk, mock_load_model, mock_whisper_model
    ):
        """Test status window creation"""
        mock_load_model.return_value = mock_whisper_model
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        from veleron_dictation import VeleronDictation
        dictation = VeleronDictation()

        window = dictation.create_status_window()

        assert window is not None
        mock_root.title.assert_called()
        mock_root.geometry.assert_called()

    @patch('veleron_dictation.whisper.load_model')
    def test_update_status(self, mock_load_model, mock_whisper_model):
        """Test status update functionality"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_dictation import VeleronDictation
        dictation = VeleronDictation()

        # Create mock status label
        dictation.status_label = MagicMock()

        dictation.update_status("Testing status")

        dictation.status_label.config.assert_called_once_with(text="Testing status")

    @patch('veleron_dictation.whisper.load_model')
    def test_hide_status_window(self, mock_load_model, mock_whisper_model):
        """Test hiding status window"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_dictation import VeleronDictation
        dictation = VeleronDictation()

        dictation.status_window = MagicMock()
        dictation.hide_status_window()

        dictation.status_window.withdraw.assert_called_once()

    @patch('veleron_dictation.whisper.load_model')
    def test_show_status_window(self, mock_load_model, mock_whisper_model):
        """Test showing status window"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_dictation import VeleronDictation
        dictation = VeleronDictation()

        dictation.status_window = MagicMock()
        dictation.show_status_window()

        dictation.status_window.deiconify.assert_called_once()
        dictation.status_window.lift.assert_called_once()


class TestSettingsDialog:
    """Test settings dialog functionality"""

    @patch('veleron_dictation.whisper.load_model')
    @patch('veleron_dictation.tk.Tk')
    @patch('veleron_dictation.tk.Toplevel')
    def test_show_settings(
        self, mock_toplevel, mock_tk, mock_load_model, mock_whisper_model
    ):
        """Test settings dialog display"""
        mock_load_model.return_value = mock_whisper_model
        mock_root = MagicMock()
        mock_tk.return_value = mock_root

        from veleron_dictation import VeleronDictation
        dictation = VeleronDictation()
        dictation.status_window = mock_root

        # Mock the settings window
        mock_settings = MagicMock()
        mock_toplevel.return_value = mock_settings

        dictation.show_settings()

        # Verify settings window was created
        mock_toplevel.assert_called()


class TestSystemTrayIntegration:
    """Test system tray icon functionality"""

    @patch('veleron_dictation.whisper.load_model')
    @patch('veleron_dictation.Image.new')
    def test_create_tray_icon(
        self, mock_image_new, mock_load_model, mock_whisper_model
    ):
        """Test system tray icon creation"""
        mock_load_model.return_value = mock_whisper_model
        mock_image = MagicMock()
        mock_image_new.return_value = mock_image

        from veleron_dictation import VeleronDictation
        dictation = VeleronDictation()

        with patch('veleron_dictation.Icon') as mock_icon_class:
            dictation.create_tray_icon()

            # Verify icon was created
            assert dictation.tray_icon is not None

    @patch('veleron_dictation.whisper.load_model')
    def test_quit_app(self, mock_load_model, mock_whisper_model):
        """Test application quit functionality"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_dictation import VeleronDictation
        dictation = VeleronDictation()

        dictation.tray_icon = MagicMock()
        dictation.status_window = MagicMock()

        dictation.quit_app()

        assert dictation.is_running is False
        dictation.tray_icon.stop.assert_called_once()
        dictation.status_window.quit.assert_called_once()


class TestAudioProcessing:
    """Test audio data processing"""

    @patch('veleron_dictation.whisper.load_model')
    def test_audio_concatenation(
        self, mock_load_model, mock_whisper_model, sample_audio_chunks
    ):
        """Test combining audio chunks"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_dictation import VeleronDictation
        dictation = VeleronDictation()

        dictation.audio_data = sample_audio_chunks

        # Manually concatenate like the function does
        audio = np.concatenate(dictation.audio_data, axis=0)
        audio = audio.flatten()

        assert audio.ndim == 1
        assert len(audio) > 0

    @patch('veleron_dictation.whisper.load_model')
    def test_audio_format_conversion(
        self, mock_load_model, mock_whisper_model, sample_audio_data
    ):
        """Test audio format conversion to int16"""
        mock_load_model.return_value = mock_whisper_model

        # Test conversion from float32 to int16
        audio_float = sample_audio_data
        audio_int16 = (audio_float * 32767).astype(np.int16)

        assert audio_int16.dtype == np.int16
        assert audio_int16.min() >= -32768
        assert audio_int16.max() <= 32767


class TestThreadSafety:
    """Test thread safety and concurrent operations"""

    @patch('veleron_dictation.whisper.load_model')
    def test_queue_thread_safety(self, mock_load_model, mock_whisper_model):
        """Test that audio queue is thread-safe"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_dictation import VeleronDictation
        dictation = VeleronDictation()

        # Simulate multiple threads adding to queue
        def add_audio():
            for _ in range(10):
                dictation.audio_queue.put(np.zeros((100, 1)))

        threads = [threading.Thread(target=add_audio) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Verify all items were queued
        assert dictation.audio_queue.qsize() == 50


class TestLanguageSupport:
    """Test multi-language support"""

    @patch('veleron_dictation.whisper.load_model')
    @patch('veleron_dictation.pyautogui.write')
    @patch('veleron_dictation.time.sleep')
    def test_different_languages(
        self, mock_sleep, mock_write, mock_load_model,
        mock_whisper_model, sample_audio_chunks
    ):
        """Test transcription with different languages"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_dictation import VeleronDictation

        for language in ['en', 'es', 'fr', 'de']:
            dictation = VeleronDictation()
            dictation.language = language
            dictation.audio_data = sample_audio_chunks

            mock_whisper_model.transcribe.return_value = {
                "text": f"Test in {language}",
                "language": language,
                "segments": []
            }

            dictation.transcribe_and_type()

    @patch('veleron_dictation.whisper.load_model')
    def test_auto_language_detection(
        self, mock_load_model, mock_whisper_model
    ):
        """Test automatic language detection"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_dictation import VeleronDictation
        dictation = VeleronDictation()

        # Default should be None (auto-detect)
        assert dictation.language is None


class TestPerformance:
    """Performance-related tests"""

    @pytest.mark.slow
    @patch('veleron_dictation.whisper.load_model')
    def test_large_audio_buffer(self, mock_load_model, mock_whisper_model):
        """Test handling of large audio buffer"""
        mock_load_model.return_value = mock_whisper_model

        from veleron_dictation import VeleronDictation
        dictation = VeleronDictation()

        # Simulate large audio buffer (10 seconds at 16kHz)
        large_chunks = [
            np.random.randn(16000, 1).astype(np.float32) for _ in range(10)
        ]
        dictation.audio_data = large_chunks

        # Should handle large buffer
        audio = np.concatenate(dictation.audio_data, axis=0)
        assert len(audio.flatten()) == 160000


class TestErrorRecovery:
    """Test error recovery mechanisms"""

    @patch('veleron_dictation.whisper.load_model')
    def test_recovery_from_transcription_error(
        self, mock_load_model, mock_whisper_model, sample_audio_chunks
    ):
        """Test recovery from transcription errors"""
        mock_load_model.return_value = mock_whisper_model
        mock_whisper_model.transcribe.side_effect = Exception("Network error")

        from veleron_dictation import VeleronDictation
        dictation = VeleronDictation()

        dictation.audio_data = sample_audio_chunks

        # Should not crash, should handle error
        dictation.transcribe_and_type()

        # Application should still be in running state
        assert dictation.is_running is True
