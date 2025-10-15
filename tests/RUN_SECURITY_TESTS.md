# Quick Guide: Running Security Module Tests

## Quick Start

```bash
# Navigate to project directory
cd "c:\Users\noelj\Projects\Veleron Dev Studios\Applications\whisper"

# Run all security tests
py -m pytest tests/test_security_utils.py tests/test_temp_file_handler.py -v
```

## Test Files

- **test_security_utils.py** - Tests for input sanitization and path validation (47 tests)
- **test_temp_file_handler.py** - Tests for secure temp file handling (37 tests)

## Common Commands

### Run All Security Tests
```bash
py -m pytest tests/test_security_utils.py tests/test_temp_file_handler.py -v
```

### Run Individual Test Files
```bash
# Security utils only
py -m pytest tests/test_security_utils.py -v

# Temp file handler only
py -m pytest tests/test_temp_file_handler.py -v
```

### Run Specific Test Class
```bash
# InputSanitizer tests only
py -m pytest tests/test_security_utils.py::TestInputSanitizer -v

# PathValidator tests only
py -m pytest tests/test_security_utils.py::TestPathValidator -v

# SecureTempFileHandler tests only
py -m pytest tests/test_temp_file_handler.py::TestSecureTempFileHandler -v
```

### Run Specific Test
```bash
# Run one test
py -m pytest tests/test_security_utils.py::TestInputSanitizer::test_sanitize_normal_text -v
```

### Run Tests by Keyword
```bash
# All tests with "sanitize" in the name
py -m pytest tests/test_security_utils.py -k "sanitize" -v

# All tests with "delete" in the name
py -m pytest tests/test_temp_file_handler.py -k "delete" -v
```

## Output Options

### Verbose Output
```bash
# Standard verbose
py -m pytest tests/test_security_utils.py -v

# Extra verbose (more details)
py -m pytest tests/test_security_utils.py -vv
```

### Show Print Statements
```bash
# Show stdout/stderr during tests
py -m pytest tests/test_security_utils.py -v -s
```

### Show Test Duration
```bash
# Show slowest 5 tests
py -m pytest tests/test_security_utils.py -v --durations=5
```

## Debugging Failed Tests

### Show Local Variables
```bash
# Show local variables on failure
py -m pytest tests/test_security_utils.py -v -l
```

### Detailed Traceback
```bash
# Full traceback on failure
py -m pytest tests/test_security_utils.py -v --tb=long
```

### Stop on First Failure
```bash
# Exit immediately on first failure
py -m pytest tests/test_security_utils.py -v -x
```

### Run Only Failed Tests
```bash
# Rerun only the tests that failed last time
py -m pytest tests/test_security_utils.py -v --lf
```

## Prerequisites

### Check Python Version
```bash
py --version
# Should be Python 3.13 or higher
```

### Check if pytest is installed
```bash
py -m pytest --version
```

### Install pytest if needed
```bash
py -m pip install pytest
```

### Check Test Dependencies
```bash
py -c "import numpy; import wave; print('Dependencies OK')"
```

## Test Coverage

### Install Coverage Tool
```bash
py -m pip install pytest-cov
```

### Run with Coverage
```bash
# Generate coverage report
py -m pytest tests/test_security_utils.py tests/test_temp_file_handler.py --cov=security_utils --cov=temp_file_handler --cov-report=html

# Open htmlcov/index.html in browser to view report
```

## Troubleshooting

### "No module named pytest"
```bash
# Install pytest
py -m pip install pytest
```

### "No module named numpy"
```bash
# Install numpy
py -m pip install numpy
```

### Tests fail on Windows with permission errors
- Some file permission tests are skipped on Windows (expected behavior)
- Antivirus software may interfere with file deletion tests
- Ensure you have write permissions in the test directory

### Platform-specific test failures
- Some tests are platform-specific and will be skipped automatically
- Windows: Unix permission tests are skipped
- Unix/Linux: Windows path tests are skipped

## Expected Results

### Successful Run
```
========================= test session starts =========================
platform win32 -- Python 3.13.7, pytest-X.X.X
collected 84 items

tests/test_security_utils.py::TestInputSanitizer::test_sanitize_normal_text PASSED [ 1%]
tests/test_security_utils.py::TestInputSanitizer::test_sanitize_preserves_basic_whitespace PASSED [ 2%]
... (more tests)
tests/test_temp_file_handler.py::TestIntegrationScenarios::test_permissions_maintained_through_write PASSED [100%]

========================= 84 passed in 2.45s =========================
```

### Some Tests Skipped (Normal on Windows)
```
========================= 82 passed, 2 skipped in 2.45s =========================
```
This is expected on Windows where Unix-specific tests are skipped.

## Integration with Development Workflow

### Before Committing Code
```bash
# Run security tests to ensure no regressions
py -m pytest tests/test_security_utils.py tests/test_temp_file_handler.py -v
```

### After Modifying Security Modules
```bash
# Run relevant tests
py -m pytest tests/test_security_utils.py -v  # if modified security_utils.py
py -m pytest tests/test_temp_file_handler.py -v  # if modified temp_file_handler.py
```

### Continuous Integration
```bash
# Run with coverage in CI pipeline
py -m pytest tests/test_security_utils.py tests/test_temp_file_handler.py --cov=security_utils --cov=temp_file_handler --cov-report=term-missing -v
```

## Test Statistics

- **Total Tests:** 84
- **test_security_utils.py:** 47 tests
- **test_temp_file_handler.py:** 37 tests
- **Average Execution Time:** ~2-3 seconds for all tests
- **Platform Coverage:** Windows, Linux, macOS

## Additional Resources

- Full test report: `SECURITY_TEST_REPORT.md`
- pytest documentation: https://docs.pytest.org/
- Project test configuration: `pytest.ini`
- Test fixtures: `tests/conftest.py`

---

**Quick Reference Card**

| Task | Command |
|------|---------|
| Run all security tests | `py -m pytest tests/test_security_utils.py tests/test_temp_file_handler.py -v` |
| Run one test file | `py -m pytest tests/test_security_utils.py -v` |
| Run specific test | `py -m pytest tests/test_security_utils.py::TestInputSanitizer::test_sanitize_normal_text -v` |
| Run tests by keyword | `py -m pytest tests/ -k "sanitize" -v` |
| Show local variables | `py -m pytest tests/ -v -l` |
| Stop on first failure | `py -m pytest tests/ -v -x` |
| Run with coverage | `py -m pytest tests/ --cov=security_utils --cov=temp_file_handler -v` |

---

**Last Updated:** 2025-10-12
