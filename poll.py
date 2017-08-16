from enum import Enum

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import pokedex


class Poll:
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

        self.all_voters = [[],[],[]]

    def description(self):
        return '{} {} {}{}'.format(self.pokemon, self.time,
            self.location, ' [CLOSED]' if self.closed else '')

    def message(self):
        msg = '<a href=\"{}\">&#8205;</a>\n'.format(self.img_url)
        msg += '<b>{} {}{}</b>\n{}\n\n'.format(self.pokemon, self.time,
            ' [CLOSED]' if self.closed else '', self.location)
        for i in range(0, len(self.all_voters)):
            voters = self.all_voters[i]
            msg += '<b>{}</b> [{}]\n'.format(Poll.options[i], len(voters))
            if Poll.show_names[i]:
                for voter in voters:
                    msg += '  {}\n'.format(voter)
            msg += '\n'

        msg += '\nPoll created by {}'.format(self.creator)
        return msg

    def add_vote(self, name, idx):
        # feels bad
        for i in range(0, len(self.all_voters)):
            if name in self.all_voters[i]:
                self.all_voters[i].remove(name)
                break

        self.all_voters[idx].append(name)
        
    def set_closed(self):
        self.closed = True
