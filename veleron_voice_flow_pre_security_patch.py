"""
Veleron Voice Flow - Custom WhisperFlow-equivalent Application (FIXED)
Real-time voice-to-text transcription powered by OpenAI Whisper

Features:
- Real-time audio recording
- Automatic transcription using Whisper
- Clean, user-friendly GUI
- Export to multiple formats (TXT, DOCX, JSON)
- Hotkey support for quick recording
- Multi-language support
- Automatic punctuation and formatting

FIXES:
- Added ffmpeg PATH detection and configuration
- Enhanced error handling with detailed logging
- Fixed temporary file handling
- Added console logging for debugging

Author: Veleron Dev Studios
License: Internal Use Only
"""

import whisper
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import queue
import sounddevice as sd
import numpy as np
import wave
import tempfile
import os
import sys
from datetime import datetime
import json
from pathlib import Path


class VeleronVoiceFlow:
    """Main application class for Veleron Voice Flow"""

    def __init__(self, root):
        self.root = root
        self.root.title("Veleron Voice Flow - AI Voice Transcription")
        self.root.geometry("900x700")

        # Application state
        self.is_recording = False
        self.audio_data = []
        self.sample_rate = 16000  # Whisper uses 16kHz
        self.model = None
        self.model_name = "base"
        self.current_language = "auto"
        self.transcription_queue = queue.Queue()
        self.selected_device = None  # Will be set to default or user selection
        self.audio_devices = []  # List of available input devices

        # Setup logging
        self.setup_logging()

        # Check and configure ffmpeg
        self.check_ffmpeg()

        # Get available audio devices
        self.get_audio_devices()

        # Setup UI
        self.setup_ui()

        # Load model in background
        self.status_var.set("Loading Whisper model...")
        threading.Thread(target=self.load_model, daemon=True).start()

    def setup_logging(self):
        """Setup console logging for debugging"""
        self.log_messages = []

    def log(self, message, level="INFO"):
        """Log a message to console and internal buffer"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        self.log_messages.append(log_entry)

        # Keep only last 100 messages
        if len(self.log_messages) > 100:
            self.log_messages.pop(0)

    def get_audio_devices(self):
        """Get list of available audio input devices (deduplicated)"""
        try:
            self.log("Scanning for audio input devices...")
            devices = sd.query_devices()
            hostapi_info = sd.query_hostapis()

            # Filter for input devices only and deduplicate
            self.audio_devices = []
            seen_devices = {}  # Track unique device names

            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    device_name = device['name'].strip()
                    hostapi_name = hostapi_info[device['hostapi']]['name']

                    # Normalize device name - remove driver paths and normalize
                    # e.g., "Headset (@System32\drivers\...)" -> "Headset"
                    base_name = device_name.split('(')[0].strip()
                    if not base_name:  # If name was just parentheses
                        base_name = device_name

                    # Further clean - some devices have extra info
                    # Keep the essential part before first special character
                    for sep in ['@', '{', '[']:
                        if sep in base_name:
                            base_name = base_name.split(sep)[0].strip()

                    # Deduplicate: prefer WASAPI, then DirectSound, then MME, then others
                    if base_name in seen_devices:
                        # Check if current API is preferred over existing
                        existing_api = seen_devices[base_name]['hostapi_name']
                        priority_current = self._get_api_priority(hostapi_name)
                        priority_existing = self._get_api_priority(existing_api)

                        if priority_current > priority_existing:
                            # Replace with higher priority device
                            seen_devices[base_name] = {
                                'id': i,
                                'name': device_name,
                                'channels': device['max_input_channels'],
                                'hostapi': device['hostapi'],
                                'hostapi_name': hostapi_name
                            }
                            self.log(f"Replaced device '{base_name}' with {hostapi_name} version (ID: {i})")
                    else:
                        # First time seeing this device
                        seen_devices[base_name] = {
                            'id': i,
                            'name': device_name,
                            'channels': device['max_input_channels'],
                            'hostapi': device['hostapi'],
                            'hostapi_name': hostapi_name
                        }
                        self.log(f"Found input device {i}: {device_name} ({hostapi_name}, {device['max_input_channels']} channels)")

            # Convert to list (sorted by device ID)
            self.audio_devices = sorted(seen_devices.values(), key=lambda x: x['id'])

            # Set default device
            try:
                default_device = sd.query_devices(kind='input')
                default_name = default_device['name'].strip()

                # Find the deduplicated device that matches
                self.selected_device = None
                for device in self.audio_devices:
                    if device['name'] == default_name or default_name in device['name']:
                        self.selected_device = device['id']
                        break

                if self.selected_device is None and self.audio_devices:
                    self.selected_device = self.audio_devices[0]['id']

                self.log(f"Default input device: {default_name} (ID: {self.selected_device})")
            except Exception as e:
                self.log(f"Could not get default device: {str(e)}", "WARNING")
                if self.audio_devices:
                    self.selected_device = self.audio_devices[0]['id']

            self.log(f"Found {len(self.audio_devices)} unique input devices (after deduplication)")

        except Exception as e:
            self.log(f"Error scanning audio devices: {str(e)}", "ERROR")
            self.audio_devices = []

    def _get_api_priority(self, api_name):
        """Return priority for audio API (higher is better)"""
        api_name_lower = api_name.lower()
        if 'wasapi' in api_name_lower:
            return 100  # Highest priority - modern Windows API, most reliable
        elif 'directsound' in api_name_lower or 'windows directsound' in api_name_lower:
            return 80  # Good compatibility
        elif 'mme' in api_name_lower or 'windows mme' in api_name_lower:
            return 60  # Basic Windows API, very compatible
        elif 'wdm' in api_name_lower or 'ks' in api_name_lower:
            return 10  # Lowest - often causes issues, requires special drivers
        else:
            return 0

    def check_ffmpeg(self):
        """Check if ffmpeg is available and add to PATH if needed"""
        self.log("Checking ffmpeg availability...")

        # Common ffmpeg locations on Windows
        possible_paths = [
            r"C:\Program Files\ffmpeg\bin",
            r"C:\Program Files (x86)\ffmpeg\bin",
            r"C:\ffmpeg\bin",
            os.path.expanduser(r"~\ffmpeg\bin"),
        ]

        # Check if ffmpeg is already in PATH
        import shutil
        ffmpeg_path = shutil.which("ffmpeg")

        if ffmpeg_path:
            self.log(f"ffmpeg found at: {ffmpeg_path}")
            return True

        self.log("ffmpeg not in PATH, searching common locations...")

        # Try to find and add ffmpeg to PATH for this session
        for path in possible_paths:
            if os.path.exists(path):
                ffmpeg_exe = os.path.join(path, "ffmpeg.exe")
                if os.path.exists(ffmpeg_exe):
                    self.log(f"Found ffmpeg at: {path}")
                    # Add to PATH for current process
                    os.environ["PATH"] = path + os.pathsep + os.environ.get("PATH", "")
                    self.log(f"Added {path} to PATH for this session")
                    return True

        # ffmpeg not found
        self.log("WARNING: ffmpeg not found. Audio file transcription may fail.", "WARNING")
        self.log("Please install ffmpeg or restart the application after PATH update.", "WARNING")
        return False

    def setup_ui(self):
        """Create the user interface"""

        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # ===== TITLE =====
        title_label = ttk.Label(
            main_frame,
            text="Veleron Voice Flow",
            font=("Arial", 20, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 10))

        # ===== CONTROL PANEL =====
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        control_frame.columnconfigure(4, weight=1)

        # Recording controls
        self.record_button = ttk.Button(
            control_frame,
            text="🎤 Start Recording",
            command=self.toggle_recording,
            width=20
        )
        self.record_button.grid(row=0, column=0, padx=5)

        self.transcribe_file_button = ttk.Button(
            control_frame,
            text="📁 Transcribe File",
            command=self.transcribe_file,
            width=20
        )
        self.transcribe_file_button.grid(row=0, column=1, padx=5)

        # Model selection
        ttk.Label(control_frame, text="Model:").grid(row=0, column=2, padx=(20, 5))
        self.model_var = tk.StringVar(value="base")
        model_combo = ttk.Combobox(
            control_frame,
            textvariable=self.model_var,
            values=["tiny", "base", "small", "medium", "large", "turbo"],
            state="readonly",
            width=10
        )
        model_combo.grid(row=0, column=3, padx=5)
        model_combo.bind("<<ComboboxSelected>>", self.change_model)

        # Language selection
        ttk.Label(control_frame, text="Language:").grid(row=1, column=0, padx=5, pady=(10, 0), sticky=tk.W)
        self.language_var = tk.StringVar(value="auto")
        language_combo = ttk.Combobox(
            control_frame,
            textvariable=self.language_var,
            values=["auto", "en", "es", "fr", "de", "it", "pt", "nl", "ja", "ko", "zh"],
            state="readonly",
            width=10
        )
        language_combo.grid(row=1, column=1, padx=5, pady=(10, 0), sticky=tk.W)

        # Microphone selection
        ttk.Label(control_frame, text="Microphone:").grid(row=1, column=2, padx=(20, 5), pady=(10, 0), sticky=tk.W)
        self.mic_var = tk.StringVar()

        self.mic_combo = ttk.Combobox(
            control_frame,
            textvariable=self.mic_var,
            state="readonly",
            width=35
        )
        self.mic_combo.grid(row=1, column=3, padx=5, pady=(10, 0), sticky=tk.W)
        self.mic_combo.bind("<<ComboboxSelected>>", self.change_microphone)

        # Refresh devices button
        self.refresh_button = ttk.Button(
            control_frame,
            text="🔄 Refresh",
            command=self.refresh_devices,
            width=10
        )
        self.refresh_button.grid(row=1, column=4, padx=5, pady=(10, 0))

        # Populate microphone dropdown
        self.update_microphone_list()

        # ===== TRANSCRIPTION AREA =====
        transcription_frame = ttk.LabelFrame(main_frame, text="Transcription", padding="10")
        transcription_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        transcription_frame.columnconfigure(0, weight=1)
        transcription_frame.rowconfigure(0, weight=1)

        self.transcription_text = scrolledtext.ScrolledText(
            transcription_frame,
            wrap=tk.WORD,
            font=("Arial", 11),
            height=20
        )
        self.transcription_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # ===== ACTION BUTTONS =====
        action_frame = ttk.Frame(main_frame)
        action_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(
            action_frame,
            text="Clear",
            command=self.clear_transcription
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            action_frame,
            text="Copy to Clipboard",
            command=self.copy_to_clipboard
        ).grid(row=0, column=1, padx=5)

        ttk.Button(
            action_frame,
            text="Export as TXT",
            command=lambda: self.export_transcription("txt")
        ).grid(row=0, column=2, padx=5)

        ttk.Button(
            action_frame,
            text="Export as JSON",
            command=lambda: self.export_transcription("json")
        ).grid(row=0, column=3, padx=5)

        ttk.Button(
            action_frame,
            text="View Logs",
            command=self.show_logs
        ).grid(row=0, column=4, padx=5)

        # ===== STATUS BAR =====
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(0, weight=1)

        self.status_var = tk.StringVar(value="Initializing...")
        status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_label.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Progress bar
        self.progress = ttk.Progressbar(
            status_frame,
            mode='indeterminate',
            length=200
        )
        self.progress.grid(row=0, column=1, padx=(10, 0))

    def show_logs(self):
        """Show application logs in a new window"""
        log_window = tk.Toplevel(self.root)
        log_window.title("Application Logs")
        log_window.geometry("800x600")

        log_text = scrolledtext.ScrolledText(
            log_window,
            wrap=tk.WORD,
            font=("Consolas", 9)
        )
        log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for log_msg in self.log_messages:
            log_text.insert(tk.END, log_msg + "\n")

        log_text.see(tk.END)

        # Add refresh button
        def refresh_logs():
            log_text.delete(1.0, tk.END)
            for log_msg in self.log_messages:
                log_text.insert(tk.END, log_msg + "\n")
            log_text.see(tk.END)

        ttk.Button(
            log_window,
            text="Refresh",
            command=refresh_logs
        ).pack(pady=5)

    def load_model(self):
        """Load the Whisper model"""
        try:
            self.log(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
            self.log(f"Model {self.model_name} loaded successfully")
            self.status_var.set(f"Ready - Model: {self.model_name}")
        except Exception as e:
            error_msg = f"Error loading model: {str(e)}"
            self.log(error_msg, "ERROR")
            self.status_var.set(error_msg)
            messagebox.showerror("Model Error", f"Failed to load model: {str(e)}")

    def change_model(self, event=None):
        """Change the Whisper model"""
        new_model = self.model_var.get()
        if new_model != self.model_name:
            self.model_name = new_model
            self.log(f"Changing model to: {new_model}")
            self.status_var.set(f"Loading {new_model} model...")
            self.model = None
            threading.Thread(target=self.load_model, daemon=True).start()

    def update_microphone_list(self):
        """Update the microphone dropdown with current devices"""
        # Build microphone list with names and API info
        mic_options = []
        for device in self.audio_devices:
            # Format: "Device Name (API)"
            api_short = device.get('hostapi_name', 'Unknown')
            # Shorten API name
            if 'WASAPI' in api_short:
                api_short = 'WASAPI'
            elif 'DirectSound' in api_short:
                api_short = 'DirectSound'
            elif 'MME' in api_short:
                api_short = 'MME'
            elif 'WDM' in api_short or 'KS' in api_short:
                api_short = 'WDM-KS'

            name = device['name']
            if len(name) > 30:
                name = name[:27] + "..."

            display_name = f"{device['id']}: {name} ({api_short})"
            mic_options.append(display_name)

        self.mic_combo['values'] = mic_options

        # Set default selection
        if self.selected_device is not None:
            for i, device in enumerate(self.audio_devices):
                if device['id'] == self.selected_device:
                    self.mic_combo.current(i)
                    break
        elif mic_options:
            self.mic_combo.current(0)

    def refresh_devices(self):
        """Refresh the list of audio devices"""
        self.log("Refreshing audio device list...")
        self.status_var.set("Refreshing devices...")

        # Save currently selected device ID
        current_selection = self.selected_device

        # Re-scan devices
        self.get_audio_devices()

        # Update the dropdown
        self.update_microphone_list()

        # Try to restore previous selection if device still exists
        device_still_exists = False
        if current_selection is not None:
            for device in self.audio_devices:
                if device['id'] == current_selection:
                    device_still_exists = True
                    self.selected_device = current_selection
                    break

        if not device_still_exists:
            # Previous device no longer available, use first available
            if self.audio_devices:
                self.selected_device = self.audio_devices[0]['id']
                self.log("Previous device not found, selected first available device", "WARNING")
            else:
                self.selected_device = None
                self.log("No audio devices found!", "ERROR")

        self.status_var.set(f"Devices refreshed - {len(self.audio_devices)} found")
        self.log(f"Device refresh complete - {len(self.audio_devices)} devices found")

    def change_microphone(self, event=None):
        """Change the selected microphone"""
        selection = self.mic_var.get()
        if selection:
            # Extract device ID from "ID: Name (API)" format
            device_id = int(selection.split(":")[0])
            self.selected_device = device_id

            # Find device name
            device_name = "Unknown"
            api_name = "Unknown"
            for device in self.audio_devices:
                if device['id'] == device_id:
                    device_name = device['name']
                    api_name = device.get('hostapi_name', 'Unknown')
                    break

            self.log(f"Microphone changed to: {device_name} (ID: {device_id}, API: {api_name})")
            self.status_var.set(f"Microphone: {device_name}")

    def toggle_recording(self):
        """Start or stop recording"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()

    def start_recording(self):
        """Start audio recording"""
        if self.model is None:
            messagebox.showwarning("Model Not Loaded", "Please wait for the model to load")
            return

        self.log("Starting recording...")
        self.is_recording = True
        self.audio_data = []
        self.record_button.config(text="⏹ Stop Recording")
        self.status_var.set("Recording... Speak now")

        # Start recording thread
        threading.Thread(target=self.record_audio, daemon=True).start()

    def record_audio(self):
        """Record audio from microphone"""
        try:
            # Log selected device info
            device_name = "default"
            device_channels = 1  # Default to mono

            if self.selected_device is not None:
                for device in self.audio_devices:
                    if device['id'] == self.selected_device:
                        device_name = device['name']
                        device_channels = device.get('channels', 1)
                        break
                self.log(f"Recording from device {self.selected_device}: {device_name}")
                self.log(f"Device has {device_channels} input channels")
            else:
                self.log("Recording from default microphone...")

            def callback(indata, frames, time, status):
                if status:
                    self.log(f"Recording status: {status}", "WARNING")
                # If stereo, convert to mono by averaging channels
                if indata.shape[1] > 1:
                    mono_data = np.mean(indata, axis=1, keepdims=True)
                    self.audio_data.append(mono_data.copy())
                else:
                    self.audio_data.append(indata.copy())

            with sd.InputStream(
                device=self.selected_device,  # Use selected device
                samplerate=self.sample_rate,
                channels=device_channels,  # Use device's native channel count
                dtype=np.float32,
                callback=callback
            ):
                while self.is_recording:
                    sd.sleep(100)

            self.log("Recording stopped")

        except Exception as e:
            error_msg = f"Recording error: {str(e)}"
            self.log(error_msg, "ERROR")
            self.log(f"Selected device was: {self.selected_device}", "ERROR")

            # Get device info for better error message
            device_info = "Unknown device"
            api_name = "Unknown"
            for device in self.audio_devices:
                if device['id'] == self.selected_device:
                    device_info = device['name']
                    api_name = device.get('hostapi_name', 'Unknown')
                    break

            # Check if this is a WDM-KS error
            error_str = str(e).lower()
            if 'wdm' in error_str or 'ks' in error_str or '9999' in error_str:
                suggestion = (
                    f"WDM-KS API error detected!\n\n"
                    f"The device '{device_info}' is using WDM-KS which often fails.\n\n"
                    f"Solution:\n"
                    f"1. Click '🔄 Refresh' to rescan devices\n"
                    f"2. The app will automatically select a better API (WASAPI)\n"
                    f"3. Try recording again\n\n"
                    f"Technical details in 'View Logs'"
                )
            elif 'channel' in error_str:
                suggestion = (
                    f"Channel mismatch error!\n\n"
                    f"Try clicking '🔄 Refresh' to update device information.\n\n"
                    f"Click 'View Logs' for details."
                )
            else:
                suggestion = (
                    f"{str(e)}\n\n"
                    f"Try:\n"
                    f"1. Click '🔄 Refresh' button\n"
                    f"2. Select a different device\n"
                    f"3. Check 'View Logs' for details"
                )

            self.status_var.set(f"Error - Click 🔄 Refresh and try again")
            self.root.after(0, lambda: messagebox.showerror("Recording Error", suggestion))
            self.is_recording = False
            self.record_button.config(text="🎤 Start Recording")

    def stop_recording(self):
        """Stop recording and transcribe"""
        if not self.is_recording:
            return

        self.log("Stopping recording and starting transcription...")
        self.is_recording = False
        self.record_button.config(text="🎤 Start Recording")
        self.status_var.set("Processing audio...")
        self.progress.start()

        # Transcribe in background thread
        threading.Thread(target=self.transcribe_recording, daemon=True).start()

    def transcribe_recording(self):
        """Transcribe the recorded audio"""
        try:
            if not self.audio_data:
                self.log("No audio data recorded", "WARNING")
                self.status_var.set("No audio recorded")
                self.progress.stop()
                return

            self.log(f"Processing {len(self.audio_data)} audio chunks...")

            # Combine audio chunks
            audio = np.concatenate(self.audio_data, axis=0)
            audio = audio.flatten()

            self.log(f"Audio shape: {audio.shape}, dtype: {audio.dtype}")

            # Create temporary directory if it doesn't exist
            temp_dir = tempfile.gettempdir()
            self.log(f"Using temp directory: {temp_dir}")

            # Save to temporary file with explicit path
            temp_filename = f"veleron_voice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
            temp_path = os.path.join(temp_dir, temp_filename)

            self.log(f"Saving audio to: {temp_path}")

            try:
                with wave.open(temp_path, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(self.sample_rate)
                    wf.writeframes((audio * 32767).astype(np.int16).tobytes())

                self.log(f"Audio file created successfully: {os.path.getsize(temp_path)} bytes")
            except Exception as e:
                self.log(f"Error saving audio file: {str(e)}", "ERROR")
                raise

            # Transcribe
            self.log(f"Starting transcription with model: {self.model_name}")
            language = None if self.language_var.get() == "auto" else self.language_var.get()

            try:
                result = self.model.transcribe(
                    temp_path,
                    language=language,
                    fp16=False
                )
                self.log(f"Transcription complete. Detected language: {result.get('language', 'unknown')}")
            except Exception as e:
                self.log(f"Error during transcription: {str(e)}", "ERROR")
                raise

            # Clean up
            try:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    self.log(f"Cleaned up temp file: {temp_path}")
            except Exception as e:
                self.log(f"Warning: Could not delete temp file: {str(e)}", "WARNING")

            # Update UI
            self.root.after(0, self.display_transcription, result)

        except Exception as e:
            error_msg = f"Transcription error: {str(e)}"
            self.log(error_msg, "ERROR")
            self.log(f"Full error details: {repr(e)}", "ERROR")
            self.status_var.set(f"Error occurred - check console")
            self.root.after(0, lambda: messagebox.showerror("Transcription Error",
                f"{str(e)}\n\nClick 'View Logs' button for details."))
        finally:
            self.progress.stop()

    def transcribe_file(self):
        """Transcribe an audio file"""
        if self.model is None:
            messagebox.showwarning("Model Not Loaded", "Please wait for the model to load")
            return

        file_path = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[
                ("Audio Files", "*.mp3 *.wav *.m4a *.flac *.ogg"),
                ("All Files", "*.*")
            ]
        )

        if not file_path:
            return

        self.log(f"Transcribing file: {file_path}")
        self.status_var.set(f"Transcribing {os.path.basename(file_path)}...")
        self.progress.start()

        # Transcribe in background
        threading.Thread(
            target=self.transcribe_file_worker,
            args=(file_path,),
            daemon=True
        ).start()

    def transcribe_file_worker(self, file_path):
        """Worker thread for file transcription"""
        try:
            self.log(f"Starting file transcription: {file_path}")
            language = None if self.language_var.get() == "auto" else self.language_var.get()

            result = self.model.transcribe(file_path, language=language, fp16=False)

            self.log(f"File transcription complete. Language: {result.get('language', 'unknown')}")
            self.root.after(0, self.display_transcription, result)

        except Exception as e:
            error_msg = f"File transcription error: {str(e)}"
            self.log(error_msg, "ERROR")
            self.status_var.set("Error occurred - check console")
            self.root.after(0, lambda: messagebox.showerror("Transcription Error",
                f"{str(e)}\n\nClick 'View Logs' button for details."))
        finally:
            self.progress.stop()

    def display_transcription(self, result):
        """Display transcription results"""
        try:
            # Add timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.transcription_text.insert(
                tk.END,
                f"\n{'='*60}\n[{timestamp}] Language: {result.get('language', 'unknown')}\n{'='*60}\n"
            )

            # Add transcription
            transcription_text = result.get("text", "").strip()
            if transcription_text:
                self.transcription_text.insert(tk.END, transcription_text + "\n")
                self.log(f"Transcription displayed: {len(transcription_text)} characters")
            else:
                self.transcription_text.insert(tk.END, "[No speech detected]\n")
                self.log("No speech detected in audio", "WARNING")

            self.transcription_text.see(tk.END)
            self.status_var.set("Transcription complete")

        except Exception as e:
            self.log(f"Error displaying transcription: {str(e)}", "ERROR")

    def clear_transcription(self):
        """Clear the transcription text"""
        self.transcription_text.delete(1.0, tk.END)
        self.log("Transcription cleared")
        self.status_var.set("Cleared")

    def copy_to_clipboard(self):
        """Copy transcription to clipboard"""
        text = self.transcription_text.get(1.0, tk.END).strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.log("Text copied to clipboard")
            self.status_var.set("Copied to clipboard")
        else:
            messagebox.showinfo("No Content", "No transcription to copy")

    def export_transcription(self, format_type):
        """Export transcription to file"""
        text = self.transcription_text.get(1.0, tk.END).strip()
        if not text:
            messagebox.showinfo("No Content", "No transcription to export")
            return

        try:
            if format_type == "txt":
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".txt",
                    filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
                )
                if file_path:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(text)
                    self.log(f"Exported to TXT: {file_path}")
                    self.status_var.set(f"Exported to {file_path}")

            elif format_type == "json":
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".json",
                    filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
                )
                if file_path:
                    data = {
                        "timestamp": datetime.now().isoformat(),
                        "model": self.model_name,
                        "language": self.language_var.get(),
                        "transcription": text
                    }
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    self.log(f"Exported to JSON: {file_path}")
                    self.status_var.set(f"Exported to {file_path}")

        except Exception as e:
            error_msg = f"Export error: {str(e)}"
            self.log(error_msg, "ERROR")
            messagebox.showerror("Export Error", str(e))


def main():
    """Main entry point"""
    print("="*60)
    print("Veleron Voice Flow - Starting Application")
    print("="*60)
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Temp directory: {tempfile.gettempdir()}")
    print("="*60)

    root = tk.Tk()
    app = VeleronVoiceFlow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
