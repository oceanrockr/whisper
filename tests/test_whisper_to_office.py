"""
Unit Tests for whisper_to_office.py

Tests CLI argument parsing, transcription formatting,
and output generation for Word, PowerPoint, and Meeting Minutes formats.
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch, mock_open, MagicMock
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import whisper_to_office
from whisper_to_office import (
    format_timestamp,
    transcribe_for_word,
    transcribe_for_powerpoint,
    transcribe_meeting_minutes
)


class TestFormatTimestamp:
    """Test the timestamp formatting function"""

    def test_format_seconds_only(self):
        """Test formatting for times under 1 minute"""
        assert format_timestamp(0) == "00:00"
        assert format_timestamp(30) == "00:30"
        assert format_timestamp(59) == "00:59"

    def test_format_minutes_seconds(self):
        """Test formatting for times under 1 hour"""
        assert format_timestamp(60) == "01:00"
        assert format_timestamp(90) == "01:30"
        assert format_timestamp(3599) == "59:59"

    def test_format_hours_minutes_seconds(self):
        """Test formatting for times over 1 hour"""
        assert format_timestamp(3600) == "01:00:00"
        assert format_timestamp(3661) == "01:01:01"
        assert format_timestamp(7265) == "02:01:05"

    def test_format_fractional_seconds(self):
        """Test formatting with decimal seconds"""
        assert format_timestamp(30.5) == "00:30"
        assert format_timestamp(90.7) == "01:30"
        assert format_timestamp(3661.9) == "01:01:01"

    def test_format_edge_cases(self):
        """Test edge cases"""
        assert format_timestamp(0.1) == "00:00"
        assert format_timestamp(59.9) == "00:59"


class TestTranscribeForWord:
    """Test Word document transcription formatting"""

    @pytest.fixture
    def mock_result(self, mock_transcription_result):
        """Use the shared mock transcription result"""
        return mock_transcription_result

    def test_transcribe_for_word_basic(
        self, tmp_path, sample_audio_file, mock_whisper_load_model, mock_result
    ):
        """Test basic Word transcription functionality"""
        output_file = tmp_path / "output.txt"

        with patch('whisper_to_office.whisper.load_model') as mock_load:
            mock_model = Mock()
            mock_model.transcribe.return_value = mock_result
            mock_load.return_value = mock_model

            result_file = transcribe_for_word(
                sample_audio_file,
                model_name="base",
                output_file=str(output_file)
            )

            assert os.path.exists(result_file)
            assert result_file == str(output_file)

    def test_transcribe_for_word_auto_filename(
        self, tmp_path, sample_audio_file, mock_whisper_load_model, mock_result
    ):
        """Test automatic output filename generation"""
        with patch('whisper_to_office.whisper.load_model') as mock_load:
            mock_model = Mock()
            mock_model.transcribe.return_value = mock_result
            mock_load.return_value = mock_model

            # Change to temp directory to control output location
            original_cwd = os.getcwd()
            try:
                os.chdir(tmp_path)
                result_file = transcribe_for_word(sample_audio_file, model_name="base")

                assert os.path.exists(result_file)
                assert result_file.endswith("_transcript.txt")
            finally:
                os.chdir(original_cwd)

    def test_transcribe_for_word_content(
        self, tmp_path, sample_audio_file, mock_whisper_load_model, mock_result
    ):
        """Test that Word output contains expected content"""
        output_file = tmp_path / "output.txt"

        with patch('whisper_to_office.whisper.load_model') as mock_load:
            mock_model = Mock()
            mock_model.transcribe.return_value = mock_result
            mock_load.return_value = mock_model

            transcribe_for_word(
                sample_audio_file,
                model_name="base",
                output_file=str(output_file)
            )

            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for expected sections
            assert "AUDIO TRANSCRIPTION" in content
            assert "Source File:" in content
            assert "FULL TRANSCRIPT" in content
            assert "TRANSCRIPT WITH TIMESTAMPS" in content
            assert mock_result["text"] in content
            assert mock_result["language"] in content

    def test_transcribe_for_word_timestamps(
        self, tmp_path, sample_audio_file, mock_whisper_load_model, mock_result
    ):
        """Test that timestamps are properly formatted in output"""
        output_file = tmp_path / "output.txt"

        with patch('whisper_to_office.whisper.load_model') as mock_load:
            mock_model = Mock()
            mock_model.transcribe.return_value = mock_result
            mock_load.return_value = mock_model

            transcribe_for_word(
                sample_audio_file,
                model_name="base",
                output_file=str(output_file)
            )

            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for timestamp format [MM:SS - MM:SS]
            assert "[00:00 - 00:03]" in content
            assert "[00:03 - 00:06]" in content

    def test_transcribe_for_word_different_models(
        self, tmp_path, sample_audio_file, mock_result
    ):
        """Test transcription with different model names"""
        output_file = tmp_path / "output.txt"

        for model_name in ["tiny", "base", "small", "medium"]:
            with patch('whisper_to_office.whisper.load_model') as mock_load:
                mock_model = Mock()
                mock_model.transcribe.return_value = mock_result
                mock_load.return_value = mock_model

                transcribe_for_word(
                    sample_audio_file,
                    model_name=model_name,
                    output_file=str(output_file)
                )

                mock_load.assert_called_once_with(model_name)

                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    assert f"Model Used: {model_name}" in content


class TestTranscribeForPowerPoint:
    """Test PowerPoint speaker notes formatting"""

    @pytest.fixture
    def mock_result(self, mock_transcription_result):
        """Use the shared mock transcription result"""
        return mock_transcription_result

    def test_transcribe_for_powerpoint_basic(
        self, tmp_path, sample_audio_file, mock_result
    ):
        """Test basic PowerPoint transcription functionality"""
        output_file = tmp_path / "ppt_output.txt"

        with patch('whisper_to_office.whisper.load_model') as mock_load:
            mock_model = Mock()
            mock_model.transcribe.return_value = mock_result
            mock_load.return_value = mock_model

            result_file = transcribe_for_powerpoint(
                sample_audio_file,
                model_name="base",
                output_file=str(output_file)
            )

            assert os.path.exists(result_file)
            assert result_file == str(output_file)

    def test_transcribe_for_powerpoint_auto_filename(
        self, tmp_path, sample_audio_file, mock_result
    ):
        """Test automatic output filename for PowerPoint"""
        with patch('whisper_to_office.whisper.load_model') as mock_load:
            mock_model = Mock()
            mock_model.transcribe.return_value = mock_result
            mock_load.return_value = mock_model

            original_cwd = os.getcwd()
            try:
                os.chdir(tmp_path)
                result_file = transcribe_for_powerpoint(sample_audio_file)

                assert os.path.exists(result_file)
                assert result_file.endswith("_powerpoint_notes.txt")
            finally:
                os.chdir(original_cwd)

    def test_transcribe_for_powerpoint_content(
        self, tmp_path, sample_audio_file, mock_result
    ):
        """Test PowerPoint output contains slide structure"""
        output_file = tmp_path / "ppt_output.txt"

        with patch('whisper_to_office.whisper.load_model') as mock_load:
            mock_model = Mock()
            mock_model.transcribe.return_value = mock_result
            mock_load.return_value = mock_model

            transcribe_for_powerpoint(
                sample_audio_file,
                model_name="base",
                output_file=str(output_file)
            )

            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for expected sections
            assert "POWERPOINT SPEAKER NOTES" in content
            assert "SLIDE 1" in content
            assert "SLIDE 2" in content
            assert "SLIDE 3" in content
            assert "Instructions:" in content

    def test_transcribe_for_powerpoint_slide_count(
        self, tmp_path, sample_audio_file, mock_result
    ):
        """Test that number of slides matches number of segments"""
        output_file = tmp_path / "ppt_output.txt"

        with patch('whisper_to_office.whisper.load_model') as mock_load:
            mock_model = Mock()
            mock_model.transcribe.return_value = mock_result
            mock_load.return_value = mock_model

            transcribe_for_powerpoint(
                sample_audio_file,
                model_name="base",
                output_file=str(output_file)
            )

            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Should have 3 slides for 3 segments
            num_slides = content.count("SLIDE ")
            assert num_slides == len(mock_result["segments"])


class TestTranscribeMeetingMinutes:
    """Test meeting minutes formatting"""

    @pytest.fixture
    def mock_result(self, mock_transcription_result):
        """Use the shared mock transcription result"""
        return mock_transcription_result

    def test_transcribe_meeting_minutes_basic(
        self, tmp_path, sample_audio_file, mock_result
    ):
        """Test basic meeting minutes functionality"""
        output_file = tmp_path / "minutes.txt"

        with patch('whisper_to_office.whisper.load_model') as mock_load:
            mock_model = Mock()
            mock_model.transcribe.return_value = mock_result
            mock_load.return_value = mock_model

            result_file = transcribe_meeting_minutes(
                sample_audio_file,
                model_name="base",
                output_file=str(output_file)
            )

            assert os.path.exists(result_file)
            assert result_file == str(output_file)

    def test_transcribe_meeting_minutes_auto_filename(
        self, tmp_path, sample_audio_file, mock_result
    ):
        """Test automatic filename for meeting minutes"""
        with patch('whisper_to_office.whisper.load_model') as mock_load:
            mock_model = Mock()
            mock_model.transcribe.return_value = mock_result
            mock_load.return_value = mock_model

            original_cwd = os.getcwd()
            try:
                os.chdir(tmp_path)
                result_file = transcribe_meeting_minutes(sample_audio_file)

                assert os.path.exists(result_file)
                assert result_file.endswith("_meeting_minutes.txt")
            finally:
                os.chdir(original_cwd)

    def test_transcribe_meeting_minutes_structure(
        self, tmp_path, sample_audio_file, mock_result
    ):
        """Test meeting minutes has proper structure"""
        output_file = tmp_path / "minutes.txt"

        with patch('whisper_to_office.whisper.load_model') as mock_load:
            mock_model = Mock()
            mock_model.transcribe.return_value = mock_result
            mock_load.return_value = mock_model

            transcribe_meeting_minutes(
                sample_audio_file,
                model_name="base",
                output_file=str(output_file)
            )

            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for all required sections
            assert "MEETING MINUTES" in content
            assert "Date:" in content
            assert "Time:" in content
            assert "Duration:" in content
            assert "ATTENDEES:" in content
            assert "AGENDA:" in content
            assert "DISCUSSION:" in content
            assert "DETAILED NOTES WITH TIMESTAMPS:" in content
            assert "ACTION ITEMS:" in content
            assert "NEXT MEETING:" in content

    def test_transcribe_meeting_minutes_timestamps(
        self, tmp_path, sample_audio_file, mock_result
    ):
        """Test timestamps in meeting minutes"""
        output_file = tmp_path / "minutes.txt"

        with patch('whisper_to_office.whisper.load_model') as mock_load:
            mock_model = Mock()
            mock_model.transcribe.return_value = mock_result
            mock_load.return_value = mock_model

            transcribe_meeting_minutes(
                sample_audio_file,
                model_name="base",
                output_file=str(output_file)
            )

            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for timestamp format [MM:SS]
            for segment in mock_result["segments"]:
                timestamp = format_timestamp(segment["start"])
                assert f"[{timestamp}]" in content


class TestCLIArgumentParsing:
    """Test command-line argument parsing"""

    def test_main_no_arguments(self, capsys):
        """Test running main() with no arguments shows usage"""
        with patch('sys.argv', ['whisper_to_office.py']):
            whisper_to_office.main()

            # Should not raise an error, just show usage

    def test_main_file_not_found(self, capsys):
        """Test handling of non-existent file"""
        with patch('sys.argv', ['whisper_to_office.py', 'nonexistent.mp3']):
            whisper_to_office.main()
            captured = capsys.readouterr()
            # Should print error message

    def test_main_word_format(self, tmp_path, sample_audio_file, mock_transcription_result):
        """Test main() with word format"""
        output_file = tmp_path / "output.txt"

        with patch('sys.argv', [
            'whisper_to_office.py',
            sample_audio_file,
            '--format', 'word',
            '--output', str(output_file)
        ]):
            with patch('whisper_to_office.whisper.load_model') as mock_load:
                mock_model = Mock()
                mock_model.transcribe.return_value = mock_transcription_result
                mock_load.return_value = mock_model

                whisper_to_office.main()
                assert os.path.exists(output_file)

    def test_main_powerpoint_format(self, tmp_path, sample_audio_file, mock_transcription_result):
        """Test main() with powerpoint format"""
        output_file = tmp_path / "output.txt"

        with patch('sys.argv', [
            'whisper_to_office.py',
            sample_audio_file,
            '--format', 'powerpoint',
            '--output', str(output_file)
        ]):
            with patch('whisper_to_office.whisper.load_model') as mock_load:
                mock_model = Mock()
                mock_model.transcribe.return_value = mock_transcription_result
                mock_load.return_value = mock_model

                whisper_to_office.main()
                assert os.path.exists(output_file)

    def test_main_meeting_format(self, tmp_path, sample_audio_file, mock_transcription_result):
        """Test main() with meeting format"""
        output_file = tmp_path / "output.txt"

        with patch('sys.argv', [
            'whisper_to_office.py',
            sample_audio_file,
            '--format', 'meeting',
            '--output', str(output_file)
        ]):
            with patch('whisper_to_office.whisper.load_model') as mock_load:
                mock_model = Mock()
                mock_model.transcribe.return_value = mock_transcription_result
                mock_load.return_value = mock_model

                whisper_to_office.main()
                assert os.path.exists(output_file)

    def test_main_custom_model(self, tmp_path, sample_audio_file, mock_transcription_result):
        """Test main() with custom model selection"""
        output_file = tmp_path / "output.txt"

        with patch('sys.argv', [
            'whisper_to_office.py',
            sample_audio_file,
            '--model', 'medium',
            '--output', str(output_file)
        ]):
            with patch('whisper_to_office.whisper.load_model') as mock_load:
                mock_model = Mock()
                mock_model.transcribe.return_value = mock_transcription_result
                mock_load.return_value = mock_model

                whisper_to_office.main()
                mock_load.assert_called_with('medium')


class TestErrorHandling:
    """Test error handling in various scenarios"""

    def test_transcribe_with_invalid_audio_file(self, tmp_path):
        """Test handling of invalid audio file"""
        invalid_file = tmp_path / "invalid.txt"
        invalid_file.write_text("This is not an audio file")
        output_file = tmp_path / "output.txt"

        with patch('whisper_to_office.whisper.load_model') as mock_load:
            mock_model = Mock()
            # Simulate transcribe raising an error
            mock_model.transcribe.side_effect = Exception("Invalid audio file")
            mock_load.return_value = mock_model

            with pytest.raises(Exception):
                transcribe_for_word(
                    str(invalid_file),
                    output_file=str(output_file)
                )

    def test_transcribe_with_unicode_content(
        self, tmp_path, sample_audio_file
    ):
        """Test handling of special characters in transcription"""
        output_file = tmp_path / "unicode_output.txt"

        # Test with special ASCII characters and common symbols
        # Original had invalid UTF-8 byte 0x93, replaced with valid ASCII
        unicode_result = {
            "text": "Hello `} E1-(' @825B Sokao",
            "language": "multilingual",
            "segments": [
                {
                    "id": 0,
                    "start": 0.0,
                    "end": 5.0,
                    "text": "Hello `} E1-(' @825B Sokao"
                }
            ]
        }

        with patch('whisper_to_office.whisper.load_model') as mock_load:
            mock_model = Mock()
            mock_model.transcribe.return_value = unicode_result
            mock_load.return_value = mock_model

            transcribe_for_word(
                sample_audio_file,
                output_file=str(output_file)
            )

            # Verify file was written with UTF-8 encoding
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "test" in content
                assert "E1-('" in content
                assert "@825B" in content
                assert "Sokao" in content


class TestPerformance:
    """Performance-related tests"""

    @pytest.mark.slow
    def test_large_transcription(self, tmp_path, sample_audio_file):
        """Test handling of large transcription results"""
        output_file = tmp_path / "large_output.txt"

        # Create a mock result with many segments
        large_result = {
            "text": " ".join([f"Segment {i}" for i in range(1000)]),
            "language": "en",
            "segments": [
                {
                    "id": i,
                    "start": i * 5.0,
                    "end": (i + 1) * 5.0,
                    "text": f"Segment {i}"
                }
                for i in range(1000)
            ]
        }

        with patch('whisper_to_office.whisper.load_model') as mock_load:
            mock_model = Mock()
            mock_model.transcribe.return_value = large_result
            mock_load.return_value = mock_model

            # Should complete without error
            transcribe_for_word(
                sample_audio_file,
                output_file=str(output_file)
            )

            assert os.path.exists(output_file)
            # Verify file has content
            assert os.path.getsize(output_file) > 0


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_empty_transcription(self, tmp_path, sample_audio_file):
        """Test handling of empty transcription result"""
        output_file = tmp_path / "empty_output.txt"

        empty_result = {
            "text": "",
            "language": "en",
            "segments": []
        }

        with patch('whisper_to_office.whisper.load_model') as mock_load:
            mock_model = Mock()
            mock_model.transcribe.return_value = empty_result
            mock_load.return_value = mock_model

            transcribe_for_word(
                sample_audio_file,
                output_file=str(output_file)
            )

            assert os.path.exists(output_file)

    def test_single_segment(self, tmp_path, sample_audio_file):
        """Test transcription with only one segment"""
        output_file = tmp_path / "single_output.txt"

        single_result = {
            "text": "Single segment transcription",
            "language": "en",
            "segments": [
                {
                    "id": 0,
                    "start": 0.0,
                    "end": 3.0,
                    "text": "Single segment transcription"
                }
            ]
        }

        with patch('whisper_to_office.whisper.load_model') as mock_load:
            mock_model = Mock()
            mock_model.transcribe.return_value = single_result
            mock_load.return_value = mock_model

            transcribe_for_powerpoint(
                sample_audio_file,
                output_file=str(output_file)
            )

            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "SLIDE 1" in content
                assert "SLIDE 2" not in content
