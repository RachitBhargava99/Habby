from datetime import timedelta
from backend.models import Activity
from sqlalchemy import and_


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
