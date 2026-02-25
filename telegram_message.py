import asyncio
import sys
from telegram import Bot

TOKEN = '8402834860:AAFlpWErSZwabKcg3BrC5HXRj7usJhn-v4o'

async def send_message(message):
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=5102936741, text=message)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        message_to_send = " ".join(sys.argv[1:])
        asyncio.run(send_message(message_to_send))
    else:
        print("Usage: python3 telegram_message.py 'Your message here'")
