from datetime import datetime, timedelta, time
import itertools
import logging
import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import zope.event

import pokedex

def from_string(t : str):
    return datetime.strptime(t, '%H:%M')

def to_string(t : datetime):
    return datetime.strftime(t, '%H:%M')


class VoteCountReachedEvent:
    def __init__(self, poll_id, start_time):
        self.poll_id = poll_id
        self.start_time = start_time
    
class StartTimePoll:
    id_generator = itertools.count(0)
    # min_votes = 5
    min_votes = 1 # TODO
    
    def __init__(self, pokemon, timer : timedelta, location, creator):
        # we have to use a separate id from the normal polls
        # showing it will be confusing!
        self.id = next(self.id_generator)%100
        self.pokemon = pokemon
        self.location = location
        self.creator = creator        
        self.end_time = datetime.now() + timer
        
        self.times = {} # key: start time, value: number of votes
        for time in self.__calc_start_times(self.end_time):
            self.times[time] = {} # keys: user id, values: user names
    
    def __calc_start_times(self, end_time : datetime):
        period_minutes = 15
        min_start_delta = timedelta(minutes=25)
        min_end_delta = timedelta(minutes=10)
        period_delta = timedelta(minutes=period_minutes)
        times = [] # as strings
        start_time = datetime.now()
        
        # round to the nearest 15 minute mark
        t = start_time
        t += timedelta(minutes=period_minutes//2)
        t -= timedelta(minutes=t.minute % 15, seconds=t.second)

        while True:
            t += period_delta
            if t - start_time >= min_start_delta:
                if end_time - t >= min_end_delta:
                    times.append(to_string(t))
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
        for time in self.times:
            row.append(InlineKeyboardButton(time, callback_data=time))
        return InlineKeyboardMarkup([row])
        
    def description(self):
        # Don't print id? it will be confusing...
        # desc = '#{} {} {} (raids ends: {})'.format(self.id_string(), self.pokemon, self.location, to_string(self.end_time))
        desc = '{} {} (raids ends: {})'.format(self.pokemon, self.location, to_string(self.end_time))
        return desc
        
    def id_string(self):
        return str(self.id).zfill(3)

    def message(self):
        msg = ''
        msg += '*{}* (tot {})\n'.format(self.pokemon, to_string(self.end_time))
        msg += '{}\n'.format(self.location)
        msg += '\n'
        for time, voters in self.times.items():
            msg += '*{}* [{}]: {}\n'.format(time, len(voters), ', '.join(voters.values()))
        msg += '\n'
        msg += 'Er wordt automatisch een poll aangemaakt na 5 stemmen.'
        
        return msg
    
    def add_vote(self, user_id, user_name, user_time : str):
        changed = False
        
        for time in self.times:
            if time == user_time:
                if user_id not in self.times[time]:
                    self.times[time][user_id] = user_name
                    changed = True
            else:
                if user_id in self.times[time]:                
                    logging.info('Removing time {} for user {} ({})'\
                        .format(time, user_name, user_id))
                    del self.times[time][user_id]
                    changed = True

        if changed and len(self.times[user_time]) >= StartTimePoll.min_votes:
            logging.debug('posting VoteCountReachedEvent({}, {})'.format(self.id, user_time))
            zope.event.notify(VoteCountReachedEvent(self.id, user_time))

        return changed