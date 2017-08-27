from datetime import datetime, timedelta
import random

from common import from_string, to_string, to_time_string
from timepoll import TimePoll

if __name__ == '__main__':
    poll = TimePoll('rhydon', datetime.now(), 'TEST', 'some guy')
    end_times = []
    for i in range(20):
        time = datetime.now() + timedelta(hours=random.randrange(1,2), minutes=random.randrange(0,60))
        end_times.append(time)
    
    for time in end_times:
        start_times = poll.calc_start_times(time)
        print('{} {} => {}'.format(to_time_string(datetime.now()), to_time_string(time), start_times))