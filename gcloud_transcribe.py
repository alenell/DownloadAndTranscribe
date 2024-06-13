from moviepy.editor import VideoFileClip
import soundfile as sf
import numpy as np
import base64
import requests
import json
import os
import tempfile

def extract_and_convert_audio(video_path, audio_path):
    # Extract audio from video
    video = VideoFileClip(video_path)
    video.audio.write_audiofile("temp_audio.wav")

    # Read the extracted audio file
    data, sample_rate = sf.read("temp_audio.wav")
    
    # If the audio is stereo, convert it to mono
    if len(data.shape) == 2:
        data = np.mean(data, axis=1)
    
    # Save the mono audio
    sf.write(audio_path, data, sample_rate)
    return sample_rate

def transcribe_chunk(api_key, audio_chunk_path, sample_rate):
    url = f"https://speech.googleapis.com/v1/speech:recognize?key={api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    with open(audio_chunk_path, 'rb') as audio_file:
        audio_content = base64.b64encode(audio_file.read()).decode('utf-8')
    
    request_data = {
        "config": {
            "encoding": "LINEAR16",
            "sampleRateHertz": sample_rate,
            "languageCode": "en-US"
        },
        "audio": {
            "content": audio_content
        }
    }
    
    response = requests.post(url, headers=headers, json=request_data)
    result = response.json()
    
    if 'results' in result:
        return result['results'][0]['alternatives'][0]['transcript']
    else:
        print("Error in chunk transcription:", result)
        return ""

def transcribe_audio_google(api_key, audio_path, output_path, chunk_duration_ms=20000):  # 20 second chunks
    data, sample_rate = sf.read(audio_path)
    num_samples_per_chunk = int(sample_rate * chunk_duration_ms / 1000)
    
    transcriptions = []
    for start_idx in range(0, len(data), num_samples_per_chunk):
        chunk = data[start_idx:start_idx + num_samples_per_chunk]
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio_file:
            sf.write(temp_audio_file.name, chunk, sample_rate)
            temp_audio_file.close()  # Ensure the file is closed before processing

            transcription = transcribe_chunk(api_key, temp_audio_file.name, sample_rate)
            transcriptions.append(transcription)
            
            os.unlink(temp_audio_file.name)  # Delete the temporary file

    full_transcription = " ".join(transcriptions)
    
    with open(output_path, 'w') as output_file:
        output_file.write(full_transcription)
    
    print("Transcription saved to:", output_path)

# Example usage
#PATH TO VIDEO DOWNLOADED FROM YOUTUBE_DL
video_path = ''
audio_path = 'audio_mono.wav'
output_path = 'transcription.txt'
api_key = ""

sample_rate = extract_and_convert_audio(video_path, audio_path)
transcribe_audio_google(api_key, audio_path, output_path)
