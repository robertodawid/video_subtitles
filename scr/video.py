# %%
#import whisper
import openai
from openai import OpenAI
from moviepy import *
import math
from pathlib import Path
import time

# %%
# Global variable to track API calls and enforce rate limits
api_call_counter = 0
start_time = time.time()

# %%
""" Reading key from openai"""
with open("././openai_key.txt", "r") as file:
    key = file.read()

# %%
openai.api_key = key
client = OpenAI(api_key = key)

# %%
""" Step 1: Extract audio from the video """
def extract_audio(video_path, output_audio_path):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(output_audio_path)
    print(f"Audio extracted to {output_audio_path}")

# %%
""" Step 2: Split audio into chunks (60 seconds by default) """
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
""" Step 3: Transcribe_audio"""
def transcribe_audio(audio_path):
    global api_call_counter, start_time

    # Rate-limiting logic: Enforce 3 requests per minute
    if api_call_counter >= 3:
        elapsed_time = time.time() - start_time
        if elapsed_time < 60:  # Less than a minute has passed
            time_to_wait = 60 - elapsed_time
            print(f"Rate limit reached. Waiting for {time_to_wait:.2f} seconds...")
            time.sleep(time_to_wait)

        # Reset counter and timer after 1 minute
        api_call_counter = 0
        start_time = time.time()
    try:
        with open(audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
            model = "whisper-1", 
            file = audio_file)
        api_call_counter += 1 #increment the counter after a call
        return transcription
    except Exception as e:
        print(f"Error: {e}")
        return None
        
# %%
""" Step 4: Generate SRT subtitles (for each chunk) """
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
#extract_audio(video_path, output_audio_path)

# %%
#audio_chunks = split_audio(audio_path)

# %%
# Transcribe each audio chunk 
transcriptions = []
for i in range(40,45):
    path = Path(f"././chunks/chunk_{i}.wav")
    transcription = transcribe_audio(path)
    if transcription:
        transcriptions.append(transcription)

# %%
generate_srt(transcriptions, srt_path)


