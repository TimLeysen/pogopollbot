from datetime import datetime, timedelta
import random

def from_string(t : str):
    return datetime.strptime(t, '%H:%M')

def to_string(t : datetime):
    return datetime.strftime(t, '%H:%M')

def calc(start_time : datetime, end_time : datetime):
    period_minutes = 15
    min_start_delta = timedelta(minutes=25)
    min_end_delta = timedelta(minutes=10)
    period_delta = timedelta(minutes=period_minutes)
    times = []
    # start_time = datetime.now()
    
    # round to the nearest 15 minute mark
    t = start_time
    t += timedelta(minutes=period_minutes//2)
    t -= timedelta(minutes=t.minute % 15, seconds=t.second)

    # print('\n')
    # print(start_time)
    # print(end_time)
    # print('rounded to 15 min mark: {}'.format(t))
    while True:
        t += period_delta
        # print('\ncheck time {}'.format(t))
        # print('t - start_time = {}'.format(t - start_time))
        if t - start_time >= min_start_delta:
            # print('end_time - t = {}'.format(end_time - t))
            # print(min_end_delta)
            if end_time - t >= min_end_delta:
                # print('appending')
                times.append(t)
            else:
                break
    
    # Only keep the last 5 times
    max_times = 5
    if len(times) > max_times:
        num_to_remove = len(times)-max_times
        return times[num_to_remove:]
    return times

if __name__ == '__main__':
    times = []
    for i in range(20):
        start = '{}:{}'.format(random.randrange(0,24), random.randrange(0,60))
        end = from_string(start) + timedelta(hours=random.randrange(1,2), minutes=random.randrange(0,60))
        times.append((from_string(start), end))
    
    for start, end in times:
        times = [to_string(x) for x in calc(start, end)]
        print('{}  {}  => {}'.format(to_string(start), to_string(end), times))
        
    # 17:11  18:34  => ['18:00', '18:15']
    # should add 17:45???
    # start = from_string('17:11')
    # end = from_string('18:34')
    # times = [to_string(x) for x in calc(start, end)]
    # print('{}  {}  => {}'.format(to_string(start), to_string(end), times))
