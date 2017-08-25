import gettext

test_version = True

# Use /chatid to get the chat id
if test_version:
    output_channel_id = '@PoGoWaaslandRaidsTest'
    output_chat_id = -1001127228363 # '@PoGoWaaslandTest'
    input_chat_id = -212819985 # PoGoWaaslandBotTest
    bot_token = '382260415:AAHcSfajoIkJgvRa93_HraivGqBTjsnwTmE'
else:
    # channel where polls are broadcast
    output_channel_id = '@PoGoWaaslandRaids'
    # general chat where create, close and delete commands are posted
    output_chat_id = -1001127550956 # '@PoGoWaasland'
    # chat from where users can send commands to the bot
    input_chat_id = -228155825 # PoGo Waasland Bot
    bot_token = '427679062:AAHeVxPcKK05S_DvXho4dCM1lu9RHLYbYpg'
    
enable_raid_command = False



# TRANSLATIONS
# See README.md for more information on how to add translations

enable_translations = False

if enable_translations:
    es = gettext.translation('pollbot', localedir='locale', languages=['nl'])
    es.install()
else:
    _ = lambda s: s