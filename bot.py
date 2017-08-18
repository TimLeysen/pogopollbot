#https://python-telegram-bot.org/

# t.me/PoGoPollBot
# 427679062:AAHeVxPcKK05S_DvXho4dCM1lu9RHLYbYpg
# https://core.telegram.org/bots/api

# Introduction to the API: https://github.com/python-telegram-bot/python-telegram-bot/wiki/Introduction-to-the-API
# !!! https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/inlinekeyboard.py

"""
BotFather /setcommands
help - shows the help message
start - starts a poll
close - closes a poll
open - reopens a closed poll
delete - deletes a poll
deleteall - deletes all polls
list - lists all polls
"""

from datetime import datetime,timedelta
import logging
import random
import time

from telegram import CallbackQuery
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

def authorized(update):
    if update.message.chat_id != config.input_chat_id:
        print('Unauthorized access from {}'.format(update.message.from_user.name))
        return False
    return True

def start(bot, update):
    #update.message.reply_text('Start message TODO')
    return

def parse_args(bot, update, args): # returns raid boss : str, start_time : str, location : str
    chat_id = config.input_chat_id
    if len(args) < 3:
        msg = 'Incorrect format. Usage: /start <raid-boss> <start-time> <location>. For example: /start Moltres 13:00 Park Sint-Niklaas'
        bot.send_message(chat_id=chat_id, text=msg)
        raise ValueError('Incorrect format: expected three arguments: raid boss, start time, location')

    # TO DO - remove this?
    pokemon = args[0]
    if not pokedex.name_exists(pokemon):
        msg = '{} is not a Pokemon. Please check your spelling!'.format(pokemon)
        bot.send_message(chat_id=chat_id, text=msg)
        raise ValueError('{} is not a Pokemon'.format(pokemon))

    # not needed and would require code changes when raid bosses change!
    # if not pokedex.is_raid_boss(args[0]):
        # raise Exception('{} is not a raid boss')

    start_time = args[1]
    try:
        datetime.strptime(start_time, '%H:%M').time()
    except:
        msg = 'Incorrect time format. Expected HH:MM. For example: 13:00'
        bot.send_message(chat_id=chat_id, text=msg)
        raise ValueError('Incorrect time format: {}'.format(start_time))

    location = ' '.join(args[2:])

    return pokemon, start_time, location

def start_poll(bot, update, args):
    if not authorized(update):
        return

    try:
        pokemon, start_time, location = parse_args(bot, update, args)
    except ValueError as e:
        logging.info(e)
        return
    creator = update.message.from_user.name
    poll = Poll(pokemon, start_time, location, creator)

    msg = '{} created a poll: {}'.format(update.message.from_user.name, ', '.join(args))
    logging.info(msg)
    bot.send_message(chat_id=update.message.chat_id, text=msg)

    msg = bot.send_message(chat_id=config.output_channel_id,
                           text=poll.message(),
                           reply_markup=poll.reply_markup(),
                           parse_mode='HTML')
    polls[msg.message_id] = poll

    dispatcher.run_async(close_poll_on_timer, *(bot, msg.message_id))
    dispatcher.run_async(delete_poll_on_timer, *(bot, msg.message_id))
   
def close_poll_on_timer(bot, message_id):
    poll = polls[message_id]
    delta = datetime.strptime(poll.time, '%H:%M') - datetime.now()
    if delta.seconds < 0: # test poll or poll with wrong time or exclusive raid
        logging.info('Poll is not closed automatically because start time is earlier than now: {}')\
            .format(poll.description())
        return

    time.sleep(delta.seconds)
    
    #TODO duplicate code with close_poll!
    poll = polls[message_id]
    if poll.closed:
        logging.info('Poll is not closed automatically because poll is already closed: {}'\
            .format(poll.description()))
        return
    
    polls[message_id].set_closed()
    poll = polls[message_id]
    bot.edit_message_text(chat_id=config.output_channel_id, message_id=message_id,
                          text=poll.message(), parse_mode='HTML')
    
    chat_id = config.input_chat_id
    msg = 'Poll {} was closed automatically'.format(poll.description())
    logging.info(msg)
    bot.send_message(chat_id=chat_id, text=msg)
    
def close_poll(bot, update, args):
    if not authorized(update):
        return

    # TO DO: check if digit and in range
    index = int(args[0])

    chat_id = config.output_channel_id
    message_id = sorted(polls)[index]
    polls[message_id].set_closed()
    poll = polls[message_id]
     # remove keyboard
    bot.edit_message_text(chat_id=chat_id,
                          message_id=message_id,
                          text=poll.message(),
                          parse_mode='HTML')
    
    chat_id = update.message.chat_id
    description = '{} {}'.format(index, poll.description())
    msg = '{} closed poll {}'.format(update.message.from_user.name, description)
    logging.info(msg)
    bot.send_message(chat_id=chat_id, text=msg)
    
    return

def open_poll(bot, update, args): # TO DO code duplication, see close_poll
    if not authorized(update):
        return

    # TO DO: check if digit and in range
    index = int(args[0])
    print(index)

    chat_id = config.output_channel_id
    message_id = sorted(polls)[index]
    polls[message_id].set_open()
    poll = polls[message_id]
    bot.edit_message_text(chat_id=chat_id,
                          message_id=message_id,
                          text=poll.message(),
                          reply_markup=poll.reply_markup(),
                          parse_mode='HTML')
    
    chat_id = update.message.chat_id
    description = '{} {}'.format(index, poll.description())
    msg = '{} reopened poll {}'.format(update.message.from_user.name, description)
    logging.info(msg)
    bot.send_message(chat_id=chat_id, text=msg)    
    
def delete_all_polls(bot, update):
    if not authorized(update):
        return
    
    chat_id = config.output_channel_id
    # TODO: ask for confirmation!
    for message_id in polls.keys():
        bot.delete_message(chat_id=chat_id, message_id=message_id)
    polls.clear()

    chat_id = update.message.chat_id
    msg = '{} deleted all polls.'.format(update.message.from_user.name)
    logging.info(msg)
    bot.send_message(chat_id=chat_id, text=msg)

def delete_poll(bot, update, args):
    if not authorized(update):
        return

    if len(args) != 1:
        logging.error('delete_poll: wrong args')
        #TODO print message
        return

    index = args[0]
    if not index.isdigit():
        logging.error('delete_poll: poll id is not a digit')
        #TODO print message
        return
        
    index = int(index)
    if not index in range(0,len(polls)):
        logging.error('delete_poll: index out of range')
        #TODO print message
        return

    msg_id = sorted(polls)[index]
    __delete_poll(bot, msg_id, update)
        
def delete_poll_on_timer(bot, msg_id):
    poll = polls[msg_id]
    delta = datetime.strptime(poll.time, '%H:%M') - datetime.now()
    if delta.seconds < 0: # test poll or poll with wrong time or exclusive raid
        logging.info('Poll is not deleted automatically because start time is earlier than now: {}')\
            .format(poll.description())
        return

    # delete 2 hours after start time
    # poll information should always be available for people that want do
    # another group later
    # time.sleep(delta.seconds + 7200)
    time.sleep(delta.seconds + 10)
    __delete_poll(bot, msg_id)

def __delete_poll(bot, msg_id, update=None):
    chat_id = config.output_channel_id
    bot.delete_message(chat_id=chat_id, message_id=msg_id)
    description = polls[msg_id].description()
    del polls[msg_id]
    
    if update is not None:
        chat_id = update.message.chat_id
        msg = '{} deleted poll {}'.format(update.message.from_user.name, description)
        logging.info(msg)
        bot.send_message(chat_id=chat_id, text=msg)
    else:
        chat_id = config.input_chat_id
        msg = 'Automatically deleted poll {}'.format(description)
        logging.info(msg)
        bot.send_message(chat_id=chat_id, text=msg)

def list_polls(bot, update):
    if not authorized(update):
        return

    msg = ''
    i = 0
    for message_id, poll in sorted(polls.items()):
        msg += '{} {}\n'.format(i, poll.description())
        i += 1

    if not msg:
        msg = 'No polls found'

    bot.send_message(chat_id=update.message.chat_id, text=msg)

def help(bot, update):
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
          '/open <id>\n'\
          'Reopens a closed poll. You can see the poll ids by typing /list.\n'\
          'Example: /open 0\n\n'\
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
    bot.send_message(chat_id=update.message.chat_id, text=msg)

def test(bot, update):
    if not authorized(update):
        return

    start_time = datetime.strftime(datetime.now() + timedelta(minutes=1), '%H:%M')
    start_poll(bot, update, ['zapdos', start_time, 'TEST'])
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
    bot.send_message(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")
    
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


logging.basicConfig(#filename='log_info.log',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


dispatcher.add_handler(CommandHandler('start', start_poll, pass_args=True))
dispatcher.add_handler(CommandHandler('close', close_poll, pass_args=True))
dispatcher.add_handler(CommandHandler('open', open_poll, pass_args=True))
dispatcher.add_handler(CommandHandler('delete', delete_poll, pass_args=True))
dispatcher.add_handler(CommandHandler('deleteall', delete_all_polls))
dispatcher.add_handler(CommandHandler('list', list_polls))
dispatcher.add_handler(CommandHandler('help', help))

if config.test_version:
    dispatcher.add_handler(CommandHandler('test', test))
dispatcher.add_handler(MessageHandler(Filters.command, unknown_command))

dispatcher.add_handler(CallbackQueryHandler(vote_callback))

dispatcher.add_error_handler(error_callback)

updater.start_polling()
print('running!')
updater.idle()