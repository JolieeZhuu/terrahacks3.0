import openai
import io
import base64
from typing import Dict, Any, Optional
import os

class OpenAITranslationService:
    def __init__(self, api_key: str):
        """Initialize with OpenAI API key"""
        self.client = openai.OpenAI(api_key=api_key)
    
    def translate_text(self, text: str, source_lang: str = 'auto', target_lang: str = 'English') -> Dict[str, Any]:
        """Translate text using OpenAI GPT"""
        try:
            # Convert language codes to full names for better GPT understanding
            target_language = self._get_language_name(target_lang)
            
            if source_lang == 'auto':
                prompt = f"Translate the following text to {target_language}. If the text is already in {target_language}, just return it as is:\n\n{text}"
            else:
                source_language = self._get_language_name(source_lang)
                prompt = f"Translate the following {source_language} text to {target_language}:\n\n{text}"
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # or "gpt-4" for better quality
                messages=[
                    {"role": "system", "content": "You are a professional translator. Only return the translated text, nothing else."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.1  # Low temperature for consistent translations
            )
            
            translated_text = response.choices[0].message.content.strip()
            
            return {
                'success': True,
                'translated_text': translated_text,
                'source_language': source_lang,
                'target_language': target_lang,
                'model_used': response.model
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Translation failed: {str(e)}'
            }
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect the language of given text using OpenAI"""
        try:
            prompt = f"What language is this text written in? Respond with only the language name and a confidence percentage (0-100):\n\n{text}"
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a language detection expert. Respond in format: 'Language: [language], Confidence: [percentage]%'"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            
            # Parse the response (this is a simple parser, you might want to make it more robust)
            try:
                parts = result.split(', ')
                language = parts[0].split(': ')[1]
                confidence = int(parts[1].split(': ')[1].replace('%', '')) / 100
            except:
                language = result
                confidence = 0.8  # Default confidence
            
            return {
                'success': True,
                'language': language,
                'confidence': confidence
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Language detection failed: {str(e)}'
            }
    
    def text_to_speech(self, text: str, voice: str = 'alloy', speed: float = 1.0) -> Dict[str, Any]:
        """Convert text to speech using OpenAI TTS"""
        try:
            response = self.client.audio.speech.create(
                model="tts-1",  # or "tts-1-hd" for higher quality
                voice=voice,    # alloy, echo, fable, onyx, nova, shimmer
                input=text,
                speed=speed     # 0.25 to 4.0
            )
            
            # Get audio data
            audio_data = response.content
            
            return {
                'success': True,
                'audio_data': audio_data,
                'content_type': 'audio/mp3',
                'voice_used': voice
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Text-to-speech failed: {str(e)}'
            }
    
    def speech_to_text(self, audio_file_path: str) -> Dict[str, Any]:
        """Convert speech to text using OpenAI Whisper (bonus feature!)"""
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            
            return {
                'success': True,
                'transcribed_text': transcript.text
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Speech-to-text failed: {str(e)}'
            }
    
    def get_supported_languages(self) -> Dict[str, Any]:
        """Get list of supported languages (OpenAI supports many languages)"""
        try:
            languages = {
                'af': 'Afrikaans',
                'ar': 'Arabic',
                'bg': 'Bulgarian',
                'bn': 'Bengali',
                'ca': 'Catalan',
                'cs': 'Czech',
                'cy': 'Welsh',
                'da': 'Danish',
                'de': 'German',
                'el': 'Greek',
                'en': 'English',
                'es': 'Spanish',
                'et': 'Estonian',
                'fa': 'Persian',
                'fi': 'Finnish',
                'fr': 'French',
                'gu': 'Gujarati',
                'he': 'Hebrew',
                'hi': 'Hindi',
                'hr': 'Croatian',
                'hu': 'Hungarian',
                'id': 'Indonesian',
                'is': 'Icelandic',
                'it': 'Italian',
                'ja': 'Japanese',
                'kn': 'Kannada',
                'ko': 'Korean',
                'lt': 'Lithuanian',
                'lv': 'Latvian',
                'mk': 'Macedonian',
                'ml': 'Malayalam',
                'mr': 'Marathi',
                'ne': 'Nepali',
                'nl': 'Dutch',
                'no': 'Norwegian',
                'pl': 'Polish',
                'pt': 'Portuguese',
                'ro': 'Romanian',
                'ru': 'Russian',
                'sk': 'Slovak',
                'sl': 'Slovenian',
                'sq': 'Albanian',
                'sr': 'Serbian',
                'sv': 'Swedish',
                'sw': 'Swahili',
                'ta': 'Tamil',
                'te': 'Telugu',
                'th': 'Thai',
                'tl': 'Filipino',
                'tr': 'Turkish',
                'uk': 'Ukrainian',
                'ur': 'Urdu',
                'vi': 'Vietnamese',
                'zh': 'Chinese',
                'zh-cn': 'Chinese (Simplified)',
                'zh-tw': 'Chinese (Traditional)'
            }
            
            return {
                'success': True,
                'languages': languages
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get languages: {str(e)}'
            }
    
    def _get_language_name(self, lang_code: str) -> str:
        """Helper method to convert language codes to full names"""
        language_map = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese',
            'ar': 'Arabic',
            'hi': 'Hindi',
            'th': 'Thai',
            'vi': 'Vietnamese',
            'nl': 'Dutch',
            'sv': 'Swedish',
            'no': 'Norwegian',
            'da': 'Danish',
            'fi': 'Finnish',
            'pl': 'Polish',
            'cs': 'Czech',
            'hu': 'Hungarian',
            'tr': 'Turkish',
            'he': 'Hebrew',
            'fa': 'Persian',
            'ur': 'Urdu',
            'bn': 'Bengali',
            'ta': 'Tamil',
            'te': 'Telugu',
            'ml': 'Malayalam',
            'kn': 'Kannada',
            'gu': 'Gujarati',
            'mr': 'Marathi'
        }
        return language_map.get(lang_code.lower(), lang_code)


# Example usage THIS IS A STUPID EXAMPLE FUCK MY LIFE
# the api key isn't an example though
if __name__ == "__main__":
    # Initialize the service with your OpenAI API key
    service = OpenAITranslationService(api_key=os.environ.get("OPEN_AI_KEY"))
    
    # Example translations
    result = service.translate_text("Hello, how are you?", target_lang="Spanish")
    print(result)
    
    # Language detection
    detection = service.detect_language("Bonjour, comment allez-vous?")
    print(detection)
    
    # Text to speech
    tts_result = service.text_to_speech("Hello, this is a test.", voice="nova")
    if tts_result['success']:
        with open("output.mp3", "wb") as f:
            f.write(tts_result['audio_data'])
        print("Audio saved to output.mp3")