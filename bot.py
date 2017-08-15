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
"""

from datetime import datetime
import logging

from telegram.ext import Updater, CommandHandler
from telegram.ext import MessageHandler, Filters

import pokedex

def start(bot, update):
    # ask user to send question
    update.message.reply_text('Steven stinkt!')

def check_args(update, args): # returns raid boss : str, timer : datetime.time
    if len(args) != 2:
        msg = 'Incorrect format. Usage: /poll <raid-boss> <start-time>. For example: /poll Moltres 13:00'
        update.message.reply_text(msg)
        raise ValueError('Incorrect format: expected two arguments: raid boss, start time')

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
        start_time = datetime.strptime(start_time, '%H:%M').time()
    except:
        msg = 'Incorrect time format. Expected HH:MM. For example: 13:00'
        update.message.reply_text(msg)
        raise ValueError('Incorrect time format: {}'.format(start_time))

    return pokemon, start_time

def create_poll(bot, update, args):
    try:
        raid_boss, start_time = check_args(update, args)
    except ValueError as e:
        logging.info(e)
        return

    # Create poll
    update.message.reply_text('creating poll!')
    logging.info('{} created a poll with args {}'.format(update.message.from_user.name, ','.join(args)))
        
        
    # bot.send_message(chat_id=update.message.chat_id, text=msg)

# on_message:
    # 1. store question
    # 2. store description (button to skip)
    # 3. store first answer
    # 4. etc.
    
# def hello(bot, update):
    # update.message.reply_text(
        # 'Hello {}'.format(update.message.from_user.first_name))

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        
updater = Updater('427679062:AAHeVxPcKK05S_DvXho4dCM1lu9RHLYbYpg')
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('poll', create_poll, pass_args=True))
#dispatcher.add_handler(MessageHandler(Filters.text, echo))

updater.start_polling()
updater.idle()