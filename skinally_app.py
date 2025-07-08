import sys
from groq import Groq
from typing import List, Dict
import json
import os
from dotenv import load_dotenv
import requests
import shutil
import assemblyai as aai
import subprocess
from jigsawstack import JigsawStack
import ffmpeg

load_dotenv()


def transcribe_all_files(folder_path: str, language: str = "pl", model: str = "whisper-large-v3") -> dict:
    """
    Transcribes all audio files in a specified folder using the Groq SDK.

    :param folder_path: Path to the folder containing audio files.
    :param language: Language code for transcription (default: "pl").
    :param model: Model to use for transcription (default: "whisper-large-v3").
    :return: Dictionary with file names as keys and transcriptions as values.
    """
    # Initialize the Groq SDK client
    groq = Groq(api_key=os.getenv("GROQ_API_KEY"))  # Replace with your Groq API key
    
    # Dictionary to store the transcriptions
    transcriptions = {}

    # Iterate through all files in the folder
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        # Process only if it's a file and has an audio extension
        if os.path.isfile(file_path) and file_name.lower().endswith((".m4a", ".mp3", ".wav", ".flac", ".mkv")):
            print(f"Transcribing with groq file: {file_name}")
            with open(file_path, "rb") as audio_file:
                # Call Groq for transcription
                transcription = groq.audio.transcriptions.create(
                    file=audio_file,  # Pass the file-like object
                    language=language,
                    model=model
                )
                # Store the result in the dictionary
                transcriptions[file_name] = transcription.text

    return transcriptions


def transcribe_one_file_aai(audio_file):
    aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")
    
    config = aai.TranscriptionConfig(
        speaker_labels=True,
        language_code="pl",
        speakers_expected=2
        
    )
    
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file,config)

    for utterance in transcript.utterances:
        print(f"Speaker {utterance.speaker}: {utterance.text}")
    #print (transcript.utterances)
    return transcript


def transcribe_all_files_aai(folder_path: str, language_code: str = "pl", speakers_expected: int = 2) -> dict:
    """
    Transcribes all audio files in a specified folder using AssemblyAI.

    :param folder_path: Path to the folder containing audio files.
    :param language_code: Language code for transcription (default: "pl").
    :param speakers_expected: Number of expected speakers (default: 2).
    :return: Dictionary with file names as keys and transcriptions as values.
    """
    # Set the AssemblyAI API key
    aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")  # Replace with your AssemblyAI API key

    # Transcription configuration
    config = aai.TranscriptionConfig(
        speaker_labels=True,
        language_code=language_code,
        speakers_expected=speakers_expected
    )

    # Create a transcriber instance
    transcriber = aai.Transcriber()

    # Dictionary to store the transcriptions
    transcriptions = {}

    # Iterate through all files in the folder
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)

        # Process only if it's a file and has an audio extension
        if os.path.isfile(file_path) and file_name.lower().endswith((".m4a", ".mp3", ".wav", ".flac", ".mkv", ".ogg")):
            print(f"Transcribing with AssemblyAI file: {file_name}")
            with open(file_path, "rb") as audio_file:
                # Transcribe the audio file
                transcript = transcriber.transcribe(audio_file, config)

                # Combine the speaker-separated utterances into a single transcription string
                full_transcription = "\n".join(
                    f"Speaker {utterance.speaker}: {utterance.text}" for utterance in transcript.utterances
                )

                # Store the transcription in the dictionary
                transcriptions[file_name] = full_transcription

    return transcriptions

def transcribe_all_files_jigsawstack(audio_file):
    jigsawstack = JigsawStack(api_key=os.getenv("JIGSAWSTACK_API_KEY"))

    with open(audio_file, "rb") as audio_file:
        audio_data = audio_file.read()
    
    # Define the upload parameters
    upload_params = {
        "filename": "speaker",
        "overwrite": True,  # Allow overwriting files on the server
    }

    # Upload the file
    result = jigsawstack.store.upload(audio_data, options=upload_params)
    file_key = result["key"]

    # Prepare the parameters for speech_to_text
    speech_to_text_params = {
        "key": file_key  # Include the file key returned by the upload
    }

    # Perform speech-to-text
    speech_result = jigsawstack.audio.speech_to_text(params=speech_to_text_params)

    # Print the transcription result
    print(speech_result)


def convert_video_to_mp3(input_file, output_file):
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", input_file,
        "-vn",
        "-acodec", "libmp3lame",
        "-ab", "192k",
        "-ar", "44100",
        "-y",
        output_file
    ]
    
    try:
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"Successfully converted {input_file} to {output_file}!")
    except subprocess.CalledProcessError as e:
        print(f"Conversion failed for {input_file} with error: {e}")

def process_videos_in_folder(videos_path, audios_path):
    """
    Processes all video files in the specified folder, converting them to MP3.

    :param videos_path: Path to the folder containing video files.
    :param audios_path: Path to the folder where audio files will be saved.
    """
    # Ensure the output directory exists
    os.makedirs(audios_path, exist_ok=True)

    # Iterate through all files in the videos folder
    for filename in os.listdir(videos_path):
        file_path = os.path.join(videos_path, filename)

        # Process only .mkv files
        if os.path.isfile(file_path) and filename.lower().endswith((".mp4", ".mkv")):
            # Get the filename without the extension
            base_name = os.path.splitext(filename)[0]

            # Construct the output file path
            output_file = os.path.join(audios_path, f"audio_{base_name}.mp3")

            # Convert the video to MP3
            convert_video_to_mp3(file_path, output_file)

def save_transcriptions_to_markdown(transcriptions: dict, output_folder: str):
    """
    Saves transcriptions as a Markdown file in the specified folder.

    :param transcriptions: Dictionary with file names as keys and transcriptions as values.
    :param output_folder: Path to the folder where the Markdown file will be saved.
    """
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Create the Markdown file path
    markdown_file = os.path.join(output_folder, "transcriptions6.md")

    # Write the transcriptions to the Markdown file
    with open(markdown_file, "w", encoding="utf-8") as file:
        file.write("# Transcriptions\n\n")
        for file_name, transcription in transcriptions.items():
            file.write(f"## {file_name}\n\n")
            file.write(f"{transcription}\n\n")

    print(f"Transcriptions saved to {markdown_file}")


def save_transcriptions_to_markdown_aai(transcript, output_folder: str):
    """
    Saves transcriptions as a Markdown file in the specified folder.

    :param transcript: Transcript object containing the transcription data.
    :param output_folder: Path to the folder where the Markdown file will be saved.
    """
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Create the Markdown file path
    markdown_file = os.path.join(output_folder, "transcriptions3.md")

    # Write the transcriptions to the Markdown file
    with open(markdown_file, "w", encoding="utf-8") as file:
        file.write("# Transcriptions\n\n")
        for utterance in transcript.utterances:
            file.write(f"## Speaker {utterance.speaker}\n\n")
            file.write(f"{utterance.text}\n\n")

    print(f"Transcriptions saved to {markdown_file}")

# Example usage
if __name__ == "__main__":

    # Paths to the video and audio folders
    videos_path = r"C:\Users\lukas\Desktop\SkinAlly\videos"
    audios_path = r"C:\Users\lukas\Desktop\SkinAlly\audios"
    transcriptions_path = r"C:\Users\lukas\Desktop\SkinAlly\transcriptions"
    audio_path = r"C:\Users\lukas\Desktop\SkinAlly\audios\audio_anna-cut2.ogg"
    
    #process_videos_in_folder(videos_path, audios_path)
    #transcriptions_dict = transcribe_all_files(audios_path)
    #save_transcriptions_to_markdown(transcriptions_dict, transcriptions_path)
    transcript = transcribe_all_files_aai(audios_path)
    save_transcriptions_to_markdown(transcript, transcriptions_path)