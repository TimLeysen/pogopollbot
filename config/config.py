import gettext

test_version = False

# Use /chatid to get the chat id
if test_version:
    raids_channel_id = <RAIDS-CHANNEL-ID>
    exclusive_raids_channel_id = <EXCLUSIVE-RAIDS-CHANNEL-ID>
    main_chat_id = <MAIN-CHAT-ID>
    bot_chat_id = <BOT-CHAT-ID>
    
    bot_token = '<BOT-TOKEN>'
else:
    # channel where raid polls are broadcast
    raids_channel_id = <RAIDS-CHANNEL-ID>
    # channel where exclusive raid polls are broadcast
    exclusive_raids_channel_id = <EXCLUSIVE-RAIDS-CHANNEL-ID>
    # general chat where create, close and delete commands are posted
    main_chat_id = <MAIN-CHAT-ID>
    # chat from where users can send commands to the bot
    bot_chat_id = <BOT-CHAT-ID>
    
    bot_token = '<BOT-TOKEN>'
    
enable_raid_command = True
enable_exclusive_polls = True


# TRANSLATIONS
# See README.md for more information on how to add translations

enable_translations = False

if enable_translations:
    es = gettext.translation('pollbot', localedir='locale', languages=['nl'])
    es.install()
else:
    _ = lambda s: s