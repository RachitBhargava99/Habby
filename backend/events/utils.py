from datetime import timedelta
from backend.models import Activity, Habit
from sqlalchemy import and_
import random
import math
from backend import db


def get_activity_data(test_date, num_days, habit_id):
    num_days_later = test_date + timedelta(days=num_days)

    all_activities = Activity.query.filter(and_(Activity.habit_id == habit_id,
                                                and_(Activity.timestamp >= test_date,
                                                     Activity.timestamp < num_days_later)))

    datewise_activity_map = {}

    for each_activity in all_activities:
        if datewise_activity_map.get(each_activity.timestamp.strftime('%m-%d-%y')) is None:
            datewise_activity_map[each_activity.timestamp.strftime('%m-%d-%y')] = 1
        else:
            datewise_activity_map[each_activity.timestamp.strftime('%m-%d-%y')] += 1

    return datewise_activity_map


def get_change_index(cat_level, pref_level):
    init_level = 0.99

    converted_pref_level = (1 - ((1 - pref_level / 3) ** 4))

    converted_cat_level = (1 - ((1 - cat_level / 7) ** 2))

    change_index = init_level * converted_pref_level * converted_cat_level

    return change_index


def set_target(habit_id):
    habit = Habit.query.filter_by(id=habit_id)
    curr_num = habit.curr_num
    new_target = math.floor(curr_num + random.random())
    habit.curr_target = new_target
    db.session.commit()
