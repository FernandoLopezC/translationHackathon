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
        tts.save("app/static/audios/output.mp3")
    elif lang == 'zh':
        tts.save("app/static/audios/zh_output.mp3")

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "D:\\Downloads\\flask-testing-py-12ad7ebbee53 1.json"

def text_to_speech_responses(text, lang='en'):
    # Convert text to speech using gTTS
    tts = gTTS(text=text[0], lang=lang, slow=False)

    if lang == 'en':
        tts.save("app/static/audios/response1.mp3")
    elif lang == 'zh':
        tts.save("app/static/audios/zh_response1.mp3")

    tts = gTTS(text=text[1], lang=lang, slow=False)

    if lang == 'en':
        tts.save("app/static/audios/response2.mp3")
    elif lang == 'zh':
        tts.save("app/static/audios/zh_response2.mp3")



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

def get_suggested_responses_and_descriptions(slang_word_or_phrase):
    results = []

    phrase_or_word = "phrase" if ' ' in slang_word_or_phrase else "word"

    prompt = f"Suggest 1 response in slang for the '{phrase_or_word}' '{slang_word_or_phrase}'"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use "gpt-3.5-turbo" or the model you're interested in
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=100,
        temperature=0.
    )

    results.append(response.choices[0]['message']['content'].strip())

    prompt = f"give me a brief description of the {phrase_or_word} '{results[0]}'"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use "gpt-3.5-turbo" or the model you're interested in
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=100,
        temperature=0.
    )

    results.append(response.choices[0]['message']['content'].strip())

    prompt = f"suggest me another response in slang for the {phrase_or_word} '{slang_word_or_phrase}' other than '{results[0]}'"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use "gpt-3.5-turbo" or the model you're interested in
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=100,
        temperature=0.
    )

    results.append(response.choices[0]['message']['content'].strip())

    prompt = f"give me a brief description of the {phrase_or_word} '{results[2]}'"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Use "gpt-3.5-turbo" or the model you're interested in
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=100,
        temperature=0.
    )

    results.append(response.choices[0]['message']['content'].strip())

    return results

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
    suggested_responses = None

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

        # Determines whether input text is a single word or a phrase. Emotional context is analyzed if it's a phrase.
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

        # Response 1 
        suggested_responses = get_suggested_responses_and_descriptions(text_to_translate)
        text_to_speech_responses([suggested_responses[0], suggested_responses[2]])

        response1_translation = translate_client.translate(suggested_responses[0], target_language=target_language)
        response1_desc_translation = translate_client.translate(suggested_responses[1], target_language=target_language)

        response1_translated_text = html.unescape(response1_translation['translatedText'])
        response1_desc_translated_text = html.unescape(response1_desc_translation['translatedText'])


        response2_translation = translate_client.translate(suggested_responses[2], target_language=target_language)
        response2_desc_translation = translate_client.translate(suggested_responses[3], target_language=target_language)

        response2_translated_text = html.unescape(response2_translation['translatedText'])
        response2_desc_translated_text = html.unescape(response2_desc_translation['translatedText'])

        text_to_speech_responses([response1_translated_text, response2_translated_text], lang=target_language)

        suggested_responses.append(response1_translated_text)
        suggested_responses.append(response1_desc_translated_text)

        suggested_responses.append(response2_translated_text)
        suggested_responses.append(response2_desc_translated_text)

    return render_template('index.html', translated_text=translated_text,
                           source_language=source_language, text_to_translate=text_to_translate,
                           target_language=target_language, speech_text=speech_text, suggested_responses=suggested_responses)