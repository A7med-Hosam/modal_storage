from telegram.ext import ContextTypes, Application

TOKEN = '8402834860:AAFlpWErSZwabKcg3BrC5HXRj7usJhn-v4o' 

async def callback_30(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=5102936741, text='SERVER STARTED AND RUNNING ...')

application = Application.builder().token(TOKEN).build()

job_queue = application.job_queue

job_queue.run_once(callback_30, 1)

application.run_polling()
