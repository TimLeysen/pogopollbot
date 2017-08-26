from datetime import datetime, timedelta
import random

from timepoll import TimePoll

def from_string(t : str):
    return datetime.strptime(t, '%H:%M')

def to_string(t : datetime):
    return datetime.strftime(t, '%H:%M')

if __name__ == '__main__':
    poll = TimePoll('rhydon', datetime.now(), 'TEST', 'some guy')
    end_times = []
    for i in range(20):
        time = datetime.now() + timedelta(hours=random.randrange(1,2), minutes=random.randrange(0,60))
        end_times.append(time)
    
    for time in end_times:
        start_times = poll.calc_start_times(time)
        print('{} {} => {}'.format(to_string(datetime.now()), to_string(time), start_times))