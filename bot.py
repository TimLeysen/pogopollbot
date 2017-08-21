"""
BotFather /setdescription
help - shows the help message. Example: /help
start - starts a poll. Example: /start Snorlax 13:00 Park
close - closes a poll. Example: /close 0
list - lists all polls. Example: /list
delete - deletes a poll. Example: /delete 0
deleteall - deletes all polls (admin only). Example: /deleteall
"""

from datetime import datetime,timedelta
import logging
import random
import time

from telegram import CallbackQuery, Chat, ChatMember
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import (TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError)
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram.ext import MessageHandler, Filters

import config
import pokedex
from poll import Poll



updater = Updater(config.bot_token)
dispatcher = updater.dispatcher

# key: Message, value: Poll
polls = {}


"""
Helper functions
"""

# Sends a message to both the input and output chats and logs it
# Messages: created/closed/deleted a poll
def send_message(bot, msg):
    logging.info(msg)
    bot.send_message(chat_id=config.input_chat_id, text=msg)
    bot.send_message(chat_id=config.output_chat_id, text=msg)

# Send a message to the channel where users send commands to the bots
# This is mainly for giving information when using a command wrong.
def send_command_message(bot, update, msg):
    logging.info(msg)
    bot.send_message(chat_id=update.message.chat_id, text=msg)

# Test if a user is allowed to send commands to the bot
def authorized(bot, update):
    if update.message.chat_id != config.input_chat_id:
        logging.warning('Unauthorized access from {} (wrong chat)'\
            .format(update.message.from_user.name))
        # bot.send_message(chat_id=update.message.chat_id, text='Not authorized')
        return False
    return True

# Test if a user is an admin
def admin(bot, update, print_warning=True):
    chat_id = config.input_chat_id
    user_id = update.message.from_user.id
    try:
        member = bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        # doesn't work
        # if member.status in [telegram.ChatMember.ADMINISTRATOR, telegram.ChatMember.CREATOR]:
        is_admin = member.status in ['administrator', 'creator']
        all_users_are_admins = update.message.chat.all_members_are_administrators
        if is_admin or all_users_are_admins:
            return True
    except:
        pass

    if print_warning:
        msg = 'Only admins can use that command.'
        send_command_message(bot, update, msg)
        
        user_name = update.message.from_user.name
        logging.warning('Unauthorized access from {} (not an admin)'.format(user_name))
    return False

def poll_exists(poll_id : int):
    for poll in polls.values():
        if poll_id == poll.id:
            return True
    return False
    
def get_poll_msg_id(poll_id : int):
    for msg_id, poll in polls.items():
        if poll.id == poll_id:
            return msg_id

def get_poll(poll_id : int):
    return polls[get_poll_msg_id(poll_id)]

def parse_poll_id_arg(bot, update, arg : str):
    id = arg.lstrip('#')
    if not id.isdigit() or not poll_exists(int(id)):
        msg = 'Unknown poll id. Type /list to see all poll ids'
        send_command_message(bot, update, msg)
        raise ValueError('Incorrect format: unknown poll id')
    return int(id)


"""
Bot commands
"""
    
def parse_args_start_poll(bot, update, args): # returns raid boss : str, start_time : str, location : str
    if len(args) < 3:
        msg = 'Incorrect format. Usage: /start <raid-boss> <start-time> <location>. For example: /start Moltres 13:00 Park Sint-Niklaas'
        send_command_message(bot, update, msg)
        raise ValueError('Incorrect format: expected three arguments: raid boss, start time, location')

    pokemon = args[0].capitalize() # TODO: Ho-Oh
    if not pokedex.name_exists(pokemon):
        msg = '{} is not a Pokemon. Please check your spelling!'.format(pokemon)
        send_command_message(bot, update, msg)
        raise ValueError('{} is not a Pokemon'.format(pokemon))

    # not needed and would require code changes when raid bosses change
    # if not pokedex.is_raid_boss(args[0]):
        # raise Exception('{} is not a raid boss')

    start_time = args[1]
    try:
        datetime.strptime(start_time, '%H:%M').time()
    except:
        msg = 'Incorrect time format. Expected HH:MM. For example: 13:00'
        send_command_message(bot, update, msg)
        raise ValueError('Incorrect time format: {}'.format(start_time))

    location = ' '.join(args[2:])

    return pokemon, start_time, location


def start_poll(bot, update, args):
    if not authorized(bot, update):
        return

    try:
        pokemon, start_time, location = parse_args_start_poll(bot, update, args)
    except ValueError as e:
        logging.info(e)
        return

    creator = update.message.from_user.name
    poll = Poll(pokemon, start_time, location, creator)
    msg = '{} created a poll: {}.'.format(creator, poll.description())
    send_message(bot, msg)

    msg = bot.send_message(chat_id=config.output_channel_id,
                           text=poll.message(),
                           reply_markup=poll.reply_markup(),
                           parse_mode='HTML')
    polls[msg.message_id] = poll

    dispatcher.run_async(close_poll_on_timer, *(bot, poll.id))
    dispatcher.run_async(delete_poll_on_timer, *(bot, poll.id))
   
def close_poll_on_timer(bot, poll_id):
    poll = get_poll(poll_id)
    delta = datetime.strptime(poll.time, '%H:%M') - datetime.now()
    if delta.seconds < 0: # test poll, poll with wrong time or exclusive raid
        logging.info('Poll is not closed automatically because start time is earlier than now: {}')\
            .format(poll.description())
        return

    time.sleep(delta.seconds)
    __close_poll(bot, poll_id, 'start tijd verstreken')


def parse_args_close_poll(bot, update, args):
    if len(args) < 1:
        msg = 'Incorrect format. Usage: /close <id> (<reason>). For example: /close 0, /close 0 Duplicate poll'
        send_command_message(bot, update, msg)
        raise ValueError('Incorrect format: expected at least 1 argument')

    id = parse_poll_id_arg(bot, update, args[0])
    reason = ' '.join(args[1:]) if len(args) > 1 else None
    
    return id, reason
    
def close_poll(bot, update, args):
    if not authorized(bot, update):
        return

    try:
        poll_id, reason = parse_args_close_poll(bot, update, args)
    except ValueError as e:
        logging.info(e)
        return

    __close_poll(bot, poll_id, reason, update)
    
    return

# TODO: id exists is checked in close_poll (user command) but also here...
def __close_poll(bot, poll_id, reason=None, update=None):
    if not poll_exists(poll_id):
        logging.info('Poll does not exist anymore')
        return

    poll = get_poll(poll_id)
    if poll.closed:
        msg = 'Poll {} is already closed'.format(poll.id)
        if update:
            send_command_message(bot, update, msg)
        else:
            logging.info(msg)
        return
    
    poll = poll.set_closed(reason)
    chat_id = config.output_channel_id
    bot.edit_message_text(chat_id=chat_id,
                          message_id=get_poll_msg_id(poll.id),
                          text=poll.message(),
                          parse_mode='HTML')

    if update:
        msg = '{} closed a poll: {}.'.format(update.message.from_user.name, poll.description())
        if reason:
            msg += ' Reason: {}.'.format(reason)
    else:
        msg = 'Automatically closed a poll: {}.'.format(poll.description())
    send_message(bot, msg)

    
def delete_all_polls(bot, update):
    if not authorized(bot, update) or not admin(bot, update):
        return
    
    chat_id = config.output_channel_id
    for message_id in polls.keys():
        bot.delete_message(chat_id=chat_id, message_id=message_id)
    polls.clear()

    msg = '{} deleted all polls.'.format(update.message.from_user.name)
    send_message(bot, msg)


def delete_poll_on_timer(bot, poll_id):
    poll = get_poll(poll_id)
    delta = datetime.strptime(poll.time, '%H:%M') - datetime.now()
    if delta.seconds < 0: # test poll or poll with wrong time or exclusive raid
        logging.info('Poll is not deleted automatically because start time is earlier than now: {}')\
            .format(poll.description())
        return

    # delete 1 hour after start time
    time.sleep(delta.seconds + 2)
    __delete_poll(bot, poll_id)


# TODO: almost the same code as close_poll    
def parse_args_delete_poll(bot, update, args):
    if len(args) < 1:
        msg = 'Incorrect format. Usage: /delete <id> (<reason>). For example: /delete 0, /delete 0 Duplicate poll'
        send_command_message(bot, update, msg)
        raise ValueError('Incorrect format: expected at least 1 argument')

    id = parse_poll_id_arg(bot, update, args[0])
    reason = ' '.join(args[1:]) if len(args) > 1 else None
    
    return id, reason
    
    
def delete_poll(bot, update, args):
    if not authorized(bot, update):
        return

    try:
        poll_id, reason = parse_args_delete_poll(bot, update, args)
    except ValueError as e:
        logging.info(e)
        return
    
    # Check if the user that tries to delete a poll is the creator of that poll or an admin
    poll = get_poll(poll_id)
    user_name = update.message.from_user.name
    own_poll = user_name == poll.creator
    if not own_poll and not admin(bot, update, print_warning=False):
        msg = '{}, you cannot delete polls that you did not create yourself'.format(user_name)
        send_command_message(bot, update, msg)
        return

    __delete_poll(bot, poll_id, reason, update)


def __delete_poll(bot, poll_id, reason=None, update=None):
    if not poll_exists(poll_id):
        logging.info('Poll {} has already been deleted'.info(poll_id))
        return

    poll = get_poll(poll_id).set_deleted(reason)
    chat_id = config.output_channel_id
    msg_id = get_poll_msg_id(poll.id)
    bot.edit_message_text(chat_id=chat_id,
                          message_id=msg_id,
                          text=poll.message(),
                          parse_mode='HTML')
    
    description = poll.description()
    if update is not None:
        msg = '{} deleted a poll: {}.'.format(update.message.from_user.name, description)
        if reason is not None:
            msg += ' Reason: {}.'.format(reason)
        send_message(bot, msg)
    else:
        msg = 'Automatically deleted a poll: {}.'.format(description)
        # don't print useless information to main chat!
        logging.info(msg)
        bot.send_message(chat_id=config.input_chat_id, text=msg)
        
    del polls[msg_id]

def list_polls(bot, update):
    if not authorized(bot, update):
        return

    msg = ''
    for msg_id, poll in sorted(polls.items()):
        msg += '{}\n'.format(poll.description())

    if not msg:
        msg = 'No polls found'

    send_command_message(bot, update, msg)

def help(bot, update):
    is_private_chat = update.message.chat.type == Chat.PRIVATE
    is_input_chat = update.message.chat_id == config.input_chat_id
    if not (is_private_chat or is_input_chat):
        return

    msg = '/help\n'\
          'Shows this message\n\n'\
          \
          '/start <pokemon> <time> <location>\n'\
          'Starts a new poll.\n'\
          'Example: /start Snorlax 13:30 Park Sint-Niklaas\n\n'\
          \
          '/close <id>\n'\
          'Closes a poll. You can see the poll ids by typing /list.\n'\
          'Example: /close 0\n\n'\
          \
          '/delete <id>\n'\
          'Deletes a poll. You can see the poll ids by typing /list.\n'\
          'Example: /delete 0\n\n'\
          \
          '/deleteall\n'\
          'Deletes all polls.\n\n'\
          \
          '/list\n'\
          'Lists all polls. Shows each poll\'s id and description.'
    send_command_message(bot, update, msg)

def chat_id(bot, update):
    chat_id = update.message.chat_id
    msg = 'This chat\'s id is {}'.format(chat_id)
    send_command_message(bot, update, msg)

def test(bot, update):
    if not authorized(bot, update):
        return

    pokemon = random.choice(list(pokedex.raid_bosses.keys()))
    start_time = datetime.strftime(datetime.now() + timedelta(minutes=1), '%H:%M')
    start_poll(bot, update, [pokemon, start_time, 'TEST'])
    # start_poll(bot, update, ['moltres', '13:00', 'TEST'])
    # start_poll(bot, update, ['snorlax', '13:00', 'TEST'])

def vote_callback(bot, update):
    query = update.callback_query
    msg_id = query.message.message_id
    
    try:
        polls[msg_id].add_vote(query.from_user.name, int(query.data))
    except KeyError as e:
        logging.info('User tried to vote for an old poll that is still open')
        return
        
    poll = polls[msg_id]

    # quite slow after the first vote from a person... takes 3s or longer to update...
    query.edit_message_text(text=poll.message(),
                            reply_markup=poll.reply_markup(),
                            parse_mode='HTML')
    bot.answer_callback_query(query.id)

def unknown_command(bot, update):
    msg = "Sorry, I didn't understand that command."
    send_command_message(bot, update, msg)

def member_joined(bot, update):
    new_members = update.message.new_chat_members
    if new_members:
        names = [x.name for x in new_members]
        logging.info('member(s) joined: {}'.format(','.join(names)))
        msg = 'Welkom {}!\n'\
              'In deze chat kan je een poll aanmaken door bvb. /start Snorlax 14:00 Park Sint-Niklaas te typen.\n'\
              'Polls worden automatisch gesloten als de start tijd verstrijkt. Je kan een poll ook manueel sluiten door bvb. '\
              '/close 1 te typen. Het nummer van de poll kan je zien door /list te typen.\n'\
              'Pols eerst even in de chat groep voor een start uur voordat je een nieuwe poll aanmaakt!\n'\
              'Type /help voor meer informatie.\n'\
                .format(','.join(names))
        send_command_message(bot, update, msg)
    
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

logFormatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.INFO)

fileHandler = logging.FileHandler('log.log')
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)


dispatcher.add_handler(CommandHandler('start', start_poll, pass_args=True))
dispatcher.add_handler(CommandHandler('close', close_poll, pass_args=True))
dispatcher.add_handler(CommandHandler('delete', delete_poll, pass_args=True))
dispatcher.add_handler(CommandHandler('deleteall', delete_all_polls))
dispatcher.add_handler(CommandHandler('list', list_polls))
dispatcher.add_handler(CommandHandler('help', help))

dispatcher.add_handler(CommandHandler('chatid', chat_id))

if config.test_version:
    dispatcher.add_handler(CommandHandler('test', test))
dispatcher.add_handler(MessageHandler(Filters.chat(chat_id=config.input_chat_id), member_joined))
dispatcher.add_handler(MessageHandler(Filters.command, unknown_command))

dispatcher.add_handler(CallbackQueryHandler(vote_callback))

dispatcher.add_error_handler(error_callback)

updater.start_polling()
logging.info('running!')
updater.idle()