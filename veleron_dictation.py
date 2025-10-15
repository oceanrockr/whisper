"""
Veleron Dictation - Real-Time Voice-to-Text System
System-wide voice dictation that types into any application

Features:
- Push-to-talk hotkey (configurable)
- Real-time streaming transcription
- Types directly into active window
- Works in Word, PowerPoint, Notepad, any text field
- System tray integration
- Low latency transcription

Author: Veleron Dev Studios
License: Internal Use Only
"""

import whisper
import pyautogui
import keyboard
import sounddevice as sd
import numpy as np
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw
import io
import wave
import tempfile
import os
import time
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


class VeleronDictation:
    """Real-time voice dictation system"""

    def __init__(self):
        # Configuration
        self.hotkey = 'ctrl+shift+space'  # Push-to-talk hotkey
        self.model_name = 'base'
        self.language = None  # Auto-detect
        self.sample_rate = 16000

        # State
        self.is_recording = False
        self.is_running = True
        self.audio_queue = queue.Queue()
        self.audio_data = []
        self.model = None

        # UI elements
        self.status_window = None
        self.status_label = None
        self.tray_icon = None

        # Initialize
        print("Veleron Dictation - Starting...")
        print(f"Loading {self.model_name} model...")
        self.load_model()
        print(f"Model loaded! Ready to use.")
        print(f"\nPress {self.hotkey.upper()} to start/stop recording")
        print("Speak while holding the hotkey, release to transcribe and type\n")

    def load_model(self):
        """Load Whisper model"""
        try:
            self.model = whisper.load_model(self.model_name)
        except Exception as e:
            print(f"Error loading model: {e}")
            raise

    def create_status_window(self):
        """Create floating status window"""
        self.status_window = tk.Tk()
        self.status_window.title("Veleron Dictation")
        self.status_window.attributes('-topmost', True)
        self.status_window.geometry("300x150+50+50")

        # Create UI
        frame = ttk.Frame(self.status_window, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(
            frame,
            text="Veleron Dictation",
            font=("Arial", 14, "bold")
        ).grid(row=0, column=0, pady=(0, 10))

        self.status_label = ttk.Label(
            frame,
            text="🎤 Ready - Press hotkey to speak",
            font=("Arial", 10),
            wraplength=250
        )
        self.status_label.grid(row=1, column=0, pady=10)

        ttk.Label(
            frame,
            text=f"Hotkey: {self.hotkey.upper()}",
            font=("Arial", 9),
            foreground="gray"
        ).grid(row=2, column=0, pady=(10, 0))

        # Settings button
        ttk.Button(
            frame,
            text="Settings",
            command=self.show_settings
        ).grid(row=3, column=0, pady=(10, 0))

        # Handle window close
        self.status_window.protocol("WM_DELETE_WINDOW", self.hide_status_window)

        return self.status_window

    def hide_status_window(self):
        """Hide status window (don't close)"""
        if self.status_window:
            self.status_window.withdraw()

    def show_status_window(self):
        """Show status window"""
        if self.status_window:
            self.status_window.deiconify()
            self.status_window.lift()

    def update_status(self, message):
        """Update status label"""
        if self.status_label:
            self.status_label.config(text=message)

    def show_settings(self):
        """Show settings dialog"""
        settings = tk.Toplevel(self.status_window)
        settings.title("Dictation Settings")
        settings.geometry("400x300")
        settings.attributes('-topmost', True)

        frame = ttk.Frame(settings, padding="20")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Model selection
        ttk.Label(frame, text="Model:").grid(row=0, column=0, sticky=tk.W, pady=5)
        model_var = tk.StringVar(value=self.model_name)
        model_combo = ttk.Combobox(
            frame,
            textvariable=model_var,
            values=["tiny", "tiny.en", "base", "base.en", "small", "small.en", "medium", "turbo"],
            state="readonly",
            width=15
        )
        model_combo.grid(row=0, column=1, sticky=tk.W, pady=5)

        # Language selection
        ttk.Label(frame, text="Language:").grid(row=1, column=0, sticky=tk.W, pady=5)
        lang_var = tk.StringVar(value=self.language or "auto")
        lang_combo = ttk.Combobox(
            frame,
            textvariable=lang_var,
            values=["auto", "en", "es", "fr", "de", "it", "pt", "nl", "ja", "ko", "zh"],
            state="readonly",
            width=15
        )
        lang_combo.grid(row=1, column=1, sticky=tk.W, pady=5)

        # Hotkey (display only for now)
        ttk.Label(frame, text="Hotkey:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Label(frame, text=self.hotkey.upper()).grid(row=2, column=1, sticky=tk.W, pady=5)

        # Info
        info_text = (
            "Model Guide:\n"
            "• tiny/base: Fastest, good for quick notes\n"
            "• small: Balanced speed/accuracy\n"
            "• medium/turbo: Best accuracy\n"
            "• .en models: English-only (more accurate)"
        )
        ttk.Label(
            frame,
            text=info_text,
            font=("Arial", 8),
            foreground="gray",
            justify=tk.LEFT
        ).grid(row=3, column=0, columnspan=2, pady=(20, 10), sticky=tk.W)

        def apply_settings():
            new_model = model_var.get()
            new_lang = lang_var.get()

            if new_model != self.model_name:
                self.model_name = new_model
                self.update_status("⏳ Loading new model...")
                threading.Thread(target=self.load_model, daemon=True).start()

            self.language = None if new_lang == "auto" else new_lang
            settings.destroy()
            self.update_status("🎤 Ready - Press hotkey to speak")

        ttk.Button(
            frame,
            text="Apply",
            command=apply_settings
        ).grid(row=4, column=0, columnspan=2, pady=(10, 0))

    def audio_callback(self, indata, frames, time_info, status):
        """Callback for audio recording"""
        if status:
            print(f"Audio status: {status}")
        if self.is_recording:
            self.audio_queue.put(indata.copy())

    def start_recording(self):
        """Start recording audio"""
        if self.is_recording:
            return

        self.is_recording = True
        self.audio_data = []
        self.update_status("🔴 Recording... (release hotkey when done)")

        # Start collecting audio from queue
        def collect_audio():
            while self.is_recording:
                try:
                    data = self.audio_queue.get(timeout=0.1)
                    self.audio_data.append(data)
                except queue.Empty:
                    continue

        threading.Thread(target=collect_audio, daemon=True).start()

    def stop_recording(self):
        """Stop recording and transcribe"""
        if not self.is_recording:
            return

        self.is_recording = False

        if not self.audio_data:
            self.update_status("🎤 Ready - Press hotkey to speak")
            return

        self.update_status("⏳ Transcribing...")

        # Process in background
        threading.Thread(target=self.transcribe_and_type, daemon=True).start()

    def transcribe_and_type(self):
        """Transcribe audio and type it out - SECURE VERSION"""
        try:
            # Combine audio chunks
            audio = np.concatenate(self.audio_data, axis=0)
            audio = audio.flatten()

            # Validate audio length
            MIN_DURATION = 0.3
            MAX_DURATION = 300  # 5 minutes max

            duration = len(audio) / self.sample_rate

            if duration < MIN_DURATION:
                self.update_status(f"⚠️ Audio too short (min: {MIN_DURATION}s)")
                time.sleep(1)
                self.update_status("🎤 Ready - Press hotkey to speak")
                return

            if duration > MAX_DURATION:
                self.update_status(f"⚠️ Audio too long (max: {MAX_DURATION}s)")
                time.sleep(1)
                self.update_status("🎤 Ready - Press hotkey to speak")
                return

            # Use secure temporary file handling
            with temp_audio_file() as temp_path:
                # Write audio to secure temp file
                write_audio_to_wav(temp_path, audio, sample_rate=self.sample_rate)

                # Transcribe
                result = self.model.transcribe(
                    str(temp_path),
                    language=self.language,
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
                        self.update_status("⚠️ Transcription resulted in empty safe text")
                        time.sleep(2)
                        self.update_status("🎤 Ready - Press hotkey to speak")
                        return

                    # Log if text was modified
                    if safe_text != text:
                        logger.warning(
                            f"Text was sanitized. Original length: {len(text)}, "
                            f"Safe length: {len(safe_text)}"
                        )

                    self.update_status(f"⌨️ Typing: {safe_text[:30]}...")

                    # Small delay to ensure target window is focused
                    time.sleep(0.1)

                    # Type the SANITIZED text
                    pyautogui.write(safe_text, interval=0.01)

                    self.update_status(f"✓ Typed: {safe_text[:30]}...")
                    time.sleep(2)

                except Exception as sanitize_error:
                    logger.error(f"Text sanitization error: {sanitize_error}")
                    self.update_status("❌ Error: Could not sanitize text safely")
                    time.sleep(2)
            else:
                self.update_status("⚠️ No speech detected")
                time.sleep(1)

            self.update_status("🎤 Ready - Press hotkey to speak")

        except Exception as e:
            logger.error(f"Transcription error: {e}", exc_info=True)
            # Don't expose error details to user
            self.update_status("❌ An error occurred during transcription")
            time.sleep(2)
            self.update_status("🎤 Ready - Press hotkey to speak")

    def setup_hotkey(self):
        """Setup keyboard hotkey"""
        keyboard.add_hotkey(self.hotkey, self.start_recording, suppress=False)
        keyboard.on_release_key(
            self.hotkey.split('+')[-1],
            lambda _: self.stop_recording() if self.is_recording else None
        )

    def create_tray_icon(self):
        """Create system tray icon"""
        # Create icon image
        def create_icon_image():
            width = 64
            height = 64
            image = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(image)
            draw.ellipse([8, 8, 56, 56], fill='blue', outline='darkblue')
            draw.text((20, 20), "VD", fill='white')
            return image

        icon_image = create_icon_image()

        # Create menu
        menu = Menu(
            MenuItem('Show Status', self.show_status_window),
            MenuItem('Settings', self.show_settings),
            MenuItem('Exit', self.quit_app)
        )

        self.tray_icon = Icon("Veleron Dictation", icon_image, "Veleron Dictation", menu)

    def quit_app(self):
        """Quit application"""
        self.is_running = False
        if self.tray_icon:
            self.tray_icon.stop()
        if self.status_window:
            self.status_window.quit()

    def run(self):
        """Run the application"""
        # Create system tray icon
        self.create_tray_icon()

        # Setup hotkey
        self.setup_hotkey()

        # Create status window
        self.create_status_window()

        # DIRECTSOUND FALLBACK: Determine best device to use
        # This prevents WDM-KS errors with USB devices
        device_spec = None  # Use default device
        device_channels = 1  # Default to mono

        print("=" * 60)
        print("DIRECTSOUND FALLBACK LOGIC - START")
        print("=" * 60)

        try:
            # Get default input device info
            default_device_id = sd.default.device[0]
            device_info = sd.query_devices(default_device_id, kind='input')
            device_name = device_info['name']
            device_channels = min(device_info['max_input_channels'], 1)  # Use mono

            print(f"[FALLBACK] Step 1: Got default input device")
            print(f"[FALLBACK]   - Device name: '{device_name}'")
            print(f"[FALLBACK]   - Device ID: {default_device_id}")
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
                            print(f"[FALLBACK]   Instead of device ID {default_device_id}")
                            print(f"[FALLBACK]   Channels: {device_channels}")
                            print("=" * 60)
                            break

                print(f"[FALLBACK] Step 3: Search complete. Checked {devices_checked} input devices.")

            if not directsound_found:
                print(f"[FALLBACK] No DirectSound version found - using default device", "WARNING")
                print(f"[FALLBACK] Will use device ID {default_device_id}")
                device_spec = default_device_id

        except Exception as e:
            print(f"[FALLBACK] WARNING: Error during device selection: {e}")
            print("[FALLBACK] Falling back to system default")
            device_spec = None
            device_channels = 1

        print("=" * 60)
        print("DIRECTSOUND FALLBACK LOGIC - END")
        print(f"Final device_spec to use: {device_spec}")
        print("=" * 60)

        # Start audio stream with optimized device
        with sd.InputStream(
            device=device_spec,
            samplerate=self.sample_rate,
            channels=device_channels,
            dtype=np.float32,
            callback=self.audio_callback
        ):
            # Run tray icon in background thread
            threading.Thread(target=self.tray_icon.run, daemon=True).start()

            # Run tkinter main loop
            self.status_window.mainloop()


def main():
    """Main entry point"""
    print("=" * 60)
    print("VELERON DICTATION - Real-Time Voice-to-Text")
    print("=" * 60)
    print()

    try:
        app = VeleronDictation()
        app.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
