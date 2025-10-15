"""
Whisper Usage Demo - Examples of using OpenAI Whisper for audio transcription

This script demonstrates different ways to use Whisper in Python.
"""

import whisper

# ========================================
# Example 1: Basic Transcription
# ========================================
def basic_transcription(audio_file, model_name="tiny"):
    """
    Basic audio transcription using Whisper

    Args:
        audio_file: Path to audio file (mp3, wav, m4a, etc.)
        model_name: Model to use (tiny, base, small, medium, large, turbo)

    Returns:
        dict: Transcription results including text, segments, and language
    """
    print(f"Loading {model_name} model...")
    model = whisper.load_model(model_name)

    print(f"Transcribing {audio_file}...")
    result = model.transcribe(audio_file)

    print("\n=== TRANSCRIPTION ===")
    print(result["text"])

    return result


# ========================================
# Example 2: Transcription with Language Detection
# ========================================
def transcribe_with_language_detection(audio_file):
    """
    Transcribe audio and detect the spoken language
    """
    model = whisper.load_model("base")

    # Load and prepare audio
    audio = whisper.load_audio(audio_file)
    audio = whisper.pad_or_trim(audio)

    # Create mel spectrogram
    mel = whisper.log_mel_spectrogram(audio, n_mels=model.dims.n_mels).to(model.device)

    # Detect language
    _, probs = model.detect_language(mel)
    detected_language = max(probs, key=probs.get)

    print(f"\n=== LANGUAGE DETECTION ===")
    print(f"Detected language: {detected_language}")
    print(f"Confidence: {probs[detected_language]:.2%}")

    # Transcribe with detected language
    result = model.transcribe(audio_file, language=detected_language)
    print(f"\nTranscription: {result['text']}")

    return result


# ========================================
# Example 3: Transcription with Timestamps
# ========================================
def transcribe_with_timestamps(audio_file, model_name="base"):
    """
    Transcribe audio and get word-level timestamps
    """
    model = whisper.load_model(model_name)

    # Transcribe with word timestamps
    result = model.transcribe(audio_file, word_timestamps=True)

    print("\n=== TRANSCRIPTION WITH TIMESTAMPS ===")
    for segment in result["segments"]:
        start = segment["start"]
        end = segment["end"]
        text = segment["text"]
        print(f"[{start:.2f}s - {end:.2f}s]: {text}")

    return result


# ========================================
# Example 4: Translation to English
# ========================================
def translate_to_english(audio_file, model_name="medium"):
    """
    Translate non-English speech to English
    Note: Use medium or large models for best translation results
    """
    model = whisper.load_model(model_name)

    # Transcribe and translate to English
    result = model.transcribe(audio_file, task="translate")

    print("\n=== TRANSLATION TO ENGLISH ===")
    print(result["text"])

    return result


# ========================================
# Example 5: Batch Processing Multiple Files
# ========================================
def batch_transcribe(audio_files, model_name="tiny"):
    """
    Transcribe multiple audio files
    """
    model = whisper.load_model(model_name)

    results = []
    for audio_file in audio_files:
        print(f"\nProcessing: {audio_file}")
        result = model.transcribe(audio_file)
        results.append({
            "file": audio_file,
            "text": result["text"],
            "language": result["language"]
        })
        print(f"Transcription: {result['text'][:100]}...")

    return results


# ========================================
# Example 6: Custom Model Location
# ========================================
def use_custom_model_location(audio_file):
    """
    Load model from a custom cache location
    """
    import os

    # Specify custom download directory
    custom_cache = os.path.expanduser("~/whisper_models")

    model = whisper.load_model("tiny", download_root=custom_cache)
    result = model.transcribe(audio_file)

    print(f"\n=== MODEL CACHED AT: {custom_cache} ===")
    print(result["text"])

    return result


# ========================================
# Example 7: GPU vs CPU
# ========================================
def check_device():
    """
    Check if CUDA GPU is available and compare performance
    """
    import torch

    print("\n=== DEVICE INFO ===")
    if torch.cuda.is_available():
        print(f"CUDA is available!")
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"CUDA version: {torch.version.cuda}")

        # Load model on GPU
        model_gpu = whisper.load_model("tiny", device="cuda")
        print("Model loaded on GPU")
    else:
        print("CUDA not available, using CPU")
        model_cpu = whisper.load_model("tiny", device="cpu")
        print("Model loaded on CPU")


# ========================================
# Available Models Information
# ========================================
def show_model_info():
    """
    Display information about available Whisper models
    """
    print("\n=== AVAILABLE WHISPER MODELS ===")
    print(f"Models: {whisper.available_models()}")

    model_info = {
        "tiny": "39M params, ~1GB VRAM, ~10x faster, best for quick tests",
        "base": "74M params, ~1GB VRAM, ~7x faster, good for demos",
        "small": "244M params, ~2GB VRAM, ~4x faster, good accuracy",
        "medium": "769M params, ~5GB VRAM, ~2x faster, great for production",
        "large": "1550M params, ~10GB VRAM, 1x speed, best accuracy",
        "turbo": "809M params, ~6GB VRAM, ~8x faster, optimized large-v3"
    }

    print("\nModel Details:")
    for model, info in model_info.items():
        print(f"  {model:10s}: {info}")

    print("\nNote: .en models (tiny.en, base.en, etc.) are English-only and perform better for English")


# ========================================
# Main Demo Runner
# ========================================
if __name__ == "__main__":
    print("=" * 60)
    print("WHISPER USAGE DEMO")
    print("=" * 60)

    # Show model information
    show_model_info()

    # Check device
    check_device()

    print("\n" + "=" * 60)
    print("USAGE EXAMPLES:")
    print("=" * 60)

    # Example usage (uncomment when you have an audio file)
    # audio_file = "path/to/your/audio.mp3"
    #
    # # Example 1: Basic transcription
    # result = basic_transcription(audio_file, model_name="tiny")
    #
    # # Example 2: Language detection
    # result = transcribe_with_language_detection(audio_file)
    #
    # # Example 3: Timestamps
    # result = transcribe_with_timestamps(audio_file)
    #
    # # Example 4: Translation
    # result = translate_to_english(audio_file, model_name="medium")
    #
    # # Example 5: Batch processing
    # files = ["audio1.mp3", "audio2.wav", "audio3.m4a"]
    # results = batch_transcribe(files)

    print("\nTo use these examples:")
    print("1. Ensure ffmpeg is installed (required for audio processing)")
    print("2. Uncomment the example you want to run")
    print("3. Replace 'path/to/your/audio.mp3' with your actual audio file path")
    print("4. Run: py whisper_demo.py")

    print("\n" + "=" * 60)
    print("COMMAND LINE USAGE:")
    print("=" * 60)
    print("\nYou can also use Whisper from the command line:")
    print("  py -m whisper audio.mp3 --model tiny")
    print("  py -m whisper audio.mp3 --model medium --language Japanese")
    print("  py -m whisper audio.mp3 --model medium --task translate")
    print("  py -m whisper audio.mp3 --output_dir ./transcripts --output_format txt")
