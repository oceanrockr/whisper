"""
Security Test Verification Script

Quick script to verify security test modules can be imported and basic functionality works.
Run this before running full pytest suite to catch import errors early.
"""

import sys
from pathlib import Path

def verify_imports():
    """Verify all required modules can be imported"""
    print("Verifying imports...")

    try:
        import pytest
        print("[PASS] pytest available")
    except ImportError:
        print("[FAIL] pytest not found - install with: py -m pip install pytest")
        return False

    try:
        import numpy
        print("[PASS] numpy available")
    except ImportError:
        print("[FAIL] numpy not found - install with: py -m pip install numpy")
        return False

    try:
        import wave
        print("[PASS] wave module available")
    except ImportError:
        print("[FAIL] wave module not found (should be in standard library)")
        return False

    try:
        import security_utils
        print("[PASS] security_utils module available")
    except ImportError as e:
        print(f"[FAIL] security_utils module not found: {e}")
        return False

    try:
        import temp_file_handler
        print("[PASS] temp_file_handler module available")
    except ImportError as e:
        print(f"[FAIL] temp_file_handler module not found: {e}")
        return False

    return True


def verify_test_files():
    """Verify test files exist"""
    print("\nVerifying test files...")

    test_dir = Path(__file__).parent / "tests"

    security_utils_tests = test_dir / "test_security_utils.py"
    temp_handler_tests = test_dir / "test_temp_file_handler.py"

    if security_utils_tests.exists():
        print(f"[PASS] test_security_utils.py exists ({security_utils_tests.stat().st_size:,} bytes)")
    else:
        print(f"[FAIL] test_security_utils.py not found at {security_utils_tests}")
        return False

    if temp_handler_tests.exists():
        print(f"[PASS] test_temp_file_handler.py exists ({temp_handler_tests.stat().st_size:,} bytes)")
    else:
        print(f"[FAIL] test_temp_file_handler.py not found at {temp_handler_tests}")
        return False

    return True


def count_tests():
    """Count test cases in test files"""
    print("\nCounting test cases...")

    test_dir = Path(__file__).parent / "tests"

    security_utils_tests = test_dir / "test_security_utils.py"
    temp_handler_tests = test_dir / "test_temp_file_handler.py"

    def count_test_methods(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return content.count('def test_')

    security_count = count_test_methods(security_utils_tests)
    temp_count = count_test_methods(temp_handler_tests)

    print(f"[PASS] test_security_utils.py: {security_count} test cases")
    print(f"[PASS] test_temp_file_handler.py: {temp_count} test cases")
    print(f"[PASS] Total: {security_count + temp_count} test cases")

    return True


def verify_basic_functionality():
    """Test basic functionality of security modules"""
    print("\nVerifying basic functionality...")

    try:
        from security_utils import InputSanitizer, PathValidator, SecurityError

        # Test InputSanitizer
        text = "Hello World"
        result = InputSanitizer.sanitize_text_for_typing(text)
        assert result == text
        print("[PASS] InputSanitizer.sanitize_text_for_typing works")

        # Test validation
        assert InputSanitizer.validate_text_content("valid text")
        print("[PASS] InputSanitizer.validate_text_content works")

        # Test PathValidator
        filename = "test<file>.txt"
        safe_name = PathValidator.sanitize_filename(filename)
        assert "<" not in safe_name
        assert ">" not in safe_name
        print("[PASS] PathValidator.sanitize_filename works")

        # Test SecurityError
        try:
            raise SecurityError("test")
        except SecurityError:
            pass
        print("[PASS] SecurityError works")

    except Exception as e:
        print(f"[FAIL] Basic functionality test failed: {e}")
        return False

    try:
        from temp_file_handler import SecureTempFileHandler, write_audio_to_wav, secure_delete
        import numpy as np
        from pathlib import Path
        import tempfile

        # Test temp file creation
        with SecureTempFileHandler.create_temp_audio_file() as temp_path:
            assert temp_path.exists()
            assert isinstance(temp_path, Path)
        assert not temp_path.exists()  # Should be deleted
        print("[PASS] SecureTempFileHandler.create_temp_audio_file works")

        # Test audio writing
        audio_data = np.random.randn(1000).astype(np.float32) * 0.1
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            temp_wav = Path(f.name)
        write_audio_to_wav(temp_wav, audio_data)
        assert temp_wav.exists()
        print("[PASS] write_audio_to_wav works")

        # Test secure delete
        secure_delete(temp_wav)
        assert not temp_wav.exists()
        print("[PASS] secure_delete works")

    except Exception as e:
        print(f"[FAIL] Temp file handler test failed: {e}")
        return False

    return True


def main():
    """Main verification routine"""
    print("=" * 70)
    print("Security Test Verification")
    print("=" * 70)

    results = []

    results.append(("Import verification", verify_imports()))
    results.append(("Test file verification", verify_test_files()))
    results.append(("Test counting", count_tests()))
    results.append(("Basic functionality", verify_basic_functionality()))

    print("\n" + "=" * 70)
    print("Verification Summary")
    print("=" * 70)

    all_passed = all(result for _, result in results)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status}: {name}")

    print("=" * 70)

    if all_passed:
        print("\n[SUCCESS] All verifications passed!")
        print("\nYou can now run the full test suite with:")
        print("  py -m pytest tests/test_security_utils.py tests/test_temp_file_handler.py -v")
        return 0
    else:
        print("\n[ERROR] Some verifications failed!")
        print("Please fix the issues above before running the full test suite.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
