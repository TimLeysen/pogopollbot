from enum import Enum

from telegram import InlineKeyboardButton, InlineKeyboardMarkup



class Poll:
    options = ['Aanwezig',
               'Ik kom pas later (volgende groep)',
               'Niet aanwezig']
    show_names = [True, True, False]
    
    @staticmethod
    def reply_markup():
        menu = []
        for i in range(0, len(Poll.options)):
            menu.append([InlineKeyboardButton(Poll.options[i], callback_data=str(i))])
        return InlineKeyboardMarkup(menu)

    def __init__(self, pokemon, time, location, creator):
        self.pokemon = pokemon
        self.time = time
        self.location = location
        self.creator = creator

        self.all_voters = [[],[],[]]

    def description(self):
        return '{} {} {}'.format(self.pokemon, self.time, self.location)
        
    def message(self):
        msg = '<b>{0} {1}</b>\n{2}\n\n'.format(self.pokemon, self.time, self.location)
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