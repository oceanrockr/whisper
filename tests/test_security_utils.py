"""
Unit tests for security_utils module

Tests input sanitization, path validation, and security controls
to ensure the security utilities work correctly.
"""

import pytest
import os
import platform
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile

from security_utils import (
    InputSanitizer,
    PathValidator,
    SecurityError,
    sanitize_for_typing,
    validate_path
)


class TestInputSanitizer:
    """Tests for InputSanitizer class"""

    def test_sanitize_normal_text(self):
        """Test that normal text passes through unchanged"""
        text = "This is a normal sentence with punctuation."
        result = InputSanitizer.sanitize_text_for_typing(text)
        assert result == text

    def test_sanitize_preserves_basic_whitespace(self):
        """Test that tabs, newlines, and spaces are preserved (but normalized)"""
        text = "Line 1\nLine 2\tTabbed"
        result = InputSanitizer.sanitize_text_for_typing(text)
        # Whitespace is normalized to single spaces
        assert "Line 1" in result
        assert "Line 2" in result
        assert "Tabbed" in result

    def test_sanitize_removes_control_characters(self):
        """Test removal of control characters (ASCII 0-31 except whitespace)"""
        # Include some control characters
        text = "Hello\x01World\x02Test\x03"
        result = InputSanitizer.sanitize_text_for_typing(text)
        assert result == "HelloWorldTest"

    def test_sanitize_removes_null_bytes(self):
        """Test removal of null bytes"""
        text = "Hello\x00World"
        result = InputSanitizer.sanitize_text_for_typing(text)
        assert result == "Hello World"

    def test_sanitize_removes_ctrl_sequences(self):
        """Test removal of Ctrl key sequences (^a, ^c, etc.)"""
        text = "Normal text ^c should be safe ^v"
        result = InputSanitizer.sanitize_text_for_typing(text)
        assert "^c" not in result
        assert "^v" not in result
        assert "Normal text" in result
        assert "should be safe" in result

    def test_sanitize_removes_alt_sequences(self):
        """Test removal of Alt key sequences (%f, %e, etc.)"""
        text = "Text with %f Alt sequence %e here"
        result = InputSanitizer.sanitize_text_for_typing(text)
        assert "%f" not in result
        assert "%e" not in result

    def test_sanitize_removes_shift_sequences(self):
        """Test removal of Shift key sequences (+a, +b, etc.)"""
        text = "Text with +a shift sequence +b here"
        result = InputSanitizer.sanitize_text_for_typing(text)
        assert "+a" not in result
        assert "+b" not in result

    def test_sanitize_removes_special_key_sequences(self):
        """Test removal of special key sequences like {enter}, {delete}"""
        text = "Press {enter} to continue {delete} this"
        result = InputSanitizer.sanitize_text_for_typing(text)
        assert "{enter}" not in result
        assert "{delete}" not in result
        assert "Press" in result
        assert "to continue" in result

    def test_sanitize_normalizes_whitespace(self):
        """Test that multiple whitespace characters are normalized"""
        text = "Too    many     spaces"
        result = InputSanitizer.sanitize_text_for_typing(text)
        assert result == "Too many spaces"

    def test_sanitize_enforces_length_limit(self):
        """Test that text exceeding max_length is truncated"""
        text = "a" * 15000
        result = InputSanitizer.sanitize_text_for_typing(text, max_length=10000)
        assert len(result) <= 10000

    def test_sanitize_custom_length_limit(self):
        """Test custom length limit"""
        text = "a" * 200
        result = InputSanitizer.sanitize_text_for_typing(text, max_length=100)
        assert len(result) <= 100

    def test_sanitize_empty_string(self):
        """Test handling of empty string"""
        result = InputSanitizer.sanitize_text_for_typing("")
        assert result == ""

    def test_sanitize_whitespace_only(self):
        """Test handling of whitespace-only string"""
        result = InputSanitizer.sanitize_text_for_typing("   \t\n  ")
        assert result == ""

    def test_sanitize_strips_leading_trailing_whitespace(self):
        """Test that leading and trailing whitespace is stripped"""
        text = "  Hello World  "
        result = InputSanitizer.sanitize_text_for_typing(text)
        assert result == "Hello World"

    def test_sanitize_complex_input(self):
        """Test sanitization of complex input with multiple issues"""
        text = "  Hello\x00{enter}World^c\t\t\tTest%f   "
        result = InputSanitizer.sanitize_text_for_typing(text)
        # Should remove null bytes, special sequences, normalize whitespace
        assert "\x00" not in result
        assert "{enter}" not in result
        assert "^c" not in result
        assert "%f" not in result
        assert "Hello" in result
        assert "World" in result
        assert "Test" in result

    def test_validate_text_content_valid(self):
        """Test that valid text passes validation"""
        text = "This is valid text"
        assert InputSanitizer.validate_text_content(text) is True

    def test_validate_text_content_empty(self):
        """Test that empty text fails validation"""
        assert InputSanitizer.validate_text_content("") is False

    def test_validate_text_content_null_bytes(self):
        """Test that text with null bytes fails validation"""
        text = "Hello\x00World"
        assert InputSanitizer.validate_text_content(text) is False

    def test_validate_text_content_excessive_control_chars(self):
        """Test that text with >10% control characters fails validation"""
        # Create text with 50% control characters
        text = "a\x01b\x02c\x03d\x04e\x05"
        assert InputSanitizer.validate_text_content(text) is False

    def test_validate_text_content_acceptable_control_chars(self):
        """Test that text with <10% control characters passes validation"""
        # Create text with ~5% control characters
        text = "abcdefghij\x01klmnopqrst"
        assert InputSanitizer.validate_text_content(text) is True

    def test_sanitize_for_typing_convenience_function(self):
        """Test the convenience function sanitize_for_typing"""
        text = "Test {enter} text"
        result = sanitize_for_typing(text)
        assert "{enter}" not in result
        assert "Test" in result


class TestPathValidator:
    """Tests for PathValidator class"""

    def test_validate_user_path(self, tmp_path):
        """Test validation of path within user's home directory"""
        # Create a test file path in home directory
        test_file = Path.home() / "test_file.txt"
        result = PathValidator.validate_output_path(str(test_file))
        assert result == test_file.resolve()

    def test_validate_path_with_base_dir(self, tmp_path):
        """Test validation with custom base directory"""
        test_file = tmp_path / "test_file.txt"
        result = PathValidator.validate_output_path(
            str(test_file),
            base_dir=tmp_path
        )
        assert result == test_file.resolve()

    def test_validate_blocks_directory_traversal(self, tmp_path):
        """Test that directory traversal attempts are blocked"""
        # Try to escape tmp_path using ../
        malicious_path = tmp_path / ".." / ".." / "etc" / "passwd"

        with pytest.raises(SecurityError) as exc_info:
            PathValidator.validate_output_path(
                str(malicious_path),
                base_dir=tmp_path
            )
        assert "must be within" in str(exc_info.value)

    @pytest.mark.skipif(os.name != 'nt', reason="Windows-specific test")
    def test_validate_blocks_windows_system_paths(self):
        """Test blocking of Windows system paths"""
        system_path = r"C:\Windows\System32\evil.txt"

        with pytest.raises(SecurityError) as exc_info:
            PathValidator.validate_output_path(
                system_path,
                base_dir=Path("C:\\Users")
            )
        # Should fail either due to system path or being outside base_dir
        assert "system directory" in str(exc_info.value) or "must be within" in str(exc_info.value)

    @pytest.mark.skipif(os.name == 'nt', reason="Unix-specific test")
    def test_validate_blocks_unix_system_paths(self, tmp_path):
        """Test blocking of Unix system paths"""
        # Try to write to /etc
        system_path = "/etc/evil.conf"

        with pytest.raises(SecurityError):
            PathValidator.validate_output_path(
                system_path,
                base_dir=tmp_path
            )

    def test_validate_allowed_extensions(self, tmp_path):
        """Test validation of allowed file extensions"""
        test_file = tmp_path / "test.txt"
        result = PathValidator.validate_output_path(
            str(test_file),
            allowed_extensions=['.txt', '.json'],
            base_dir=tmp_path
        )
        assert result == test_file.resolve()

    def test_validate_blocks_disallowed_extensions(self, tmp_path):
        """Test blocking of disallowed file extensions"""
        test_file = tmp_path / "test.exe"

        with pytest.raises(ValueError) as exc_info:
            PathValidator.validate_output_path(
                str(test_file),
                allowed_extensions=['.txt', '.json'],
                base_dir=tmp_path
            )
        assert "Invalid file extension" in str(exc_info.value)

    def test_validate_case_insensitive_extensions(self, tmp_path):
        """Test that extension validation is case-insensitive"""
        test_file = tmp_path / "test.TXT"
        result = PathValidator.validate_output_path(
            str(test_file),
            allowed_extensions=['.txt'],
            base_dir=tmp_path
        )
        assert result == test_file.resolve()

    def test_validate_creates_parent_directory(self, tmp_path):
        """Test that parent directory is created if it doesn't exist"""
        test_file = tmp_path / "subdir1" / "subdir2" / "test.txt"

        result = PathValidator.validate_output_path(
            str(test_file),
            base_dir=tmp_path
        )

        assert result == test_file.resolve()
        assert result.parent.exists()

    def test_validate_empty_path(self):
        """Test that empty path raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            PathValidator.validate_output_path("")
        assert "cannot be empty" in str(exc_info.value)

    def test_validate_returns_absolute_path(self, tmp_path):
        """Test that returned path is absolute"""
        test_file = tmp_path / "test.txt"
        result = PathValidator.validate_output_path(
            str(test_file),
            base_dir=tmp_path
        )
        assert result.is_absolute()

    def test_sanitize_filename_removes_path_separators(self):
        """Test removal of path separators from filename"""
        filename = "path/to/file.txt"
        result = PathValidator.sanitize_filename(filename)
        assert "/" not in result
        assert "\\" not in result
        assert result == "path_to_file.txt"

    def test_sanitize_filename_removes_dangerous_chars(self):
        """Test removal of dangerous characters from filename"""
        filename = "file<>:\"|?*.txt"
        result = PathValidator.sanitize_filename(filename)
        # All dangerous chars should be replaced with _
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
        assert '"' not in result
        assert "|" not in result
        assert "?" not in result
        assert "*" not in result

    def test_sanitize_filename_limits_length(self):
        """Test that filename length is limited to 255 characters"""
        filename = "a" * 300 + ".txt"
        result = PathValidator.sanitize_filename(filename)
        assert len(result) <= 255

    def test_sanitize_filename_preserves_extension(self):
        """Test that file extension is preserved when truncating"""
        filename = "a" * 300 + ".txt"
        result = PathValidator.sanitize_filename(filename)
        assert result.endswith(".txt")

    def test_sanitize_filename_empty_string(self):
        """Test handling of empty filename"""
        result = PathValidator.sanitize_filename("")
        assert result == "untitled"

    def test_sanitize_filename_whitespace_only(self):
        """Test handling of whitespace-only filename"""
        result = PathValidator.sanitize_filename("   ")
        assert result == "untitled"

    def test_sanitize_filename_normal_name(self):
        """Test that normal filename passes through with minimal changes"""
        filename = "my_file.txt"
        result = PathValidator.sanitize_filename(filename)
        assert result == "my_file.txt"

    def test_validate_path_convenience_function(self, tmp_path):
        """Test the convenience function validate_path"""
        test_file = tmp_path / "test.txt"

        # Use the convenience function with home directory as default
        # We need to ensure the path is within home
        home_file = Path.home() / "test.txt"
        result = validate_path(str(home_file))
        assert result == home_file.resolve()


class TestSecurityError:
    """Tests for SecurityError exception"""

    def test_security_error_raised(self):
        """Test that SecurityError can be raised and caught"""
        with pytest.raises(SecurityError):
            raise SecurityError("Test error")

    def test_security_error_message(self):
        """Test that SecurityError preserves error message"""
        message = "Security violation detected"
        with pytest.raises(SecurityError) as exc_info:
            raise SecurityError(message)
        assert message in str(exc_info.value)

    def test_security_error_is_exception(self):
        """Test that SecurityError is an Exception subclass"""
        error = SecurityError("test")
        assert isinstance(error, Exception)


class TestIntegrationScenarios:
    """Integration tests for common security scenarios"""

    def test_sanitize_and_validate_workflow(self, tmp_path):
        """Test complete workflow: sanitize text and validate path"""
        # Sanitize some potentially dangerous text
        text = "Save this {enter} to file^c"
        clean_text = InputSanitizer.sanitize_text_for_typing(text)

        # Create a safe filename from cleaned text
        filename = PathValidator.sanitize_filename(clean_text + ".txt")

        # Validate the full path
        full_path = tmp_path / filename
        validated_path = PathValidator.validate_output_path(
            str(full_path),
            allowed_extensions=['.txt'],
            base_dir=tmp_path
        )

        assert validated_path.parent == tmp_path
        assert validated_path.name == filename

    def test_multiple_security_checks(self, tmp_path):
        """Test multiple security checks in sequence"""
        # Check text is safe
        text = "User input data"
        assert InputSanitizer.validate_text_content(text)

        # Sanitize it
        clean_text = InputSanitizer.sanitize_text_for_typing(text)

        # Create safe path
        file_path = tmp_path / "output.txt"
        validated_path = PathValidator.validate_output_path(
            str(file_path),
            base_dir=tmp_path
        )

        # All checks should pass
        assert clean_text == text  # No changes needed
        assert validated_path.parent.exists()

    def test_malicious_input_handling(self, tmp_path):
        """Test handling of various malicious inputs"""
        malicious_inputs = [
            "Run {enter}malicious^c command%f",
            "Path ../../etc/passwd",
            "Null\x00byte\x00attack",
            "Control\x01chars\x02everywhere\x03"
        ]

        for malicious in malicious_inputs:
            # Should sanitize successfully
            clean = InputSanitizer.sanitize_text_for_typing(malicious)
            # Should not contain dangerous sequences
            assert "{enter}" not in clean
            assert "^c" not in clean
            assert "%f" not in clean
            assert "\x00" not in clean

    def test_edge_case_paths(self, tmp_path):
        """Test various edge cases for path validation"""
        # Very long path component
        long_name = "a" * 300
        safe_name = PathValidator.sanitize_filename(long_name)
        assert len(safe_name) <= 255

        # Path with spaces
        path_with_spaces = tmp_path / "my folder" / "my file.txt"
        result = PathValidator.validate_output_path(
            str(path_with_spaces),
            base_dir=tmp_path
        )
        assert result.parent.exists()

        # Path with unicode
        unicode_path = tmp_path / "файл.txt"
        result = PathValidator.validate_output_path(
            str(unicode_path),
            base_dir=tmp_path
        )
        assert result.parent == tmp_path
