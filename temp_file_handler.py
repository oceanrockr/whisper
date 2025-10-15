"""
Secure temporary file handling for audio processing
"""

import tempfile
import os
import wave
import numpy as np
from pathlib import Path
from contextlib import contextmanager
from typing import Generator
import logging

logger = logging.getLogger(__name__)


class SecureTempFileHandler:
    """Handle temporary files securely"""

    @staticmethod
    @contextmanager
    def create_temp_audio_file(
        suffix: str = '.wav',
        prefix: str = 'veleron_audio_'
    ) -> Generator[Path, None, None]:
        """
        Create a secure temporary audio file with guaranteed cleanup

        Args:
            suffix: File suffix (extension)
            prefix: File prefix for identification

        Yields:
            Path to temporary file

        Example:
            with create_temp_audio_file() as temp_path:
                # Use temp_path
                write_audio_to_wav(temp_path, audio_data)
                result = transcribe(temp_path)
            # File automatically deleted here
        """
        temp_file = None
        temp_path = None

        try:
            # Create temporary file with secure permissions
            temp_file = tempfile.NamedTemporaryFile(
                mode='w+b',
                suffix=suffix,
                prefix=prefix,
                delete=False
            )
            temp_path = Path(temp_file.name)

            # Set restrictive permissions (owner read/write only)
            # This works on Unix-like systems
            if hasattr(os, 'chmod'):
                os.chmod(temp_path, 0o600)

            # Close file handle but keep file
            temp_file.close()

            logger.debug(f"Created secure temp file: {temp_path}")

            yield temp_path

        except Exception as e:
            logger.error(f"Error with temporary file: {e}")
            raise

        finally:
            # Guaranteed cleanup
            if temp_path and temp_path.exists():
                try:
                    # Secure deletion (overwrite before delete)
                    secure_delete(temp_path)
                    logger.debug(f"Deleted temp file: {temp_path}")
                except Exception as e:
                    logger.warning(f"Failed to delete temp file {temp_path}: {e}")


def write_audio_to_wav(
    file_path: Path,
    audio_data: np.ndarray,
    sample_rate: int = 16000,
    channels: int = 1
) -> None:
    """
    Write audio data to WAV file

    Args:
        file_path: Output file path
        audio_data: Audio samples (float32, -1.0 to 1.0)
        sample_rate: Sample rate in Hz
        channels: Number of audio channels
    """
    # Ensure audio is 1D if mono
    if channels == 1 and audio_data.ndim > 1:
        audio_data = audio_data.flatten()

    # Convert float to int16
    audio_int16 = (audio_data * 32767).astype(np.int16)

    # Write WAV file
    with wave.open(str(file_path), 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(audio_int16.tobytes())


def secure_delete(file_path: Path) -> None:
    """
    Securely delete a file by overwriting before removal

    Args:
        file_path: Path to file to delete
    """
    if not file_path.exists():
        return

    try:
        # Get file size
        file_size = file_path.stat().st_size

        # Overwrite with random data (multiple passes for extra security)
        with open(file_path, 'wb') as f:
            # Pass 1: Random data
            f.write(os.urandom(file_size))
            f.flush()
            os.fsync(f.fileno())

            # Pass 2: Zeros
            f.seek(0)
            f.write(b'\x00' * file_size)
            f.flush()
            os.fsync(f.fileno())

        # Delete file
        file_path.unlink()

    except Exception as e:
        logger.error(f"Secure delete failed for {file_path}: {e}")
        # Fallback to regular delete
        try:
            file_path.unlink()
        except:
            pass


# Convenience function
@contextmanager
def temp_audio_file() -> Generator[Path, None, None]:
    """Shorthand for creating temporary audio file"""
    with SecureTempFileHandler.create_temp_audio_file() as path:
        yield path
