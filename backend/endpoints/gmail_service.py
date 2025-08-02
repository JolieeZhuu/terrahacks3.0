from email import encoders
from email.mime.base import MIMEBase
import os
import json
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from config import Config

class GmailService:
    def __init__(self):
        self.service = None
        self.creds = None
        
    def get_authorization_url(self):
        """Generate authorization URL for OAuth2 flow"""
        flow = Flow.from_client_secrets_file(
            Config.CREDENTIALS_FILE,
            scopes=Config.SCOPES,
            redirect_uri=Config.GOOGLE_REDIRECT_URI
        )
        
        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        return authorization_url
    
    def exchange_code_for_token(self, authorization_code):
        """Exchange authorization code for access token"""
        flow = Flow.from_client_secrets_file(
            Config.CREDENTIALS_FILE,
            scopes=Config.SCOPES,
            redirect_uri=Config.GOOGLE_REDIRECT_URI
        )
        
        flow.fetch_token(code=authorization_code)
        
        # Save credentials
        self.creds = flow.credentials
        self._save_credentials()
        self._build_service()
        
        return True
    
    def load_credentials(self):
        """Load existing credentials"""
        if os.path.exists(Config.TOKEN_FILE):
            self.creds = Credentials.from_authorized_user_file(
                Config.TOKEN_FILE, Config.SCOPES
            )
        
        # Refresh if expired
        if self.creds and self.creds.expired and self.creds.refresh_token:
            self.creds.refresh(Request())
            self._save_credentials()
        
        if self.creds and self.creds.valid:
            self._build_service()
            return True
        
        return False
    
    def _save_credentials(self):
        """Save credentials to file"""
        with open(Config.TOKEN_FILE, 'w') as token:
            token.write(self.creds.to_json())
    
    def _build_service(self):
        """Build Gmail service"""
        self.service = build('gmail', 'v1', credentials=self.creds)
    
    def get_messages(self, query='', max_results=10):
        """Get messages based on query"""
        if not self.service:
            return None
        
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            # Get full message details
            full_messages = []
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me',
                    id=message['id']
                ).execute()
                
                # Extract text content
                email_data = self._extract_message_data(msg)
                full_messages.append(email_data)
            
            return full_messages
            
        except Exception as error:
            print(f'An error occurred: {error}')
            return None
    
    def get_message_by_id(self, message_id):
        """Get specific message by ID"""
        if not self.service:
            return None
        
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id
            ).execute()
            
            return self._extract_message_data(message)
            
        except Exception as error:
            print(f'An error occurred: {error}')
            return None
    
    def _extract_message_data(self, message):
        """Extract relevant data from message"""
        headers = message['payload'].get('headers', [])
        
        # Extract headers
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
        
        # Extract body
        body = self._extract_body(message['payload'])
        
        return {
            'id': message['id'],
            'subject': subject,
            'sender': sender,
            'date': date,
            'body': body,
            'snippet': message.get('snippet', '')
        }
    
    def _extract_body(self, payload):
        """Extract body text from message payload"""
        body = ''
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    break
                elif part['mimeType'] == 'multipart/alternative':
                    body = self._extract_body(part)
        else:
            if payload['mimeType'] == 'text/plain':
                data = payload['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8')
        
        return body
    
    def send_email(self, to, subject, body, html_body=None, attachments=None):
        """Send an email"""
        if not self.service:
            return None
        
        try:
            message = self._create_message(to, subject, body, html_body, attachments)
            sent_message = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            return {
                'id': sent_message['id'],
                'threadId': sent_message['threadId'],
                'status': 'sent'
            }
            
        except Exception as error:
            print(f'An error occurred: {error}')
            return None
    
    def send_reply(self, original_message_id, to, subject, body, html_body=None):
        """Reply to an existing email"""
        if not self.service:
            return None
        
        try:
            # Get the original message to get thread ID
            original_message = self.service.users().messages().get(
                userId='me',
                id=original_message_id
            ).execute()
            
            thread_id = original_message['threadId']
            
            # Create reply message
            message = self._create_message(to, subject, body, html_body)
            message['threadId'] = thread_id
            
            # Add In-Reply-To and References headers
            headers = message.get('payload', {}).get('headers', [])
            message_id_header = next(
                (h['value'] for h in original_message['payload']['headers'] 
                 if h['name'] == 'Message-ID'), None
            )
            
            if message_id_header:
                headers.extend([
                    {'name': 'In-Reply-To', 'value': message_id_header},
                    {'name': 'References', 'value': message_id_header}
                ])
            
            sent_message = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            return {
                'id': sent_message['id'],
                'threadId': sent_message['threadId'],
                'status': 'sent'
            }
            
        except Exception as error:
            print(f'An error occurred: {error}')
            return None
    
    def _create_message(self, to, subject, body, html_body=None, attachments=None):
        """Create a message for an email"""
        if html_body or attachments:
            message = MIMEMultipart('alternative')
        else:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
        
        message['to'] = to
        message['subject'] = subject
        
        # Add plain text part
        text_part = MIMEText(body, 'plain')
        message.attach(text_part)
        
        # Add HTML part if provided
        if html_body:
            html_part = MIMEText(html_body, 'html')
            message.attach(html_part)
        
        # Add attachments if provided
        if attachments:
            for attachment in attachments:
                self._add_attachment(message, attachment)
        
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
    
    def _add_attachment(self, message, attachment_path):
        """Add an attachment to the message"""
        content_type, encoding = mimetypes.guess_type(attachment_path)
        
        if content_type is None or encoding is not None:
            content_type = 'application/octet-stream'
        
        main_type, sub_type = content_type.split('/', 1)
        
        with open(attachment_path, 'rb') as fp:
            attachment_data = fp.read()
        
        attachment = MIMEBase(main_type, sub_type)
        attachment.set_payload(attachment_data)
        encoders.encode_base64(attachment)
        
        filename = os.path.basename(attachment_path)
        attachment.add_header(
            'Content-Disposition',
            f'attachment; filename= {filename}'
        )
        
        message.attach(attachment)
    
    def get_draft_messages(self):
        """Get draft messages"""
        if not self.service:
            return None
        
        try:
            results = self.service.users().drafts().list(userId='me').execute()
            drafts = results.get('drafts', [])
            
            draft_details = []
            for draft in drafts:
                draft_detail = self.service.users().drafts().get(
                    userId='me',
                    id=draft['id']
                ).execute()
                
                message_data = self._extract_message_data(draft_detail['message'])
                message_data['draft_id'] = draft['id']
                draft_details.append(message_data)
            
            return draft_details
            
        except Exception as error:
            print(f'An error occurred: {error}')
            return None
    
    def create_draft(self, to, subject, body, html_body=None):
        """Create a draft email"""
        if not self.service:
            return None
        
        try:
            message = self._create_message(to, subject, body, html_body)
            draft = {
                'message': message
            }
            
            draft = self.service.users().drafts().create(
                userId='me',
                body=draft
            ).execute()
            
            return {
                'id': draft['id'],
                'message_id': draft['message']['id'],
                'status': 'draft'
            }
            
        except Exception as error:
            print(f'An error occurred: {error}')
            return None