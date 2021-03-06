"""
Copyright 2017 Tim Leysen

This file is part of PoGoPollBot.

PoGoPollBot is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PoGoPollBot is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from datetime import datetime, timedelta, time
import itertools
import logging
import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import zope.event

from common import from_string, to_string, to_time_string
import config
import pokedex
from poll import Poll


if not config.enable_translations:
    _ = lambda s: s



class VoteCountReachedEvent:
    def __init__(self, poll_id, start_time):
        self.poll_id = poll_id
        self.start_time = start_time


class TimePoll(Poll):
    min_votes = 3 if not config.test_version else 1
    max_times = 3
    
    def __init__(self, pokemon, end_time : datetime, location, creator):
        super().__init__(pokemon, end_time, location, creator)
              
        self.times = {} # key: start time, value: voters
        for time in self.calc_start_times(self.end_time):
            self.times[time] = {} # key: user id, value: user names
    
    def calc_start_times(self, end_time : datetime):
        period_minutes = 15
        min_start_delta = timedelta(minutes=10)
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
                    times.append(to_time_string(t))
                else:
                    break
        
        if len(times) > self.max_times:
            num_to_remove = len(times) - self.max_times
            return times[num_to_remove:]
        return times

    def reply_markup(self):
        if self.closed or self.deleted or self.finished:
            return InlineKeyboardMarkup([])    

        row = []
        for time in self.times:
            row.append(InlineKeyboardButton(time, callback_data=time))
        return InlineKeyboardMarkup([row])

    def message(self):
        msg = ''
        msg += '<b>{}</b> (tot {})'.format(self.pokemon, self.time_string())
        msg += super().description_suffix()
        msg += '\n'
        msg += '{}'.format(self.location)
        
        if self.deleted:
            if self.deleted_reason is not None:
                msg += '\n{}'.format(self.deleted_reason)
            msg += '\n#{}'.format(self.id_string())
            return msg        
        
        msg += '\n\n'
        if self.closed and self.closed_reason:
            msg += '{}: {}\n\n'.format(_('Closure reason'), self.closed_reason)
        desc = _('You can vote for a start time here.\n'
                 '{} votes will create a new raid poll.').format(self.min_votes)
        msg += desc + '\n\n'
        for time, voters in self.times.items():
            msg += '<b>{}</b> [{}]: {}\n'.format(time, len(voters), ', '.join(voters.values()))
        msg += '\n'
        msg += '{} {}\n'.format(_('Poll created by'), self.creator)
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

        if changed and len(self.times[user_time]) >= TimePoll.min_votes:
            logging.debug('posting VoteCountReachedEvent({}, {})'.format(self.id, user_time))
            zope.event.notify(VoteCountReachedEvent(self.id, user_time))

        return changed
        
    def vote_count_reached(self):
        times = []
        for time in self.times:
            if len(self.times[time]) >= TimePoll.min_votes:
                times.append(time)
        return times
        
        return times
        
    def get_users(self, time): # returns a dict of users: key = id, value = name
        return self.times[time]
            