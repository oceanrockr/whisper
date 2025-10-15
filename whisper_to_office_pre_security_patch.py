"""
Whisper to Office - Transcribe audio and format for Microsoft Office

This script transcribes audio files and creates formatted output
suitable for Word documents or PowerPoint slides.
"""

import whisper
import argparse
from datetime import datetime
import os


def transcribe_for_word(audio_file, model_name="base", output_file=None):
    """
    Transcribe audio and format as a Word-ready document

    Args:
        audio_file: Path to audio file
        model_name: Whisper model to use
        output_file: Output file path (optional)
    """
    print(f"Loading {model_name} model...")
    model = whisper.load_model(model_name)

    print(f"Transcribing {audio_file}...")
    result = model.transcribe(audio_file)

    # Generate output filename if not provided
    if output_file is None:
        base_name = os.path.splitext(os.path.basename(audio_file))[0]
        output_file = f"{base_name}_transcript.txt"

    # Format the transcript
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("AUDIO TRANSCRIPTION\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Source File: {audio_file}\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Language: {result['language']}\n")
        f.write(f"Model Used: {model_name}\n")
        f.write("\n" + "=" * 70 + "\n\n")

        # Full transcript
        f.write("FULL TRANSCRIPT\n")
        f.write("-" * 70 + "\n\n")
        f.write(result["text"].strip() + "\n\n")

        # Segmented transcript with timestamps
        f.write("\n" + "=" * 70 + "\n\n")
        f.write("TRANSCRIPT WITH TIMESTAMPS\n")
        f.write("-" * 70 + "\n\n")

        for segment in result["segments"]:
            start_time = format_timestamp(segment["start"])
            end_time = format_timestamp(segment["end"])
            text = segment["text"].strip()
            f.write(f"[{start_time} - {end_time}]\n{text}\n\n")

    print(f"\n✓ Transcript saved to: {output_file}")
    print(f"✓ You can now open this file and copy the content to Word")

    return output_file


def transcribe_for_powerpoint(audio_file, model_name="base", output_file=None):
    """
    Transcribe audio and format as PowerPoint speaker notes
    Creates one slide worth of content per segment
    """
    print(f"Loading {model_name} model...")
    model = whisper.load_model(model_name)

    print(f"Transcribing {audio_file}...")
    result = model.transcribe(audio_file)

    # Generate output filename if not provided
    if output_file is None:
        base_name = os.path.splitext(os.path.basename(audio_file))[0]
        output_file = f"{base_name}_powerpoint_notes.txt"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("POWERPOINT SPEAKER NOTES\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Source: {audio_file}\n")
        f.write(f"Language: {result['language']}\n\n")
        f.write("Instructions: Copy each section below as speaker notes\n")
        f.write("for individual PowerPoint slides.\n")
        f.write("\n" + "=" * 70 + "\n\n")

        # Break into slides (every ~30 seconds or logical segment)
        slide_num = 1
        for segment in result["segments"]:
            start_time = format_timestamp(segment["start"])
            text = segment["text"].strip()

            f.write(f"SLIDE {slide_num}\n")
            f.write(f"Time: {start_time}\n")
            f.write("-" * 70 + "\n")
            f.write(f"{text}\n")
            f.write("\n" + "=" * 70 + "\n\n")

            slide_num += 1

    print(f"\n✓ PowerPoint notes saved to: {output_file}")
    print(f"✓ Copy each section as speaker notes for your slides")

    return output_file


def transcribe_meeting_minutes(audio_file, model_name="base", output_file=None):
    """
    Transcribe and format as meeting minutes
    """
    print(f"Loading {model_name} model...")
    model = whisper.load_model(model_name)

    print(f"Transcribing {audio_file}...")
    result = model.transcribe(audio_file)

    if output_file is None:
        base_name = os.path.splitext(os.path.basename(audio_file))[0]
        output_file = f"{base_name}_meeting_minutes.txt"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("MEETING MINUTES\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write(f"Time: {datetime.now().strftime('%H:%M')}\n")
        f.write(f"Duration: {format_timestamp(result['segments'][-1]['end'])}\n")
        f.write(f"Recording: {audio_file}\n\n")

        f.write("ATTENDEES:\n")
        f.write("- [Add attendee names here]\n\n")

        f.write("AGENDA:\n")
        f.write("- [Add agenda items here]\n\n")

        f.write("DISCUSSION:\n")
        f.write("-" * 70 + "\n\n")
        f.write(result["text"].strip() + "\n\n")

        f.write("\nDETAILED NOTES WITH TIMESTAMPS:\n")
        f.write("-" * 70 + "\n\n")

        for segment in result["segments"]:
            timestamp = format_timestamp(segment["start"])
            text = segment["text"].strip()
            f.write(f"[{timestamp}] {text}\n\n")

        f.write("\nACTION ITEMS:\n")
        f.write("- [Review transcript and add action items here]\n\n")

        f.write("NEXT MEETING:\n")
        f.write("- Date: [TBD]\n")
        f.write("- Time: [TBD]\n")

    print(f"\n✓ Meeting minutes saved to: {output_file}")

    return output_file


def format_timestamp(seconds):
    """Convert seconds to MM:SS or HH:MM:SS format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe audio for Microsoft Office applications"
    )
    parser.add_argument("audio_file", help="Path to audio file")
    parser.add_argument(
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large", "turbo"],
        help="Whisper model to use (default: base)"
    )
    parser.add_argument(
        "--format",
        default="word",
        choices=["word", "powerpoint", "meeting"],
        help="Output format (default: word)"
    )
    parser.add_argument(
        "--output",
        help="Output file path (optional)"
    )

    args = parser.parse_args()

    # Check if file exists
    if not os.path.exists(args.audio_file):
        print(f"Error: File not found: {args.audio_file}")
        return

    # Transcribe based on format
    if args.format == "word":
        transcribe_for_word(args.audio_file, args.model, args.output)
    elif args.format == "powerpoint":
        transcribe_for_powerpoint(args.audio_file, args.model, args.output)
    elif args.format == "meeting":
        transcribe_meeting_minutes(args.audio_file, args.model, args.output)


if __name__ == "__main__":
    print("=" * 70)
    print("WHISPER TO OFFICE - Audio Transcription Tool")
    print("=" * 70)
    print()

    # Check if running with arguments
    import sys
    if len(sys.argv) == 1:
        print("Usage examples:")
        print()
        print("  For Word document:")
        print("    py whisper_to_office.py recording.mp3 --format word")
        print()
        print("  For PowerPoint speaker notes:")
        print("    py whisper_to_office.py presentation.mp3 --format powerpoint")
        print()
        print("  For meeting minutes:")
        print("    py whisper_to_office.py meeting.mp3 --format meeting")
        print()
        print("  With custom model:")
        print("    py whisper_to_office.py audio.mp3 --model medium --format word")
        print()
        print("Available models: tiny, base, small, medium, large, turbo")
        print("  - tiny/base: Fast, good for quick drafts")
        print("  - small/medium: Balanced speed and accuracy")
        print("  - large/turbo: Best accuracy, slower")
        print()
    else:
        main()
