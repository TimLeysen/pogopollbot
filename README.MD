# PoGoPollBot

A Telegram bot for organizing Pokemon Go raids.

PoGoPollBot is a Telegram bot written in Python 3.6 using version 3.2 of the python-telegram-bot library.



## Installing and running PoGoPollBot

1. Download and install Python 3.6 for your operating system from https://www.python.org/downloads/release/python-360/

2. Install python-telegram-bot by running the following command in your command prompt:
     pip install python-telegram-bot
   See https://github.com/python-telegram-bot/python-telegram-bot for troubleshooting
   
3. Download the files in this repository.

4. Go here https://core.telegram.org/bots#6-botfather and follow the instructions to create a new Telegram bot.
   In short, send /newbot to @BotFather on Telegram. Choose a name for your bot and write down the bot token that BotFather gives you.
   
5. Copy pollbot.db from the db folder to the main folder.
   
6. Copy config.py from the config folder to the main folder.

7. Open config.py in the main folder in a text editor and replace <YOUR-BOT-TOKEN-HERE> with the bot token you have
   received from BotFather in step 4.

8. Run the bot.py from the command prompt.
   If successful it should print 'Ready to work!' to the window.



## Configuring PoGoPollBot

1. Open config.py again in a text editor.
   In the next steps we will create the channels and group chats that you will use.
   Their chat ids will have to be entered in the 'if not test_version' section.
   
2. Create a new telegram channel (not a group) and add your bot to it as an admin.
   This is the channel where raid polls will be posted.
   Your bot's name is the one that you chose in step 4 with @ prepended to it. E.g. @MyPoGoPollBot.
   Type /chatid in the channel. The bot should reply with: 'This chat's id is <YOUR-CHAT-ID>'.
   Now replace <RAIDS-CHANNEL-ID> in config.py with the chat id you've just received.
   
3. Repeat step 2 for a channel where exclusive raids will be posted.
   If you want exclusive raids to be posted in the same channel as normal raids, replace
   <EXCLUSIVE-RAIDS-CHANNEL-ID> with the chat id of the channel that you created in step 2.

4. Create a new telegram group and add your bot to it as a member.
   This is the group from which people will be able to send commands to the bot.
   Type /chatid and replace <BOT-CHAT-ID> in config.py with the correct chat id.
   
5. Create a new telegram group and add your bot to it as a member.
   This is the main chat where the bot will notifiy when someone has started, closed or deleted a poll
   and where users can report a raid.
   If your group contains a lot of members you can upgrade it to a supergroup if you wish.
   Type /chatid and replace <MAIN-CHAT-ID> in config.py with the correct chat id.

6. Save config.py and rerun bot.py from the command prompt or terminal window.

7. If you make your own additions and want to test them in separate test channels:
    Use BotFather to create a new test bot and paste your bot token in the test version section of config.py
    Repeat steps 1-7 to create test channels and groups.
    Set test_version = True in config.py.
    You can use the command /test to generate a test raid poll.



## Using PoGoPollBot

Type /help in BOT-CHAT or in PM for more information about the commands.

### POWER USER COMMANDS:
The following commands can be used in BOT-CHAT.
/poll <pokemon> <time> <location>
Starts a new raid poll.
Example: /poll Snorlax 13:30 Central station

/pollex <pokemon> <date> <time> <location>
Starts a new exclusive raid poll.
Example: /pollex Mewtwo 30/10 19:00 Central Station

/close <id> (<reason>)
Closes the poll with id <id>. You can add a reason (optional).
You can see the poll ids by typing /list.
Example: /close 8 starting time changed

/delete <id> (<reason>)
Deletes the poll with id <id>. You can add a reason (optional).
You can see the poll ids by typing /list.
Example: /delete 8 wrong pokemon name

/list
Lists all polls. Shows each poll's id and description.

/help
Shows this message. Also works in PM.


### GENERAL USER COMMANDS (CHAT):
The following commands can be used in MAIN-CHAT or BOT-CHAT.
/raid <pokemon> <timer> <location>
Starts a new time poll for a raid where users can vote for the starting time.
Example: /raid Snorlax 1:45 Central Station


### GENERAL USER COMMANDS (PM):
The following commands can only be used in PM.
/setlevel <level>
Sets your trainer level to <level>.
Example: /setlevel 40


### ADMIN COMMANDS:
The following commands can only be used in BOT-CHAT by admins.
/deleteall
Deletes all polls.

/enableraidcommand
Enables the /raid command for general users.

/disableraidcommand
Disables the /raid command for general users.

/quit
saves the state to file and shuts down the bot.


Note: If you need to restart the bot you should use the /quit command.
This will save all the information about the current polls to a file before stopping the bot.
This file is automatically loaded on startup so users can continue voting on current polls.



## Translating PoGoPollBot

If you want to translate the poll messages in the raids channel, follow these steps:

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