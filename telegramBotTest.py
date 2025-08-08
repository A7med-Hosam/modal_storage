from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import ast
from pathlib import Path
from pprint import pprint
import requests
from pathlib import Path
from pybit.unified_trading import HTTP
from datetime import datetime, timedelta, timezone
import time
import asyncio
from telethon import TelegramClient, events, sync

script_dir = Path(__file__).parent

TOKEN: Final = '8402834860:AAEscTZBvCGSC0G1s495m96DIlZDokW8Z9M'
BOT_USERNAME: Final = '@notion_trading_dashboard_bot'
BYBIT_API_KEY: Final = "X2IkVTBrSGigrygWl6"
BYBIT_API_SECRET: Final = "Pt1TfrpaxJ6C1Qw8dwMPf77NbAqCJlAkFWWe"

api_id = 28658026
api_hash = '54460e1ff82af4a70f596208a2bdd9a3'

client = TelegramClient('session_name', api_id, api_hash)
client.start()

# print(client.get_me().stringify())

CHAT_ID = -1002835451717
ifttt_id = "@ifttt"
dashboard_bot_id = "@notion_trading_dashboard_bot"


def get_volume(period,min_10m_volume,interval):
    # min_10m_volume = 2 * 1000 * 1000
    # min_turnover = 1 * 1000

    from pybit.unified_trading import HTTP
    from pprint import pprint
    import json
    from pathlib import Path
    from datetime import datetime, timedelta

    script_dir = Path(__file__).parent

    session = HTTP(
        testnet=False,
        api_key=BYBIT_API_KEY,
        api_secret=BYBIT_API_SECRET,
    )


    def save_json(data,file_name):
        script_dir = Path(__file__).parent
        with open(f'{script_dir}/{file_name}.json', 'w', encoding='utf8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    current_days_date_full= datetime.now()
    current_timestamp= int(datetime.timestamp(current_days_date_full)*1000)

    def get_start_timestamp(start_period): # start_period is how many minutes ago
        date = (current_days_date_full - timedelta(1*start_period/(24*60)))
        start_timestamp = int(datetime.timestamp(date)*1000)
        return start_timestamp


    def get_kline(interval,start_period):
        coin_kline = session.get_kline(
            category="linear",
            symbol="MOODENGUSDT",
            interval=interval,
            start=get_start_timestamp(start_period),
            end=current_timestamp,
            )
        return coin_kline

    coin_kline_data = get_kline(interval,period)

    coin_kline_list = coin_kline_data["result"]["list"]
    coin_turnover_volume_list = []

    for list in coin_kline_list:
        volume = int(list[5])
        turnover = int(float(list[6]))
        # print(f'volume= {volume} Turnover= {turnover}')
        coin_turnover_volume_list.append([volume,turnover])

    save_json(coin_kline_data,"coin_kline")
    save_json(coin_turnover_volume_list,f'coin_turnover_volume_list')


    def volume_turnover_sum():
        volume_sum = 0
        turnover_sum = 0
        for list in coin_turnover_volume_list:
            volume_sum+= list[0]
            turnover_sum+= list[1]
        return volume_sum,turnover_sum

    volume_sum = volume_turnover_sum()[0]
    turnover_sum = volume_turnover_sum()[1]

    print(f'Volume sum = {volume_sum:,}')
    print(f'Turnover sum = {turnover_sum:,}')
    print("----------------------------")
    alert = False
    if volume_sum > min_10m_volume:
        print(f"alert triggerd, volume in the last 15m is higher than {min_10m_volume}")
        alert=True

    return volume_sum,turnover_sum,alert

def check_volume(min_volume,period,interval):
    Volume_turnover = get_volume(period,min_volume,interval)
    volume = Volume_turnover[0]
    turnover = Volume_turnover[2]
    if volume > min_volume:
        client.send_message(ifttt_id, f'in {period/interval} consecutive {period}m volume: {volume:,} Turnover: ({turnover:,}) ')
    return

async def callback_minute(context: ContextTypes.DEFAULT_TYPE):
    min_10m_volume = 10 * 1000 * 1000
    period = 10
    interval = 5
    Volume_turnover_10_min = get_volume(period,min_10m_volume,interval)
    Volume_10_min = Volume_turnover_10_min[0]
    Turnover_10_min = Volume_turnover_10_min[1]
    if Volume_10_min > min_10m_volume:
        await client.send_message(ifttt_id, f'volume in the last {period}m is above: {Volume_10_min:,} Turnover: ({Turnover_10_min:,}) ')
    await client.send_message(dashboard_bot_id, f"{period}m volume: ( {Volume_10_min:,} ) Turnover: ({Turnover_10_min:,})")


def get_pnl_balance():
    NOTION_TOKEN = "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"
    PAGE_ID = "22267e6ab25480d0b2f2d2e0fe98b971"
    DATABASE_ID = "22267e6ab25480a0abd3d704c959d194"
    WALLET_BALANCE_ID = '22867e6a-b254-8005-8b58-de1397c59453'
    TODAYS_TOTAL_PNL_ID = '22267e6a-b254-805e-9153-e722274b4bdc'
    CLOSED_PNL_ID = "22967e6a-b254-8037-81c5-c1dac0d24893"
    LIVE_PNL_ID = "22967e6a-b254-805a-8658-e523626ac208"

    headers = {
        "Authorization": "Bearer " + NOTION_TOKEN,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    session = HTTP(
        testnet=False,
        api_key=BYBIT_API_KEY,
        api_secret=BYBIT_API_SECRET,
    )


    balanceDetails = session.get_wallet_balance(
        accountType="UNIFIED",
        coin="USDT",
    )["result"]["list"][0]


    def get_day_pnl(day_num):
        todays_date_full=  datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        end_date_full= todays_date_full - timedelta(day_num)
        end_date_timestamp= int(datetime.timestamp(end_date_full)*1000)
        end_date_format= end_date_full.strftime('%Y-%m-%d')

        start_date_full= todays_date_full - timedelta(day_num+1)
        start_date_timestamp= int(datetime.timestamp(start_date_full)*1000)
        start_date_format= start_date_full.strftime('%Y-%m-%d')

        trades_data= (session.get_closed_pnl(
            category="linear",
            startTime= start_date_timestamp,
            endTime= end_date_timestamp,
            limit=10000,
        ))['result']['list']

        day_pnl= 0
        for trade in trades_data:
            day_pnl+= float(trade["closedPnl"])
        day_pnl= round(day_pnl,4)

        return day_pnl,start_date_format,start_date_full,start_date_timestamp

    def get_multiple_days_pnl(num_days):
        today = -1
        days= num_days-1
        while today < days:
            pnl= get_day_pnl(today)[0]
            
            today+=1
        return round(pnl,4)

    def edit_block(block_id, data,type):
        url = f"https://api.notion.com/v1/blocks/{block_id}/"

        payload = {type: data}
        results = requests.patch(url, json=payload, headers=headers)

        pprint(results)
        return results

    def update_number(block_id,number,static,type):
        if static == False:
            sign = ""
            number_color = "gray"
            if number > 0:
                number_color = "green"
                sign = "+"
            elif number < 0:
                number_color = "red"
                sign = "-"
            else:
                number_color = "gray"
            number_str = f'{sign} {abs(number)}$'
        else:
            number_color = "gray"
            number_str = f'{abs(number)}$'

        data = {
        "rich_text": [
            {
                "type": "text",
                "text": {
                    "content": number_str,
                    "link": None
                },
                "annotations": {
                    "bold": False,
                    "italic": False,
                    "strikethrough": False,
                    "underline": False,
                    "code": False,
                    "color": number_color
                },
                "plain_text": "+ 0.53$",
                "href": None
            }
            ],
            "color": number_color
        }
        edit_block(block_id, data,type)


    wallet_balance = round(float(balanceDetails["totalEquity"]),4)
    live_pnl = round(float(balanceDetails["coin"][0]["unrealisedPnl"]),4)
    todays_closed_pnl = get_multiple_days_pnl(1)
    total_pnl = round(todays_closed_pnl + live_pnl,4)

    # simple text dashboard for telegram
    Simple_Dashboard = f'''
    Balance = {wallet_balance}
    Today's Pnl 
        {total_pnl}
  Live             Closed
  {live_pnl}        {todays_closed_pnl}

'''

    # update_number(LIVE_PNL_ID,live_pnl,False,"paragraph")

    # update_number(CLOSED_PNL_ID,todays_closed_pnl,False,"paragraph")

    # update_number(TODAYS_TOTAL_PNL_ID,total_pnl,False,"heading_2")

    # update_number(WALLET_BALANCE_ID, wallet_balance,True,"heading_2")

    full_list = [wallet_balance,total_pnl,live_pnl,todays_closed_pnl]

    return full_list


def update_notion_dashboard():

    NOTION_TOKEN = "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"
    PAGE_ID = "22267e6ab25480d0b2f2d2e0fe98b971"
    DATABASE_ID = "22267e6ab25480a0abd3d704c959d194"
    WALLET_BALANCE_ID = '22867e6a-b254-8005-8b58-de1397c59453'
    TODAYS_TOTAL_PNL_ID = '22267e6a-b254-805e-9153-e722274b4bdc'
    CLOSED_PNL_ID = "22967e6a-b254-8037-81c5-c1dac0d24893"
    LIVE_PNL_ID = "22967e6a-b254-805a-8658-e523626ac208"

    headers = {
        "Authorization": "Bearer " + NOTION_TOKEN,
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    session = HTTP(
        testnet=False,
        api_key=BYBIT_API_KEY,
        api_secret=BYBIT_API_SECRET,
    )


    balanceDetails = session.get_wallet_balance(
        accountType="UNIFIED",
        coin="USDT",
    )["result"]["list"][0]


    def get_day_pnl(day_num):
        todays_date_full=  datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        end_date_full= todays_date_full - timedelta(day_num)
        end_date_timestamp= int(datetime.timestamp(end_date_full)*1000)
        end_date_format= end_date_full.strftime('%Y-%m-%d')

        start_date_full= todays_date_full - timedelta(day_num+1)
        start_date_timestamp= int(datetime.timestamp(start_date_full)*1000)
        start_date_format= start_date_full.strftime('%Y-%m-%d')

        trades_data= (session.get_closed_pnl(
            category="linear",
            startTime= start_date_timestamp,
            endTime= end_date_timestamp,
            limit=10000,
        ))['result']['list']

        day_pnl= 0
        for trade in trades_data:
            day_pnl+= float(trade["closedPnl"])
        day_pnl= round(day_pnl,4)

        return day_pnl,start_date_format,start_date_full,start_date_timestamp

    def get_multiple_days_pnl(num_days):
        today = -1
        days= num_days-1
        while today < days:
            pnl= get_day_pnl(today)[0]
            
            today+=1
        return round(pnl,4)

    def edit_block(block_id, data,type):
        url = f"https://api.notion.com/v1/blocks/{block_id}/"

        payload = {type: data}
        results = requests.patch(url, json=payload, headers=headers)

        pprint(results)
        return results

    def update_number(block_id,number,static,type):
        if static == False:
            sign = ""
            number_color = "gray"
            if number > 0:
                number_color = "green"
                sign = "+"
            elif number < 0:
                number_color = "red"
                sign = "-"
            else:
                number_color = "gray"
            number_str = f'{sign} {abs(number)}$'
        else:
            number_color = "gray"
            number_str = f'{abs(number)}$'

        data = {
        "rich_text": [
            {
                "type": "text",
                "text": {
                    "content": number_str,
                    "link": None
                },
                "annotations": {
                    "bold": False,
                    "italic": False,
                    "strikethrough": False,
                    "underline": False,
                    "code": False,
                    "color": number_color
                },
                "plain_text": "+ 0.53$",
                "href": None
            }
            ],
            "color": number_color
        }
        edit_block(block_id, data,type)


    wallet_balance = round(float(balanceDetails["totalEquity"]),4)
    live_pnl = round(float(balanceDetails["coin"][0]["unrealisedPnl"]),4)
    todays_closed_pnl = get_multiple_days_pnl(1)
    total_pnl = round(todays_closed_pnl + live_pnl,4)

    # simple text dashboard for telegram
    Simple_Dashboard = f'''
    Balance = {wallet_balance}
    Today's Pnl 
        {total_pnl}
  Live             Closed
  {live_pnl}        {todays_closed_pnl}

'''

    update_number(LIVE_PNL_ID,live_pnl,False,"paragraph")

    update_number(CLOSED_PNL_ID,todays_closed_pnl,False,"paragraph")

    update_number(TODAYS_TOTAL_PNL_ID,total_pnl,False,"heading_2")

    update_number(WALLET_BALANCE_ID, wallet_balance,True,"heading_2")

    full_list = [wallet_balance,total_pnl,live_pnl,todays_closed_pnl]

    return full_list

def change_sign(number):
    sign = ""
    if number > 0:
        sign = "+"
    elif number < 0:
        sign = "-"
    else:
        sign = ""
    number_str = f'{sign} {abs(number)} $'
    return number_str

# --------------------------------------------



# Commands /
    # print(f"Chat ID: {update.effective_chat.id}")
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await client.send_message(ifttt_id, 'volume has reached 10 million')
    # await update.message.reply_text('/ifttt volume')
    # await context.bot.send_message(chat_id=CHAT_ID, text="/ifttt volume")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('getting current bybit status ....')
    full_list = get_pnl_balance()
    full_list_formated = f"""
------------------------------
    Balance = {full_list[0]} $

    Today's Pnl 
        {change_sign(full_list[1])}
  Live             Closed
  {change_sign(full_list[2])}                  {change_sign(full_list[3])}
------------------------------
"""
    print(full_list_formated)
    await update.message.reply_text(f"{full_list_formated}")

async def update_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Updating Dashboard ....')
    full_list = update_notion_dashboard()
    full_list_formated = f"""
------------------------------
    Balance = {full_list[0]} $

    Today's Pnl 
        {change_sign(full_list[1])}
  Live             Closed
  {change_sign(full_list[2])}                  {change_sign(full_list[3])}
------------------------------
"""
    print(full_list_formated)
    await update.message.reply_text(f"Dashboard has been updated successfully ✅ {full_list_formated}")

async def greet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('greetings Ahmed I am your Notion Trading Dashboard')

async def message_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_url = "https://images.pexels.com/photos/36704/pexels-photo.jpg"
    # photo_file = open(f"{script_dir}/pexels-photo.jpg","rb")
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_url)

# Responses

def handle_response(text: str) -> str:
    processed: str = text.lower()

    if "hello" in processed:
        return "Hey there!"
    
    if "how are you" in processed:
        return "I am good!"
    
    # return "I don't get that"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type} : "{text}"')
    
    if message_type == "group":
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, "").strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    print('Bot:', response)
    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__  == '__main__':
    print(" Starting bot...")
    app = Application.builder().token(TOKEN).build()
    # commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('greet', greet_command))
    app.add_handler(CommandHandler('status', status_command))
    app.add_handler(CommandHandler('update_notion', update_command))
    app.add_handler(CommandHandler('photo', message_photo))
    # app.add_handler(CommandHandler('alert', message_photo))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # errors
    app.add_error_handler(error)

    # schedule jobs in a queue
    job_queue = app.job_queue
    job_queue2 = app.job_queue
    job_minute = job_queue.run_repeating(callback_minute, interval=120, first=1)
    # job_minute2 = job_queue2.run_repeating(, interval=30, first=1)

    # check new messages
    print('polling messages ...')
    app.run_polling(poll_interval=3)

    
