import speech_recognition as sr
import pandas as pd
import requests
import os
import pygame
import time
from fuzzywuzzy import fuzz, process

# Load Dataset
DATASET_PATH = r"C:\Users\sivakarthikeyan\Documents\AI tutor.csv"
df = pd.read_csv(DATASET_PATH)
df["question"] = df["question"].str.lower()  # Normalize text for case-insensitive matching

# Initialize Speech Recognizer
recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = True  # Enable adaptive noise filtering

# Ensure 'temp' directory exists for audio storage
audio_dir = os.path.join(os.getcwd(), "temp")
os.makedirs(audio_dir, exist_ok=True)

# ElevenLabs API Configuration
ELEVENLABS_API_KEY = "sk_528c9535d1b2b040236e8a2c498da0e808a31fc60e75fcb5"  # Replace with your actual API key
VOICE_ID = "estqUGMf1aT87bdaym6N"  # Change to your preferred ElevenLabs voice

def speak(text):
    """Use ElevenLabs API for high-quality text-to-speech output and play audio directly in the terminal using pygame."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {
        "text": text,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8
        }
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 200:
        audio_path = os.path.join(audio_dir, f"output_{int(time.time())}.mp3")  # Unique filename
        
        with open(audio_path, "wb") as f:
            f.write(response.content)
        
        # Reinitialize pygame mixer before each playback
        pygame.mixer.init()
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)  # Wait for the audio to finish playing
        
        pygame.mixer.quit()  # Ensure mixer is reset for the next usage
    else:
        print("Error in generating speech:", response.json())

def listen():
    """Capture speech, remove unnecessary pauses, and improve recognition accuracy."""
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Faster adjustment
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=7)  # Shorter timeout
            return recognizer.recognize_google(audio).lower()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            print("Check your internet connection.")
            return ""
        except sr.WaitTimeoutError:
            print("No speech detected. Try again.")
            return ""

def get_best_answer(question):
    """Find the most relevant answer quickly using fuzzy matching."""
    best_match = process.extractOne(question, df["question"], scorer=fuzz.token_set_ratio)
    
    if best_match and best_match[1] >= 70:  # If confidence score is 70% or above
        return df.loc[df["question"] == best_match[0], "answer"].values[0]
    
    return "I'm sorry, but I don't have an answer for that."  # Default response

# AI Tutor Conversation Loop
if __name__ == "__main__":
    speak("Hello! I'm your AI tutor. What would you like to know today?")
    while True:
        user_input = listen()
        if "bye" in user_input:
            speak("Goodbye! Have a fantastic day ahead!")
            break
        elif user_input:
            response = get_best_answer(user_input)
            print(f"AI Tutor: {response}")
            speak(response)
