from datetime import datetime
import itertools

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from common import from_string, to_string, to_time_string
import config
import pokedex
from poll import Poll


if not config.enable_translations:
    _ = lambda s: s



class Voter:
    def __init__(self, id, name, level):
        self.id = id
        self.name = name
        self.level = level
        self.count = 1

    def add_player(self, name, level):
        self.name = name
        self.level = level
        self.count +=1


class Voters:
    def __init__(self):
        self.voters = []
        return

    def add(self, id, name, level):
        idx = self.__index_of(id)
        if idx != -1:
            self.voters[idx].add_player(name, level)
        else:
            self.voters.append(Voter(id, name, level))

    def remove(self, id):
        idx = self.__index_of(id)
        if idx != -1:
            del self.voters[idx]

    def total_count(self):
        count = 0
        for voter in self.voters:
            count += voter.count
        return count
    
    def exists(self, id):
        return self.__index_of(id) > -1

    def __index_of(self, id):
        i = 0
        for voter in self.voters:
            if voter.id == id:
                return i
            i += 1
        return -1
        
    def sort_by_level(self):
        self.voters = sorted(self.voters, key = lambda x : x.level, reverse = True)



class RaidPoll(Poll):
    # The vote count of the last option is not visualized!
    # This options is used to unsubscribe.
    options = [_('Subscribe'), _('Unsubscribe')]
    option_emojis = [u'\U00002705', None] # # white heavy check mark
    show_names = [True, False]
    
    def reply_markup(self):
        if self.closed or self.deleted or self.finished:
            return InlineKeyboardMarkup([])

        row = []
        for i in range(0, len(RaidPoll.options)):
            row.append(InlineKeyboardButton(RaidPoll.options[i], callback_data=str(i)))
        return InlineKeyboardMarkup([row])

    def __init__(self, pokemon, time : datetime, location, creator):
        super().__init__(pokemon, time, location, creator)

        self.time_poll_id = None

        self.all_voters = [Voters()]

    def message(self):
        # disabled: image is too big on phones and we can't change the preview size
        # msg = '<a href=\"{}\">&#8205;</a>\n'.format(self.img_url)
        msg = ''
        msg += '<b>{} {}</b>'.format(self.pokemon, self.time_string())
        msg += super().description_suffix()
        msg += '\n'
        msg += '{}'.format(self.location)
        
        if self.deleted:
            if self.deleted_reason is not None:
                msg += '\n{}'.format(self.deleted_reason)
            msg += '\n#{}'.format(self.id_string())
            return msg
        
        msg += '\n\n'
        weaknesses = []
        try:
            for weakness in pokedex.raid_bosses[self.pokemon.lower()]:
                weaknesses.append('<b>{}</b>'.format(weakness) if weakness[-2:]=='x2' else weakness)
        except:
            pass
        msg += 'Weaknesses: {}\n\n'.format(', '.join(weaknesses))
        
        if self.closed and self.closed_reason:
            msg += '{}: {}\n\n'.format(_('Closure reason'), self.closed_reason)
        
        for i in range(0, len(self.all_voters)):
            emoji = RaidPoll.option_emojis[i]
            if emoji:
                msg += emoji + ' '
            voters = self.all_voters[i]

            msg += '<b>{}</b> [{}]\n'.format(RaidPoll.options[i], voters.total_count())
            if RaidPoll.show_names[i]:
                for voter in voters.voters:
                    prefix = '[Lvl {}]'.format(str(voter.level).rjust(2, ' ') if voter.level>0 else '??')
                    suffix = '({})'.format(voter.count) if voter.count > 1 else ''
                    msg += '    {} {} {}\n'.format(prefix, voter.name, suffix)
            msg += '\n'

        msg += '{} {}\n'.format(_('Poll created by'), self.creator)
        msg += '#{}'.format(self.id_string())
        return msg

    def add_vote(self, id, name, level, choice):
        changed = False
        first_vote = not self.all_voters[0].exists(id)

        # clunky but whatever
        if choice is 0: # I can come
            # Multiple votes will increase a voter's player count
            self.all_voters[0].add(id, name, level)
            changed = True
        
        if choice is 1: # I can't come (anymore)
            # don't care about these users so don't store anything
            if not first_vote:
                self.all_voters[0].remove(id)
                changed = True

        if changed and first_vote:
            self.all_voters[0].sort_by_level()
        return changed