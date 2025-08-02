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

# email function fetching
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


@app.route('/api/emails/send', methods=['POST'])
def send_email():
    """Send a new email"""
    if not gmail_service.load_credentials():
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    
    # Validate required fields
    if not data.get('to') or not data.get('subject') or not data.get('body'):
        return jsonify({'error': 'Missing required fields: to, subject, body'}), 400
    
    result = gmail_service.send_email(
        to=data['to'],
        subject=data['subject'],
        body=data['body'],
        html_body=data.get('html_body'),
        attachments=data.get('attachments')
    )
    
    if result is None:
        return jsonify({'error': 'Failed to send email'}), 500
    
    return jsonify({'result': result})

@app.route('/api/emails/<message_id>/reply', methods=['POST'])
def reply_to_email(message_id):
    """Reply to an email"""
    if not gmail_service.load_credentials():
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    
    if not data.get('to') or not data.get('body'):
        return jsonify({'error': 'Missing required fields: to, body'}), 400
    
    # Get original email to create proper subject
    original_email = gmail_service.get_message_by_id(message_id)
    if not original_email:
        return jsonify({'error': 'Original email not found'}), 404
    
    # Create reply subject
    original_subject = original_email.get('subject', '')
    reply_subject = f"Re: {original_subject}" if not original_subject.startswith('Re:') else original_subject
    
    result = gmail_service.send_reply(
        original_message_id=message_id,
        to=data['to'],
        subject=reply_subject,
        body=data['body'],
        html_body=data.get('html_body')
    )
    
    if result is None:
        return jsonify({'error': 'Failed to send reply'}), 500
    
    return jsonify({'result': result})

@app.route('/api/drafts', methods=['GET'])
def get_drafts():
    """Get draft emails"""
    if not gmail_service.load_credentials():
        return jsonify({'error': 'Not authenticated'}), 401
    
    drafts = gmail_service.get_draft_messages()
    
    if drafts is None:
        return jsonify({'error': 'Failed to fetch drafts'}), 500
    
    return jsonify({'drafts': drafts})

@app.route('/api/drafts', methods=['POST'])
def create_draft():
    """Create a draft email"""
    if not gmail_service.load_credentials():
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    
    if not data.get('to') or not data.get('subject') or not data.get('body'):
        return jsonify({'error': 'Missing required fields: to, subject, body'}), 400
    
    result = gmail_service.create_draft(
        to=data['to'],
        subject=data['subject'],
        body=data['body'],
        html_body=data.get('html_body')
    )
    
    if result is None:
        return jsonify({'error': 'Failed to create draft'}), 500
    
    return jsonify({'result': result})