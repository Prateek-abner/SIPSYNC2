# language_support.py

import os
from googletrans import Translator
from langdetect import detect
import pycountry

# Initialize translator
translator = Translator()

# Supported languages with their codes
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'fr': 'French',
    'es': 'Spanish',
    'zh': 'Chinese',
    'hi': 'Hindi',
    'ar': 'Arabic',
    'bn': 'Bengali',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ja': 'Japanese'
}

def detect_language(text):
    """
    Detect the language of input text.
    """
    try:
        lang_code = detect(text)
        language = pycountry.languages.get(alpha_2=lang_code)
        return lang_code, language.name if language else SUPPORTED_LANGUAGES.get(lang_code, 'Unknown')
    except:
        return 'en', 'English'

def translate_text(text, target_lang='en'):
    """
    Translate text to target language.
    """
    try:
        if target_lang not in SUPPORTED_LANGUAGES:
            target_lang = 'en'
        translation = translator.translate(text, dest=target_lang)
        return translation.text
    except:
        return text

def translate_recommendation(recommendation, target_lang='en'):
    """
    Translate a recommendation dictionary to target language.
    """
    if target_lang == 'en':
        return recommendation

    translated = recommendation.copy()
    try:
        # Translate main fields
        fields_to_translate = [
            'drink', 'light_food', 'brewing_tip', 'personalized_message',
            'cultural_origin', 'scientific_evidence'
        ]
        
        for field in fields_to_translate:
            if field in translated:
                translated[field] = translate_text(translated[field], target_lang)
        
        # Translate lists
        list_fields = ['benefits', 'ingredients', 'eco_friendly_tips']
        for field in list_fields:
            if field in translated:
                translated[field] = [
                    translate_text(item, target_lang) 
                    for item in translated[field]
                ]
        
        return translated
    except:
        return recommendation

def get_language_name(lang_code):
    """
    Get the full name of a language from its code.
    """
    return SUPPORTED_LANGUAGES.get(lang_code, 'Unknown') 