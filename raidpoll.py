import itertools

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import pokedex
from poll import Poll


class Voter:
    def __init__(self, name, level):
        self.name = name
        self.level = level
        self.count = 1

    def add_player(self, level):
        self.level = level
        self.count +=1


class Voters:
    def __init__(self):
        self.voters = []
        return

    def add(self, name, level):
        idx = self.__index_of(name)
        if idx != -1:
            self.voters[idx].add_player(level)
        else:
            self.voters.append(Voter(name, level))

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


class RaidPoll(Poll):
    # The vote count of the last option is not visualized!
    # This options is used to unsubscribe.
    options = ['Ik kom',
               'Ik kom niet meer']
    show_names = [True, False]
    
    @staticmethod
    def reply_markup():
        menu = []
        for i in range(0, len(RaidPoll.options)):
            menu.append([InlineKeyboardButton(RaidPoll.options[i], callback_data=str(i))])
        return InlineKeyboardMarkup(menu)

    def __init__(self, pokemon, time, location, creator):
        super().__init__(creator)
        
        self.pokemon = pokemon
        self.img_url = 'http://floatzel.net/pokemon/black-white/sprites/images/{0}.png'\
                        .format(pokedex.get_id(pokemon))
        self.time = time
        self.location = location

        self.time_poll_id = None

        self.all_voters = [Voters()]

    def description(self):
        desc = '#{} {} {} {}'.format(self.id_string(), self.pokemon, self.time, self.location)
        if self.deleted:
            desc += ' [{}]'.format(RaidPoll.deleted_text)
        elif self.closed:
            desc += ' [{}]'.format(RaidPoll.closed_text)
        return desc

    def message(self):
        # disabled: image is too big on phones and we can't change the preview size
        # msg = '<a href=\"{}\">&#8205;</a>\n'.format(self.img_url)
        msg = ''
        msg += '<b>{} {}</b>'.format(self.pokemon, self.time)
        if self.deleted:
            msg += ' <b>[{}]</b>'.format(RaidPoll.deleted_text)
        elif self.closed:
            msg += ' <b>[{}]</b>'.format(RaidPoll.closed_text)
        msg += '\n'
        msg += '{}'.format(self.location)
        
        if self.deleted:
            msg += '\n#{}'.format(self.id_string())
            return msg
        
        msg += '\n\n'
        weaknesses = []
        for weakness in pokedex.raid_bosses[self.pokemon.lower()]:
            weaknesses.append('<b>{}</b>'.format(weakness) if weakness[-2:]=='x2' else weakness)
        msg += 'Weaknesses: {}\n\n'.format(', '.join(weaknesses))
        
        if self.closed:
            msg += '{} {}\n\n'.format(RaidPoll.closed_reason_text, self.closed_reason)
        
        for i in range(0, len(self.all_voters)):
            voters = self.all_voters[i]
            msg += '<b>{}</b> [{}]\n'.format(RaidPoll.options[i], voters.total_count())
            if RaidPoll.show_names[i]:
                for voter in voters.voters:
                    prefix = '[Lvl {}]'.format(str(voter.level).rjust(2, ' ') if voter.level>0 else '??')
                    suffix = '({})'.format(voter.count) if voter.count > 1 else ''
                    msg += '  {} {} {}\n'.format(prefix, voter.name, suffix)
            msg += '\n'

        msg += '{} {}\n'.format(RaidPoll.created_by_text, self.creator)
        msg += '#{}'.format(self.id_string())
        return msg

    def add_vote(self, name, level, choice):
        # clunky but whatever
        if choice is 0: # I can come
            # Multiple votes will increase a voter's player count
            self.all_voters[0].add(name, level)
        
        if choice is 1: # I can't come (anymore)
            # don't care about these users so don't store anything
            self.all_voters[0].remove(name)