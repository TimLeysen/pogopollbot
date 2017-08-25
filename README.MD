# PoGoPollBot
A Telegram helper bot for organizing Pokemon Go raids.

PoGoPollBot is a Telegram bot written in Python 3.6 using version 3.2 of the python-telegram-bot library.



## Directions for installing and running the bot on your server:

1. Download and install Python 3.6 for your operating system from https://www.python.org/downloads/release/python-360/

2. Install python-telegram-bot by running the following command in your command prompt:
     pip install python-telegram-bot
   See https://github.com/python-telegram-bot/python-telegram-bot for troubleshooting
   
3. Download the files in this repository.

4. Go here https://core.telegram.org/bots#6-botfather and follow the instructions to create a new Telegram bot.
   In short, send /newbot to @BotFather on Telegram. Choose a name for your bot and write down the bot token that BotFather gives you.
   
5. Open config.py in a text editor and replace <YOUR-BOT-TOKEN-HERE> with the bot token you have received from BotFather in step 4.

6. Run the bot.py from the command prompt or terminal window.
   If successful it should print 'Ready to work!' to the window.


## Configuring PoGoPollBot

1. Open config.py in a text editor.
   
2. Create a new telegram channel (not a group) and add your bot to it as an admin.
   This is the channel where raid polls will be posted.
   Your bot's name is the one that you choose in step 4 with a @ prepended to it. E.g. @MyPoGoPollBot.
   Type /chatid in the channel. The bot should reply with: 'This chat's id is <YOUR-CHAT-ID>'.
   Now replace <OUTPUT-CHANNEL-ID> in config.py with the chat id you've just received.
   
3. Create a new telegram group and add your bot to it as a member.
   This is the group from which people will be able to send commands to the bot.
   Type /chatid again and replace <INPUT-CHAT-ID> in config.py with the correct chat id.
   
4. Create a new telegram (super)group and add your bot to it as a member.
   This is the main chat where the bot will notifiy when someone has started, closed or deleted a poll. 
   Type /chatid again and replace <OUTPUT-CHAT-ID> in config.py with the correct chat id.

5. Set enable_raid_command = True if you want normal users to be able to report a raid from the main chat (OUTPUT-CHAT).
   When a raid is reported, a poll is created where users can vote for a start time.
   If enough votes have been reached, a raid poll is created for that start time.

6. Set enable_easter_eggs = True if you want to enable easter eggs. See eastereggs.py for what this does.

7. Save config.py and rerun bot.py from the command prompt or terminal window.



## Using PoGoPollBot

Type /help in INPUT-CHAT for more information about the commands.

The following commands can be used by all members of INPUT-CHAT (power users):
    /start <raid-boss> <start-time> <location>
    /close <id>
    /delete <id>
    /list
    /help

The following commands can only be used by admins of INPUT-CHAT:
    /deleteall
    /save
    /load
    /quit

The following commands can only be used in PM (by anyone):
    /setlevel <level>
    
If you restart the bot you should do so by using the /quit command. It will then save the state and automatically load it on start up.

Try these commands from INPUT-CHAT to see how the bot works:
/start snorlax 13:00 test location
/list
/close 1
/delete 1

/raid charizard 1:50 test location
/close 2
/delete 2



## Translating PoGoPollBot
1. Install Poedit from https://poedit.net/

2. Open Poedit. Go to File, New from POT/PO File and open pollbot.pot.
   Choose the language that you want to add translations for and click OK.
   
3. Translate all the strings and click the save button.
   Change the filename to pollbot.po.
   Save the file to locale\<locale>\LC_MESSAGES where <locale> is the locale of your language, e.g. de for German, es for Spanish, etc.
   
4. Open config.py with a text editor.
   Change enable_translations = False to enable_translations = True
   Replace 'nl' in the following line by your locale:
       es = gettext.translation('pollbot', localedir='locale', languages=['nl'])
   
5. Restart the bot.



## Known Issues

Slow reaction when voting multiple times

Manually deleting messages from the channel can cause polls not to be closed and deleted automatically anymore.
