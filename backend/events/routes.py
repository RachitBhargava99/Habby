from flask import Blueprint, request, current_app
from backend.models import User, Category
from backend import db, mail
import json
import requests
from datetime import datetime
from flask_mail import Message

events = Blueprint('queues', __name__)


# Checker to see whether or not is the server running
@events.route('/event', methods=['GET'])
def checker():
    return "Hello"


@events.route('/event/cat/add', methods=['POST'])
def add_new_category():
    """Adds a new category to the database

    Method Type: POST

    JSON Parameters
    ---------------
    cat_name : str
        Name of the category to be added
    cat_level : int
        Level of the category you want to add

    Returns
    -------
    JSON
        status : int
            Tells whether or not did the function work - 1 for success, 0 for failure
    """
    request_json = request.get_json()

    auth_token = request_json['auth_token']
    user = User.verify_auth_token(auth_token)

    if user is None:
        return json.dumps({'status': 0, 'error': "User Not Authenticated"})

    if not user.isAdmin:
        return json.dumps({'status': 0, 'error': "Access Denied"})

    cat_name = request_json['cat_name']
    cat_level = request_json['cat_level']
    new_cat = Category(name=cat_name, level=cat_level)
    db.session.add(new_cat)
    db.session.commit()

    return json.dumps({'status': 1})
