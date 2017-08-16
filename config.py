test_version = True

# Get chat id: invite bot and type something e.g. /my_id @get_id_bot
# https://api.telegram.org/bot382260415:AAHcSfajoIkJgvRa93_HraivGqBTjsnwTmE/getUpdates

# bot user names: @PoGoPollBot, @PoGoPollTestBot

if test_version:
    output_channel_id = '@PoGoWaaslandTest'
    input_chat_id = -212819985 # PoGoWaaslandBotTest
    bot_token = '382260415:AAHcSfajoIkJgvRa93_HraivGqBTjsnwTmE'
else:
    output_channel_id = '@PoGoWaaslandRaids'
    input_chat_id = -228155825 # PoGo Waasland Bot
    bot_token = '427679062:AAHeVxPcKK05S_DvXho4dCM1lu9RHLYbYpg'