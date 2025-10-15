"""
Veleron Dictation v2 - Improved Real-Time Voice-to-Text System
System-wide voice dictation with better UI and microphone selection

Improvements:
- Visible status window
- Microphone selection dropdown
- Better hotkey handling
- Clear visual feedback
- Test recording feature

Author: Veleron Dev Studios
License: Internal Use Only
"""

import whisper
import pyautogui
import sounddevice as sd
import numpy as np
import queue
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import wave
import tempfile
import os
import time
from datetime import datetime
from pathlib import Path
from security_utils import sanitize_for_typing, SecurityError
from temp_file_handler import temp_audio_file, write_audio_to_wav
import logging

# Configure logging
log_dir = Path.home() / '.veleron_dictation'
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'security.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class VeleronDictationV2:
    """Improved real-time voice dictation system"""

    def __init__(self):
        # Configuration
        self.model_name = 'base'
        self.language = None  # Auto-detect
        self.sample_rate = 16000
        self.selected_device = None

        # State
        self.is_recording = False
        self.is_running = True
        self.audio_queue = queue.Queue()
        self.audio_data = []
        self.model = None

        # Create main window
        self.root = tk.Tk()
        self.root.title("Veleron Dictation v2")
        self.root.geometry("500x700")
        self.root.attributes('-topmost', True)  # Always on top

        # Setup UI
        self.setup_ui()

        # Load model in background
        self.status_var.set("Loading model...")
        threading.Thread(target=self.load_model, daemon=True).start()

    def setup_ui(self):
        """Create the user interface"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # ===== TITLE =====
        title_label = ttk.Label(
            main_frame,
            text="Veleron Dictation v2",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # ===== STATUS INDICATOR =====
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        self.status_var = tk.StringVar(value="Initializing...")
        self.status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Arial", 11),
            wraplength=450
        )
        self.status_label.grid(row=0, column=0, sticky=tk.W)

        # ===== MICROPHONE SELECTION =====
        mic_frame = ttk.LabelFrame(main_frame, text="Microphone", padding="10")
        mic_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(mic_frame, text="Select Device:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

        # Get available audio devices
        self.audio_devices = self.get_audio_devices()
        device_names = [f"{d['index']}: {d['name']}" for d in self.audio_devices]

        self.device_var = tk.StringVar()
        device_combo = ttk.Combobox(
            mic_frame,
            textvariable=self.device_var,
            values=device_names,
            state="readonly",
            width=50
        )
        device_combo.grid(row=0, column=1, sticky=(tk.W, tk.E))
        mic_frame.columnconfigure(1, weight=1)

        # Set default device
        if self.audio_devices:
            default_device = sd.default.device[0]
            for i, dev in enumerate(self.audio_devices):
                if dev['index'] == default_device:
                    device_combo.current(i)
                    self.selected_device = dev['index']
                    break
            if self.selected_device is None:
                device_combo.current(0)
                self.selected_device = self.audio_devices[0]['index']

        def on_device_change(event):
            selected = self.device_var.get()
            device_index = int(selected.split(':')[0])
            self.selected_device = device_index
            self.status_var.set(f"✓ Microphone changed to: {selected}")

        device_combo.bind('<<ComboboxSelected>>', on_device_change)

        # Test microphone button
        ttk.Button(
            mic_frame,
            text="Test Microphone",
            command=self.test_microphone
        ).grid(row=1, column=0, columnspan=2, pady=(10, 0))

        # ===== CONTROLS =====
        control_frame = ttk.LabelFrame(main_frame, text="Recording", padding="10")
        control_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Big record button
        self.record_button = tk.Button(
            control_frame,
            text="🎤 HOLD to Record\n(Click and Hold)",
            font=("Arial", 14, "bold"),
            bg="#4CAF50",
            fg="white",
            height=3,
            relief=tk.RAISED,
            cursor="hand2"
        )
        self.record_button.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        control_frame.columnconfigure(0, weight=1)

        # Bind mouse events for hold-to-record
        self.record_button.bind('<ButtonPress-1>', lambda e: self.start_recording())
        self.record_button.bind('<ButtonRelease-1>', lambda e: self.stop_recording())

        # Instructions
        instructions = (
            "HOW TO USE:\n"
            "1. Click and HOLD the green button\n"
            "2. Speak clearly while holding\n"
            "3. Release when done speaking\n"
            "4. Text will appear in your active window!"
        )
        ttk.Label(
            control_frame,
            text=instructions,
            font=("Arial", 9),
            foreground="gray",
            justify=tk.LEFT
        ).grid(row=1, column=0, pady=(10, 0), sticky=tk.W)

        # ===== SETTINGS =====
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))

        # Model selection
        ttk.Label(settings_frame, text="Model:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.model_var = tk.StringVar(value=self.model_name)
        model_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.model_var,
            values=["tiny", "tiny.en", "base", "base.en", "small", "small.en", "medium", "turbo"],
            state="readonly",
            width=15
        )
        model_combo.grid(row=0, column=1, sticky=tk.W)
        model_combo.bind("<<ComboboxSelected>>", self.change_model)

        # Language selection
        ttk.Label(settings_frame, text="Language:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.language_var = tk.StringVar(value="auto")
        lang_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.language_var,
            values=["auto", "en", "es", "fr", "de", "it", "pt", "nl", "ja", "ko", "zh"],
            state="readonly",
            width=15
        )
        lang_combo.grid(row=1, column=1, sticky=tk.W, pady=(5, 0))

        # ===== TRANSCRIPTION LOG =====
        log_frame = ttk.LabelFrame(main_frame, text="Recent Transcriptions", padding="10")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        main_frame.rowconfigure(5, weight=1)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=("Arial", 9),
            height=10
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        # Clear log button
        ttk.Button(
            log_frame,
            text="Clear Log",
            command=lambda: self.log_text.delete(1.0, tk.END)
        ).grid(row=1, column=0, pady=(5, 0))

        # ===== FOOTER =====
        footer_frame = ttk.Frame(main_frame)
        footer_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E))

        self.footer_var = tk.StringVar(value="Ready to record")
        ttk.Label(
            footer_frame,
            textvariable=self.footer_var,
            font=("Arial", 8),
            foreground="blue"
        ).grid(row=0, column=0, sticky=tk.W)

    def get_audio_devices(self):
        """Get list of input audio devices"""
        devices = []
        try:
            device_list = sd.query_devices()
            for i, device in enumerate(device_list):
                if device['max_input_channels'] > 0:  # Input device
                    devices.append({
                        'index': i,
                        'name': device['name'],
                        'channels': device['max_input_channels'],
                        'sample_rate': device['default_samplerate']
                    })
        except Exception as e:
            print(f"Error querying devices: {e}")
        return devices

    def test_microphone(self):
        """Test microphone by recording a short sample"""
        if self.selected_device is None:
            messagebox.showwarning("No Device", "Please select a microphone first")
            return

        self.status_var.set("🔴 Testing microphone... Speak now!")
        self.root.update()

        try:
            # Record 2 seconds
            duration = 2  # seconds
            recording = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=1,
                device=self.selected_device,
                dtype=np.float32
            )
            sd.wait()

            # Check if we got audio
            max_amplitude = np.max(np.abs(recording))
            if max_amplitude < 0.01:
                self.status_var.set("⚠️ Microphone test: No sound detected!")
                messagebox.showwarning(
                    "Low Audio",
                    f"Microphone is working but audio level is very low.\n"
                    f"Max amplitude: {max_amplitude:.4f}\n\n"
                    f"Try:\n"
                    f"- Speaking louder\n"
                    f"- Moving closer to microphone\n"
                    f"- Checking microphone permissions"
                )
            else:
                self.status_var.set(f"✓ Microphone test passed! Level: {max_amplitude:.2f}")
                messagebox.showinfo(
                    "Test Success",
                    f"Microphone is working correctly!\n"
                    f"Audio level: {max_amplitude:.2f}"
                )

        except Exception as e:
            self.status_var.set(f"❌ Microphone test failed: {str(e)}")
            messagebox.showerror("Test Failed", f"Error: {str(e)}")

    def load_model(self):
        """Load the Whisper model"""
        try:
            self.model = whisper.load_model(self.model_name)
            self.status_var.set(f"✓ Ready! Model: {self.model_name}")
            self.footer_var.set("Click and hold the green button to record")
        except Exception as e:
            self.status_var.set(f"❌ Error loading model: {str(e)}")
            messagebox.showerror("Model Error", f"Failed to load model: {str(e)}")

    def change_model(self, event=None):
        """Change the Whisper model"""
        new_model = self.model_var.get()
        if new_model != self.model_name:
            self.model_name = new_model
            self.status_var.set(f"Loading {new_model} model...")
            self.model = None
            threading.Thread(target=self.load_model, daemon=True).start()

    def start_recording(self):
        """Start recording audio"""
        if self.model is None:
            messagebox.showwarning("Model Not Loaded", "Please wait for the model to load")
            return

        if self.selected_device is None:
            messagebox.showwarning("No Microphone", "Please select a microphone")
            return

        self.is_recording = True
        self.audio_data = []
        self.record_button.config(bg="#f44336", text="🔴 RECORDING...\n(Release to stop)")
        self.status_var.set("🔴 Recording... Speak now!")
        self.footer_var.set("Recording audio...")

        # Start recording in a separate thread
        def record():
            try:
                # DIRECTSOUND FALLBACK: Determine best device to use
                # This prevents WDM-KS errors with USB devices
                device_spec = self.selected_device
                device_channels = 1

                print("=" * 60)
                print("DIRECTSOUND FALLBACK LOGIC - START")
                print("=" * 60)

                try:
                    # Get selected device info
                    device_info = sd.query_devices(self.selected_device, kind='input')
                    device_name = device_info['name']
                    device_channels = min(device_info['max_input_channels'], 1)  # Use mono

                    print(f"[FALLBACK] Step 1: Got selected device info")
                    print(f"[FALLBACK]   - Device name: '{device_name}'")
                    print(f"[FALLBACK]   - Device ID: {self.selected_device}")
                    print(f"[FALLBACK]   - Device channels: {device_channels}")

                    # Extract base name for device matching
                    selected_base_name = device_name.split('(')[0].strip()
                    print(f"[FALLBACK]   - Base name extracted: '{selected_base_name}'")

                    # Try to find DirectSound version of the same device
                    directsound_found = False
                    if selected_base_name:
                        print(f"[FALLBACK] Step 2: Searching for DirectSound version of '{selected_base_name}'...")
                        all_devices = sd.query_devices()
                        hostapi_info = sd.query_hostapis()
                        print(f"[FALLBACK] Total devices from sd.query_devices(): {len(all_devices)}")

                        devices_checked = 0

                        for i, full_device in enumerate(all_devices):
                            if full_device['max_input_channels'] > 0:
                                devices_checked += 1
                                full_name = full_device['name'].strip()
                                full_base = full_name.split('(')[0].strip()
                                hostapi = hostapi_info[full_device['hostapi']]['name']

                                # Log every input device we're checking
                                print(f"[FALLBACK]   Checking device {i}: '{full_name}' (API: {hostapi})")
                                print(f"[FALLBACK]     - Base name: '{full_base}'")
                                print(f"[FALLBACK]     - Match check: base=='{selected_base_name}' ? {full_base == selected_base_name}")
                                print(f"[FALLBACK]     - DirectSound check: 'DirectSound' in '{hostapi}' ? {'DirectSound' in hostapi}")

                                if full_base == selected_base_name and 'DirectSound' in hostapi:
                                    device_spec = i
                                    device_channels = min(full_device['max_input_channels'], 1)
                                    directsound_found = True
                                    print("=" * 60)
                                    print(f"[FALLBACK] ✓ SUCCESS! SWITCHING TO DIRECTSOUND:")
                                    print(f"[FALLBACK]   Using device ID {i} ({full_name})")
                                    print(f"[FALLBACK]   Instead of device ID {self.selected_device}")
                                    print(f"[FALLBACK]   Channels: {device_channels}")
                                    print("=" * 60)
                                    break

                        print(f"[FALLBACK] Step 3: Search complete. Checked {devices_checked} input devices.")

                    if not directsound_found:
                        print(f"[FALLBACK] No DirectSound version found - using selected device")
                        print(f"[FALLBACK] Will use device ID {device_spec}")

                except Exception as device_error:
                    print(f"[FALLBACK] WARNING: Error during device selection: {device_error}")
                    print("[FALLBACK] Falling back to selected device")

                print("=" * 60)
                print("DIRECTSOUND FALLBACK LOGIC - END")
                print(f"Final device_spec to use: {device_spec}")
                print("=" * 60)

                with sd.InputStream(
                    samplerate=self.sample_rate,
                    channels=device_channels,
                    device=device_spec,
                    dtype=np.float32
                ) as stream:
                    while self.is_recording:
                        data, overflowed = stream.read(1024)
                        if overflowed:
                            print("Audio buffer overflowed")
                        self.audio_data.append(data)
            except Exception as e:
                self.status_var.set(f"❌ Recording error: {str(e)}")
                messagebox.showerror("Recording Error", str(e))

        threading.Thread(target=record, daemon=True).start()

    def stop_recording(self):
        """Stop recording and transcribe"""
        if not self.is_recording:
            return

        self.is_recording = False
        self.record_button.config(bg="#4CAF50", text="🎤 HOLD to Record\n(Click and Hold)")
        self.status_var.set("⏳ Processing audio...")
        self.footer_var.set("Transcribing...")

        # Process in background
        threading.Thread(target=self.transcribe_and_type, daemon=True).start()

    def transcribe_and_type(self):
        """Transcribe audio and type it out - SECURE VERSION"""
        try:
            if not self.audio_data:
                self.status_var.set("⚠️ No audio recorded")
                self.footer_var.set("Ready to record")
                return

            # Combine audio chunks
            audio = np.concatenate(self.audio_data, axis=0)
            audio = audio.flatten()

            # Validate audio length
            MIN_DURATION = 0.3
            MAX_DURATION = 300  # 5 minutes max

            duration = len(audio) / self.sample_rate

            if duration < MIN_DURATION:
                self.status_var.set(f"⚠️ Audio too short (min: {MIN_DURATION}s)")
                self.footer_var.set("Ready to record")
                return

            if duration > MAX_DURATION:
                self.status_var.set(f"⚠️ Audio too long (max: {MAX_DURATION}s)")
                self.footer_var.set("Ready to record")
                return

            # Check audio level
            max_amplitude = np.max(np.abs(audio))
            if max_amplitude < 0.01:
                self.status_var.set("⚠️ No speech detected - try speaking louder")
                self.footer_var.set("Ready to record")
                return

            # Use secure temporary file handling
            with temp_audio_file() as temp_path:
                # Write audio to secure temp file
                write_audio_to_wav(temp_path, audio, sample_rate=self.sample_rate)

                # Transcribe
                language = None if self.language_var.get() == "auto" else self.language_var.get()
                result = self.model.transcribe(
                    str(temp_path),
                    language=language,
                    fp16=False
                )

                # Temp file automatically deleted after this block

            # Get transcribed text
            text = result["text"].strip()

            if text:
                # SECURITY FIX: Sanitize text before typing
                try:
                    safe_text = sanitize_for_typing(text)

                    if not safe_text:
                        self.status_var.set("⚠️ Transcription resulted in empty safe text")
                        self.footer_var.set("Ready to record")
                        return

                    # Log if text was modified
                    if safe_text != text:
                        logger.warning(
                            f"Text was sanitized. Original length: {len(text)}, "
                            f"Safe length: {len(safe_text)}"
                        )

                    # Log the transcription (use safe_text)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    self.log_text.insert(tk.END, f"[{timestamp}] {safe_text}\n")
                    self.log_text.see(tk.END)

                    self.status_var.set(f"⌨️ Typing: {safe_text[:50]}...")
                    self.footer_var.set("Typing text...")

                    # Small delay to ensure target window is focused
                    time.sleep(0.1)

                    # Type the SANITIZED text
                    pyautogui.write(safe_text, interval=0.01)

                    self.status_var.set(f"✓ Typed: {safe_text[:50]}...")
                    self.footer_var.set(f"Success! Last typed: {len(safe_text)} characters")

                except Exception as sanitize_error:
                    logger.error(f"Text sanitization error: {sanitize_error}")
                    self.status_var.set("❌ Error: Could not sanitize text safely")
                    self.footer_var.set("Error occurred - check logs")
            else:
                self.status_var.set("⚠️ No speech detected in audio")
                self.footer_var.set("Ready to record")

        except Exception as e:
            logger.error(f"Transcription error: {e}", exc_info=True)
            # Don't expose error details to user
            self.status_var.set("❌ An error occurred during transcription")
            self.footer_var.set("Error occurred - check logs")

    def run(self):
        """Run the application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    print("=" * 60)
    print("VELERON DICTATION V2 - Real-Time Voice-to-Text")
    print("=" * 60)
    print()
    print("Improved features:")
    print("  - Visible status window")
    print("  - Microphone selection")
    print("  - Test microphone button")
    print("  - Click-and-hold to record")
    print("  - Clear visual feedback")
    print()

    try:
        app = VeleronDictationV2()
        app.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
