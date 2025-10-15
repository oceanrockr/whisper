"""
Security utilities for Veleron Whisper applications
Provides input sanitization and validation functions
"""

import re
import os
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class InputSanitizer:
    """Sanitize user inputs for security"""

    # Control characters to remove (except whitespace)
    CONTROL_CHARS = ''.join(
        chr(i) for i in range(32) if chr(i) not in '\t\n\r'
    ) + chr(127)

    # Dangerous keyboard sequences (PyAutoGUI format)
    DANGEROUS_SEQUENCES = [
        r'\^[a-z]',      # Ctrl sequences (^a, ^c, etc.)
        r'%[a-z]',       # Alt sequences (%f, %e, etc.)
        r'\+[a-z]',      # Shift sequences (+a, +b, etc.)
        r'{[^}]+}',      # Special key sequences ({enter}, {delete}, etc.)
    ]

    @classmethod
    def sanitize_text_for_typing(cls, text: str, max_length: int = 10000) -> str:
        """
        Sanitize text before typing with PyAutoGUI

        Args:
            text: Text to sanitize
            max_length: Maximum allowed text length

        Returns:
            Sanitized text safe for keyboard automation

        Raises:
            ValueError: If text is too long or invalid
        """
        if not text:
            return ""

        # Enforce length limit
        if len(text) > max_length:
            logger.warning(f"Text truncated from {len(text)} to {max_length} characters")
            text = text[:max_length]

        # Remove control characters (keep common whitespace)
        text = ''.join(
            char for char in text
            if char not in cls.CONTROL_CHARS
        )

        # Remove dangerous keyboard sequences
        for pattern in cls.DANGEROUS_SEQUENCES:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        # Remove null bytes
        text = text.replace('\x00', '')

        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)

        # Trim
        text = text.strip()

        return text

    @classmethod
    def validate_text_content(cls, text: str) -> bool:
        """
        Validate that text is safe for processing

        Args:
            text: Text to validate

        Returns:
            True if text is safe, False otherwise
        """
        if not text:
            return False

        # Check for null bytes
        if '\x00' in text:
            return False

        # Check for excessive control characters
        control_count = sum(1 for c in text if c in cls.CONTROL_CHARS)
        if control_count > len(text) * 0.1:  # >10% control chars
            return False

        return True


class PathValidator:
    """Validate and sanitize file paths"""

    # Sensitive system paths to block
    BLOCKED_PATHS_WINDOWS = [
        r'C:\Windows',
        r'C:\Program Files',
        r'C:\Program Files (x86)',
        r'C:\ProgramData',
    ]

    BLOCKED_PATHS_UNIX = [
        '/etc',
        '/sys',
        '/proc',
        '/boot',
        '/bin',
        '/sbin',
        '/usr/bin',
        '/usr/sbin',
    ]

    @classmethod
    def validate_output_path(
        cls,
        file_path: str,
        allowed_extensions: Optional[list] = None,
        base_dir: Optional[Path] = None
    ) -> Path:
        """
        Validate output file path for security

        Args:
            file_path: Path to validate
            allowed_extensions: List of allowed file extensions (e.g., ['.txt', '.json'])
            base_dir: Base directory to restrict paths to (default: user home)

        Returns:
            Validated absolute Path object

        Raises:
            ValueError: If path is invalid or unsafe
            SecurityError: If path violates security constraints
        """
        if not file_path:
            raise ValueError("File path cannot be empty")

        # Convert to Path and get absolute path
        path = Path(file_path).resolve()

        # Set default base directory to user home
        if base_dir is None:
            base_dir = Path.home()
        else:
            base_dir = Path(base_dir).resolve()

        # Ensure path is within base directory (prevent directory traversal)
        try:
            path.relative_to(base_dir)
        except ValueError:
            raise SecurityError(
                f"File path must be within {base_dir}. "
                f"Attempted path: {path}"
            )

        # Check for system paths
        path_str = str(path)
        blocked_paths = (
            cls.BLOCKED_PATHS_WINDOWS if os.name == 'nt'
            else cls.BLOCKED_PATHS_UNIX
        )

        for blocked in blocked_paths:
            if path_str.startswith(blocked):
                raise SecurityError(
                    f"Cannot write to system directory: {blocked}"
                )

        # Validate extension
        if allowed_extensions:
            ext = path.suffix.lower()
            if ext not in [e.lower() for e in allowed_extensions]:
                raise ValueError(
                    f"Invalid file extension '{ext}'. "
                    f"Allowed: {allowed_extensions}"
                )

        # Ensure parent directory exists or can be created
        if not path.parent.exists():
            logger.info(f"Creating directory: {path.parent}")
            path.parent.mkdir(parents=True, exist_ok=True)

        return path

    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """
        Sanitize filename to remove dangerous characters

        Args:
            filename: Filename to sanitize

        Returns:
            Safe filename
        """
        # Remove path separators
        filename = filename.replace('/', '_').replace('\\', '_')

        # Remove other dangerous characters
        filename = re.sub(r'[<>:"|?*\x00-\x1f]', '_', filename)

        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:250] + ext

        # Ensure not empty
        if not filename or filename.isspace():
            filename = 'untitled'

        return filename


class SecurityError(Exception):
    """Custom exception for security violations"""
    pass


# Convenience functions
def sanitize_for_typing(text: str) -> str:
    """Shorthand for text sanitization"""
    return InputSanitizer.sanitize_text_for_typing(text)


def validate_path(file_path: str, allowed_extensions: Optional[list] = None) -> Path:
    """Shorthand for path validation"""
    return PathValidator.validate_output_path(file_path, allowed_extensions)
