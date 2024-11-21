from flask import Flask, request, jsonify
import os
from yt_dlp import YoutubeDL
import whisper
import torch
import subprocess


from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

device = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("base").to(device)  

def download_audio_from_youtube(url, output_path='.'):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',  
            'preferredquality': '192',
        }],
        'ffmpeg_location': 'C:/ffmpeg/bin'
    }

    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_title = info_dict.get('title', None)
        ydl.download([url])
        
    return os.path.join(output_path, f"{video_title}.wav")

def convert_audio_for_transcription(input_filename):
    output_filename = os.path.join(os.path.dirname(input_filename), "temp_converted.wav")
    try:
        subprocess.run([
            'ffmpeg', '-i', input_filename, '-ar', '16000', '-ac', '1', output_filename
        ], check=True)
        return output_filename
    except subprocess.CalledProcessError as e:
        print(f"Error converting audio: {e}")
        return None

def transcribe_audio_file(audio_filename):
    temp_filename = convert_audio_for_transcription(audio_filename)
    if temp_filename:
        try:
            result = model.transcribe(temp_filename, fp16=torch.cuda.is_available())
            os.remove(temp_filename)
            return result['text']
        except Exception as e:
            print(f"Error transcribing audio file {audio_filename}: {e}")
            os.remove(temp_filename)
            return "[Error processing the audio file]"
    else:
        return "[Conversion failed, no transcription performed]"

@app.route('/transcribe', methods=['POST'])
def transcribe():
    data = request.json
    url = data.get("url")
    
    if not url:
        return jsonify({"error": "URL not provided"}), 400
    
    audio_file = download_audio_from_youtube(url)
    transcript = transcribe_audio_file(audio_file)
    
    # Clean up downloaded audio file
    os.remove(audio_file)
    
    return jsonify({"transcript": transcript})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
