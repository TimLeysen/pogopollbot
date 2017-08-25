import config
import logging
import time

chat_id = config.output_chat_id

def print_countdown(bot, i):
    bot.send_message(chat_id=chat_id, text=str(5-i))
    
def check_poll_count(bot, count):
    logging.info('check poll count: {}'.format(count))
    time.sleep(5)
    cookie = u'\U0001F36A'

    if count == 100:
        msg = '100 polls?! Here, have a cookie! {}'.format(cookie)
        bot.send_message(chat_id=chat_id, text=msg)
        return
        
    if count == 200:
        msg = '200 polls?! Sorry, I\'m out of cookies ( ._.)'
        bot.send_message(chat_id=chat_id, text=msg)
        return
        
    if count == 300:
        msg = '300 polls?! Here\'s a badly drawn Pikachu:\n'
        with open('ascii_pikachu.txt', 'r') as f:
            msg += f.read()
        bot.send_message(chat_id=chat_id, text=msg)
        return

    if count == 400:
        bot.send_message(chat_id=chat_id, text='400 polls?! Time for a joke!')
        time.sleep(5)
        bot.send_message(chat_id=chat_id, text='What do you call a Weedle who does stunts on a motorcycle?')
        time.sleep(10)
        bot.send_message(chat_id=chat_id, text='Weedle Knievell!')
        return

    if count == 500:
        msg = '500 polls?! Congrats Trainer, you\'re more than halfway to Level 31! '\
              'Join millions of Pokemon GO trainers leveling up this week.'
        bot.send_message(chat_id=chat_id, text=msg)
        return

    if count == 600:
        bot.send_message(chat_id=chat_id, text='600 polls?! Here\'s another cookie! {}'.format(cookie))
        return

    if count == 700:
        bot.send_message(chat_id=chat_id, text='700 polls?! Here\'s a riddle!')
        time.sleep(5)
        bot.send_message(chat_id=chat_id, text='What belongs to you but others use it more than you do?')
        return

    if count == 800:
        bot.send_message(chat_id=chat_id, text='800 polls?!')
        time.sleep(5)
        bot.send_message(chat_id=chat_id, text='I\'m uhhh... quite hungover.')
        time.sleep(3)
        sleeping = u'\U0001F634'
        bot.send_message(chat_id=chat_id, text='Make your own jokes. I\'m going back to bed {}.'.format(sleeping))
        return   

    if count == 900:
        bot.send_message(chat_id=chat_id, text='900 polls?!')
        time.sleep(3)
        bot.send_message(chat_id=chat_id, text='▲\n▲ ▲')
        time.sleep(3)
        bot.send_message(chat_id=chat_id, text='Damn it...')
        return

    if count == 1000:
        bot.send_message(chat_id=chat_id, text='Wow 1000 polls!!!')
        time.sleep(2)
        # bot.send_message(chat_id=chat_id, text='BLEEP BLOOP')
        # time.sleep(2)
        bot.send_message(chat_id=chat_id, text='My job here is done...')
        time.sleep(3)
        bot.send_message(chat_id=chat_id, text='Goodbye trainers...')
        time.sleep(3)        
        bot.send_message(chat_id=chat_id, text='SELF DESTRUCTING...')
        for i in range(0,5):
            time.sleep(1)
            print_countdown(bot, i)
        # time.sleep(7)
        # bot.send_message(chat_id=chat_id, text='Just kidding! I\'m still here!')
        return