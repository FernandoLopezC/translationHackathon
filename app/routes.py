from app import app
from flask import render_template, request
from google.cloud import translate_v2 as translate

# Initialize the Google Cloud Translation API client
translate_client = translate.Client("")

@app.route('/', methods=['GET', 'POST'])
def index():
    translated_text = None
    source_language = None
    target_language = None
    if request.method == 'POST':
        text_to_translate = request.form['text']
        target_language = request.form['target_language']
        # Detect language and translate
        translation = translate_client.translate(text_to_translate, target_language=target_language)
        translated_text = translation['translatedText']
        source_language = translation['detectedSourceLanguage']

    return render_template('index.html', translated_text=translated_text,
                           source_language=source_language, target_language=target_language)
