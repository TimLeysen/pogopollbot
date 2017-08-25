import config
import logging
import time

chat_id = config.output_chat_id

def print_countdown(bot, i):
    bot.send_message(chat_id=chat_id, text=str(5-i))
    
def check_poll_count(bot, count):
    time.sleep(5)

    if count == 100:
        cookie = u'\U0001F36A'
        msg = '100 polls? Here, have a cookie! {}'.format(cookie)
        bot.send_message(chat_id=chat_id, text=msg)
        return
        
    if count == 200:
        msg = '200 polls! Sorry, I am out of cookies ( ._.)'
        bot.send_message(chat_id=chat_id, text=msg)
        return
        
    if count == 300:
        msg = '300 polls?! Here\'s a badly drawn Pikachu:\n'
        with open('ascii_pikachu.txt', 'r') as f:
            msg += f.read()
        bot.send_message(chat_id=chat_id, text=msg)
        return
        
    if count == 400:
        msg = '400 polls?! Congrats Trainer, you\'re more than halfway to Level 31! '\
              'Join millions of Pokemon GO trainers leveling up this week.'
        bot.send_message(chat_id=chat_id, text=msg)
        return
        
    if count == 500:
        bot.send_message(chat_id=chat_id, text='Wow 500 polls!!!')
        time.sleep(2)
        # bot.send_message(chat_id=chat_id, text='BLEEP BLOOP')
        # time.sleep(2)
        bot.send_message(chat_id=chat_id, text='Finally! My job here is done!')
        time.sleep(2)
        bot.send_message(chat_id=chat_id, text='Goodbye trainers...')
        time.sleep(2)        
        bot.send_message(chat_id=chat_id, text='SELF DESTRUCTING...')
        for i in range(0,5):
            time.sleep(1)
            print_countdown(bot, i)
        time.sleep(7)
        bot.send_message(chat_id=chat_id, text='Just kidding! I\'m still here!')
        return
        
    if count == 1000:
        bot.send_message(chat_id=chat_id, text='1000 polls! You make me proud!')
        return