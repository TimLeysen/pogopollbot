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

from abc import ABCMeta, abstractmethod
from datetime import datetime
import itertools

from common import from_string, to_string, to_time_string
import config
import pokedex


class Poll(metaclass=ABCMeta):
    __metaclass__ = ABCMeta

    id_generator = itertools.count(1)
    closed_suffix = ' <b>[{}]</b>'.format(_('CLOSED'))
    deleted_suffix = ' <b>[{}]</b>'.format(_('DELETED'))
    finished_suffix = ' <b>[{}]</b>'.format(_('FINISHED'))

    def __init__(self, pokemon, end_time : datetime, location, creator, exclusive=False):
        self.global_id = next(self.id_generator)
        self.id = (self.global_id-1)%1000 +1
        
        self.pokemon = pokemon
        # self.img_url = 'http://floatzel.net/pokemon/black-white/sprites/images/{0}.png'\
        #                 .format(pokedex.get_id(pokemon))
        self.end_time = end_time
        self.location = location
        self.creator = creator
        self.exclusive = exclusive

        self.closed = False
        self.closed_reason = None
        self.deleted = False
        self.deleted_reason = None
        self.finished = False

        if self.exclusive:
            self.channel_name = config.exclusive_raids_channel_id
        else:
            self.channel_name = config.raids_channel_id
        self.chat_id = None
        self.message_id = None
    
    def id_string(self):
        return str(self.id).zfill(3)
    
    def description(self):
        desc = '#{} {} {} {}'.format(self.id_string(), self.pokemon, self.time_string(), self.location)
        desc += self.description_suffix()
        return desc

    def description_suffix(self):
        # order matters
        # finished polls are also deleted
        # delete and finished polls are also closed
        suffix = ''
        if self.finished:
            suffix += ' [{}]'.format(_('FINISHED'))
        elif self.deleted:
            suffix += ' [{}]'.format(_('DELETED'))
        elif self.closed:
            suffix += ' [{}]'.format(_('CLOSED'))
        return suffix

    def time_string(self):
        if self.exclusive:
            return to_string(self.end_time)
        return to_time_string(self.end_time)
        
    def set_closed(self, reason = None):
        self.closed = True
        self.closed_reason = reason
        
    def set_deleted(self, reason = None):
        self.deleted = True
        self.deleted_reason = reason
        
    def set_finished(self):
        self.finished = True

    @abstractmethod    
    def reply_markup(self):
        return        
        
    @abstractmethod    
    def message(self):
        return