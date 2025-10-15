"""
Verify security fixes are properly applied

This script tests all security modules and verifies that critical
security fixes are working correctly before deployment.

Usage:
    python verify_security_fixes.py

Exit Codes:
    0 - All tests passed
    1 - One or more tests failed
"""

import sys
from pathlib import Path


def verify_security_modules():
    """Verify security modules exist"""
    required_files = [
        'security_utils.py',
        'temp_file_handler.py'
    ]

    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)

    if missing:
        print(f"FAILED: Missing security modules: {missing}")
        return False

    print("PASSED: All security modules present")
    return True


def verify_imports():
    """Verify applications import security modules"""
    try:
        from security_utils import sanitize_for_typing, validate_path
        from temp_file_handler import temp_audio_file

        print("PASSED: Security modules can be imported")
        return True
    except ImportError as e:
        print(f"FAILED: Import error: {e}")
        return False


def verify_sanitization():
    """Test input sanitization"""
    from security_utils import sanitize_for_typing

    test_cases = [
        ("Hello world", "Hello world"),
        ("Test^C", "Test"),  # Ctrl+C sequence removed (^C is a keyboard shortcut)
        ("Line1\x00Line2", "Line1Line2"),  # Null byte removed
        ("Test{enter}", "Test"),  # Special key removed
    ]

    for input_text, expected in test_cases:
        result = sanitize_for_typing(input_text)
        if result != expected:
            print(f"FAILED: Sanitization failed: '{input_text}' -> '{result}' (expected '{expected}')")
            return False

    print("PASSED: Input sanitization working correctly")
    return True


def verify_path_validation():
    """Test path validation"""
    from security_utils import validate_path, SecurityError
    from pathlib import Path

    # Should succeed (user home)
    try:
        safe_path = validate_path(
            str(Path.home() / 'test.txt'),
            allowed_extensions=['.txt']
        )
        print("PASSED: Valid path accepted")
    except:
        print("FAILED: Valid path rejected")
        return False

    # Should fail (system directory)
    try:
        if sys.platform == 'win32':
            validate_path('C:\\Windows\\test.txt')
        else:
            validate_path('/etc/test.txt')

        print("FAILED: System path was not blocked!")
        return False
    except SecurityError:
        print("PASSED: System path blocked correctly")

    return True


def main():
    """Run all verification tests"""
    print("=" * 60)
    print("SECURITY FIXES VERIFICATION")
    print("=" * 60)
    print()

    tests = [
        ("Security Modules", verify_security_modules),
        ("Module Imports", verify_imports),
        ("Input Sanitization", verify_sanitization),
        ("Path Validation", verify_path_validation),
    ]

    results = []

    for name, test_func in tests:
        print(f"\nTesting: {name}")
        print("-" * 60)
        results.append(test_func())

    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    if all(results):
        print("\nPASSED: ALL SECURITY FIXES VERIFIED SUCCESSFULLY")
        return 0
    else:
        print("\nFAILED: SOME SECURITY FIXES FAILED VERIFICATION")
        return 1


if __name__ == "__main__":
    sys.exit(main())
