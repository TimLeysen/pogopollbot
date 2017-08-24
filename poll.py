import itertools

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import pokedex


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


class Poll:
    id_generator = itertools.count(1)

    # The vote count of the last option is not visualized!
    # This options is used to unsubscribe.
    options = ['Ik kom',
               'Ik kom niet meer']
    show_names = [True, False]
    closed_text = 'GESLOTEN'
    closed_reason_text = 'Gesloten wegens:'
    deleted_text = 'VERWIJDERD'
    created_by_text = 'Poll aangemaakt door'
    
    @staticmethod
    def reply_markup():
        menu = []
        for i in range(0, len(Poll.options)):
            menu.append([InlineKeyboardButton(Poll.options[i], callback_data=str(i))])
        return InlineKeyboardMarkup(menu)

    def __init__(self, pokemon, time, location, creator):
        self.global_id = next(self.id_generator)
        self.id = (self.global_id-1)%100 +1
        self.pokemon = pokemon
        self.img_url = 'http://floatzel.net/pokemon/black-white/sprites/images/{0}.png'\
                        .format(pokedex.get_id(pokemon))
        self.time = time
        self.location = location
        self.creator = creator
        self.closed = False
        self.closed_reason = None
        self.deleted = False
        self.delete_reason = None
        
        self.message_id = None
        self.time_poll_id = None

        self.all_voters = [Voters()]

    def description(self):
        desc = '#{} {} {} {}'.format(self.id_string(), self.pokemon, self.time, self.location)
        if self.deleted:
            desc += ' [{}]'.format(Poll.deleted_text)
        elif self.closed:
            desc += ' [{}]'.format(Poll.closed_text)
        return desc

    def id_string(self):
        return str(self.id).zfill(3)

    def message(self):
        # disabled: image is too big on phones and we can't change the preview size
        # msg = '<a href=\"{}\">&#8205;</a>\n'.format(self.img_url)
        msg = ''
        msg += '<b>{} {}</b>'.format(self.pokemon, self.time)
        if self.deleted:
            msg += ' <b>[{}]</b>'.format(Poll.deleted_text)
        elif self.closed:
            msg += ' <b>[{}]</b>'.format(Poll.closed_text)
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
            msg += '{} {}\n\n'.format(Poll.closed_reason_text, self.closed_reason)
        
        for i in range(0, len(self.all_voters)):
            voters = self.all_voters[i]
            msg += '<b>{}</b> [{}]\n'.format(Poll.options[i], voters.total_count())
            if Poll.show_names[i]:
                for voter in voters.voters:
                    prefix = '[Lvl {}]'.format(str(voter.level).rjust(2, ' ') if voter.level>0 else '??')
                    suffix = '({})'.format(voter.count) if voter.count > 1 else ''
                    msg += '  {} {} {}\n'.format(prefix, voter.name, suffix)
            msg += '\n'

        msg += '{} {}\n'.format(Poll.created_by_text, self.creator)
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
        
    def set_closed(self, reason = None):
        self.closed = True
        self.closed_reason = reason
        
    def set_deleted(self, reason = None):
        self.deleted = True
        self.delete_reason = reason