from enum import Enum

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import pokedex


class Voter:
    def __init__(self, name):
        self.name = name
        self.count = 1

    def add_player(self):
        self.count +=1
        
class Voters:
    def __init__(self):
        self.voters = []
        return

    def add(self, name):
        idx = self.__index_of(name)
        if idx != -1:
            self.voters[idx].add_player()
        else:
            self.voters.append(Voter(name))

    def remove(self, name):
        idx = self.__index_of(name)
        if idx != -1:
            del self.voters[idx]

    def total_count(self):
        count = 0
        for voter in self.voters:
            count += voter.count
        return count
    
    def __index_of(self, name):
        i = 0
        for voter in self.voters:
            if voter.name == name:
                return i
            i += 1
        return -1
    

class Poll:
    # last option is not visualized!
    options = ['Ik kom',
               'Ik kan pas later (volgende groep)',
               'Ik kom niet']
    show_names = [True, True, False]
    
    @staticmethod
    def reply_markup():
        menu = []
        for i in range(0, len(Poll.options)):
            menu.append([InlineKeyboardButton(Poll.options[i], callback_data=str(i))])
        return InlineKeyboardMarkup(menu)

    def __init__(self, pokemon, time, location, creator):
        self.pokemon = pokemon
        self.img_url = 'http://floatzel.net/pokemon/black-white/sprites/images/{0}.png'\
                        .format(pokedex.get_id(pokemon))
        self.time = time
        self.location = location
        self.creator = creator
        self.closed = False

        # self.present = Choice()
        # self.later = Choice()
        # self.not_present = Choice()
        self.all_voters = [Voters(), Voters()]

    def description(self):
        return '{} {} {}{}'.format(self.pokemon, self.time,
            self.location, ' [CLOSED]' if self.closed else '')

    def message(self):
        # disabled: image is too big on phones
        # msg = '<a href=\"{}\">&#8205;</a>\n'.format(self.img_url)
        msg = ''
        msg += '<b>{} {}{}</b>\n{}\n\n'.format(self.pokemon, self.time,
            ' [CLOSED]' if self.closed else '', self.location)
        for i in range(0, len(self.all_voters)):
            voters = self.all_voters[i]
            msg += '<b>{}</b> [{}]\n'.format(Poll.options[i], voters.total_count())
            if Poll.show_names[i]:
                for voter in voters.voters:
                    suffix = ' ({})'.format(voter.count) if voter.count > 1 else ''
                    msg += '  {}{}\n'.format(voter.name, suffix)
            msg += '\n'

        msg += 'Poll created by {}'.format(self.creator)
        return msg

    def add_vote(self, name, choice):
        # clunky but whatever
        if choice is 0: # ik kom
            # Multiple votes will increase a voter's player count
            self.all_voters[0].add(name)
            self.all_voters[1].remove(name)

        if choice is 1: # ik kan pas later
            # Multiple votes will increase a voter's player count
            self.all_voters[0].remove(name)
            self.all_voters[1].add(name)
        
        if choice is 2: # ik kom niet (meer)
            # don't care about these users so don't store anything
            self.all_voters[0].remove(name)
            self.all_voters[1].remove(name)
        
    def set_closed(self):
        self.closed = True
