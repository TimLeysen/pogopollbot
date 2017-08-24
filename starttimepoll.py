from datetime import datetime, timedelta, time
import itertools
import logging
import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import zope.event

import pokedex
from poll import Poll

def from_string(t : str):
    return datetime.strptime(t, '%H:%M')

def to_string(t : datetime):
    return datetime.strftime(t, '%H:%M')


class VoteCountReachedEvent:
    def __init__(self, poll_id, start_time):
        self.poll_id = poll_id
        self.start_time = start_time
    
class StartTimePoll(Poll):
    # min_votes = 5
    min_votes = 1 # TODO
    
    def __init__(self, pokemon, timer : timedelta, location, creator):
        super().__init__(creator)
        
        self.pokemon = pokemon
        self.end_time = datetime.now() + timer
        self.location = location
              
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
        desc = '#{} {} {} (ends: {})'.format(self.id_string(), self.pokemon, self.location, to_string(self.end_time))
        return desc

    def message(self):
        msg = ''
        msg += '<b>{}</b> (tot {})'.format(self.pokemon, to_string(self.end_time))
        if self.closed:
            msg += ' <b>[{}]</b>'.format(StartTimePoll.closed_text)
        msg += '\n'
        msg += '{}\n'.format(self.location)
        msg += '\n'
        msg += 'Hier kan je stemmen voor de start tijd.\n'
        msg += 'Vanaf vijf stemmen voor een bepaalde tijd wordt er een raid poll aangemaakt voor die tijd.\n'
        for time, voters in self.times.items():
            msg += '<b>{}</b> [{}]: {}\n'.format(time, len(voters), ', '.join(voters.values()))
        msg += '\n'
        msg += '{} {}\n'.format(StartTimePoll.created_by_text, self.creator)
        msg += '#{}'.format(self.id_string())
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