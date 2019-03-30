from flask import Blueprint, request, current_app
from backend.models import User, Category, Habit, Activity
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

    Special Restrictions
    --------------------
    User must be logged in
    User must be admin

    JSON Parameters
    ---------------
    auth_token : str
        Token to authorize the request - released when logging in
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


@events.route('/event/habit/attach', methods=['POST'])
def attach_habit_to_user():
    """Attaches a new habit to a user and makes an instance of it in database

    Method Type: POST

    Special Restrictions
    --------------------
    User must be logged in

    JSON Parameters
    ---------------
    auth_token : str
        Token to authorize the request - released when logging in
    habit_name : str
        Name of the habit to be added
    pref_level : int
        Level indicated by user for the habit
    cat_id : int
        ID of the category to link the habit to

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

    habit_name = request_json['habit_name']
    pref_level = request_json['pref_level']
    cat_id = request_json['cat_id']

    new_habit = Habit(name=habit_name, pref_level=pref_level, user_id=user.id, cat_id=cat_id)
    db.session.add(new_habit)
    db.session.commit()

    return json.dumps({'status': 1})


@events.route('/event/activity/report', methods=['POST'])
def report_activity():
    """Adds new activity to a habit

    Method Type: POST

    Special Restrictions
    --------------------
    User must be logged in
    Habit must exist
    Habit must belong to user logged in

    JSON Parameters
    ---------------
    auth_token : str
        Token to authorize the request - released when logging in
    habit_id : int
        ID of the habit reporting activity to

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

    habit_id = request_json['habit_id']
    habit = Habit.query.filter_by(id=habit_id).first()

    if not habit:
        return json.dumps({'status': 0, 'error': "Habit Not Found"})

    if user.id != habit.user_id:
        return json.dumps({'status': 0, 'error': "The selected habit does not belong to the logged in user."})

    new_activity = Activity(habit_id=habit_id)
    db.session.add(new_activity)
    db.session.commit()

    return json.dumps({'status': 1})
