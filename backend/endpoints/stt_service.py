import speech_recognition as sr
import whisper
import tempfile
import os
from pydub import AudioSegment
import io

class SpeechToTextService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.whisper_model = None
        
    def load_whisper_model(self, model_size="base"):
        """Load Whisper model (run once at startup)"""
        try:
            self.whisper_model = whisper.load_model(model_size)
            return True
        except Exception as e:
            print(f"Failed to load Whisper model: {e}")
            return False
    
    def transcribe_with_google(self, audio_file):
        """Transcribe using Google Speech Recognition (free, requires internet)"""
        try:
            # Convert audio file to proper format
            audio_data = self._prepare_audio_for_sr(audio_file)
            
            with sr.AudioFile(audio_data) as source:
                audio = self.recognizer.record(source)
            
            # Recognize speech using Google
            text = self.recognizer.recognize_google(audio)
            return {
                'success': True,
                'transcription': text,
                'confidence': 1.0,  # Google doesn't provide confidence
                'method': 'google'
            }
            
        except sr.UnknownValueError:
            return {
                'success': False,
                'error': 'Could not understand audio',
                'method': 'google'
            }
        except sr.RequestError as e:
            return {
                'success': False,
                'error': f'Google Speech Recognition error: {e}',
                'method': 'google'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Transcription failed: {e}',
                'method': 'google'
            }
    
    def transcribe_with_whisper(self, audio_file):
        """Transcribe using OpenAI Whisper (offline, more accurate)"""
        if not self.whisper_model:
            if not self.load_whisper_model():
                return {
                    'success': False,
                    'error': 'Whisper model not loaded',
                    'method': 'whisper'
                }
        
        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
                # Convert to format Whisper can handle
                audio_segment = self._convert_to_wav(audio_file)
                audio_segment.export(tmp_file.name, format='wav')
                
                # Transcribe with Whisper
                result = self.whisper_model.transcribe(tmp_file.name)
                
                # Clean up
                os.unlink(tmp_file.name)
                
                return {
                    'success': True,
                    'transcription': result['text'].strip(),
                    'confidence': 1.0,  # Whisper doesn't provide confidence scores
                    'language': result.get('language', 'unknown'),
                    'method': 'whisper'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Whisper transcription failed: {e}',
                'method': 'whisper'
            }
    
    def transcribe_with_sphinx(self, audio_file):
        """Transcribe using CMU Sphinx (offline, less accurate but fast)"""
        try:
            audio_data = self._prepare_audio_for_sr(audio_file)
            
            with sr.AudioFile(audio_data) as source:
                audio = self.recognizer.record(source)
            
            # Recognize speech using Sphinx
            text = self.recognizer.recognize_sphinx(audio)
            return {
                'success': True,
                'transcription': text,
                'confidence': 1.0,
                'method': 'sphinx'
            }
            
        except sr.UnknownValueError:
            return {
                'success': False,
                'error': 'Sphinx could not understand audio',
                'method': 'sphinx'
            }
        except sr.RequestError as e:
            return {
                'success': False,
                'error': f'Sphinx error: {e}',
                'method': 'sphinx'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Sphinx transcription failed: {e}',
                'method': 'sphinx'
            }
    
    def _prepare_audio_for_sr(self, audio_file):
        """Convert audio file to format suitable for speech_recognition library"""
        try:
            # Convert to WAV format
            audio_segment = self._convert_to_wav(audio_file)
            
            # Export to BytesIO
            wav_io = io.BytesIO()
            audio_segment.export(wav_io, format='wav')
            wav_io.seek(0)
            
            return wav_io
            
        except Exception as e:
            raise Exception(f"Audio preparation failed: {e}")
    
    def _convert_to_wav(self, audio_file):
        """Convert any audio format to WAV using pydub"""
        try:
            # Read the file content
            audio_file.seek(0)
            file_content = audio_file.read()
            
            # Detect format based on file content
            audio_segment = AudioSegment.from_file(
                io.BytesIO(file_content),
                format="webm"  # Default to webm since that's what MediaRecorder produces
            )
            
            # Convert to mono, 16kHz (good for speech recognition)
            audio_segment = audio_segment.set_channels(1).set_frame_rate(16000)
            
            return audio_segment
            
        except Exception as e:
            # Try alternative formats
            formats_to_try = ['wav', 'mp3', 'ogg', 'm4a']
            
            for fmt in formats_to_try:
                try:
                    audio_file.seek(0)
                    file_content = audio_file.read()
                    audio_segment = AudioSegment.from_file(
                        io.BytesIO(file_content),
                        format=fmt
                    )
                    return audio_segment.set_channels(1).set_frame_rate(16000)
                except:
                    continue
            
            raise Exception(f"Could not convert audio file: {e}")
    
    def transcribe(self, audio_file, method='google'):
        """Main transcription method that tries multiple approaches"""
        methods = {
            'google': self.transcribe_with_google,
            'whisper': self.transcribe_with_whisper,
            'sphinx': self.transcribe_with_sphinx
        }
        
        if method in methods:
            return methods[method](audio_file)
        else:
            # Try all methods in order of preference
            for method_name in ['whisper', 'google', 'sphinx']:
                result = methods[method_name](audio_file)
                if result['success']:
                    return result
            
            return {
                'success': False,
                'error': 'All transcription methods failed',
                'method': 'all'
            }