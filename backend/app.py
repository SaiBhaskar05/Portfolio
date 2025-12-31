from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)  # allow frontend requests

# Config
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

mail = Mail(app)

@app.route('/send-mail', methods=['POST'])
def send_mail():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    if not name or not email or not message:
        return jsonify({'message': 'Please fill in all fields'}), 400

    try:
        msg = Message(
            subject=f"Portfolio: Contact Form Submission from {name}",
            sender=app.config['MAIL_USERNAME'],
            recipients=[app.config['MAIL_USERNAME']],
            body=f"Name: {name}\nEmail: {email}\nMessage:\n{message}"
        )
        mail.send(msg)
        return jsonify({'message': 'Message sent successfully!'}), 200
    except Exception as e:
        print(e)
        return jsonify({'message': 'Something went wrong while sending email.'}), 500

if __name__ == '__main__':
    app.run(debug=False)
