import asyncio
from telegram import Bot

TOKEN = '8402834860:AAFlpWErSZwabKcg3BrC5HXRj7usJhn-v4o'

async def send_message():
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=5102936741, text='SERVER STARTED AND RUNNING ...')

asyncio.run(send_message())
