import config
import logging
import time

chat_id = config.output_chat_id

# sticker_set_name = 'Stickers'
#sticker = bot.upload_sticker_file(user_id=, png_sticker='icons/cookie.png')
# bot.create_new_sticker_set(user_id=,name='cookie', title=sticker_set_name)
# bot.add_sticker_to_set(user_id, name=sticker_set_name, png_sticker = 'icons/cookie.png')

def print_countdown(bot, i):
    bot.send_message(chat_id=chat_id, text=str(5-i))

def check_poll_count(bot, count):
    # time.sleep(5)
    if count == 100:
        msg = '100 raids? Here, have a cookie!'
        bot.send_message(chat_id=chat_id, text=msg)
        # bot.send_photo(chat_id=chat_id, photo='icons/cookie.png')
        return
        
    if count == 200:
        msg = '200 raids! Sorry, I am out of cookies ( ._.)'
        bot.send_message(chat_id=chat_id, text=msg)
        return
        
    if count == 300:
        msg = 'Wow 300 raids! Slightly impressive! Here\'s a badly drawn Pikachu:\n'
        with open('ascii_pikachu.txt', 'r') as f:
            msg += f.read()
        bot.send_message(chat_id=chat_id, text=msg)
        # bot.send_photo(chat_id=chat_id, photo='icons/bulbasaur_sleeping.png')
        return
        
    if count == 400:
        msg = '400 raids??!! Congrats Trainer, you\'re more than halfway to Level 31! '\
              'Join millions of Pokemon GO trainers leveling up this week.'
        bot.send_message(chat_id=chat_id, text=msg)
        return
        
    if count == 500:
        bot.send_message(chat_id=chat_id, text='Wow 500 raids!!! 500???! RAIDS!?!?!?')
        time.sleep(2)
        bot.send_message(chat_id=chat_id, text='..................')
        time.sleep(2)        
        bot.send_message(chat_id=chat_id, text='BLEEP BLOOP!')
        time.sleep(2)
        bot.send_message(chat_id=chat_id, text='TOO MANY RAIDS TO HANDLE!?@#!_')
        time.sleep(2)
        bot.send_message(chat_id=chat_id, text='!#$%+3;$ SELF DESTRUCT$&@ING+;...')
        for i in range(0,5):
            time.sleep(1)
            print_countdown(bot, i)
        time.sleep(7)
        bot.send_message(chat_id=chat_id, text='Just kidding! I\'m still here!')
        return
        
    if count == 1000:
        bot.send_message(chat_id=chat_id, text='1000 raids! You make me proud!')
        return