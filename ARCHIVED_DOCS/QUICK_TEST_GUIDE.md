# Quick Test Guide - Veleron Whisper Voice-to-Text

## 1-Minute Quick Start

```bash
# Install dependencies
pip install -r requirements-test.txt

# Run all tests with coverage
run_tests.bat coverage
```

That's it! The test suite will run and open a coverage report in your browser.

## Common Commands

| Command | What it does |
|---------|-------------|
| `run_tests.bat` | Run all tests |
| `run_tests.bat coverage` | Run tests + generate coverage report |
| `run_tests.bat fast` | Run only fast tests (skip slow ones) |
| `run_tests.bat dictation` | Test veleron_dictation.py only |
| `run_tests.bat voiceflow` | Test veleron_voice_flow.py only |
| `run_tests.bat office` | Test whisper_to_office.py only |
| `run_tests.bat integration` | Run integration tests only |

## Understanding Test Output

### Success
```
====== test session starts ======
tests/test_whisper_to_office.py ............ [ 26%]
tests/test_veleron_dictation.py ............. [ 60%]
tests/test_veleron_voice_flow.py ........... [ 88%]
tests/test_integration.py ............... [100%]

====== 173 passed in 18.52s ======
```

### Failure
```
FAILED tests/test_whisper_to_office.py::TestFormatTimestamp::test_format_seconds_only
```
Look for the `FAILED` line - it shows exactly which test broke.

## What's Being Tested?

### whisper_to_office.py (45 tests)
- Timestamp formatting
- Word document generation
- PowerPoint notes generation
- Meeting minutes generation
- CLI argument parsing
- Error handling

### veleron_dictation.py (52 tests)
- Real-time audio recording
- Model loading
- Transcription pipeline
- Hotkey functionality
- System tray integration
- Typing automation

### veleron_voice_flow.py (48 tests)
- GUI initialization
- Recording and transcription
- File transcription
- Export to TXT/JSON
- Clipboard operations
- Model switching

### Integration Tests (28 tests)
- Complete end-to-end workflows
- Multi-format export
- Error recovery
- Unicode handling

## Test Coverage Report

After running `run_tests.bat coverage`, open `htmlcov/index.html` to see:
- Line-by-line coverage
- Missing coverage areas
- Overall statistics

## Writing Your Own Tests

### Quick Template

```python
# In tests/test_my_feature.py

import pytest
from unittest.mock import Mock, patch

class TestMyFeature:
    """Tests for my new feature"""

    def test_basic_functionality(self, mock_whisper_load_model):
        """Test that my feature works"""
        # Arrange
        expected = "expected result"

        # Act
        result = my_function()

        # Assert
        assert result == expected
```

### Run Your New Test

```bash
pytest tests/test_my_feature.py -v
```

## Troubleshooting

### Tests Won't Run
**Error:** `pytest: command not found`
**Fix:** Run `pip install -r requirements-test.txt`

### Tests Hang
**Problem:** Not using mocks
**Fix:** Make sure you're using `mock_whisper_load_model` fixture

### Import Errors
**Problem:** Can't find application modules
**Fix:** Tests automatically add parent dir to path - check sys.path setup

## Advanced Usage

### Run Specific Test
```bash
# Run one test file
pytest tests/test_whisper_to_office.py

# Run one test class
pytest tests/test_whisper_to_office.py::TestFormatTimestamp

# Run one specific test
pytest tests/test_whisper_to_office.py::TestFormatTimestamp::test_format_seconds_only
```

### Run Tests in Parallel (Faster!)
```bash
pytest -n auto
```

### Stop on First Failure
```bash
pytest -x
```

### Show Print Statements
```bash
pytest -s
```

### Show More Details
```bash
pytest -vv
```

## Key Files

| File | Purpose |
|------|---------|
| `tests/conftest.py` | Shared test fixtures and mocks |
| `tests/test_*.py` | Individual test files |
| `requirements-test.txt` | Test dependencies |
| `pytest.ini` | Pytest configuration |
| `run_tests.bat` | Easy test runner |

## Test Statistics

- **Total Tests:** 173
- **Coverage:** 92%
- **Execution Time:** 15-30 seconds (fast tests)
- **Execution Time:** 2-5 minutes (all tests)

## Need Help?

1. Check `tests/README.md` for detailed documentation
2. Check `TESTING_SUMMARY.md` for comprehensive overview
3. Look at existing tests for examples
4. Run `pytest --help` for pytest options

## Pre-Commit Checklist

Before committing code:
- [ ] Run `run_tests.bat` - all tests pass
- [ ] Run `run_tests.bat coverage` - coverage at least 90%
- [ ] Review coverage report for new code
- [ ] Add tests for any new features
- [ ] Update tests if you changed functionality

## CI/CD Integration

The test suite is ready for CI/CD:
- No external dependencies (all mocked)
- No hardware requirements
- Fast execution
- Generates coverage reports
- Cross-platform compatible

## Quick Tips

1. **Mock everything external** - Models, audio devices, GUI
2. **Use fixtures** - Don't repeat setup code
3. **Test one thing** - Each test should verify one behavior
4. **Name tests clearly** - `test_function_with_input_returns_output`
5. **Mark slow tests** - Use `@pytest.mark.slow` for long tests
6. **Check coverage** - Aim for 90%+ on new code

That's it! You're ready to run tests. Start with `run_tests.bat coverage` and go from there.
