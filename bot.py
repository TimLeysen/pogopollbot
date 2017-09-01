"""
BotFather /setdescription
help - shows the help message
poll - starts a raid poll
pollex - starts an exclusive poll
raid - reports a raid
close - closes a poll
delete - deletes a poll
list - lists all polls
setlevel - sets your trainer level (PM only)
"""

from datetime import date,datetime,timedelta
import logging
import os
import pickle
import random
import threading
import time

from telegram import CallbackQuery, Chat, ChatMember
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import (TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError)
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext.dispatcher import run_async
import zope.event

import config
import database
# import eastereggs
import pokedex
from poll import Poll
from raidpoll import RaidPoll
from timepoll import TimePoll, VoteCountReachedEvent



updater = Updater(config.bot_token, workers=32)
bot = updater.bot
dispatcher = updater.dispatcher

# key: Poll.id, value: Poll
polls = {}

# level_3_bosses = ['Flareon','Jolteon','Vaporeon','Gengar','Machamp','Alakazam','Arcanine']
# level_4_bosses = ['Venusaur','Blastoise','Charizard','Rhydon','Snorlax','Tyranitar','Lapras']
# level_5_bosses = ['Moltres','Zapdos','Articuno','Lugia','Ho-Oh','Mewtwo']
# allowed_bosses_to_report = sorted(level_3_bosses + level_4_bosses + level_5_bosses)

class Settings:
    def __init__(self):
        self.enable_raid_command = False

settings = Settings()

"""
Helper functions
"""

# Sends a message to both the main and the bot chat
# Messages: created/closed/deleted a poll
def send_message(msg):
    logging.info('send message: {}'.format(msg))
    bot.send_message(chat_id=config.bot_chat_id, text=msg, disable_web_page_preview=True)
    bot.send_message(chat_id=config.main_chat_id, text=msg, disable_web_page_preview=True)

# Sends a message to the bot chat
# Normally we would use send_command_message but __create_poll e.g. can't do this cause it has no update object
def send_bot_chat_message(msg):
    logging.info('send bot chat message: {}'.format(msg))
    bot.send_message(chat_id=config.bot_chat_id, text=msg, disable_web_page_preview=True)

# Send a message to the channel where a user used a command
# This is mainly for giving information when using a command wrong.
def send_command_message(update, msg):
    logging.info('send command message: {}'.format(msg))
    bot.send_message(chat_id=update.message.chat_id, text=msg,
                     disable_web_page_preview=True, parse_mode='markdown')

# Test if a user is allowed to send commands to the bot
def authorized(update):
    if update.message.chat_id != config.bot_chat_id:
        logging.warning('Unauthorized access from {} (wrong chat)'\
            .format(update.message.from_user.name))
        # bot.send_message(chat_id=update.message.chat_id, text='Not authorized')
        return False
    return True

def private_chat(update):
    return update.message.chat.type == Chat.PRIVATE
    
# Test if a user is authorized and an admin
def admin(update, print_warning=True):
    if not authorized(update):
        return

    chat_id = config.bot_chat_id
    user_id = update.message.from_user.id
    try:
        member = bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        is_admin = member.status in [ChatMember.ADMINISTRATOR, ChatMember.CREATOR]
        all_users_are_admins = update.message.chat.all_members_are_administrators
        if is_admin or all_users_are_admins:
            return True
    except:
        pass

    if print_warning:
        msg = 'Only admins can use that command.'
        send_command_message(update, msg)
        
    user_name = update.message.from_user.name
    logging.warning('Unauthorized access from {} (not an admin)'.format(user_name))
    return False

def poll_exists(id : int):
    return id in polls
    
def get_poll(chat_id, msg_id):
    for poll in polls.values():
        if poll.chat_id == chat_id and poll.message_id == msg_id:
            return poll
    raise ValueError('Poll with message_id {} in chat with id {} does not exist!'.format(msg_id, chat_id))

def parse_poll_id_arg(update, arg : str):
    id = arg.lstrip('#')
    if not id.isdigit() or not poll_exists(int(id)):
        msg = 'Unknown poll id. Type /list to see all poll ids'
        send_command_message(update, msg)
        raise ValueError('Incorrect format: unknown poll id')
    return int(id)

def __post_poll(poll):
    try:
        msg = bot.send_message(chat_id=poll.channel_name,
                               text=poll.message(),
                               reply_markup=poll.reply_markup(),
                               parse_mode='html')
        poll.chat_id = msg.chat.id
        poll.message_id = msg.message_id
    except Exception as e:
        logging.error('Failed to create poll message for start time poll {}'.format(poll.id))
        logging.exception(e)
        raise e

def update_poll_message(poll):
    try:
        logging.info('Update poll message for poll with id {}'.format(poll.id))
        bot.edit_message_text(chat_id=poll.chat_id, message_id=poll.message_id,
                              text=poll.message(), reply_markup=poll.reply_markup(),
                              parse_mode='html')
    except Exception as e:
        logging.error('Failed to edit message text for poll {} with message id {}'\
                        .format(poll.id, poll.message_id))
        logging.exception(e)

def log_command(update, command, args = None):
    msg = update.message
    user = msg.from_user
    command = '{} {}'.format(command, ', '.join(args) if args is not None else '')
    if msg.chat.type == Chat.PRIVATE:
        chat_title = 'private'
    else:
        chat_title = update.message.chat.title
    logging.info('{} ({}) used command \'{}\' in chat {}'.format(user.name, user.id, command, chat_title))

def __delete_poll_message(poll):
    bot.delete_message(chat_id = poll.chat_id, message_id=poll.message_id)
    del[polls[poll.id]]

def start_on_timer(seconds, f, args):
    threading.Timer(seconds, f, args).start()



"""
Command argument parsing
"""

def parse_args_pokemon(update, arg):
    pokemon = pokedex.capwords(arg)
    if not pokedex.name_exists(pokemon):
        msg = '{} is not a Pokemon. Please check your spelling!'.format(pokemon)
        send_command_message(update, msg)
        raise ValueError('Passed argument is not a Pokemon')

    return pokemon

def parse_args_date(update, arg): # returns date
    try:
        d = datetime.strptime(arg, '%d/%m').date()
    except:
        msg = '{} is not a date. Expected format: day/month. For example: 1/9'.format(arg)
        send_command_message(update, msg)
        raise ValueError('Incorrect date format. Expected %d/%m.')

    year = datetime.now().year
    return date(year, d.month, d.day)

def parse_args_time(update, arg): # returns time
    try:
        return datetime.strptime(arg, '%H:%M').time()
    except:
        msg = '{} is not a time. Expected format: hour:minute. For example: 13:00'.format(arg)
        send_command_message(update, msg)
        raise ValueError('Incorrect time format. Expected %H:%M.')

def parse_args_timer(update, arg): # returns timedelta
    timer = arg
    try:
        t = datetime.strptime(timer, '%H:%M').time()
        timer = timedelta(hours=t.hour, minutes=t.minute)
    except:
        msg = '{} is not a timer. Expected format: hour:minute. For example: 1:45.'.format(arg)
        send_command_message(update, msg)
        raise ValueError('Incorrect timer format. Expected %H:%M.')

    if timer.total_seconds() > 7200:
        msg = 'Timer should be less than 2:00.'
        send_command_message(update, msg)
        raise ValueError(msg)

    return timer

def __add_date_to_time(t : time):
    now = datetime.now()
    d = now.date()
    if now.time() > t:
        d += timedelta(days=1)
    return datetime.combine(d, t)

"""
Bot commands
"""

def start_poll(bot, update, args):
    log_command(update, start_poll.__name__, args)
    if not authorized(update):
        return

    if len(args) < 3:
        msg = 'Incorrect format. Usage: /poll <raid-boss> <time> <location>. For example: /poll Moltres 13:00 Park Sint-Niklaas'
        send_command_message(update, msg)
        raise ValueError('Incorrect format: expected three arguments: raid boss, time, location')

    try:
        pokemon = parse_args_pokemon(update, args[0])
        t = parse_args_time(update, args[1])
        location = ' '.join(args[2:])
    except ValueError as e:
        logging.info(e)
        return

    dt = __add_date_to_time(t)
    creator = update.message.from_user.name
    __create_poll(pokemon, dt, location, creator, exclusive=False)

def start_exclusive_poll(bot, update, args):
    log_command(update, start_poll.__name__, args)
    if not authorized(update):
        return

    if len(args) < 4:
        msg = 'Incorrect format. Usage: /pollex <raid-boss> <date> <time> <location>. For example: /pollex Mewtwo 1/9 13:00 Park Sint-Niklaas'
        send_command_message(update, msg)
        raise ValueError('Incorrect format: expected four arguments: raid boss, date, time, location')

    try:
        pokemon = parse_args_pokemon(update, args[0])
        d = parse_args_date(update, args[1])
        t = parse_args_time(update, args[2])
        location = ' '.join(args[3:])
    except ValueError as e:
        logging.info(e)
        return

    dt = datetime.combine(d, t)
    print(dt)
    creator = update.message.from_user.name
    __create_poll(pokemon, dt, location, creator, exclusive=True)

def __create_poll(pokemon, dt : datetime, location, creator, exclusive):
    poll = RaidPoll(pokemon, dt, location, creator, exclusive)

    try:
        __post_poll(poll)
    except:
        msg = 'Error posting poll {}'.format(poll.description())
        send_bot_chat_message(msg)
        return
    
    polls[poll.id] = poll

    prefix = 'an exclusive' if poll.exclusive else 'a'
    msg = '{} created {} raid poll: {}.\n'.format(creator, prefix, poll.description())
    msg += 'You can subscribe in {}'.format(poll.channel_name)
    send_message(msg)

    close_poll_on_timer(poll.id)
    delete_poll_on_timer(poll.id)
    
    # dispatcher.run_async(eastereggs.check_poll_count, *(bot, poll.global_id))
    
    return poll

@run_async
def close_poll_on_timer(poll_id, silent=False):
    poll = polls[poll_id]

    if poll.end_time > datetime.now():
        delta = poll.end_time - datetime.now()
    else:
        logging.warning('close_poll_on_timer: poll end time is earlier than now. '\
                        'Closing poll anyway. {}'.format(poll.description()))

    start_on_timer(delta.seconds, __close_poll, [poll_id, _('time expired'), None, silent])

def parse_args_close_poll(update, args):
    if len(args) < 1:
        msg = 'Incorrect format. Usage: /close <id> (<reason>). For example: /close 0, /close 0 Duplicate poll'
        send_command_message(update, msg)
        raise ValueError('Incorrect format: expected at least 1 argument')

    id = parse_poll_id_arg(update, args[0])
    reason = ' '.join(args[1:]) if len(args) > 1 else None
    
    return id, reason
    
def close_poll(bot, update, args):
    log_command(update, close_poll.__name__, args)
    if not authorized(update):
        return

    try:
        poll_id, reason = parse_args_close_poll(update, args)
    except ValueError as e:
        logging.info(e)
        return

    __close_poll(poll_id, reason, update, silent=False)
    
    return

# TODO: id exists is checked in close_poll (user command) but also here...
def __close_poll(poll_id, reason=None, update=None, silent=False):
    if not poll_exists(poll_id):
        logging.info('Poll does not exist anymore')
        return

    poll = polls[poll_id]
    if poll.closed:
        msg = 'Poll {} is already closed'.format(poll.id)
        if update:
            send_command_message(update, msg)
        else:
            logging.info(msg)
        return
    
    description = poll.description()
    poll.set_closed(reason)
    update_poll_message(poll)

    if update:
        msg = '{} closed a poll: {}.'.format(update.message.from_user.name, description)
        if reason:
            msg += ' Reason: {}.'.format(reason)
    else:
        msg = 'A raid is starting: {}.'.format(description)
    
    if silent:
        logging.info(msg)
    else:
        send_message(msg)

    
def delete_all_polls(bot, update):
    log_command(update, delete_all_polls.__name__)
    if not admin(update):
        return
    
    for poll in polls.values():
        try:
            bot.delete_message(chat_id=poll.chat_id, message_id=poll.message_id)
        except Exception as e:
            logging.error('Failed to delete poll {} with message id {}'.format(poll.id, poll.message_id))
            logging.exception(e)
    polls.clear()

    msg = '{} deleted all polls.'.format(update.message.from_user.name)
    send_message(msg)


@run_async
def delete_poll_on_timer(poll_id):
    poll = polls[poll_id]
    delta = timedelta(hours=1)
    if (poll.end_time + delta) > datetime.now():
        delta = poll.end_time + delta - datetime.now()
    else: # test poll or poll with wrong time or too many worker threads busy and this function is called way too late!
        logging.warning('delete_poll_on_timer: poll end time is earlier than now. '\
                        'Deleting poll anyway. {}'.format(poll.description()))

    start_on_timer(delta.seconds, __delete_poll, [poll_id])


# TODO: almost the same code as close_poll
def parse_args_delete_poll(update, args):
    if len(args) < 1:
        msg = 'Incorrect format. Usage: /delete <id> (<reason>). For example: /delete 0, /delete 0 Duplicate poll'
        send_command_message(update, msg)
        raise ValueError('Incorrect format: expected at least 1 argument')

    id = parse_poll_id_arg(update, args[0])
    reason = ' '.join(args[1:]) if len(args) > 1 else None
    
    return id, reason
    
    
def delete_poll(bot, update, args):
    log_command(update, delete_poll.__name__, args)
    if not authorized(update):
        return

    try:
        poll_id, reason = parse_args_delete_poll(update, args)
    except ValueError as e:
        logging.info(e)
        return
    
    # Check if the user that tries to delete a poll is the creator of that poll or an admin
    poll = polls[poll_id]
    user_name = update.message.from_user.name
    own_poll = user_name == poll.creator
    if not own_poll and not admin(update, print_warning=False):
        msg = '{}, you cannot delete polls that you did not create yourself'.format(user_name)
        send_command_message(update, msg)
        return

    __delete_poll(poll_id, reason, update)


def __delete_poll(poll_id, reason=None, update=None):
    if not poll_exists(poll_id):
        logging.info('Poll {} has already been deleted'.format(poll_id))
        return

    poll = polls[poll_id]
    description = poll.description()
    poll.set_deleted(reason)
    if update is None: # automatically deleted
        poll.set_finished()
    update_poll_message(poll)
    
    if update is not None:
        msg = '{} deleted a poll: {}.'.format(update.message.from_user.name, description)
        if reason is not None:
            msg += ' Reason: {}.'.format(reason)
        send_command_message(update, msg)
    else:
        msg = 'Automatically deleted a poll: {}.'.format(description)
        logging.info(msg)
        # Pretty useless information so don't send it to the chat
        # bot.send_message(chat_id=config.bot_chat_id, text=msg)
        
    del polls[poll_id]

def list_polls(bot, update):
    log_command(update, list_polls.__name__)
    if not authorized(update):
        return

    msg = ''
    for id, poll in sorted(polls.items()):
        msg += '{}\n'.format(poll.description())

    if not msg:
        msg = 'No polls found'

    send_command_message(update, msg)

def __verify_pokemon(update, pokemon_list):
    for pokemon in pokemon_list:
        if not pokedex.name_exists(pokemon):
            msg = '{} is not a Pokemon! Check your spelling!'.format(pokemon)
            send_command_message(update, msg)
            return False
    return True
    
def __print_bosses():
    return ', '.join(allowed_bosses_to_report)    
    
def set_bosses(bot, update, args):
    log_command(update, set_bosses.__name__)
    if not authorized(update):
        return
    
    if not __verify_pokemon(update, args):
        return

    bosses = sorted(list(set([pokedex.capwords(x) for x in args])))
    global allowed_bosses_to_report
    allowed_bosses_to_report = bosses
    
    msg = 'Users can now report the following raid bosses: {}'\
            .format(__print_bosses())
    send_command_message(update, msg)

def add_bosses(bot, update, args):
    log_command(update, add_bosses.__name__)
    if not authorized(update):
        return

    if not __verify_pokemon(update, args):
        return

    new_bosses = sorted(list(set([pokedex.capwords(x) for x in args])))
    global allowed_bosses_to_report
    allowed_bosses_to_report.extend([x for x in new_bosses if x not in allowed_bosses_to_report])
    allowed_bosses_to_report = sorted(allowed_bosses_to_report)
    
    msg = 'Users can now report the following raid bosses: {}'\
            .format(__print_bosses())
    send_command_message(update, msg)

def rem_bosses(bot, update, args):
    log_command(update, rem_bosses.__name__)
    if not authorized(update):
        return

    if not __verify_pokemon(update, args):
        return

    new_bosses = sorted(list(set([pokedex.capwords(x) for x in args])))
    global allowed_bosses_to_report
    allowed_bosses_to_report = [x for x in allowed_bosses_to_report if x not in new_bosses]
    allowed_bosses_to_report = sorted(allowed_bosses_to_report)

    msg = 'Users can now report the following raid bosses: {}'\
            .format(__print_bosses())
    send_command_message(update, msg)
    
def list_bosses(bot, update, args):
    log_command(update, list_bosses.__name__)
    if not authorized(update):
        return

    msg = 'Users can report the following raid bosses: {}'\
            .format(__print_bosses())
    send_command_message(update, msg)
    
def help(bot, update):
    # log_command(update, help.__name__)
    if not private_chat(update):
        return

    msg = '*POWER USER COMMANDS*:\n'\
          '/poll <pokemon> <time> <location>\n'\
          'Starts a new raid poll.\n'\
          'Example: /poll Snorlax 13:30 Central station\n\n'\
          \
          '/pollex <pokemon> <date> <time> <location>\n'\
          'Starts a new exclusive raid poll.\n'\
          'Example: /pollex Mewtwo 30/10 19:00 Central Station\n\n'\
          \
          '/close <id> (<reason>)\n'\
          'Closes the poll with id <id>. You can add a reason (optional).\n'\
          'You can see the poll ids by typing /list.\n'\
          'Example: /close 8 starting time changed\n\n'\
          \
          '/delete <id> (<reason>)\n'\
          'Deletes the poll with id <id>. You can add a reason (optional).\n'\
          'You can see the poll ids by typing /list.\n'\
          'Example: /delete 8 wrong pokemon name\n\n'\
          \
          '/list\n'\
          'Lists all polls. Shows each poll\'s id and description.\n\n\n'\

    if settings.enable_raid_command:
        msg += '*GENERAL USER COMMANDS (CHAT)*:\n'\
               '/raid <pokemon> <timer> <location>\n'\
               'Starts a new time poll for a raid where users can vote for the starting time.\n'\
               'Example: /raid Snorlax 1:45 Central Station\n\n\n'

    msg += \
          '*GENERAL USER COMMANDS (PM)*:\n'\
          '/setlevel <level>\n'\
          'Sets your trainer level to <level>.\n'\
          'Example: /setlevel 40\n\n'\
          \
          '/help\n'\
          'Shows this message\n\n\n'\
          \
          '*ADMIN COMMANDS*:\n'\
          '/deleteall\n'\
          'Deletes all polls.\n\n'\
          \
          '/enableraidcommand\n'\
          'Enables the /raid command for general users.\n\n'\
          \
          '/disableraidcommand\n'\
          'Disables the /raid command for general users.'
    send_command_message(update, msg)

"""
USER COMMANDS (CHAT)
"""
def __parse_args_report_raid(update, args): # returns raid boss : str, timer : str, location : str
    if len(args) < 3:
        msg = 'Incorrect format. Usage: /raid <pokemon> <timer> <location>. '\
              'For example: /raid Moltres 1:45 Park Sint-Niklaas'
        send_command_message(update, msg)
        raise ValueError('Incorrect format: expected three arguments: boss, timer, location')

    try:
        pokemon = parse_args_pokemon(update, args[0])
        timer = parse_args_timer(update, args[1])
        location = ' '.join(args[2:])
    except ValueError as e:
        logging.info(e)
        return        

    # Disabled so people won't complain
    # if not pokemon in allowed_bosses_to_report:
        # msg = 'Reporting {} is not allowed'.format(pokemon)
        # send_command_message(update, msg)
        # raise ValueError('Pokemon is not a raid boss or too low level')
        
    dt = datetime.now() + timer
    return pokemon, dt, location


def report_raid(bot, update, args):
    log_command(update, report_raid.__name__, args)
    if update.message.chat_id != config.main_chat_id and not authorized(update):
        return

    if not settings.enable_raid_command:
        send_command_message(update, 'The raid command is currently disabled.')
        return

    try:
        pokemon, end_time, location = __parse_args_report_raid(update, args)
    except ValueError as e:
        logging.info(e)
        return

    creator = update.message.from_user.name
    poll = TimePoll(pokemon, end_time, location, creator)
    if not poll.times:
        msg = 'Unable to choose proper start times. Please create a poll manually!'
        send_command_message(update, msg)
        return

    try:
        __post_poll(poll)
    except:
        msg = 'Error posting poll {}'.format(poll.description())
        send_command_message(update, msg)
        return
    
    polls[poll.id] = poll

    msg = '{} reported a raid: {}\n'.format(creator, poll.description())
    msg += 'You can vote for a start time in {}'.format(poll.channel_name)
    send_message(msg)
    
    dispatcher.run_async(close_poll_on_timer, *(poll.id, True))
    dispatcher.run_async(delete_poll_on_timer, *(poll.id, ))
    
    # dispatcher.run_async(eastereggs.check_poll_count, *(bot, poll.global_id))

    
"""
USER COMMANDS (PM)
"""

def set_level(bot, update, args):
    log_command(update, set_level.__name__, args)
    
    if not private_chat(update):
        return

    if len(args) != 1:
        msg = 'Wrong format. Usage: /setlevel level. Example: /setlevel 30'
        send_command_message(update, msg)
        return
    
    user = update.message.from_user

    level = args[0]
    try:
        level = int(level)
    except:
        msg = '{}, your level should be a number!'.format(user.name)
        send_command_message(update, msg)
        return
        
    if level not in range(1,41):
        msg = 'Please don\'t try to fool me {}. I\'m a smart Bulbasaur!'.format(user.name)
        send_command_message(update, msg)
        return
    
    database.set_level(user.id, user.name, level)
    msg = '{}, your level is now {}'.format(user.name, level)    
    send_command_message(update, msg)

"""
ADMIN COMMANDS
"""
    
def chat_id(bot, update):
    log_command(update, 'chat_id')
    msg = 'This chat\'s id is {}'.format(update.message.chat_id)
    send_command_message(update, msg)

def __random_pokemon():
    return random.choice(list(pokedex.raid_bosses.keys()))

def testpoll(bot, update):
    log_command(update, testpoll.__name__)

    pokemon = __random_pokemon()
    start_time = datetime.strftime(datetime.now() + timedelta(minutes=10), '%H:%M')
    start_poll(bot, update, [pokemon, start_time, 'TEST'])
    # start_poll(bot, update, ['moltres', '13:00', 'TEST'])
    # start_poll(bot, update, ['snorlax', '13:00', 'TEST'])

def testpollex(bot, update):
    log_command(update, testpollex.__name__)

    pokemon = __random_pokemon()
    hours = random.randrange(24, 72)
    dt = datetime.now() +timedelta(hours=hours)
    d = datetime.strftime(dt, '%d/%m')
    t = datetime.strftime(dt, '%H:%M')
    start_exclusive_poll(bot, update, [pokemon, d, t, 'TEST'])

def testraid(bot, update):
    log_command(update, testraid.__name__)

    pokemon = __random_pokemon()
    h = random.randrange(1, 2)
    m = random.randrange(0, 60)
    timer = '{}:{}'.format(h, str(m).zfill(2))
    report_raid(bot, update, [pokemon, timer, 'TEST'])

data_file = 'data.pickle'
def save_state(bot, update):
    log_command(update, save_state.__name__)
    if not admin(update):
        return

    if __save_state():
        send_command_message(update, 'Saved state to file')
    else:
        send_command_message(update, 'Failed to save state to file')

def __save_state():
    try:
        with open(data_file, 'wb') as f:
            data = {'id_generator' : Poll.id_generator,
                    'polls' : polls,
                    'enable_raid_command' : settings.enable_raid_command}
            pickle.dump(data, f)
        logging.info('Saved state to file')
        return True
    except Exception as e:
        logging.error('Failed to save state to file')
        logging.exception(e)    
        return False

def load_state(bot, update):
    log_command(update, load_state.__name__)
    if not admin(update):
        return

    __load_state()

def __load_state():
    global polls
    
    try:
        with open(data_file, 'rb') as f:
            data = pickle.load(f)
            Poll.id_generator = data['id_generator']
            polls = data['polls']
            settings.enable_raid_command = data['enable_raid_command']
        logging.info('Loaded state from file')
        return True
    except Exception as e:
        logging.error('Failed to load state from file')
        logging.exception(e)
        return False

def quit(bot, update):
    log_command(update, quit.__name__)
    if not admin(update):
        return
    
    __save_state()
    send_command_message(update, 'Shutting down...')
    os._exit(0)

def enable_raid_command(bot, update):
    log_command(update, enable_raid_command.__name__)
    if not admin(update):
        return

    settings.enable_raid_command = True
    __save_state()
    send_command_message(update, 'Raid command enabled. Users can now report a raid by typing /raid <pokemon> <timer> <location>.')

def disable_raid_command(bot, update):
    log_command(update, disable_raid_command.__name__)
    if not admin(update):
        return

    settings.enable_raid_command = False
    __save_state()
    send_command_message(update, 'Raid command disabled.')



"""
UNKNOWN COMMANDS
"""
def unknown_command(bot, update):
    # setlevel command will be done in pm
    if not authorized(update) and not private_chat(update):
        return

    msg = "Sorry, that command is unown to me."
    send_command_message(update, msg)    

    

"""
OTHER STUFF
"""        
def vote_callback(bot, update):
    query = update.callback_query
    chat_id = query.message.chat.id
    msg_id = query.message.message_id
    
    poll = get_poll(chat_id, msg_id)
    if type(poll) is RaidPoll:
        return __raid_poll_vote_callback(update, poll)
    
    if type(poll) is TimePoll:
        return __time_poll_vote_callback(update, poll)

        
def __raid_poll_vote_callback(update, poll):
    query = update.callback_query
    user = query.from_user
    level = database.get_level(query.from_user.id)
    choice = int(query.data)
    
    try:
        changed = poll.add_vote(user.id, user.name, level, choice)
    except KeyError as e:
        logging.info('User tried to vote for an old poll that is still open')
        return
        
    logging.info('{} voted {} on poll {} with message id {}'\
        .format(user.name, choice, poll.id, poll.message_id))

    # quite slow after the first vote from a person... takes 3s or longer to update...
    # seems to be the way how long polling works?
    if changed:
        update_poll_message(poll)

    bot.answer_callback_query(query.id)


def __time_poll_vote_callback(update, poll):
    query = update.callback_query
    user = query.from_user
    time = query.data

    try:
        results_changed = poll.add_vote(user.id, user.name, time)
    except KeyError as e:
        logging.info('User tried to vote for an old poll that is still open')
        return
        
    logging.info('{} voted {} on time poll {} with message id {}'\
        .format(user.name, time, poll.id, poll.message_id))

    times = poll.vote_count_reached()
    if times:
        __delete_poll_message(poll)
    elif results_changed:
        update_poll_message(poll)

    bot.answer_callback_query(query.id)

    
def member_joined(bot, update):
    new_members = update.message.new_chat_members
    if new_members:
        names = [x.name for x in new_members]
        logging.info('member(s) joined: {}'.format(','.join(names)))
        msg = _('Welcome {}!\n'
                'In this chat you can create a raid poll by typing e.g. /poll Snorlax 14:00 Park.\n'
                'Polls are automatically closed when the start time elapses.\n'
                'You can also manually close a poll by typing e.g. /close 8 You can see the number of the poll by typing /list.\n'
                'Please discuss a proper starting time in the main chat before creating a new poll!\n'
                'Type /help in a private message to me for more information.'
                ).format(','.join(names))
        send_command_message(update, msg)
    
def error_callback(bot, update, error):
    try:
        logging.error(error)
        raise error
    except Unauthorized:
        # remove update.message.chat_id from conversation list
        return
    except BadRequest:
        # handle malformed requests - read more below!
        return
    except TimedOut:
        # handle slow connection problems
        return
    except NetworkError:
        # handle other connection problems
        return
    except ChatMigrated as e:
        # the chat_id of a group has changed, use e.new_chat_id instead
        return
    except TelegramError:
        # handle all other telegram related errors
        return

def HandleVoteCountReachedEvent(event):
    logging.info('got event {} {}'.format(event.poll_id, event.start_time))
    
    # create a new poll if one doesn't exist yet
    for id, poll in polls.items():
        if type(poll) is RaidPoll:
            # Only allow 1 automatic poll for now
            if poll.time_poll_id == event.poll_id:# and poll.end_time == event.start_time:
                logging.info('HandleVoteCountReachedEvent: a poll has already been created for {}'\
                            .format(poll.description()))
                return

    time_poll = polls[event.poll_id]
    d = datetime.now().date()
    t = datetime.strptime(event.start_time, '%H:%M').time()
    time = datetime.combine(d, t)
    creator = bot.username
    poll = __create_poll(time_poll.pokemon, time, time_poll.location, creator, exclusive=False)
    
    poll.time_poll_id = time_poll.id

    # Add users that voted for the chosen start time to the raid poll
    for user_id, user_name in time_poll.get_users(event.start_time).items():
        logging.info('Adding {} ({}) to raid poll {} ({})'.\
            format(user_name, user_id, poll.id, poll.description()))
        poll.add_vote(user_id, user_name, database.get_level(user_id), 0)
        
    update_poll_message(poll)

zope.event.subscribers.append(HandleVoteCountReachedEvent)
        
logFormatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.INFO)

fileHandler = logging.FileHandler('log.log')
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)

# BOT USER COMMANDS
dispatcher.add_handler(CommandHandler('poll', start_poll, pass_args=True))
dispatcher.add_handler(CommandHandler('pollex', start_exclusive_poll, pass_args=True))
dispatcher.add_handler(CommandHandler('close', close_poll, pass_args=True))
dispatcher.add_handler(CommandHandler('delete', delete_poll, pass_args=True))
dispatcher.add_handler(CommandHandler('deleteall', delete_all_polls))
dispatcher.add_handler(CommandHandler('list', list_polls))
# dispatcher.add_handler(CommandHandler('setbosses', set_bosses, pass_args=True))
# dispatcher.add_handler(CommandHandler('addbosses', add_bosses, pass_args=True))
# dispatcher.add_handler(CommandHandler('rembosses', rem_bosses, pass_args=True))
# dispatcher.add_handler(CommandHandler('listbosses', list_bosses, pass_args=True))
dispatcher.add_handler(CommandHandler('help', help))

# GENERAL USER COMMANDS (CHAT)
dispatcher.add_handler(CommandHandler('raid', report_raid, pass_args=True))

# GENERAL USER COMMANDS (PM)
dispatcher.add_handler(CommandHandler('setlevel', set_level, pass_args=True))

# ADMIN COMMANDS
dispatcher.add_handler(CommandHandler('chatid', chat_id))
dispatcher.add_handler(CommandHandler('save', save_state))
dispatcher.add_handler(CommandHandler('load', load_state))
dispatcher.add_handler(CommandHandler('quit', quit))
dispatcher.add_handler(CommandHandler('enableraidcommand', enable_raid_command))
dispatcher.add_handler(CommandHandler('disableraidcommand', disable_raid_command))
if config.test_version:
    dispatcher.add_handler(CommandHandler('testpoll', testpoll))
    dispatcher.add_handler(CommandHandler('testpollex', testpollex))
    dispatcher.add_handler(CommandHandler('testraid', testraid))

# UNKNOWN COMMANDS
dispatcher.add_handler(MessageHandler(Filters.command, unknown_command))

# OTHER STUFF
dispatcher.add_handler(CallbackQueryHandler(vote_callback))
dispatcher.add_handler(MessageHandler(Filters.chat(chat_id=config.bot_chat_id), member_joined))
dispatcher.add_error_handler(error_callback)

__load_state()
updater.start_polling()
logging.info('Ready to work!')
bot.send_message(chat_id=config.bot_chat_id, text='Ready to work!')
updater.idle()
logging.error('after updater.idle()')
__save_state()