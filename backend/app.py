from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
from threading import Thread
import time
from functools import wraps

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # allow frontend requests

# Config
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_MAX_EMAILS'] = None
app.config['MAIL_ASCII_ATTACHMENTS'] = False

# Connection timeout settings
app.config['MAIL_TIMEOUT'] = 10  # 10 seconds timeout

mail = Mail(app)

def async_send_email(app, msg, max_retries=3):
    """Send email asynchronously with retry logic"""
    with app.app_context():
        for attempt in range(max_retries):
            try:
                logger.info(f"Attempting to send email (attempt {attempt + 1}/{max_retries})")
                mail.send(msg)
                logger.info("Email sent successfully")
                return True
            except Exception as e:
                logger.error(f"Email sending failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    # Exponential backoff: wait 2^attempt seconds before retrying
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to send email after {max_retries} attempts")
                    return False

def send_async_email(msg):
    """Send email in a background thread"""
    thread = Thread(target=async_send_email, args=(app, msg))
    thread.daemon = True
    thread.start()

@app.route('/send-mail', methods=['POST'])
def send_mail():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    if not name or not email or not message:
        return jsonify({'message': 'Please fill in all fields'}), 400

    try:
        # Email to you (the portfolio owner) with the message details
        owner_msg = Message(
            subject=f"Portfolio: Contact Form Submission from {name}",
            sender=app.config['MAIL_USERNAME'],
            recipients=[app.config['MAIL_USERNAME']],
            body=f"Name: {name}\nEmail: {email}\nMessage:\n{message}",
            reply_to=email
        )
        
        # Confirmation email to the person who filled the form
        user_msg = Message(
            subject="Thank you for contacting me!",
            sender=app.config['MAIL_USERNAME'],
            recipients=[email],
            body=f"Hi {name},\n\nThank you for reaching out! I have received your message and will get back to you as soon as possible.\n\nYour message:\n{message}\n\nBest regards"
        )
        
        # Send both emails asynchronously
        send_async_email(owner_msg)
        send_async_email(user_msg)
        
        logger.info(f"Emails queued for sending from {name} ({email})")
        return jsonify({'message': 'Message sent successfully!'}), 200
        
    except Exception as e:
        logger.error(f"Error queueing email: {str(e)}")
        return jsonify({'message': 'Something went wrong while sending email.'}), 500

if __name__ == '__main__':
    app.run(debug=False)
