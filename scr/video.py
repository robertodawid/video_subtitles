# %%
#import whisper
from openai import OpenAi
from moviepy import *
import math


# %%
# Step 1: Extract audio from the video
def extract_audio(video_path, output_audio_path):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(output_audio_path)
    print(f"Audio extracted to {output_audio_path}")

# %%
# Step 2: Split audio into chunks (60 seconds by default)
def split_audio(audio_path, chunk_duration_ms=60000):  # 60 seconds per chunk
    audio = AudioSegment.from_wav(audio_path)
    num_chunks = math.ceil(len(audio) / chunk_duration_ms)

    chunks = []
    for i in range(num_chunks):
        start_ms = i * chunk_duration_ms
        end_ms = min((i + 1) * chunk_duration_ms, len(audio))
        chunk = audio[start_ms:end_ms]
        chunk_path = f"chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)

    return chunks

# %%
def transcribe_audio(audio_path):
    # Initialize recognizer
    recognizer = sr.Recognizer()

    # Load the audio file
    with sr.AudioFile(audio_path) as audio_file:
        # Listen to the audio file
        audio_data = recognizer.record(audio_file)
        
        # Use the recognizer to transcribe the audio
        try:
            transcription = recognizer.recognize_sphinx(audio_data)
            print("Transcription complete:")
            return transcription
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand the audio.")
            return ""
        except sr.RequestError as e:
            print(f"Sphinx request failed; {e}")
            return ""


# %%
# Step 4: Generate SRT subtitles (for each chunk)
def generate_srt(transcriptions, output_srt_path):
    with open(output_srt_path, "w") as srt_file:
        start_time = 0  # Start timestamp for the first chunk
        for i, transcription in enumerate(transcriptions):
            end_time = start_time + 60  # Assuming each chunk is 60 seconds long (adjust as needed)

            # Format timestamps for SRT
            start_time_srt = format_timestamp(start_time)
            end_time_srt = format_timestamp(end_time)

            # Write to SRT file
            srt_file.write(f"{i + 1}\n")
            srt_file.write(f"{start_time_srt} --> {end_time_srt}\n")
            srt_file.write(f"{transcription}\n\n")

            start_time = end_time  # Update start time for the next chunk

    print(f"Subtitles saved to {output_srt_path}")

# %%
# Helper: Format timestamp in SRT format
def format_timestamp(seconds):
    ms = int((seconds - int(seconds)) * 1000)
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{ms:03}"


# %%
# Main Workflow
video_path = "Video/video1704472434.mp4"
audio_path = "Video/extracted_audio.wav"
srt_path = "Video/output_subtitles.srt"

# %%
extract_audio(video_path, output_audio_path)

# %%
audio_chunks = split_audio(audio_path)

# %%
# Transcribe each audio chunk using Sphinx
transcriptions = []
for chunk in audio_chunks:
    transcription = transcribe_audio(chunk)
    if transcription:
        transcriptions.append(transcription)

# %%
generate_srt(transcriptions, srt_path)

