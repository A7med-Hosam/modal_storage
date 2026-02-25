import asyncio
from telegram import Bot

TOKEN = '8402834860:AAFlpWErSZwabKcg3BrC5HXRj7usJhn-v4o'

async def send_message(message):
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=5102936741, text=message)

# asyncio.run(send_message('Server is exiting - restarting now ....'))
