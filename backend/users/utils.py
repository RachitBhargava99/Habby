from backend import mail
from flask import url_for
from flask_mail import Message


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender = 'rachitbhargava99@gmail.com', recipients = [user.email])
    msg.body = f'''To reset your password, kindly visit: {url_for('users.reset', token = token, _external = True)}

Kindly ignore this email if you did not make this request'''
    mail.send(msg)
