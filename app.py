from flask import Flask, render_template, request, jsonify
from googletrans import Translator
from langdetect import detect, LangDetectException
import re
import speech_recognition as sr

app = Flask(__name__)
translator = Translator()
recognizer = sr.Recognizer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    data = request.get_json()
    text_to_translate = data.get('text', '')
    source_lang = data.get('source_lang', 'auto')  # Default to auto-detect
    target_lang = data.get('target_lang', 'en')    # Default target language

    # Auto-detect language using langdetect if source_lang is 'auto'
    if source_lang == 'auto':
        try:
            source_lang = detect(text_to_translate)
        except LangDetectException as e:
            return jsonify({
                'error': 'Language detection failed. Please provide a valid text.'
            }), 400

    try:
        translation = translator.translate(text_to_translate, src=source_lang, dest=target_lang)
        return jsonify({
            'original_text': text_to_translate,
            'translated_text': translation.text,
            'detected_source_lang': source_lang  # Return detected language
        })
    except Exception as e:
        return jsonify({
            'error': f'Translation failed: {str(e)}'
        }), 500

@app.route('/recognize', methods=['POST'])
def recognize():
    file = request.files['audio']
    audio_data = sr.AudioFile(file)
    with audio_data as source:
        audio = recognizer.record(source)
    try:
        recognized_text = recognizer.recognize_google(audio)
        return jsonify({
            'recognized_text': recognized_text
        })
    except sr.UnknownValueError:
        return jsonify({
            'error': 'Speech recognition could not understand the audio'
        }), 400
    except sr.RequestError as e:
        return jsonify({
            'error': f'Speech recognition request failed: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
