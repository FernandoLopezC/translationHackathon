from app import app
from flask import render_template, request, flash
from google.cloud import translate_v2 as translate
import os
import openai
import html
import speech_recognition as sr

from gtts import gTTS
import io
import pygame


def speech_to_text():
    # Initialize recognizer
    recognizer = sr.Recognizer()

    # Use microphone for input
    with sr.Microphone() as source:
        print("Adjusting for ambient noise, please wait...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Listening for your speech...")

        # Capture the audio from microphone
        audio = recognizer.listen(source)
        text = None

        try:
            # Use Google Web Speech API for recognition (can replace with other APIs)
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand the audio.")
        except sr.RequestError:
            print("Sorry, there's an issue with the API request.")
        if text:
            return text
        else:
            return "Sorry, I couldn't understand the audio."


def text_to_speech(text, lang='en'):
    # Convert text to speech using gTTS
    tts = gTTS(text=text, lang=lang, slow=False)
    if lang == 'en':
        tts.save("static/output.mp3")
    elif lang == 'zh':
        tts.save("static/zh_output.mp3")

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "C:/Users/Fernando/Downloads/flask-testing-py-12ad7ebbee53.json"



def get_slang_definition(slang_word):

    prompt = f"Define the slang word '{slang_word}' and provide a description."

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use "gpt-3.5-turbo" or the model you're interested in
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=100,
        temperature=0.
    )

    return response.choices[0].message['content'].strip()


def get_emotional_context(expression):
    prompt = f"Analyze the English phrase '{expression}' and explain the emotional or implied meaning in this context. For example, if someone says 'don't be wet,' it may mean 'grow up' or 'don't be soft,' not actually being wet."

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use "gpt-3.5-turbo" or the model you're interested in
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=100,
        temperature=0.
    )

    return response.choices[0]['message']['content'].strip()

# Initialize the Google Cloud Translation API client
translate_client = translate.Client("")

@app.route('/', methods=['GET', 'POST'])
def index():
    translated_text = None
    source_language = None
    target_language = 'zh'  # Default target language (can be changed by user)
    text_to_translate = None
    audio_fp = None
    speech_text = None

    if request.method == 'POST':
        if 'speech' in request.form:
            # Handle speech recognition
            speech_text = speech_to_text()
            text_to_translate = speech_text
            if text_to_translate == "Sorry, I couldn't understand the audio.":
                flash("Sorry, I couldn't understand the audio.")
                return render_template('index.html')
        else:
            # Handle regular text input
            text_to_translate = request.form['text']
            target_language = request.form['target_language']

        if ' ' in text_to_translate:
            text_to_translate = text_to_translate + ' - ' + get_emotional_context(text_to_translate)
        else:
            text_to_translate = text_to_translate + ' - ' + get_slang_definition(text_to_translate)

        # Step 1: Translate the text using Google Cloud Translate
        translation = translate_client.translate(text_to_translate, target_language=target_language)
        translated_text = html.unescape(translation['translatedText'])
        source_language = translation['detectedSourceLanguage']

        # Step 3: Convert the translation to speech using gTTS
        text_to_speech(translated_text, lang=target_language)
        text_to_speech(text_to_translate)

    return render_template('index.html', translated_text=translated_text,
                           source_language=source_language, text_to_translate=text_to_translate,
                           target_language=target_language, speech_text=speech_text)