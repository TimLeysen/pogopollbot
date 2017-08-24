from datetime import datetime, timedelta, time
import itertools
import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import pokedex

def from_string(t : str):
    return datetime.strptime(t, '%H:%M')

def to_string(t : datetime):
    return datetime.strftime(t, '%H:%M')

class StartTimePoll:
    id_generator = itertools.count(0)
    
    def __init__(self, pokemon, timer : timedelta, location, creator):
        # we have to use a separate id from the normal polls
        # showing it will be confusing!
        self.id = next(self.id_generator)%100
        self.pokemon = pokemon
        self.location = location
        self.creator = creator
        
        self.end_time = datetime.now() + timer
        self.start_times = self.__calc_start_times(self.end_time)
        self.votes = {}
        for time in self.start_times:
            self.votes[time] = 0
    
    def __calc_start_times(self, end_time : datetime):
        period_minutes = 15
        min_start_delta = timedelta(minutes=25)
        min_end_delta = timedelta(minutes=10)
        period_delta = timedelta(minutes=period_minutes)
        times = []
        start_time = datetime.now()
        
        # round to the nearest 15 minute mark
        t = start_time
        t += timedelta(minutes=period_minutes//2)
        t -= timedelta(minutes=t.minute % 15, seconds=t.second)

        while True:
            t += period_delta
            if t - start_time >= min_start_delta:
                if end_time - t >= min_end_delta:
                    times.append(t)
                else:
                    break
        
        # only keep the last 5 times
        max_times = 5
        if len(times) > max_times:
            num_to_remove = len(times)-max_times
            return times[num_to_remove:]
        return times
    
    def reply_markup(self):
        row = []
        for time in self.start_times:
            time_str = to_string(time)
            row.append(InlineKeyboardButton(time_str, callback_data=time_str))
        return InlineKeyboardMarkup([row])
        
    def description(self):
        # desc = '#{} {} {} {}'.format(self.id_string(), self.pokemon, self.end_time, self.location)
        # Don't print id, it will be confusing...
        desc = '{} {} (ends: {})'.format(self.pokemon, self.location, to_string(self.end_time))
        # if self.deleted:
            # desc += ' [{}]'.format(Poll.deleted_text)
        # elif self.closed:
            # desc += ' [{}]'.format(Poll.closed_text)
        return desc
        
    def message(self):
        return '???'
        
    def add_vote(self, name, choice):
        return