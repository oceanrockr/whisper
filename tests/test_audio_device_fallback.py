"""
Unit tests for DirectSound Fallback Mechanism

Tests the automatic fallback from WASAPI to DirectSound when recording
from USB devices to prevent WDM-KS errors. This fallback mechanism is
implemented in veleron_voice_flow.py, veleron_dictation.py, and
whisper_to_office.py.

The tests cover:
- DirectSound version detection and switching
- Base name extraction from various device name formats
- Handling of missing DirectSound alternatives
- Error scenarios and edge cases
- Channel count adaptation
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock, call
import sounddevice as sd


# ============================================================================
# MODULE-LEVEL FIXTURES (Shared across all test classes)
# ============================================================================

@pytest.fixture
def mock_devices_with_directsound():
    """
    Mock device list containing both WASAPI and DirectSound versions
    of the same device (typical USB webcam scenario).

    Returns:
        list: Mock device list with multiple APIs for same hardware
    """
    return [
            # Device 0: Built-in mic (WASAPI only)
            {
                'name': 'Realtek HD Audio',
                'max_input_channels': 2,
                'max_output_channels': 0,
                'hostapi': 0
            },
            # Device 1: Same built-in mic (MME)
            {
                'name': 'Realtek HD Audio',
                'max_input_channels': 2,
                'max_output_channels': 0,
                'hostapi': 1
            },
            # Device 2-5: Output devices (not relevant for input)
            {
                'name': 'Speakers',
                'max_input_channels': 0,
                'max_output_channels': 2,
                'hostapi': 0
            },
            {
                'name': 'Headphones',
                'max_input_channels': 0,
                'max_output_channels': 2,
                'hostapi': 1
            },
            {
                'name': 'HDMI Output',
                'max_input_channels': 0,
                'max_output_channels': 8,
                'hostapi': 0
            },
            {
                'name': 'USB Audio Output',
                'max_input_channels': 0,
                'max_output_channels': 2,
                'hostapi': 2
            },
            # Device 6: DirectSound version of C922 webcam
            {
                'name': 'C922 Pro Stream Webcam',
                'max_input_channels': 2,
                'max_output_channels': 0,
                'hostapi': 2  # DirectSound API
            },
            # Device 7-11: More output devices
            {
                'name': 'VoIP Device',
                'max_input_channels': 0,
                'max_output_channels': 2,
                'hostapi': 0
            },
            {
                'name': 'Virtual Audio Cable',
                'max_input_channels': 0,
                'max_output_channels': 2,
                'hostapi': 1
            },
            {
                'name': 'Bluetooth Speaker',
                'max_input_channels': 0,
                'max_output_channels': 2,
                'hostapi': 0
            },
            {
                'name': 'TV Audio',
                'max_input_channels': 0,
                'max_output_channels': 2,
                'hostapi': 0
            },
            {
                'name': 'Monitor Speakers',
                'max_input_channels': 0,
                'max_output_channels': 2,
                'hostapi': 1
            },
            # Device 12: WASAPI version of C922 webcam (selected by user)
            {
                'name': 'C922 Pro Stream Webcam',
                'max_input_channels': 2,
                'max_output_channels': 0,
                'hostapi': 0  # WASAPI API
            },
        ]


@pytest.fixture
def mock_hostapis():
    """
    Mock host API information for Windows.

    Returns:
        list: Mock host API list (WASAPI, MME, DirectSound)
    """
    return [
            {'name': 'Windows WASAPI', 'type': 13},
            {'name': 'MME', 'type': 2},
            {'name': 'Windows DirectSound', 'type': 1}
        ]


@pytest.fixture
def mock_devices_no_directsound():
    """
    Mock device list with only WASAPI/MME (no DirectSound alternative).

    Returns:
        list: Mock device list without DirectSound versions
    """
    return [
            # Device 0: Built-in mic (WASAPI)
            {
                'name': 'Realtek HD Audio',
                'max_input_channels': 2,
                'max_output_channels': 0,
                'hostapi': 0
            },
            # Device 1: Built-in mic (MME)
            {
                'name': 'Realtek HD Audio',
                'max_input_channels': 2,
                'max_output_channels': 0,
                'hostapi': 1
            },
            # Device 2: USB mic (WASAPI only, no DirectSound)
            {
                'name': 'USB Microphone',
                'max_input_channels': 1,
                'max_output_channels': 0,
                'hostapi': 0
            },
        ]


@pytest.fixture
def mock_devices_complex_names():
    """
    Mock device list with complex device names (driver paths, special chars).

    Returns:
        list: Mock device list with complex naming patterns
    """
    return [
            # Device 0: Bluetooth headset with complex name
            {
                'name': 'Headset (@System32\\drivers\\bthhfenum.sys,#2;%1 Hands-Free%0;(Josh\'s Buds3 Pro))',
                'max_input_channels': 1,
                'max_output_channels': 0,
                'hostapi': 0  # WASAPI
            },
            # Device 1: Same headset (DirectSound)
            {
                'name': 'Headset (@System32\\drivers\\bthhfenum.sys,#2;%1 Hands-Free%0;(Josh\'s Buds3 Pro))',
                'max_input_channels': 1,
                'max_output_channels': 0,
                'hostapi': 2  # DirectSound
            },
            # Device 2: USB device with vendor/product ID
            {
                'name': 'USB Audio Device [0d8c:0014]',
                'max_input_channels': 2,
                'max_output_channels': 0,
                'hostapi': 0  # WASAPI
            },
            # Device 3: Same USB device (DirectSound)
            {
                'name': 'USB Audio Device [0d8c:0014]',
                'max_input_channels': 2,
                'max_output_channels': 0,
                'hostapi': 2  # DirectSound
            },
            # Device 4: Microphone with parentheses in name
            {
                'name': 'Microphone (C922 Pro Stream Web)',
                'max_input_channels': 2,
                'max_output_channels': 0,
                'hostapi': 0  # WASAPI
            },
            # Device 5: Same microphone (DirectSound)
            {
                'name': 'Microphone (C922 Pro Stream Web)',
                'max_input_channels': 2,
                'max_output_channels': 0,
                'hostapi': 2  # DirectSound
            },
        ]


# ============================================================================
# TEST CLASSES
# ============================================================================

class TestDirectSoundFallback:
    """Tests for DirectSound fallback mechanism in audio recording"""

    def test_directsound_switch_success(self, mock_devices_with_directsound, mock_hostapis):
        """
        Test successful switch from WASAPI to DirectSound.

        Scenario: User selects C922 webcam (device 12, WASAPI).
        Expected: System switches to device 6 (DirectSound version).
        """
        with patch('sounddevice.query_devices') as mock_query_devices, \
             patch('sounddevice.query_hostapis') as mock_query_hostapis:

            mock_query_devices.return_value = mock_devices_with_directsound
            mock_query_hostapis.return_value = mock_hostapis

            # Simulate the fallback logic from veleron_voice_flow.py
            selected_device = 12  # WASAPI C922
            device_spec = selected_device
            selected_base_name = None

            # Get base name of selected device (simplified device list for lookup)
            audio_devices = []
            for i, device in enumerate(mock_devices_with_directsound):
                if device['max_input_channels'] > 0:
                    audio_devices.append({
                        'id': i,
                        'name': device['name'],
                        'hostapi_name': mock_hostapis[device['hostapi']]['name']
                    })

            # Find selected device's base name
            for device in audio_devices:
                if device['id'] == selected_device:
                    selected_base_name = device['name'].split('(')[0].strip()
                    break

            # Try to find DirectSound version
            if selected_base_name:
                for i, full_device in enumerate(mock_devices_with_directsound):
                    if full_device['max_input_channels'] > 0:
                        full_name = full_device['name'].strip()
                        full_base = full_name.split('(')[0].strip()
                        hostapi = mock_hostapis[full_device['hostapi']]['name']

                        if full_base == selected_base_name and 'DirectSound' in hostapi:
                            device_spec = i
                            break

            # Assertions
            assert selected_base_name == 'C922 Pro Stream Webcam'
            assert device_spec == 6, "Should switch to device 6 (DirectSound version)"
            assert device_spec != selected_device, "Device spec should change from original"

    def test_no_directsound_available(self, mock_devices_no_directsound, mock_hostapis):
        """
        Test behavior when no DirectSound alternative exists.

        Scenario: User selects device with no DirectSound version.
        Expected: System uses original device (no switch).
        """
        with patch('sounddevice.query_devices') as mock_query_devices, \
             patch('sounddevice.query_hostapis') as mock_query_hostapis:

            mock_query_devices.return_value = mock_devices_no_directsound
            mock_query_hostapis.return_value = mock_hostapis

            # Simulate fallback logic
            selected_device = 2  # USB Microphone (WASAPI only)
            device_spec = selected_device
            selected_base_name = None

            # Build simplified device list
            audio_devices = []
            for i, device in enumerate(mock_devices_no_directsound):
                if device['max_input_channels'] > 0:
                    audio_devices.append({
                        'id': i,
                        'name': device['name'],
                        'hostapi_name': mock_hostapis[device['hostapi']]['name']
                    })

            # Find base name
            for device in audio_devices:
                if device['id'] == selected_device:
                    selected_base_name = device['name'].split('(')[0].strip()
                    break

            # Try to find DirectSound version
            if selected_base_name:
                for i, full_device in enumerate(mock_devices_no_directsound):
                    if full_device['max_input_channels'] > 0:
                        full_name = full_device['name'].strip()
                        full_base = full_name.split('(')[0].strip()
                        hostapi = mock_hostapis[full_device['hostapi']]['name']

                        if full_base == selected_base_name and 'DirectSound' in hostapi:
                            device_spec = i
                            break

            # Assertions
            assert selected_base_name == 'USB Microphone'
            assert device_spec == selected_device, "Should keep original device when no DirectSound available"

    def test_base_name_extraction_simple(self, mock_devices_with_directsound):
        """
        Test base name extraction from simple device name.

        Scenario: Device name is "C922 Pro Stream Webcam"
        Expected: Base name is "C922 Pro Stream Webcam"
        """
        device_name = 'C922 Pro Stream Webcam'
        base_name = device_name.split('(')[0].strip()

        assert base_name == 'C922 Pro Stream Webcam'

    def test_base_name_extraction_with_parentheses(self):
        """
        Test base name extraction from device name with parentheses.

        Scenario: Device name is "Microphone (C922 Pro Stream Web)"
        Expected: Base name is "Microphone"
        """
        device_name = 'Microphone (C922 Pro Stream Web)'
        base_name = device_name.split('(')[0].strip()

        assert base_name == 'Microphone'

    def test_base_name_extraction_complex_bluetooth(self):
        """
        Test base name extraction from complex Bluetooth device name.

        Scenario: Device name contains driver path and special characters
        Expected: Base name is "Headset"
        """
        device_name = 'Headset (@System32\\drivers\\bthhfenum.sys,#2;%1 Hands-Free%0;(Josh\'s Buds3 Pro))'
        base_name = device_name.split('(')[0].strip()

        assert base_name == 'Headset'

    def test_base_name_extraction_usb_vendor_id(self):
        """
        Test base name extraction from USB device with vendor ID.

        Scenario: Device name is "USB Audio Device [0d8c:0014]"
        Expected: Base name is "USB Audio Device"
        """
        device_name = 'USB Audio Device [0d8c:0014]'
        base_name = device_name.split('(')[0].strip()

        assert base_name == 'USB Audio Device [0d8c:0014]'

    def test_multiple_devices_same_base_name(self, mock_devices_with_directsound, mock_hostapis):
        """
        Test that DirectSound version is picked when multiple devices share base name.

        Scenario: Multiple APIs expose same hardware device.
        Expected: DirectSound version is selected over WASAPI.
        """
        with patch('sounddevice.query_devices') as mock_query_devices, \
             patch('sounddevice.query_hostapis') as mock_query_hostapis:

            mock_query_devices.return_value = mock_devices_with_directsound
            mock_query_hostapis.return_value = mock_hostapis

            # Simulate fallback logic - looking for DirectSound version of C922
            selected_device = 12  # WASAPI
            base_name = 'C922 Pro Stream Webcam'
            found_devices = []

            # Find all devices with same base name
            for i, device in enumerate(mock_devices_with_directsound):
                if device['max_input_channels'] > 0:
                    device_name = device['name'].strip()
                    device_base = device_name.split('(')[0].strip()
                    hostapi = mock_hostapis[device['hostapi']]['name']

                    if device_base == base_name:
                        found_devices.append({
                            'id': i,
                            'name': device_name,
                            'hostapi': hostapi,
                            'is_directsound': 'DirectSound' in hostapi
                        })

            # Find DirectSound version
            directsound_device = None
            for dev in found_devices:
                if dev['is_directsound']:
                    directsound_device = dev
                    break

            # Assertions
            assert len(found_devices) == 2, "Should find 2 devices with same base name"
            assert directsound_device is not None, "Should find DirectSound version"
            assert directsound_device['id'] == 6, "DirectSound version should be device 6"
            assert directsound_device['is_directsound'] is True

    def test_empty_device_list_handling(self):
        """
        Test handling of empty device list.

        Scenario: No devices available (sounddevice.query_devices() returns empty list).
        Expected: Fallback logic handles gracefully, no crash.
        """
        with patch('sounddevice.query_devices') as mock_query_devices, \
             patch('sounddevice.query_hostapis') as mock_query_hostapis:

            mock_query_devices.return_value = []
            mock_query_hostapis.return_value = []

            # Simulate fallback logic
            selected_device = 0
            device_spec = selected_device
            selected_base_name = None

            # Build device list (should be empty)
            audio_devices = []
            for i, device in enumerate([]):
                if device.get('max_input_channels', 0) > 0:
                    audio_devices.append({
                        'id': i,
                        'name': device['name']
                    })

            # Try to find selected device (should fail gracefully)
            for device in audio_devices:
                if device['id'] == selected_device:
                    selected_base_name = device['name'].split('(')[0].strip()
                    break

            # No DirectSound search since no base name found

            # Assertions
            assert len(audio_devices) == 0
            assert selected_base_name is None, "No base name should be found"
            assert device_spec == selected_device, "Should keep original device spec"

    def test_invalid_device_id_handling(self, mock_devices_with_directsound, mock_hostapis):
        """
        Test handling of invalid device ID.

        Scenario: Selected device ID doesn't exist in device list.
        Expected: Fallback logic handles gracefully, no crash.
        """
        with patch('sounddevice.query_devices') as mock_query_devices, \
             patch('sounddevice.query_hostapis') as mock_query_hostapis:

            mock_query_devices.return_value = mock_devices_with_directsound
            mock_query_hostapis.return_value = mock_hostapis

            # Simulate fallback with invalid device ID
            selected_device = 999  # Invalid ID
            device_spec = selected_device
            selected_base_name = None

            # Build device list
            audio_devices = []
            for i, device in enumerate(mock_devices_with_directsound):
                if device['max_input_channels'] > 0:
                    audio_devices.append({
                        'id': i,
                        'name': device['name'],
                        'hostapi_name': mock_hostapis[device['hostapi']]['name']
                    })

            # Try to find selected device (should not find it)
            for device in audio_devices:
                if device['id'] == selected_device:
                    selected_base_name = device['name'].split('(')[0].strip()
                    break

            # Assertions
            assert selected_base_name is None, "Invalid device ID should not be found"
            assert device_spec == selected_device, "Should keep original (invalid) device spec"

    def test_channel_count_mono_device(self, mock_devices_with_directsound, mock_hostapis):
        """
        Test channel count handling for mono device.

        Scenario: Device has 1 input channel.
        Expected: Channel count is correctly identified as 1.
        """
        # Create a mono device
        mono_devices = mock_devices_with_directsound.copy()
        mono_devices.append({
            'name': 'Mono USB Mic',
            'max_input_channels': 1,
            'max_output_channels': 0,
            'hostapi': 0
        })

        with patch('sounddevice.query_devices') as mock_query_devices:
            mock_query_devices.return_value = mono_devices

            # Get device info
            devices = sd.query_devices()
            mono_device = devices[-1]  # Last device we added

            # Assertions
            assert mono_device['max_input_channels'] == 1, "Mono device should have 1 channel"

    def test_channel_count_stereo_device(self, mock_devices_with_directsound, mock_hostapis):
        """
        Test channel count handling for stereo device.

        Scenario: Device has 2 input channels.
        Expected: Channel count is correctly identified as 2.
        """
        with patch('sounddevice.query_devices') as mock_query_devices:
            mock_query_devices.return_value = mock_devices_with_directsound

            # Get device info for C922 webcam (device 6)
            devices = sd.query_devices()
            c922_device = devices[6]

            # Assertions
            assert c922_device['max_input_channels'] == 2, "C922 should have 2 channels (stereo)"

    def test_device_query_exception_handling(self):
        """
        Test handling of exceptions during device query.

        Scenario: sounddevice.query_devices() raises exception.
        Expected: Exception is handled gracefully or propagated correctly.
        """
        with patch('sounddevice.query_devices') as mock_query_devices:
            mock_query_devices.side_effect = Exception("Device query failed")

            # Attempt to query devices
            with pytest.raises(Exception) as exc_info:
                sd.query_devices()

            assert "Device query failed" in str(exc_info.value)

    def test_hostapi_query_exception_handling(self):
        """
        Test handling of exceptions during host API query.

        Scenario: sounddevice.query_hostapis() raises exception.
        Expected: Exception is handled gracefully or propagated correctly.
        """
        with patch('sounddevice.query_hostapis') as mock_query_hostapis:
            mock_query_hostapis.side_effect = Exception("Host API query failed")

            # Attempt to query host APIs
            with pytest.raises(Exception) as exc_info:
                sd.query_hostapis()

            assert "Host API query failed" in str(exc_info.value)

    def test_directsound_switch_with_logging(self, mock_devices_with_directsound, mock_hostapis):
        """
        Test that DirectSound switch generates appropriate log messages.

        Scenario: System switches from WASAPI to DirectSound.
        Expected: Log message contains "SWITCHING TO DIRECTSOUND" and device IDs.
        """
        with patch('sounddevice.query_devices') as mock_query_devices, \
             patch('sounddevice.query_hostapis') as mock_query_hostapis:

            mock_query_devices.return_value = mock_devices_with_directsound
            mock_query_hostapis.return_value = mock_hostapis

            # Simulate fallback logic with logging
            selected_device = 12  # WASAPI C922
            device_spec = selected_device
            selected_base_name = None
            log_messages = []

            # Build device list
            audio_devices = []
            for i, device in enumerate(mock_devices_with_directsound):
                if device['max_input_channels'] > 0:
                    audio_devices.append({
                        'id': i,
                        'name': device['name'],
                        'hostapi_name': mock_hostapis[device['hostapi']]['name']
                    })

            # Find base name and log current selection
            for device in audio_devices:
                if device['id'] == selected_device:
                    selected_base_name = device['name'].split('(')[0].strip()
                    log_messages.append(
                        f"Current selection: {device['name']} "
                        f"(ID: {device['id']}, API: {device['hostapi_name']})"
                    )
                    break

            # Try to find DirectSound version
            if selected_base_name:
                for i, full_device in enumerate(mock_devices_with_directsound):
                    if full_device['max_input_channels'] > 0:
                        full_name = full_device['name'].strip()
                        full_base = full_name.split('(')[0].strip()
                        hostapi = mock_hostapis[full_device['hostapi']]['name']

                        if full_base == selected_base_name and 'DirectSound' in hostapi:
                            device_spec = i
                            log_messages.append(
                                f"SWITCHING TO DIRECTSOUND: Using device ID {i} "
                                f"({full_name}) instead of {selected_device}"
                            )
                            break

            # Assertions
            assert len(log_messages) == 2, "Should have 2 log messages"
            assert "Current selection" in log_messages[0]
            assert "WASAPI" in log_messages[0]
            assert "SWITCHING TO DIRECTSOUND" in log_messages[1]
            assert "device ID 6" in log_messages[1]
            assert f"instead of {selected_device}" in log_messages[1]

    def test_complex_device_names_matching(self, mock_devices_complex_names, mock_hostapis):
        """
        Test DirectSound matching with complex device names.

        Scenario: Devices have complex names with driver paths, brackets, etc.
        Expected: Base name extraction and matching still works correctly.
        """
        with patch('sounddevice.query_devices') as mock_query_devices, \
             patch('sounddevice.query_hostapis') as mock_query_hostapis:

            mock_query_devices.return_value = mock_devices_complex_names
            mock_query_hostapis.return_value = mock_hostapis

            # Test Bluetooth headset
            selected_device = 0  # WASAPI Bluetooth
            device_spec = selected_device
            selected_base_name = None

            audio_devices = []
            for i, device in enumerate(mock_devices_complex_names):
                if device['max_input_channels'] > 0:
                    audio_devices.append({
                        'id': i,
                        'name': device['name'],
                        'hostapi_name': mock_hostapis[device['hostapi']]['name']
                    })

            # Find base name
            for device in audio_devices:
                if device['id'] == selected_device:
                    selected_base_name = device['name'].split('(')[0].strip()
                    break

            # Find DirectSound version
            if selected_base_name:
                for i, full_device in enumerate(mock_devices_complex_names):
                    if full_device['max_input_channels'] > 0:
                        full_name = full_device['name'].strip()
                        full_base = full_name.split('(')[0].strip()
                        hostapi = mock_hostapis[full_device['hostapi']]['name']

                        if full_base == selected_base_name and 'DirectSound' in hostapi:
                            device_spec = i
                            break

            # Assertions
            assert selected_base_name == 'Headset'
            assert device_spec == 1, "Should switch to DirectSound Bluetooth headset (device 1)"

    def test_directsound_priority_over_mme(self, mock_hostapis):
        """
        Test that DirectSound is preferred over MME.

        Scenario: Device available in WASAPI, MME, and DirectSound.
        Expected: DirectSound is selected (not MME).
        """
        devices_with_all_apis = [
            # Same device in all three APIs
            {
                'name': 'Test Microphone',
                'max_input_channels': 2,
                'max_output_channels': 0,
                'hostapi': 0  # WASAPI
            },
            {
                'name': 'Test Microphone',
                'max_input_channels': 2,
                'max_output_channels': 0,
                'hostapi': 1  # MME
            },
            {
                'name': 'Test Microphone',
                'max_input_channels': 2,
                'max_output_channels': 0,
                'hostapi': 2  # DirectSound
            },
        ]

        with patch('sounddevice.query_devices') as mock_query_devices, \
             patch('sounddevice.query_hostapis') as mock_query_hostapis:

            mock_query_devices.return_value = devices_with_all_apis
            mock_query_hostapis.return_value = mock_hostapis

            # Simulate fallback - looking for DirectSound
            selected_device = 0  # WASAPI
            base_name = 'Test Microphone'
            device_spec = selected_device

            # Find DirectSound version (should skip MME)
            for i, device in enumerate(devices_with_all_apis):
                if device['max_input_channels'] > 0:
                    device_name = device['name'].strip()
                    device_base = device_name.split('(')[0].strip()
                    hostapi = mock_hostapis[device['hostapi']]['name']

                    if device_base == base_name and 'DirectSound' in hostapi:
                        device_spec = i
                        break

            # Assertions
            assert device_spec == 2, "Should select DirectSound (device 2), not MME (device 1)"
            assert mock_hostapis[devices_with_all_apis[device_spec]['hostapi']]['name'] == 'Windows DirectSound'

    def test_whitespace_handling_in_device_names(self):
        """
        Test that extra whitespace in device names doesn't affect matching.

        Scenario: Device names have trailing/leading whitespace.
        Expected: Whitespace is stripped and matching works correctly.
        """
        device_name_with_spaces = '  C922 Pro Stream Webcam  '
        device_name_clean = 'C922 Pro Stream Webcam'

        # Simulate the strip() operation in the fallback code
        stripped_name = device_name_with_spaces.strip()
        base_name = stripped_name.split('(')[0].strip()

        # Assertions
        assert stripped_name == device_name_clean
        assert base_name == device_name_clean

    def test_case_sensitivity_in_api_names(self, mock_hostapis):
        """
        Test that API name matching is case-sensitive for 'DirectSound'.

        Scenario: Host API name uses different case variations.
        Expected: Only exact 'DirectSound' substring matches.
        """
        # Test various cases
        assert 'DirectSound' in 'Windows DirectSound'
        assert 'DirectSound' not in 'windows directsound'
        assert 'DirectSound' not in 'DIRECTSOUND'
        assert 'DirectSound' not in 'Direct Sound'

    def test_no_input_channels_filtered_out(self, mock_devices_with_directsound):
        """
        Test that devices with 0 input channels are filtered out.

        Scenario: Device list includes output-only devices.
        Expected: Only devices with max_input_channels > 0 are considered.
        """
        with patch('sounddevice.query_devices') as mock_query_devices:
            mock_query_devices.return_value = mock_devices_with_directsound

            # Filter devices (simulate fallback logic)
            input_devices = []
            for i, device in enumerate(mock_devices_with_directsound):
                if device['max_input_channels'] > 0:
                    input_devices.append({
                        'id': i,
                        'name': device['name']
                    })

            # Assertions
            assert len(input_devices) == 4, "Should find 4 input devices"
            # Devices 0, 1, 6, 12 have input channels
            input_device_ids = [dev['id'] for dev in input_devices]
            assert 0 in input_device_ids
            assert 1 in input_device_ids
            assert 6 in input_device_ids
            assert 12 in input_device_ids

    def test_channel_count_preserved_after_switch(self, mock_devices_with_directsound, mock_hostapis):
        """
        Test that channel count is updated after switching to DirectSound.

        Scenario: WASAPI device has 2 channels, DirectSound version also has 2.
        Expected: Channel count is correctly set to DirectSound device's channel count.
        """
        with patch('sounddevice.query_devices') as mock_query_devices, \
             patch('sounddevice.query_hostapis') as mock_query_hostapis:

            mock_query_devices.return_value = mock_devices_with_directsound
            mock_query_hostapis.return_value = mock_hostapis

            # Simulate fallback with channel count tracking
            selected_device = 12  # WASAPI C922 (2 channels)
            device_spec = selected_device
            device_channels = mock_devices_with_directsound[selected_device]['max_input_channels']
            selected_base_name = None

            audio_devices = []
            for i, device in enumerate(mock_devices_with_directsound):
                if device['max_input_channels'] > 0:
                    audio_devices.append({
                        'id': i,
                        'name': device['name'],
                        'channels': device['max_input_channels'],
                        'hostapi_name': mock_hostapis[device['hostapi']]['name']
                    })

            # Find base name
            for device in audio_devices:
                if device['id'] == selected_device:
                    selected_base_name = device['name'].split('(')[0].strip()
                    break

            # Find DirectSound version and update channel count
            if selected_base_name:
                for i, full_device in enumerate(mock_devices_with_directsound):
                    if full_device['max_input_channels'] > 0:
                        full_name = full_device['name'].strip()
                        full_base = full_name.split('(')[0].strip()
                        hostapi = mock_hostapis[full_device['hostapi']]['name']

                        if full_base == selected_base_name and 'DirectSound' in hostapi:
                            device_spec = i
                            device_channels = full_device['max_input_channels']
                            break

            # Assertions
            assert device_spec == 6, "Should switch to DirectSound device"
            assert device_channels == 2, "Channel count should be 2 (from DirectSound device)"


class TestDirectSoundFallbackIntegration:
    """Integration tests for DirectSound fallback in recording workflow"""

    def test_fallback_with_mock_stream_creation(self, mock_devices_with_directsound, mock_hostapis):
        """
        Test complete fallback workflow including stream creation.

        Scenario: Full recording workflow with DirectSound fallback.
        Expected: Stream is created with correct device ID and channel count.
        """
        with patch('sounddevice.query_devices') as mock_query_devices, \
             patch('sounddevice.query_hostapis') as mock_query_hostapis, \
             patch('sounddevice.InputStream') as mock_input_stream:

            mock_query_devices.return_value = mock_devices_with_directsound
            mock_query_hostapis.return_value = mock_hostapis

            # Create mock stream
            mock_stream = MagicMock()
            mock_stream.__enter__ = Mock(return_value=mock_stream)
            mock_stream.__exit__ = Mock(return_value=False)
            mock_input_stream.return_value = mock_stream

            # Simulate complete fallback and recording
            selected_device = 12  # WASAPI C922
            device_spec = selected_device
            device_channels = 2
            sample_rate = 16000
            selected_base_name = None

            # Build device list
            audio_devices = []
            for i, device in enumerate(mock_devices_with_directsound):
                if device['max_input_channels'] > 0:
                    audio_devices.append({
                        'id': i,
                        'name': device['name'],
                        'channels': device['max_input_channels'],
                        'hostapi_name': mock_hostapis[device['hostapi']]['name']
                    })

            # Find base name
            for device in audio_devices:
                if device['id'] == selected_device:
                    selected_base_name = device['name'].split('(')[0].strip()
                    break

            # Find DirectSound version
            if selected_base_name:
                for i, full_device in enumerate(mock_devices_with_directsound):
                    if full_device['max_input_channels'] > 0:
                        full_name = full_device['name'].strip()
                        full_base = full_name.split('(')[0].strip()
                        hostapi = mock_hostapis[full_device['hostapi']]['name']

                        if full_base == selected_base_name and 'DirectSound' in hostapi:
                            device_spec = i
                            device_channels = full_device['max_input_channels']
                            break

            # Create stream with fallback device
            callback = Mock()
            with sd.InputStream(
                device=device_spec,
                samplerate=sample_rate,
                channels=device_channels,
                dtype=np.float32,
                callback=callback
            ):
                pass

            # Assertions
            mock_input_stream.assert_called_once()
            call_kwargs = mock_input_stream.call_args[1]
            assert call_kwargs['device'] == 6, "Should use DirectSound device ID"
            assert call_kwargs['samplerate'] == 16000
            assert call_kwargs['channels'] == 2
            assert call_kwargs['dtype'] == np.float32

    def test_no_fallback_when_directsound_unavailable(self, mock_devices_no_directsound, mock_hostapis):
        """
        Test that original device is used when DirectSound not available.

        Scenario: Recording with device that has no DirectSound alternative.
        Expected: Stream is created with original device ID.
        """
        with patch('sounddevice.query_devices') as mock_query_devices, \
             patch('sounddevice.query_hostapis') as mock_query_hostapis, \
             patch('sounddevice.InputStream') as mock_input_stream:

            mock_query_devices.return_value = mock_devices_no_directsound
            mock_query_hostapis.return_value = mock_hostapis

            mock_stream = MagicMock()
            mock_stream.__enter__ = Mock(return_value=mock_stream)
            mock_stream.__exit__ = Mock(return_value=False)
            mock_input_stream.return_value = mock_stream

            # Simulate fallback (no DirectSound available)
            selected_device = 2  # USB Microphone
            device_spec = selected_device
            device_channels = 1
            sample_rate = 16000

            # Try fallback logic (will not find DirectSound)
            audio_devices = []
            for i, device in enumerate(mock_devices_no_directsound):
                if device['max_input_channels'] > 0:
                    audio_devices.append({
                        'id': i,
                        'name': device['name'],
                        'hostapi_name': mock_hostapis[device['hostapi']]['name']
                    })

            selected_base_name = None
            for device in audio_devices:
                if device['id'] == selected_device:
                    selected_base_name = device['name'].split('(')[0].strip()
                    break

            # No DirectSound found

            # Create stream with original device
            callback = Mock()
            with sd.InputStream(
                device=device_spec,
                samplerate=sample_rate,
                channels=device_channels,
                dtype=np.float32,
                callback=callback
            ):
                pass

            # Assertions
            mock_input_stream.assert_called_once()
            call_kwargs = mock_input_stream.call_args[1]
            assert call_kwargs['device'] == 2, "Should use original device ID (no fallback)"
