from flask import Blueprint, request, current_app
from backend.models import User, Category, Habit, Activity
from backend import db, mail
import json
import requests
from datetime import datetime
from flask_mail import Message
from backend.events.utils import get_activity_data, get_change_index

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
    cat_ideal_num : int
        Ideal number to be reached

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
    cat_ideal_num = request_json['cat_ideal_num']
    new_cat = Category(name=cat_name, level=cat_level, ideal_num=cat_ideal_num)
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
    Category must exist

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
    curr_num : int
        Current number the user is at for the habit
        For example, this field shall be 7 if a user does something SEVEN times a day

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
    curr_num = request_json['curr_nun']

    cat = Category.query.filter_by(id=cat_id).first()

    if not cat:
        return json.dumps({'status': 0, 'error': "Category Not Found"})

    change_index = get_change_index(cat.level, pref_level)

    new_habit = Habit(name=habit_name, pref_level=pref_level, change_index=change_index, user_id=user.id, cat_id=cat_id,
                      curr_num=curr_num)
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


@events.route('/event/activity/get_data', methods=['POST'])
def get_activity_data():
    """Get all logged activity data of a habit

    Method Type: POST

    Special Restrictions
    --------------------
    User must be logged in
    Habit must exist
    Habit must belong to user logged in
    Mode must either be W, M, or Y

    JSON Parameters
    ---------------
    auth_token : str
        Token to authorize the request - released when logging in
    habit_id : int
        ID of the habit reporting activity to
    mode : str
        Mode of search to perform - weekly, monthly, yearly
    test_date : str
        Date from which the search must start
        Must be in MM-DD-YY format

    Returns
    -------
    JSON
        status : int
            Tells whether or not did the function work - 1 for success, 0 for failure
        datewise_activity_map : dict(str -> int)
            Map of dates to number of occurrences of activity
                Dates (key) formatted in MM-DD-YY format
                Numbers (value) specify the number of occurrences of activity
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

    mode = request_json['mode']

    test_date = datetime.strptime(request_json['test_date'], '%m-%d-%y')

    if mode == 'W':
        datewise_activity_map = get_activity_data(test_date, 7, habit_id)
    elif mode == 'M':
        datewise_activity_map = get_activity_data(test_date, 30, habit_id)
    elif mode == 'Y':
        datewise_activity_map = get_activity_data(test_date, 365, habit_id)
    else:
        return json.dumps({'status': 0, 'error': "Invalid Mode Provided"})

    return json.dumps({'status': 1, 'datewise_activity_map': datewise_activity_map})
