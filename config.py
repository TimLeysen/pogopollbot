import gettext

test_version = True

# Use /chatid to get the chat id
if test_version:
    raids_channel_id = '@PoGoWaaslandRaidsTest'
    exclusive_raids_channel_id = '@PoGoWaaslandExclusiveRaidsTest'
    main_chat_id = -1001127228363 # '@PoGoWaaslandTest'
    bot_chat_id = -212819985 # PoGoWaaslandBotTest
    bot_token = '382260415:AAHcSfajoIkJgvRa93_HraivGqBTjsnwTmE'
else:
    # channel where raid polls are broadcast
    raids_channel_id = '@PoGoWaaslandRaids'
    # channel where exclusive raid polls are broadcast
    exclusive_raids_channel_id = '@PoGoWaaslandExclusiveRaids'
    # general chat where create, close and delete commands are posted
    main_chat_id = -1001127550956 # '@PoGoWaasland'
    # chat from where users can send commands to the bot
    bot_chat_id = -228155825 # PoGo Waasland Bot
    bot_token = '427679062:AAHeVxPcKK05S_DvXho4dCM1lu9RHLYbYpg'
    
enable_raid_command = True



# TRANSLATIONS
# See README.md for more information on how to add translations

enable_translations = True

if enable_translations:
    es = gettext.translation('pollbot', localedir='locale', languages=['nl'])
    es.install()
else:
    _ = lambda s: s