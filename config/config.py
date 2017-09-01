import gettext

test_version = False

# Use /chatid to get the chat id
if not test_version:
    # channel where raid polls are broadcast
    raids_channel_id = <RAIDS-CHANNEL-ID>
    # channel where exclusive raid polls are broadcast
    exclusive_raids_channel_id = <EXCLUSIVE-RAIDS-CHANNEL-ID>
    # main chat where create, close and delete commands are posted
    main_chat_id = <MAIN-CHAT-ID>
    # bot chat where users can send commands to the bot
    bot_chat_id = <BOT-CHAT-ID>
    
    bot_token = '<BOT-TOKEN>'
else:
    # Only fill in this section if you want to be able to run a test version of the bot
    raids_channel_id = <RAIDS-CHANNEL-ID>
    exclusive_raids_channel_id = <EXCLUSIVE-RAIDS-CHANNEL-ID>
    main_chat_id = <MAIN-CHAT-ID>
    bot_chat_id = <BOT-CHAT-ID>
    bot_token = '<BOT-TOKEN>'


enable_raid_command = True
enable_translations = False


# TRANSLATIONS
# See README.md for more information on how to add translations
if enable_translations:
    es = gettext.translation('pollbot', localedir='locale', languages=['nl'])
    es.install()
else:
    _ = lambda s: s