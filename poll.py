from abc import ABCMeta, abstractmethod
from datetime import datetime
import itertools

import config

class Poll(metaclass=ABCMeta):
    __metaclass__ = ABCMeta

    id_generator = itertools.count(1)
    closed_suffix = ' <b>[{}]</b>'.format(_('CLOSED'))
    deleted_suffix = ' <b>[{}]</b>'.format(_('DELETED'))
    finished_suffix = ' <b>[{}]</b>'.format(_('FINISHED'))

    def __init__(self, end_time : datetime, creator):
        self.global_id = next(self.id_generator)
        self.id = (self.global_id-1)%100 +1
        
        self.end_time = end_time
        self.creator = creator
        self.closed = False
        self.closed_reason = None
        self.deleted = False
        self.delete_reason = None
        self.finished = False
        
        self.message_id = None        
    
    def id_string(self):
        return str(self.id).zfill(3)
    
    def set_closed(self, reason = None):
        self.closed = True
        self.closed_reason = reason
        
    def set_deleted(self, reason = None):
        self.deleted = True
        self.delete_reason = reason
        
    def set_finished(self):
        self.finished = True

    @abstractmethod    
    def reply_markup(self):
        return        

    @abstractmethod
    def description(self):
        pass    
        
    @abstractmethod    
    def message(self):
        return
        
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