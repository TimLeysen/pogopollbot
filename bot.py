#https://python-telegram-bot.org/

# t.me/PoGoPollBot
# 427679062:AAHeVxPcKK05S_DvXho4dCM1lu9RHLYbYpg
# https://core.telegram.org/bots/api

# Introduction to the API: https://github.com/python-telegram-bot/python-telegram-bot/wiki/Introduction-to-the-API

""""
Can use inline commands e.g. @poll moltres 19:30
Can show option to user in broadcast channel: Yes, No
Can I remove the option when the poll is closed?

Random thoughts:
what if two users create a poll at the same time?
"""

"""
CODE SNIPPETS:
--------------
fetch messages sent to your bot:
updates = bot.get_updates()
print([u.message.text for u in updates])

reply to messages:
chat_id = bot.get_updates()[-1].message.chat_id

post a test message:
bot.send_message(chat_id=chat_id, text="I'm sorry Dave I'm afraid I can't do that.")

reply:
update.message.reply_text("I'm sorry Dave I'm afraid I can't do that.")

build a menu with buttons:
https://github.com/python-telegram-bot/python-telegram-bot/wiki/Code-snippets#build-a-menu-with-buttons


EXAMPLES:
---------
https://github.com/kolar/telegram-poll-bot
"""

from datetime import datetime
import logging

from telegram.error import (TelegramError, Unauthorized, BadRequest, TimedOut, ChatMigrated, NetworkError)
from telegram.ext import Updater, CommandHandler
from telegram.ext import MessageHandler, Filters

import pokedex

# channel to which to post poll
channel_id = '@PoGoWaaslandRaids'

def start(bot, update):
    # ask user to send question
    update.message.reply_text('Steven stinkt!')

def parse_args(update, args): # returns raid boss : str, start_time : str, location : str
    if len(args) < 3:
        msg = 'Incorrect format. Usage: /start <raid-boss> <start-time> <location>. For example: /start Moltres 13:00 Park Sint-Niklaas'
        update.message.reply_text(msg)
        raise ValueError('Incorrect format: expected three arguments: raid boss, start time, location')

    pokemon = args[0]
    if not pokedex.name_exists(pokemon):
        msg = '{} is not a Pokemon. Please check your spelling!'.format(pokemon)
        update.message.reply_text(msg)
        raise ValueError('{} is not a Pokemon'.format(pokemon))

    # not needed and would require code changes when raid bosses change!
    # if not pokedex.is_raid_boss(args[0]):
        # raise Exception('{} is not a raid boss')
    # raid_boss = args[0]

    start_time = args[1]
    try:
        datetime.strptime(start_time, '%H:%M').time()
    except:
        msg = 'Incorrect time format. Expected HH:MM. For example: 13:00'
        update.message.reply_text(msg)
        raise ValueError('Incorrect time format: {}'.format(start_time))

    location = ' '.join(args[2:])

    return pokemon, start_time, location

def start_poll(bot, update, args):
    try:
        raid_boss, start_time, location = parse_args(update, args)
    except ValueError as e:
        logging.info(e)
        return

    # Create poll
    # post raid boss, time, pokestop in channel_id
    # give users the following options: Ik ben aanwezig op dat uur, Ik wil de boss later doen, Ik kom niet
    
    # poll layout:
    # icon? <boss>
    # Location: ...
    # Time: ...
    # poll results

    logging.info('{} created a poll with args {}'.format(update.message.from_user.name, ','.join(args)))
    update.message.reply_text('poll created!')
    
    msg = 'test'
    bot.send_message(chat_id=channel_id, text=msg)

def close_poll(bot, update, args):
    # TODO
    return

def list_polls(bot, update):
    # TODO
    return
    
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



logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        
updater = Updater('427679062:AAHeVxPcKK05S_DvXho4dCM1lu9RHLYbYpg')
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start_poll, pass_args=True))
dispatcher.add_handler(CommandHandler('close', close_poll, pass_args=True))
dispatcher.add_handler(CommandHandler('list', list_polls))
dispatcher.add_handler(MessageHandler(Filters.command, unknown_command))

dispatcher.add_error_handler(error_callback)

updater.start_polling()
updater.idle()