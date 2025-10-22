"""
Email verification and password reset utilities
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app, url_for
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

def get_token_serializer() -> URLSafeTimedSerializer:
    """Get configured token serializer for email tokens"""
    secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')
    return URLSafeTimedSerializer(secret_key, salt='email-tokens')

def generate_verification_token(user_id: int, email: str) -> str:
    """Generate verification token for user email"""
    serializer = get_token_serializer()
    payload = {
        'user_id': user_id,
        'email': email,
        'type': 'verification',
        'timestamp': datetime.utcnow().isoformat()
    }
    return serializer.dumps(payload)

def generate_reset_token(user_id: int, email: str) -> str:
    """Generate password reset token"""
    serializer = get_token_serializer()
    payload = {
        'user_id': user_id,
        'email': email,
        'type': 'reset',
        'timestamp': datetime.utcnow().isoformat()
    }
    return serializer.dumps(payload)

def verify_token(token: str, token_type: str) -> Optional[Dict[str, Any]]:
    """Verify and decode token, return payload if valid"""
    serializer = get_token_serializer()
    try:
        payload = serializer.loads(token, max_age=3600)  # 1 hour expiry
        if payload.get('type') != token_type:
            return None
        return payload
    except (BadSignature, SignatureExpired):
        return None

def send_email_via_resend(to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
    """Send email via Resend API"""
    api_key = os.getenv('RESEND_API_KEY')
    if not api_key:
        logger.warning("RESEND_API_KEY not configured, skipping email send")
        return False
    
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "from": "Ahoy Indie Media <noreply@ahoy.example>",
        "to": [to_email],
        "subject": subject,
        "html": html_content
    }
    
    if text_content:
        data["text"] = text_content
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        logger.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email via Resend: {e}")
        return False

def send_email_via_smtp(to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
    """Send email via SMTP"""
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    
    if not all([smtp_host, smtp_user, smtp_password]):
        logger.warning("SMTP configuration incomplete, skipping email send")
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = "Ahoy Indie Media <noreply@ahoy.example>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        if text_content:
            msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {to_email} via SMTP")
        return True
    except Exception as e:
        logger.error(f"Failed to send email via SMTP: {e}")
        return False

def send_verification_email(user_email: str, user_id: int) -> bool:
    """Send email verification email"""
    token = generate_verification_token(user_id, user_email)
    verify_url = url_for('verify_email', token=token, _external=True)
    
    subject = "Verify your Ahoy Indie Media account"
    html_content = f"""
    <html>
    <body>
        <h2>Welcome to Ahoy Indie Media!</h2>
        <p>Please verify your email address by clicking the link below:</p>
        <p><a href="{verify_url}" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Email</a></p>
        <p>Or copy this link: {verify_url}</p>
        <p>This link will expire in 1 hour.</p>
        <p>If you didn't create an account, please ignore this email.</p>
    </body>
    </html>
    """
    
    text_content = f"""
    Welcome to Ahoy Indie Media!
    
    Please verify your email address by visiting: {verify_url}
    
    This link will expire in 1 hour.
    
    If you didn't create an account, please ignore this email.
    """
    
    # Try Resend first, fallback to SMTP
    if not send_email_via_resend(user_email, subject, html_content, text_content):
        return send_email_via_smtp(user_email, subject, html_content, text_content)
    return True

def send_reset_email(user_email: str, user_id: int) -> bool:
    """Send password reset email"""
    token = generate_reset_token(user_id, user_email)
    reset_url = url_for('reset_password', token=token, _external=True)
    
    subject = "Reset your Ahoy Indie Media password"
    html_content = f"""
    <html>
    <body>
        <h2>Password Reset Request</h2>
        <p>You requested to reset your password. Click the link below to set a new password:</p>
        <p><a href="{reset_url}" style="background: #dc3545; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
        <p>Or copy this link: {reset_url}</p>
        <p>This link will expire in 1 hour.</p>
        <p>If you didn't request this, please ignore this email.</p>
    </body>
    </html>
    """
    
    text_content = f"""
    Password Reset Request
    
    You requested to reset your password. Visit: {reset_url}
    
    This link will expire in 1 hour.
    
    If you didn't request this, please ignore this email.
    """
    
    # Try Resend first, fallback to SMTP
    if not send_email_via_resend(user_email, subject, html_content, text_content):
        return send_email_via_smtp(user_email, subject, html_content, text_content)
    return True
