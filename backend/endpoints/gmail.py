from flask import Flask, request, jsonify, redirect, session
from flask_cors import CORS
from backend.endpoints.gmail_service import GmailService
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, origins=['http://localhost:5173'])  # Vite default port

gmail_service = GmailService()

@app.route('/api/auth/login')
def login():
    """Initiate OAuth2 flow"""
    auth_url = gmail_service.get_authorization_url()
    return jsonify({'auth_url': auth_url})

@app.route('/oauth2/callback')
def oauth_callback():
    """Handle OAuth2 callback"""
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        return redirect('http://localhost:5173/error')
    
    if code:
        success = gmail_service.exchange_code_for_token(code)
        if success:
            return redirect('http://localhost:5173/dashboard')
    
    return redirect('http://localhost:5173/error')

@app.route('/api/auth/status')
def auth_status():
    """Check if user is authenticated"""
    is_authenticated = gmail_service.load_credentials()
    return jsonify({'authenticated': is_authenticated})

@app.route('/api/emails')
def get_emails():
    """Get emails with optional query"""
    query = request.args.get('query', '')
    max_results = int(request.args.get('max_results', 10))
    
    if not gmail_service.load_credentials():
        return jsonify({'error': 'Not authenticated'}), 401
    
    messages = gmail_service.get_messages(query, max_results)
    
    if messages is None:
        return jsonify({'error': 'Failed to fetch emails'}), 500
    
    return jsonify({'messages': messages})

@app.route('/api/emails/<message_id>')
def get_email(message_id):
    """Get specific email by ID"""
    if not gmail_service.load_credentials():
        return jsonify({'error': 'Not authenticated'}), 401
    
    message = gmail_service.get_message_by_id(message_id)
    
    if message is None:
        return jsonify({'error': 'Email not found'}), 404
    
    return jsonify({'message': message})

@app.route('/api/auth/logout')
def logout():
    """Logout user"""
    # Remove token file
    import os
    if os.path.exists(Config.TOKEN_FILE):
        os.remove(Config.TOKEN_FILE)
    
    return jsonify({'message': 'Logged out successfully'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)