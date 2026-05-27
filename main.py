# import whisper
# import webbrowser
# import pyttsx3
# import sounddevice as sd
# import numpy as np

# model = whisper.load_model("base")
# engine = pyttsx3.init()


# def speak(text):
#     engine.say(text)
#     engine.runAndWait()


# def listen(duration=5, samplerate=16000):
#     print("Listening...")
#     audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float32')
#     sd.wait()
#     audio = np.squeeze(audio)

#     try:
#         result = model.transcribe(audio, fp16=False)
#         command = result.get("text", "").lower().strip()
#     except Exception as e:
#         print(f"Transcription error: {e}")
#         command = ""

#     print("You said:", command)
#     return command


# def process_command(command):
#     if not command:
#         speak("I did not catch that. Please try again.")
#         return

#     if "open google" in command:
#         speak("Opening Google.")
#         webbrowser.open("https://www.google.com")
#     elif "what is your name" in command or "who are you" in command:
#         speak("I am oscar.")
#     elif "exit" in command or "quit" in command or "stop" in command:
#         speak("Shutting down.")
#         raise KeyboardInterrupt
#     else:
#         speak("Command received.")


# if __name__ == "__main__":
#     speak("Initializing oscar.")

#     try:
#         while True:
#             print("recognizing...")
#             command = listen()
#             if command:
#                 if "oscar" in command:
#                     speak("Yes?")
#                     process_command(command)
#                 else:
#                     print("Wake word not detected. Say 'oscar' first.")
#             else:
#                 print("No command detected.")
#     except KeyboardInterrupt:
#         print("Exiting.")
#         speak("Goodbye.")

import speech_recognition as sr
import webbrowser
import pyttsx3
import musicLibrary
import requests
from google import genai
from gtts import gTTS
import pyperclip
import pygame
import os
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi

# 1. Load the hidden variables from your .env file
load_dotenv()
my_google_api_key = os.getenv("GOOGLE_API_KEY")

recognizer = sr.Recognizer()
engine = pyttsx3.init() 

def speak_old(text):
    engine.say(text)
    engine.runAndWait()

def speak(text):
    tts = gTTS(text)
    tts.save('temp.mp3') 

    # Initialize Pygame mixer
    pygame.mixer.init()

    # Load the MP3 file
    pygame.mixer.music.load('temp.mp3')

    # Play the MP3 file
    pygame.mixer.music.play()

    # Keep the program running until the music stops playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    pygame.mixer.music.unload()
    os.remove("temp.mp3") 

def aiProcess(command):
    # Safely load the Google GenAI client using the environment variable
    client = genai.Client(api_key=my_google_api_key)
    
    try:
        # Generate content using the fast, free gemini-2.5-flash model
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=command,
            # Pass the system instructions to keep oscar acting like a short-spoken assistant
            config=genai.types.GenerateContentConfig(
                system_instruction="You are a virtual assistant named oscar skilled in general tasks like Alexa and Google Cloud. Give short responses please"
            )
        )
        return response.text
    except Exception as e:
        print(f"AI Error: {e}")
        return "Sorry, I had trouble processing that."

def summarize_youtube_video(video_id):
    try:
        speak("Give me a moment to analyze the video data...")
        
        # Fetch the transcript from YouTube
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        
        # Combine all the little caption pieces into one massive paragraph
        transcript_text = " ".join([t['text'] for t in transcript_list])
        
        # Create a smart prompt to send to your existing AI function
        prompt = f"Please read this video transcript and provide a short, concise research summary of the main points: {transcript_text}"
        
        # Let your existing aiProcess handle the Gemini request!
        summary = aiProcess(prompt)
        
        print(f"Oscar's Summary: {summary}")
        speak("Here is the summary.")
        speak(summary)
        
    except Exception as e:
        print(f"Transcript Error: {e}")
        speak("I am sorry, I couldn't extract the transcript for that video. It might not have closed captions.")

def processCommand(c):
    if "open google" in c.lower():
        webbrowser.open("https://google.com")
    elif "open facebook" in c.lower():
        webbrowser.open("https://facebook.com")
    elif "open youtube" in c.lower():
        webbrowser.open("https://youtube.com")
    elif "open linkedin" in c.lower():
        webbrowser.open("https://linkedin.com")
    elif c.lower().startswith("play"):
        song = c.lower().split(" ")[1]
        link = musicLibrary.music[song]
        webbrowser.open(link)

    elif "news" in c.lower():
        news_api_key = os.getenv("NEWS_API_KEY")
        url = f"https://api.worldnewsapi.com/search-news?api-key={news_api_key}&source-country=in&language=en"
        
        try:
            r = requests.get(url)
            if r.status_code == 200:
                data = r.json()
                articles = data.get('news', [])
                
                # Read out the top 3 headlines
                if articles:
                    for article in articles[:3]:
                        speak(article['title'])
                else:
                    speak("I couldn't find any news articles right now.")
            else:
                print(f"Error fetching news. Status code: {r.status_code}")
                speak("Sorry, I am having trouble accessing the news service.")
        except Exception as e:
            print(f"Request Error: {e}")
            speak("Sorry, I could not connect to the internet.")

    # We check if variations of "summarize" AND the word "video" are anywhere in the command
    # elif ("summarize" in c.lower() or "summarise" in c.lower() or "summary" in c.lower()) and "video" in c.lower():
    #     speak("Checking your clipboard for a YouTube link...")
    #     try:
    #         # 1. Grab the text you copied to your clipboard
    #         clipboard_text = pyperclip.paste()
            
    #         # 2. Check if it's a YouTube link and extract the 11-character ID
    #         if "youtube.com/watch?v=" in clipboard_text:
    #             video_id = clipboard_text.split("v=")[1][:11]
    #         elif "youtu.be/" in clipboard_text:
    #             video_id = clipboard_text.split("youtu.be/")[1][:11]
    #         else:
    #             speak("I couldn't find a valid YouTube link in your clipboard. Please copy a link and try again.")
    #             return # Stop running if there is no valid link
                
    #         # 3. Send the extracted ID to your summarizer function!
    #         summarize_youtube_video(video_id)
            
    #     except Exception as e:
    #         print(f"Clipboard Error: {e}")
    #         speak("Sorry, I had trouble reading your clipboard.")

    else:
        # Let gemini handle the request
        output = aiProcess(c)
        speak(output) 

if __name__ == "__main__":
    speak("Initializing oscar....")
    while True:
        r = sr.Recognizer()
        print("recognizing...")
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = r.listen(source, timeout=5, phrase_time_limit=3)
            word = r.recognize_google(audio)
            
            if word.lower() == "oscar":
                speak("ya")
                
                # Listen for command
                with sr.Microphone() as source:
                    print("oscar Active...")
                    audio = r.listen(source)
                    command = r.recognize_google(audio)
                    processCommand(command)

        except Exception as e:
            print("Error; {0}".format(e))





