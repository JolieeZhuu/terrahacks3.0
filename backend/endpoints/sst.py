from flask import Flask, request, jsonify, redirect, session
from speech_service import SpeechToTextService
import os
from werkzeug.utils import secure_filename

# Initialize speech service
speech_service = SpeechToTextService()

# Load Whisper model at startup (optional)
# speech_service.load_whisper_model("base")  # Uncomment to use Whisper

@app.route('/api/transcribe', methods=['POST'])
def transcribe_audio():
    """Transcribe uploaded audio file"""
    try:
        # Check if file was uploaded
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        
        if audio_file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get transcription method from query params (default to google)
        method = request.args.get('method', 'google')
        
        # Transcribe the audio
        result = speech_service.transcribe(audio_file, method=method)
        
        if result['success']:
            return jsonify({
                'transcription': result['transcription'],
                'method': result['method'],
                'confidence': result.get('confidence', 1.0),
                'language': result.get('language', 'unknown')
            })
        else:
            return jsonify({
                'error': result['error'],
                'method': result['method']
            }), 500
            
    except Exception as e:
        return jsonify({'error': f'Transcription failed: {str(e)}'}), 500

@app.route('/api/transcribe/methods', methods=['GET'])
def get_available_methods():
    """Get available transcription methods"""
    methods = {
        'google': 'Google Speech Recognition (requires internet)',
        'whisper': 'OpenAI Whisper (offline, more accurate)',
        'sphinx': 'CMU Sphinx (offline, fast but less accurate)'
    }
    
    # Check which methods are actually available
    available = {}
    
    # Google is available if we have internet
    available['google'] = True
    
    # Whisper is available if model is loaded
    available['whisper'] = speech_service.whisper_model is not None
    
    # Sphinx is usually available
    available['sphinx'] = True
    
    return jsonify({
        'methods': methods,
        'available': available
    })