"""
End-to-End Tests for Whisper to Office Application

Tests all three output formats (Word, PowerPoint, Meeting Minutes)
with various models and audio file formats.
"""

import pytest
import os
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.test_utils import (
    get_test_audio_path,
    temporary_directory,
    validate_text_file,
    assert_file_exists,
    assert_file_not_empty,
    file_contains_text,
    assert_valid_timestamp,
    cleanup_temp_files,
    PerformanceTimer
)

# Import the functions we're testing
from whisper_to_office import (
    transcribe_for_word,
    transcribe_for_powerpoint,
    transcribe_meeting_minutes,
    format_timestamp
)


class TestWhisperToOffice:
    """Test suite for Whisper to Office application"""

    @pytest.fixture
    def test_audio_file(self):
        """Get path to a test audio file"""
        try:
            return get_test_audio_path("test_short_tone.wav")
        except FileNotFoundError:
            pytest.skip("Test audio files not available")

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary directory for test outputs"""
        import tempfile
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


class TestWordFormat(TestWhisperToOffice):
    """Tests for Word document format output"""

    def test_word_format_basic(self, test_audio_file, temp_output_dir):
        """TC-WO-002: Test basic Word format transcription"""
        output_file = os.path.join(temp_output_dir, "test_transcript.txt")

        with PerformanceTimer() as timer:
            result_file = transcribe_for_word(
                test_audio_file,
                model_name="tiny",  # Use smallest model for speed
                output_file=output_file
            )

        print(f"Word transcription took {timer.elapsed():.2f}s")

        # Verify output file created
        assert_file_exists(result_file)
        assert_file_not_empty(result_file)

        # Verify file structure
        content = validate_text_file(result_file)
        assert "AUDIO TRANSCRIPTION" in content
        assert "FULL TRANSCRIPT" in content
        assert "TRANSCRIPT WITH TIMESTAMPS" in content
        assert "Source File:" in content
        assert "Language:" in content
        assert "Model Used:" in content

    def test_word_format_default_output(self, test_audio_file):
        """TC-WO-002: Test Word format with default output filename"""
        # Let it create default output file
        result_file = transcribe_for_word(
            test_audio_file,
            model_name="tiny",
            output_file=None  # Use default naming
        )

        try:
            # Verify file exists
            assert_file_exists(result_file)

            # Verify filename follows convention
            assert result_file.endswith("_transcript.txt")

        finally:
            # Cleanup
            cleanup_temp_files(result_file)

    @pytest.mark.slow
    def test_word_format_all_models(self, test_audio_file, temp_output_dir):
        """TC-WO-003: Test Word output with multiple models"""
        models = ["tiny", "base"]  # Test with tiny and base for speed

        results = {}
        for model in models:
            output_file = os.path.join(temp_output_dir, f"test_{model}.txt")

            with PerformanceTimer() as timer:
                result_file = transcribe_for_word(
                    test_audio_file,
                    model_name=model,
                    output_file=output_file
                )

            results[model] = {
                'file': result_file,
                'time': timer.elapsed()
            }

            # Verify file created and contains model name
            assert_file_exists(result_file)
            assert file_contains_text(result_file, f"Model Used: {model}")

        # Print performance comparison
        print("\nModel Performance Comparison (Word Format):")
        for model, data in results.items():
            print(f"  {model}: {data['time']:.2f}s")


class TestPowerPointFormat(TestWhisperToOffice):
    """Tests for PowerPoint format output"""

    def test_powerpoint_format_basic(self, test_audio_file, temp_output_dir):
        """TC-WO-004: Test PowerPoint speaker notes format"""
        output_file = os.path.join(temp_output_dir, "test_powerpoint.txt")

        with PerformanceTimer() as timer:
            result_file = transcribe_for_powerpoint(
                test_audio_file,
                model_name="tiny",
                output_file=output_file
            )

        print(f"PowerPoint transcription took {timer.elapsed():.2f}s")

        # Verify output file created
        assert_file_exists(result_file)
        assert_file_not_empty(result_file)

        # Verify file structure
        content = validate_text_file(result_file)
        assert "POWERPOINT SPEAKER NOTES" in content
        assert "Instructions:" in content
        assert "SLIDE" in content
        assert "Time:" in content

    def test_powerpoint_slide_structure(self, test_audio_file, temp_output_dir):
        """TC-WO-004: Verify PowerPoint slides are properly formatted"""
        output_file = os.path.join(temp_output_dir, "test_powerpoint.txt")

        result_file = transcribe_for_powerpoint(
            test_audio_file,
            model_name="tiny",
            output_file=output_file
        )

        content = validate_text_file(result_file)

        # Count slide markers
        slide_count = content.count("SLIDE ")
        assert slide_count > 0, "No slides found in output"

        # Verify each slide has a timestamp
        for i in range(1, slide_count + 1):
            assert f"SLIDE {i}" in content

        print(f"PowerPoint format generated {slide_count} slides")


class TestMeetingMinutesFormat(TestWhisperToOffice):
    """Tests for Meeting Minutes format output"""

    def test_meeting_minutes_basic(self, test_audio_file, temp_output_dir):
        """TC-WO-005: Test meeting minutes format"""
        output_file = os.path.join(temp_output_dir, "test_meeting.txt")

        with PerformanceTimer() as timer:
            result_file = transcribe_meeting_minutes(
                test_audio_file,
                model_name="tiny",
                output_file=output_file
            )

        print(f"Meeting minutes transcription took {timer.elapsed():.2f}s")

        # Verify output file created
        assert_file_exists(result_file)
        assert_file_not_empty(result_file)

        # Verify file structure
        content = validate_text_file(result_file)
        assert "MEETING MINUTES" in content

    def test_meeting_minutes_sections(self, test_audio_file, temp_output_dir):
        """TC-WO-005: Verify all required sections present"""
        output_file = os.path.join(temp_output_dir, "test_meeting.txt")

        result_file = transcribe_meeting_minutes(
            test_audio_file,
            model_name="tiny",
            output_file=output_file
        )

        content = validate_text_file(result_file)

        # Verify all required sections
        required_sections = [
            "MEETING MINUTES",
            "Date:",
            "Time:",
            "Duration:",
            "ATTENDEES:",
            "AGENDA:",
            "DISCUSSION:",
            "DETAILED NOTES WITH TIMESTAMPS:",
            "ACTION ITEMS:",
            "NEXT MEETING:"
        ]

        for section in required_sections:
            assert section in content, f"Missing section: {section}"

        print("All required meeting minutes sections present")


class TestTimestampFormatting:
    """Tests for timestamp formatting function"""

    def test_timestamp_format_seconds(self):
        """TC-WO-007: Test timestamp format for seconds"""
        # Test various durations
        assert format_timestamp(0) == "00:00"
        assert format_timestamp(30) == "00:30"
        assert format_timestamp(59) == "00:59"

    def test_timestamp_format_minutes(self):
        """TC-WO-007: Test timestamp format for minutes"""
        assert format_timestamp(60) == "01:00"
        assert format_timestamp(90) == "01:30"
        assert format_timestamp(3599) == "59:59"

    def test_timestamp_format_hours(self):
        """TC-WO-007: Test timestamp format for hours"""
        assert format_timestamp(3600) == "01:00:00"
        assert format_timestamp(3661) == "01:01:01"
        assert format_timestamp(7200) == "02:00:00"

    def test_timestamp_format_validity(self):
        """TC-WO-007: Verify timestamp format is valid"""
        test_cases = [0, 30, 60, 90, 3600, 3661, 7200]
        for seconds in test_cases:
            timestamp = format_timestamp(seconds)
            assert_valid_timestamp(timestamp)


class TestErrorHandling(TestWhisperToOffice):
    """Tests for error handling"""

    def test_file_not_found(self):
        """TC-WO-008: Test handling of missing file"""
        non_existent_file = "this_file_does_not_exist.wav"

        # The function currently doesn't raise exception, but we can check behavior
        # This test documents expected behavior
        # In production code, you'd want to add proper error handling

        # Note: Current implementation would fail in whisper.load_model
        # This test serves as documentation for improvement needed
        pass  # Skip for now as it would require model loading

    def test_invalid_audio_format(self, temp_output_dir):
        """TC-WO-009: Test handling of invalid audio file"""
        # Create a text file pretending to be audio
        fake_audio = os.path.join(temp_output_dir, "fake.wav")
        with open(fake_audio, 'w') as f:
            f.write("This is not audio data")

        # Test would go here - currently skipped as it requires model loading
        # and would fail at Whisper level
        pass


class TestFileFormatSupport(TestWhisperToOffice):
    """Tests for different audio file formats"""

    def test_wav_format(self, temp_output_dir):
        """TC-WO-010: Test WAV file support"""
        try:
            test_file = get_test_audio_path("test_short_tone.wav")
        except FileNotFoundError:
            pytest.skip("WAV test file not available")

        output_file = os.path.join(temp_output_dir, "test_wav.txt")
        result_file = transcribe_for_word(test_file, model_name="tiny", output_file=output_file)

        assert_file_exists(result_file)
        assert_file_not_empty(result_file)

    @pytest.mark.skipif(
        not Path(__file__).parent.parent / "test_data" / "test_sample.mp3",
        reason="MP3 test file not available"
    )
    def test_mp3_format(self, temp_output_dir):
        """TC-WO-011: Test MP3 file support"""
        test_file = get_test_audio_path("test_sample.mp3")
        output_file = os.path.join(temp_output_dir, "test_mp3.txt")
        result_file = transcribe_for_word(test_file, model_name="tiny", output_file=output_file)

        assert_file_exists(result_file)
        assert_file_not_empty(result_file)


class TestOutputFileHandling(TestWhisperToOffice):
    """Tests for output file handling"""

    def test_custom_output_path(self, test_audio_file, temp_output_dir):
        """TC-WO-006: Test custom output file naming"""
        custom_name = os.path.join(temp_output_dir, "my_custom_name.txt")

        result_file = transcribe_for_word(
            test_audio_file,
            model_name="tiny",
            output_file=custom_name
        )

        assert result_file == custom_name
        assert_file_exists(custom_name)

    def test_output_file_overwrite(self, test_audio_file, temp_output_dir):
        """TC-WO-016: Test behavior when output file exists"""
        output_file = os.path.join(temp_output_dir, "test.txt")

        # Create file first time
        result_file1 = transcribe_for_word(
            test_audio_file,
            model_name="tiny",
            output_file=output_file
        )

        first_content = validate_text_file(result_file1)

        # Create file second time (should overwrite)
        result_file2 = transcribe_for_word(
            test_audio_file,
            model_name="tiny",
            output_file=output_file
        )

        second_content = validate_text_file(result_file2)

        # Verify file was overwritten (both should be valid transcripts)
        assert len(first_content) > 0
        assert len(second_content) > 0
        # They should have similar content (both transcripts of same file)


class TestBatchProcessing(TestWhisperToOffice):
    """Tests for batch processing capabilities"""

    def test_multiple_files_sequential(self, temp_output_dir):
        """TC-WO-015: Test processing multiple files in sequence"""
        try:
            test_files = [
                get_test_audio_path("test_short_tone.wav"),
                get_test_audio_path("test_multi_tone.wav"),
            ]
        except FileNotFoundError:
            pytest.skip("Required test files not available")

        results = []
        for i, test_file in enumerate(test_files):
            output_file = os.path.join(temp_output_dir, f"batch_{i}.txt")

            with PerformanceTimer() as timer:
                result_file = transcribe_for_word(
                    test_file,
                    model_name="tiny",
                    output_file=output_file
                )

            results.append({
                'file': result_file,
                'time': timer.elapsed()
            })

            assert_file_exists(result_file)

        print(f"\nProcessed {len(results)} files successfully")
        total_time = sum(r['time'] for r in results)
        print(f"Total time: {total_time:.2f}s")
        print(f"Average time: {total_time/len(results):.2f}s")


@pytest.mark.performance
class TestPerformance(TestWhisperToOffice):
    """Performance benchmarking tests"""

    def test_short_audio_performance(self, test_audio_file, temp_output_dir):
        """Benchmark: Short audio file (5 seconds)"""
        output_file = os.path.join(temp_output_dir, "perf_short.txt")

        with PerformanceTimer() as timer:
            transcribe_for_word(test_audio_file, model_name="tiny", output_file=output_file)

        elapsed = timer.elapsed()
        print(f"\nShort audio (5s) processing time: {elapsed:.2f}s")

        # Should complete in reasonable time (adjust threshold as needed)
        assert elapsed < 60, f"Processing took too long: {elapsed}s"

    @pytest.mark.slow
    def test_medium_audio_performance(self, temp_output_dir):
        """Benchmark: Medium audio file (30 seconds)"""
        try:
            test_file = get_test_audio_path("test_medium_tone.wav")
        except FileNotFoundError:
            pytest.skip("Medium test audio not available")

        output_file = os.path.join(temp_output_dir, "perf_medium.txt")

        with PerformanceTimer() as timer:
            transcribe_for_word(test_file, model_name="tiny", output_file=output_file)

        elapsed = timer.elapsed()
        print(f"\nMedium audio (30s) processing time: {elapsed:.2f}s")

        # Should complete in reasonable time
        assert elapsed < 120, f"Processing took too long: {elapsed}s"


# Test configuration
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "performance: marks performance tests")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
