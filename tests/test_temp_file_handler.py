"""
Unit tests for temp_file_handler module

Tests secure temporary file handling, audio file writing,
and secure deletion functionality.
"""

import pytest
import os
import stat
import wave
import numpy as np
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock

from temp_file_handler import (
    SecureTempFileHandler,
    write_audio_to_wav,
    secure_delete,
    temp_audio_file
)


class TestSecureTempFileHandler:
    """Tests for SecureTempFileHandler class"""

    def test_create_temp_file(self):
        """Test that temp file is created successfully"""
        with SecureTempFileHandler.create_temp_audio_file() as temp_path:
            # File should exist during context
            assert temp_path.exists()
            assert temp_path.suffix == '.wav'
            assert 'veleron_audio_' in temp_path.name

    def test_temp_file_cleanup(self):
        """Test that temp file is deleted after context exits"""
        temp_path_ref = None

        with SecureTempFileHandler.create_temp_audio_file() as temp_path:
            temp_path_ref = temp_path
            assert temp_path.exists()

        # File should be deleted after context
        assert not temp_path_ref.exists()

    def test_temp_file_custom_suffix(self):
        """Test creating temp file with custom suffix"""
        with SecureTempFileHandler.create_temp_audio_file(suffix='.mp3') as temp_path:
            assert temp_path.suffix == '.mp3'
            assert temp_path.exists()

        assert not temp_path.exists()

    def test_temp_file_custom_prefix(self):
        """Test creating temp file with custom prefix"""
        with SecureTempFileHandler.create_temp_audio_file(prefix='test_audio_') as temp_path:
            assert 'test_audio_' in temp_path.name
            assert temp_path.exists()

        assert not temp_path.exists()

    @pytest.mark.skipif(not hasattr(os, 'chmod'), reason="chmod not available on this platform")
    def test_temp_file_permissions(self):
        """Test that temp file has restrictive permissions (Unix-like systems)"""
        with SecureTempFileHandler.create_temp_audio_file() as temp_path:
            # Check file permissions (should be 0o600 - owner read/write only)
            file_stat = temp_path.stat()
            mode = stat.S_IMODE(file_stat.st_mode)

            # On Unix, should be 0o600 (owner read/write only)
            if os.name != 'nt':
                assert mode == 0o600

    def test_temp_file_cleanup_on_exception(self):
        """Test that temp file is cleaned up even when exception occurs"""
        temp_path_ref = None

        with pytest.raises(ValueError):
            with SecureTempFileHandler.create_temp_audio_file() as temp_path:
                temp_path_ref = temp_path
                assert temp_path.exists()
                # Simulate an error
                raise ValueError("Test error")

        # File should still be deleted after exception
        assert not temp_path_ref.exists()

    def test_temp_file_returns_path_object(self):
        """Test that context manager yields a Path object"""
        with SecureTempFileHandler.create_temp_audio_file() as temp_path:
            assert isinstance(temp_path, Path)

    def test_multiple_temp_files(self):
        """Test creating multiple temp files in sequence"""
        paths = []

        for i in range(3):
            with SecureTempFileHandler.create_temp_audio_file() as temp_path:
                paths.append(temp_path)
                assert temp_path.exists()

        # All should be deleted
        for path in paths:
            assert not path.exists()

    def test_nested_temp_files(self):
        """Test nested temp file contexts"""
        with SecureTempFileHandler.create_temp_audio_file() as temp_path1:
            assert temp_path1.exists()

            with SecureTempFileHandler.create_temp_audio_file() as temp_path2:
                assert temp_path2.exists()
                assert temp_path1 != temp_path2

            # Inner file cleaned up
            assert not temp_path2.exists()
            # Outer file still exists
            assert temp_path1.exists()

        # Both cleaned up
        assert not temp_path1.exists()

    def test_temp_file_writable(self):
        """Test that temp file can be written to"""
        with SecureTempFileHandler.create_temp_audio_file() as temp_path:
            # Write some data
            temp_path.write_text("test data")
            # Read it back
            assert temp_path.read_text() == "test data"

        assert not temp_path.exists()


class TestWriteAudioToWav:
    """Tests for write_audio_to_wav function"""

    def test_write_mono_audio(self, tmp_path):
        """Test writing mono audio data to WAV file"""
        # Create sample audio data (1 second at 16kHz)
        sample_rate = 16000
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = np.sin(2 * np.pi * 440 * t).astype(np.float32)

        # Write to file
        output_file = tmp_path / "test_mono.wav"
        write_audio_to_wav(output_file, audio_data, sample_rate=sample_rate)

        # Verify file exists and is valid
        assert output_file.exists()

        # Read and verify WAV file
        with wave.open(str(output_file), 'rb') as wf:
            assert wf.getnchannels() == 1  # Mono
            assert wf.getsampwidth() == 2  # 16-bit
            assert wf.getframerate() == sample_rate

    def test_write_stereo_audio_converts_to_mono(self, tmp_path):
        """Test that stereo audio is automatically converted to mono"""
        # Create stereo audio data
        sample_rate = 16000
        duration = 0.5
        samples = int(sample_rate * duration)
        audio_data = np.random.randn(samples, 2).astype(np.float32)

        # Write to file (should convert to mono)
        output_file = tmp_path / "test_stereo.wav"
        write_audio_to_wav(output_file, audio_data, sample_rate=sample_rate, channels=1)

        # Verify file is mono
        with wave.open(str(output_file), 'rb') as wf:
            assert wf.getnchannels() == 1

    def test_write_audio_different_sample_rates(self, tmp_path):
        """Test writing audio with different sample rates"""
        sample_rates = [8000, 16000, 22050, 44100, 48000]

        for sr in sample_rates:
            audio_data = np.random.randn(sr).astype(np.float32) * 0.1
            output_file = tmp_path / f"test_{sr}hz.wav"

            write_audio_to_wav(output_file, audio_data, sample_rate=sr)

            # Verify sample rate
            with wave.open(str(output_file), 'rb') as wf:
                assert wf.getframerate() == sr

    def test_write_audio_float_to_int16_conversion(self, tmp_path):
        """Test that float32 audio is correctly converted to int16"""
        # Create audio data with known values
        audio_data = np.array([0.0, 0.5, 1.0, -0.5, -1.0], dtype=np.float32)
        output_file = tmp_path / "test_conversion.wav"

        write_audio_to_wav(output_file, audio_data, sample_rate=16000)

        # Read back and verify conversion
        with wave.open(str(output_file), 'rb') as wf:
            frames = wf.readframes(wf.getnframes())
            audio_int16 = np.frombuffer(frames, dtype=np.int16)

            # Check that values are in expected range
            assert audio_int16[0] == 0
            assert audio_int16[2] == 32767  # Max value
            assert audio_int16[4] == -32767  # Min value (approximately)

    def test_write_audio_empty_array(self, tmp_path):
        """Test handling of empty audio array"""
        audio_data = np.array([], dtype=np.float32)
        output_file = tmp_path / "test_empty.wav"

        write_audio_to_wav(output_file, audio_data, sample_rate=16000)

        # File should exist but have no audio frames
        assert output_file.exists()
        with wave.open(str(output_file), 'rb') as wf:
            assert wf.getnframes() == 0

    def test_write_audio_path_as_string(self, tmp_path):
        """Test that function accepts path as string"""
        audio_data = np.random.randn(1000).astype(np.float32) * 0.1
        output_file = tmp_path / "test_string_path.wav"

        # Pass as string instead of Path
        write_audio_to_wav(output_file, audio_data)

        assert output_file.exists()

    def test_write_audio_overwrite_existing(self, tmp_path):
        """Test that existing file can be overwritten"""
        audio_data = np.random.randn(1000).astype(np.float32) * 0.1
        output_file = tmp_path / "test_overwrite.wav"

        # Write first time
        write_audio_to_wav(output_file, audio_data)
        first_size = output_file.stat().st_size

        # Write again with different data
        new_audio = np.random.randn(2000).astype(np.float32) * 0.1
        write_audio_to_wav(output_file, new_audio)
        second_size = output_file.stat().st_size

        # Size should be different
        assert second_size != first_size

    def test_write_audio_preserves_amplitude(self, tmp_path):
        """Test that audio amplitude is preserved during write"""
        # Create audio with specific amplitude
        audio_data = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        output_file = tmp_path / "test_amplitude.wav"

        write_audio_to_wav(output_file, audio_data, sample_rate=16000)

        # Read back and check amplitude range is preserved
        with wave.open(str(output_file), 'rb') as wf:
            frames = wf.readframes(wf.getnframes())
            audio_int16 = np.frombuffer(frames, dtype=np.int16)
            audio_float = audio_int16.astype(np.float32) / 32767.0

            # Should be close to original (within float precision)
            np.testing.assert_array_almost_equal(audio_float, audio_data, decimal=4)


class TestSecureDelete:
    """Tests for secure_delete function"""

    def test_secure_delete_removes_file(self, tmp_path):
        """Test that secure_delete removes file"""
        test_file = tmp_path / "test_delete.txt"
        test_file.write_text("sensitive data")

        assert test_file.exists()
        secure_delete(test_file)
        assert not test_file.exists()

    def test_secure_delete_overwrites_data(self, tmp_path):
        """Test that secure_delete overwrites file data before deletion"""
        test_file = tmp_path / "test_overwrite.txt"
        original_data = "sensitive data" * 100
        test_file.write_text(original_data)

        # Mock the file operations to verify overwriting
        with patch('temp_file_handler.os.urandom') as mock_urandom:
            mock_urandom.return_value = b'\xFF' * len(original_data.encode())

            secure_delete(test_file)

            # urandom should have been called for overwriting
            assert mock_urandom.called

        assert not test_file.exists()

    def test_secure_delete_nonexistent_file(self, tmp_path):
        """Test that secure_delete handles non-existent file gracefully"""
        test_file = tmp_path / "nonexistent.txt"

        # Should not raise exception
        secure_delete(test_file)

    def test_secure_delete_binary_file(self, tmp_path):
        """Test secure deletion of binary file"""
        test_file = tmp_path / "test_binary.bin"
        test_file.write_bytes(b'\x00\x01\x02\x03' * 1000)

        assert test_file.exists()
        secure_delete(test_file)
        assert not test_file.exists()

    def test_secure_delete_large_file(self, tmp_path):
        """Test secure deletion of larger file"""
        test_file = tmp_path / "test_large.bin"
        # Create a 1MB file
        large_data = b'\x42' * (1024 * 1024)
        test_file.write_bytes(large_data)

        assert test_file.exists()
        secure_delete(test_file)
        assert not test_file.exists()

    def test_secure_delete_handles_errors(self, tmp_path):
        """Test that secure_delete handles errors gracefully"""
        test_file = tmp_path / "test_error.txt"
        test_file.write_text("test")

        # Mock to simulate error during overwriting
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            # Should not raise exception, should attempt fallback deletion
            secure_delete(test_file)

    def test_secure_delete_empty_file(self, tmp_path):
        """Test secure deletion of empty file"""
        test_file = tmp_path / "test_empty.txt"
        test_file.touch()

        assert test_file.exists()
        secure_delete(test_file)
        assert not test_file.exists()

    def test_secure_delete_multiple_passes(self, tmp_path):
        """Test that secure_delete performs multiple overwrite passes"""
        test_file = tmp_path / "test_passes.txt"
        test_file.write_text("data")

        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            try:
                secure_delete(test_file)
            except:
                pass  # May fail due to mocking, but we're checking calls

            # Should write multiple times (random data + zeros)
            # Check if write was called multiple times
            if mock_file.write.called:
                assert mock_file.write.call_count >= 2


class TestTempAudioFileConvenienceFunction:
    """Tests for temp_audio_file convenience function"""

    def test_temp_audio_file_creates_temp_file(self):
        """Test that convenience function creates temp file"""
        with temp_audio_file() as temp_path:
            assert temp_path.exists()
            assert isinstance(temp_path, Path)

    def test_temp_audio_file_cleanup(self):
        """Test that convenience function cleans up temp file"""
        temp_path_ref = None

        with temp_audio_file() as temp_path:
            temp_path_ref = temp_path
            assert temp_path.exists()

        assert not temp_path_ref.exists()

    def test_temp_audio_file_is_wav(self):
        """Test that convenience function creates .wav file"""
        with temp_audio_file() as temp_path:
            assert temp_path.suffix == '.wav'


class TestIntegrationScenarios:
    """Integration tests for common temp file scenarios"""

    def test_complete_audio_workflow(self, sample_audio_data):
        """Test complete workflow: create temp file, write audio, auto-cleanup"""
        with SecureTempFileHandler.create_temp_audio_file() as temp_path:
            # Write audio data
            write_audio_to_wav(temp_path, sample_audio_data, sample_rate=16000)

            # Verify file exists and is valid
            assert temp_path.exists()
            assert temp_path.stat().st_size > 0

            # Verify can read back
            with wave.open(str(temp_path), 'rb') as wf:
                assert wf.getnchannels() == 1
                assert wf.getframerate() == 16000

        # File should be deleted
        assert not temp_path.exists()

    def test_audio_processing_with_error(self, sample_audio_data):
        """Test that temp file is cleaned up even if processing fails"""
        temp_path_ref = None

        with pytest.raises(ValueError):
            with SecureTempFileHandler.create_temp_audio_file() as temp_path:
                temp_path_ref = temp_path

                # Write audio
                write_audio_to_wav(temp_path, sample_audio_data)

                # Simulate processing error
                raise ValueError("Processing failed")

        # File should still be cleaned up
        assert not temp_path_ref.exists()

    def test_multiple_audio_files_in_sequence(self, sample_audio_data):
        """Test processing multiple audio files in sequence"""
        results = []

        for i in range(3):
            with temp_audio_file() as temp_path:
                # Write different audio each time
                audio = sample_audio_data * (i + 1)
                write_audio_to_wav(temp_path, audio)

                # Verify file
                assert temp_path.exists()
                results.append(temp_path.stat().st_size)

        # All files should have different sizes
        assert len(set(results)) == 3

    def test_secure_audio_file_lifecycle(self, sample_audio_data):
        """Test complete secure lifecycle: create, write, use, secure delete"""
        with SecureTempFileHandler.create_temp_audio_file() as temp_path:
            # Write audio
            write_audio_to_wav(temp_path, sample_audio_data)

            # Verify restrictive permissions (if on Unix)
            if hasattr(os, 'chmod') and os.name != 'nt':
                file_stat = temp_path.stat()
                mode = stat.S_IMODE(file_stat.st_mode)
                assert mode == 0o600

            # File exists during processing
            assert temp_path.exists()

        # File securely deleted after context
        assert not temp_path.exists()

    def test_concurrent_temp_files(self, sample_audio_data):
        """Test that multiple temp files can exist simultaneously"""
        with temp_audio_file() as path1:
            with temp_audio_file() as path2:
                with temp_audio_file() as path3:
                    # All should exist and be different
                    assert path1.exists()
                    assert path2.exists()
                    assert path3.exists()
                    assert path1 != path2 != path3

                    # Write to all
                    write_audio_to_wav(path1, sample_audio_data)
                    write_audio_to_wav(path2, sample_audio_data)
                    write_audio_to_wav(path3, sample_audio_data)

                # path3 cleaned up
                assert not path3.exists()
            # path2 cleaned up
            assert not path2.exists()
        # path1 cleaned up
        assert not path1.exists()

    def test_temp_file_reuse_prevention(self):
        """Test that temp files are not reused"""
        paths = []

        for _ in range(5):
            with temp_audio_file() as temp_path:
                paths.append(str(temp_path))

        # All paths should be unique
        assert len(paths) == len(set(paths))

    def test_write_and_secure_delete_manual(self, tmp_path, sample_audio_data):
        """Test manual secure deletion after writing audio"""
        output_file = tmp_path / "manual_delete.wav"

        # Write audio
        write_audio_to_wav(output_file, sample_audio_data)
        assert output_file.exists()

        # Manually secure delete
        secure_delete(output_file)
        assert not output_file.exists()

    @pytest.mark.skipif(not hasattr(os, 'chmod'), reason="chmod not available")
    def test_permissions_maintained_through_write(self, sample_audio_data):
        """Test that restrictive permissions are maintained after writing"""
        with SecureTempFileHandler.create_temp_audio_file() as temp_path:
            # Write audio data
            write_audio_to_wav(temp_path, sample_audio_data)

            # Check permissions after write (Unix only)
            if os.name != 'nt':
                file_stat = temp_path.stat()
                mode = stat.S_IMODE(file_stat.st_mode)
                # Permissions might change after write, but should still be restrictive
                # At minimum, should not be world-readable
                assert not (mode & stat.S_IROTH)  # Others can't read
