from datetime import datetime

def from_string(dt : str):
    return datetime.strptime(dt, '%H:%M')

def to_time_string(dt : datetime):
    return datetime.strftime(dt, '%H:%M')

def to_string(dt : datetime):
    return datetime.strftime(dt, '%a %d %b %H:%M')