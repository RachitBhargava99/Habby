from flask import Blueprint, request, current_app
from backend.models import User, Category, Habit, Activity
from backend import db, mail
import json
import requests
from datetime import datetime
from flask_mail import Message
from backend.events.utils import get_habit_activity_data, get_change_index, set_target

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
    curr_num = request_json['curr_num']

    cat = Category.query.filter_by(id=cat_id).first()

    if not cat:
        return json.dumps({'status': 0, 'error': "Category Not Found"})

    change_index = get_change_index(cat.level, pref_level)

    new_habit = Habit(name=habit_name, pref_level=pref_level, change_index=change_index, user_id=user.id, cat_id=cat_id,
                      curr_num=curr_num, init_num=curr_num)
    db.session.add(new_habit)
    db.session.commit()

    set_target(new_habit.id)

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
        datewise_activity_map = get_habit_activity_data(test_date, 7, habit_id)
    elif mode == 'M':
        datewise_activity_map = get_habit_activity_data(test_date, 30, habit_id)
    elif mode == 'Y':
        datewise_activity_map = get_habit_activity_data(test_date, 365, habit_id)
    else:
        return json.dumps({'status': 0, 'error': "Invalid Mode Provided"})

    return json.dumps({'status': 1, 'datewise_activity_map': datewise_activity_map})


@events.route('/event/activity/get_data', methods=['GET'])
def update_habit_data():
    """Update habit data based on the activities logged in on the previous day

    Method Type: GET

    Special Restrictions
    --------------------
    N/A

    Returns
    -------
    JSON
        status : int
            Tells whether or not did the function work - 1 for success, 0 for failure
    """
    curr_time = datetime.now()
    date_string = curr_time.strftime("%m-%d-%y")
    curr_date = datetime.strptime(date_string, "%m-%d-%y")

    all_habits = Habit.query.all()

    for each_habit in all_habits:
        single_activity_map = get_habit_activity_data(curr_date, 1, each_habit.id)
        num_times = single_activity_map.get(date_string, default=0)
        diff = each_habit.curr_target - num_times
        if diff >= 0:
            each_habit.curr_num *= each_habit.change_index ** (diff + 1)
        else:
            each_habit.curr_num /= each_habit.change_index ** (diff * (-1))
        db.session.commit()
        set_target(each_habit.id)

    return json.dumps({'status': 1})


@events.route('/event/habit/get_data', methods=['POST'])
def get_habit_data():
    """Get basic data of a habit

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
        data : dict(str -> str, str -> int, str -> int)
            Map containing the basic data related to the requested habit
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

    return json.dumps({
        'status': 1,
        'data': {
            'name': habit.name,
            'level_index': ((habit.init_num - habit.curr_num) / habit.init_num),
            'curr_target': habit.curr_target
        }
    })


@events.route('/event/cat/get_sorted', methods=['POST'])
def get_sorted_cat():
    """Get sorted list of all category names based on how close they are related to provided text

    Method Type: POST

    Special Restrictions
    --------------------
    User must be logged in

    JSON Parameters
    ---------------
    auth_token : str
        Token to authorize the request - released when logging in
    text : str
        Text to compare

    Returns
    -------
    JSON
        status : int
            Tells whether or not did the function work - 1 for success, 0 for failure
        data : list of tuples
            Index 0: Match index of category
            Index 1: Category name
    """
    request_json = request.get_json()

    auth_token = request_json['auth_token']
    user = User.verify_auth_token(auth_token)

    if user is None:
        return json.dumps({'status': 0, 'error': "User Not Authenticated"})

    text_to_compare = request_json['text']

    all_cat = Category.query.all()
    effective_cat = [(x.name, x.id) for x in all_cat]

    marked_cat = []

    for cat in effective_cat:
        request_data = requests.post('http://api.cortical.io/rest/compare?retina_name=en_associative', json=
        [
            {
                'text': cat[0]
            },
            {
                'text': text_to_compare
            }
        ]
                                     )
        data = request_data.json()
        try:
            marked_cat.append((data['weightedScoring'], cat[0], cat[1]))
        except Exception:
            marked_cat.append((0, cat[0], cat[1]))

    marked_cat.sort(reverse=True)

    return json.dumps({
        'status': 1,
        'data': marked_cat
    })


@events.route('/event/habit/get_all', methods=['POST'])
def get_all_user_habits():
    """Get data of all habits registered by the logged in user

    Method Type: POST

    Special Restrictions
    --------------------
    User must be logged in

    JSON Parameters
    ---------------
    auth_token : str
        Token to authorize the request - released when logging in

    Returns
    -------
    JSON
        status : int
            Tells whether or not did the function work - 1 for success, 0 for failure
        data : list of dicts specifying data of each habit of the user
    """
    request_json = request.get_json()

    auth_token = request_json['auth_token']
    user = User.verify_auth_token(auth_token)

    if user is None:
        return json.dumps({'status': 0, 'error': "User Not Authenticated"})

    all_habits = Habit.query.filter_by(user_id=user.id)

    habit_list = []

    for habit in all_habits:
        habit_list.append({
            'id': habit.id,
            'name': habit.name,
            'curr_num': habit.curr_num,
            'init_num': habit.init_num,
            'pref_level': habit.pref_level,
            'curr_target': habit.curr_target,
            'num_today': get_habit_activity_data(datetime.strptime(datetime.now().strftime("%m-%d-%y"), "%m-%d-%y"), 7,
                                                 habit.id),
            'cat_id': habit.cat_id
        })

    return json.dumps({'status': 1, 'data': habit_list})
