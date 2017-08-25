from abc import ABCMeta, abstractmethod
from datetime import datetime
import itertools


class Poll(metaclass=ABCMeta):
    __metaclass__ = ABCMeta

    id_generator = itertools.count(1)

    def __init__(self, end_time : datetime, creator):
        self.global_id = next(self.id_generator)
        self.id = (self.global_id-1)%100 +1
        
        self.end_time = end_time
        self.creator = creator
        self.closed = False
        self.closed_reason = None
        self.deleted = False
        self.delete_reason = None
        
        self.message_id = None        
    
    def id_string(self):
        return str(self.id).zfill(3)
    
    def set_closed(self, reason = None):
        self.closed = True
        self.closed_reason = reason
        
    def set_deleted(self, reason = None):
        self.deleted = True
        self.delete_reason = reason            

    @abstractmethod    
    def reply_markup(self):
        return        

    @abstractmethod
    def description(self):
        pass    
        
    @abstractmethod    
    def message(self):
        return