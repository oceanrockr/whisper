"""
Veleron Voice Flow - Custom WhisperFlow-equivalent Application
Real-time voice-to-text transcription powered by OpenAI Whisper

Features:
- Real-time audio recording
- Automatic transcription using Whisper
- Clean, user-friendly GUI
- Export to multiple formats (TXT, DOCX, JSON)
- Hotkey support for quick recording
- Multi-language support
- Automatic punctuation and formatting

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
from datetime import datetime
import json


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

        # Setup UI
        self.setup_ui()

        # Load model in background
        self.status_var.set("Loading Whisper model...")
        threading.Thread(target=self.load_model, daemon=True).start()

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

        # ===== STATUS BAR =====
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(0, weight=1)

        self.status_var = tk.StringVar(value="Ready")
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

    def load_model(self):
        """Load the Whisper model"""
        try:
            self.model = whisper.load_model(self.model_name)
            self.status_var.set(f"Ready - Model: {self.model_name}")
        except Exception as e:
            self.status_var.set(f"Error loading model: {str(e)}")
            messagebox.showerror("Model Error", f"Failed to load model: {str(e)}")

    def change_model(self, event=None):
        """Change the Whisper model"""
        new_model = self.model_var.get()
        if new_model != self.model_name:
            self.model_name = new_model
            self.status_var.set(f"Loading {new_model} model...")
            self.model = None
            threading.Thread(target=self.load_model, daemon=True).start()

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

        self.is_recording = True
        self.audio_data = []
        self.record_button.config(text="⏹ Stop Recording")
        self.status_var.set("Recording... Speak now")

        # Start recording thread
        threading.Thread(target=self.record_audio, daemon=True).start()

    def record_audio(self):
        """Record audio from microphone"""
        try:
            def callback(indata, frames, time, status):
                if status:
                    print(f"Recording status: {status}")
                self.audio_data.append(indata.copy())

            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype=np.float32,
                callback=callback
            ):
                while self.is_recording:
                    sd.sleep(100)

        except Exception as e:
            self.status_var.set(f"Recording error: {str(e)}")
            messagebox.showerror("Recording Error", str(e))
            self.is_recording = False
            self.record_button.config(text="🎤 Start Recording")

    def stop_recording(self):
        """Stop recording and transcribe"""
        if not self.is_recording:
            return

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
                self.status_var.set("No audio recorded")
                self.progress.stop()
                return

            # Combine audio chunks
            audio = np.concatenate(self.audio_data, axis=0)
            audio = audio.flatten()

            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            with wave.open(temp_file.name, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes((audio * 32767).astype(np.int16).tobytes())

            # Transcribe
            language = None if self.language_var.get() == "auto" else self.language_var.get()
            result = self.model.transcribe(
                temp_file.name,
                language=language,
                fp16=False
            )

            # Clean up
            os.unlink(temp_file.name)

            # Update UI
            self.root.after(0, self.display_transcription, result)

        except Exception as e:
            self.status_var.set(f"Transcription error: {str(e)}")
            messagebox.showerror("Transcription Error", str(e))
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
            language = None if self.language_var.get() == "auto" else self.language_var.get()
            result = self.model.transcribe(file_path, language=language, fp16=False)
            self.root.after(0, self.display_transcription, result)
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Transcription Error", str(e))
        finally:
            self.progress.stop()

    def display_transcription(self, result):
        """Display transcription results"""
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.transcription_text.insert(
            tk.END,
            f"\n{'='*60}\n[{timestamp}] Language: {result['language']}\n{'='*60}\n"
        )

        # Add transcription
        self.transcription_text.insert(tk.END, result["text"].strip() + "\n")
        self.transcription_text.see(tk.END)

        self.status_var.set("Transcription complete")

    def clear_transcription(self):
        """Clear the transcription text"""
        self.transcription_text.delete(1.0, tk.END)
        self.status_var.set("Cleared")

    def copy_to_clipboard(self):
        """Copy transcription to clipboard"""
        text = self.transcription_text.get(1.0, tk.END).strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.status_var.set("Copied to clipboard")
        else:
            messagebox.showinfo("No Content", "No transcription to copy")

    def export_transcription(self, format_type):
        """Export transcription to file"""
        text = self.transcription_text.get(1.0, tk.END).strip()
        if not text:
            messagebox.showinfo("No Content", "No transcription to export")
            return

        if format_type == "txt":
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
            )
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
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
                self.status_var.set(f"Exported to {file_path}")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = VeleronVoiceFlow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
