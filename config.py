test_version = True

# Get chat id: invite bot and type something e.g. /my_id @get_id_bot
# https://api.telegram.org/bot382260415:AAHcSfajoIkJgvRa93_HraivGqBTjsnwTmE/getUpdates

# bot user names: @PoGoPollBot, @PoGoPollTestBot

if test_version:
    # channel where polls are broadcasted
    output_channel_id = '@PoGoWaaslandRaidsTest'
    # general chat where create, close and delete commands are also posted
    output_chat_id = '@PoGoWaaslandTest'
    # chat from where users can send commands to the bot
    # you can use /chat_id to the bot to get the chat id
    input_chat_id = -212819985 # PoGoWaaslandBotTest
    bot_token = '382260415:AAHcSfajoIkJgvRa93_HraivGqBTjsnwTmE'
else:
    output_channel_id = '@PoGoWaaslandRaids'
    output_chat_id = '@PoGoWaasland'
    input_chat_id = -228155825 # PoGo Waasland Bot
    bot_token = '427679062:AAHeVxPcKK05S_DvXho4dCM1lu9RHLYbYpg'