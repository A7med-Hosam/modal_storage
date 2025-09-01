import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    Application,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from uuid import uuid4
from buttons_functions import *

# Define states for conversation
MENU, BALANCE_MENU, PNL, MAIN_MENU, TRANSFER, ACROSS_ACCOUNTS, INTERNAL,FROM , TO , AMOUNT, CUSTOM_AMOUNT= range(11)

# Set up logging for the bot
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

main_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("balance", callback_data="balance")],
    [InlineKeyboardButton("PNL", callback_data="pnl")],
    [InlineKeyboardButton("Transfer", callback_data="Transfer")],
    ])

pnl_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("live", callback_data="live")],
    [InlineKeyboardButton("closed", callback_data="closed")],
    [InlineKeyboardButton("⬅️️", callback_data="⬅️️")],
    ])

balance_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("transfer", callback_data="transfer")],
        [InlineKeyboardButton("accounts' balances", callback_data="accounts' balances")],
    [InlineKeyboardButton("⬅️️", callback_data="⬅️️")],
    ])

transfer_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("Across Accounts", callback_data="Across Accounts")],
    [InlineKeyboardButton("Internal", callback_data="Internal")],
    [InlineKeyboardButton("⬅️️", callback_data="⬅️️")],
    ])

def edit_across_accounts_menu(from_value,to_value,amount):
    across_accounts_menu  = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Amount [ {amount} $ ]", callback_data="Amount")],
        [InlineKeyboardButton(f" ", callback_data=" ")],
        [InlineKeyboardButton(f"From   [ {from_value} ]", callback_data="From")],
        [InlineKeyboardButton(f"🔃", callback_data="🔃")],
        [InlineKeyboardButton(f"To      [ {to_value} ] ", callback_data="To")],
        [InlineKeyboardButton(f" ", callback_data=" ")],
        [InlineKeyboardButton(f"Make Transfer ✅", callback_data="Make Transfer ✅")],
        [InlineKeyboardButton("⬅️️", callback_data="⬅️️")],
        ])
    return across_accounts_menu

def across_accounts_menu_text(from_value,to_value,amount):
    text = f"""Transfer [ {amount} $ ] 
    from: [ {from_value} ] 
       to: [ {to_value} ] 
    """
    return text

accounts_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton(f"Main Account", callback_data="Main Account")],
    [InlineKeyboardButton(f"Volume Flow", callback_data="Volume Flow")],
    [InlineKeyboardButton(f"EmergencyFunds", callback_data="EmergencyFunds")],
    [InlineKeyboardButton("⬅️️", callback_data="⬅️️")],
    ])

amount_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton(f"All", callback_data="All")],
    [InlineKeyboardButton(f"0.01", callback_data="0.01")],
    [InlineKeyboardButton(f"0.2", callback_data="0.2")],
    [InlineKeyboardButton(f"0.5", callback_data="0.5")],
    [InlineKeyboardButton(f"1.0", callback_data="1.0")],
    [InlineKeyboardButton("⬅️️", callback_data="⬅️️")],
    ])

empty_menu = InlineKeyboardMarkup([
    [InlineKeyboardButton("⬅️️", callback_data="⬅️️")],
    ])


# Start command handler
async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text(
        "Welcome! Please choose an option:", reply_markup=main_menu
    )
    context.user_data["from"] = "Main Account"
    context.user_data["from_id"] = MAIN_ACCOUNT_ID
    context.user_data["to"] = "Volume Flow"
    context.user_data["to_id"] = VOLUME_FLOW_ID
    context.user_data["amount"] = 0.0
    return MAIN_MENU

async def main_menu_options(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "balance":
        await query.edit_message_text(text="Total balance: 0.89$ ",reply_markup=balance_menu)
        return BALANCE_MENU
    elif query.data == "pnl":
        await query.edit_message_text(text="Total pnl: 0.0338$",reply_markup=pnl_menu)
        return PNL
    elif query.data == "Transfer":
        await query.edit_message_text(text="Total pnl: 0.0338$",reply_markup=transfer_menu)
        return TRANSFER
    elif query.data == "⬅️️":
        await query.edit_message_text(text="Unknown option selected.")
        return MAIN_MENU

async def pnl_options(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    if query.data == "live":
        await query.edit_message_text(text="Your your live pnl is 0.89$ ",reply_markup=empty_menu)
        # return BALANCE_MENU
    elif query.data == "closed":
        await query.edit_message_text(text="your closed pnl is 0.0338$",reply_markup=empty_menu)
        # return PNL
    elif query.data == "⬅️️":
        await query.edit_message_text(text="Welcome! Please choose an option:",reply_markup=main_menu)
        return MAIN_MENU

async def balance_options(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == "transfer":
        await query.edit_message_text(text="choose the type of transfer ",reply_markup=transfer_menu)
        return TRANSFER
    elif query.data == "accounts' balances":
        await query.edit_message_text(text="Welcome! Please choose an option:",reply_markup=empty_menu)
        # return MAIN_MENU
    elif query.data == "⬅️️":
        await query.edit_message_text(text="Welcome! Please choose an option:",reply_markup=main_menu)
        return MAIN_MENU
    
async def transfer_options(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    from_value = context.user_data.get("from", 'Not found')
    to_value = context.user_data.get("to", 'Not found')
    amount = context.user_data.get("amount", 'Not found')
    menu_text = f"{across_accounts_menu_text(from_value,to_value,amount)}"
    if query.data == "Across Accounts":
        await query.edit_message_text(text=menu_text,reply_markup=edit_across_accounts_menu(from_value,to_value,amount))
        return ACROSS_ACCOUNTS
    elif query.data == "Internal":
        await query.edit_message_text(text="sorry you can't transfer right now",reply_markup=transfer_menu)
        # return BALANCE_MENU
    elif query.data == "⬅️️":
        await query.edit_message_text(text="Welcome! Please choose an option:",reply_markup=main_menu)
        return MAIN_MENU
    
async def across_accounts_options(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    if "From" == query.data:
        await query.edit_message_text(text=f"From",reply_markup=accounts_menu)
        return FROM
    elif "🔃" == query.data:
        amount = context.user_data.get("amount", 'Not found')
        # switch from_id and to_id
        old_from_id = context.user_data.get("from_id", 'Not found')
        old_to_id = context.user_data.get("to_id", 'Not found')
        context.user_data["from_id"] = old_to_id
        context.user_data["to_id"] = old_from_id
        # switch from_value and to_value
        old_from_value = context.user_data.get("from", 'Not found')
        old_to_value = context.user_data.get("to", 'Not found')
        context.user_data["from"] = old_to_value
        context.user_data["to"] = old_from_value
        # -----------
        from_value = context.user_data.get("from", 'Not found')
        to_value = context.user_data.get("to", 'Not found')
        menu_text = f"{across_accounts_menu_text(from_value,to_value,amount)}"
        await query.edit_message_text(text=f"{menu_text}",reply_markup=edit_across_accounts_menu(from_value,to_value,amount))
        # return AMOUNT
    elif "To" == query.data:
        await query.edit_message_text(text=f"To",reply_markup=accounts_menu)
        return TO
    elif "Amount" == query.data:
        await query.edit_message_text(text="Amount",reply_markup=amount_menu)
        return AMOUNT
    elif "Make Transfer ✅" == query.data:
        from_value = context.user_data.get("from", 'Not found')
        to_value = context.user_data.get("to", 'Not found')
        from_id = context.user_data.get("from_id", 'Not found')
        to_id = context.user_data.get("to_id", 'Not found')
        amount = context.user_data.get("amount", 'Not found')
        transferable_amount = float(get_balance_details(from_id,"UNIFIED")["transferBalance"])
        if float(amount) > transferable_amount:
            menu_text = f'Transfer Failed ❌\nTransferable amount is [ {transferable_amount} $ ]'
        else:
            menu_text = f"Successful Transfer ✅\n\n {across_accounts_menu_text(from_value,to_value,amount)}"
            new_across_account_transfer(from_id,to_id,"UNIFIED","UNIFIED",amount)

        await query.edit_message_text(text=menu_text,reply_markup=edit_across_accounts_menu(from_value,to_value,amount))
        return ACROSS_ACCOUNTS
    elif query.data == "⬅️️":
        await query.edit_message_text(text="choose the type of transfer ",reply_markup=transfer_menu)
        return TRANSFER

async def From_options(update: Update,context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    from_value = context.user_data.get("from", 'Not found')
    to_value = context.user_data.get("to", 'Not found')
    amount = context.user_data.get("amount", 'Not found')
    menu_text = f"{across_accounts_menu_text(from_value,to_value,amount)}"
    if query.data == "Main Account":
        context.user_data["from"] = "Main Account"
        context.user_data["from_id"] = MAIN_ACCOUNT_ID
        from_value = context.user_data.get("from", 'Not found')
        menu_text = f"{across_accounts_menu_text(from_value,to_value,amount)}"
        await query.edit_message_text(text=menu_text,reply_markup=edit_across_accounts_menu(from_value,to_value,amount))
        return ACROSS_ACCOUNTS
    elif query.data == "Volume Flow":
        context.user_data["from"] = "Volume Flow"
        context.user_data["from_id"] = VOLUME_FLOW_ID
        from_value = context.user_data.get("from", 'Not found')
        menu_text = f"{across_accounts_menu_text(from_value,to_value,amount)}"
        await query.edit_message_text(text=menu_text,reply_markup=edit_across_accounts_menu(from_value,to_value,amount))
        return ACROSS_ACCOUNTS
    elif query.data == "EmergencyFunds":
        context.user_data["from"] = "EmergencyFunds"
        context.user_data["from_id"] = EMERGENCYFUNDS_ID
        from_value = context.user_data.get("from", 'Not found') 
        menu_text = f"{across_accounts_menu_text(from_value,to_value,amount)}"
        await query.edit_message_text(text=menu_text,reply_markup=edit_across_accounts_menu(from_value,to_value,amount))
        return ACROSS_ACCOUNTS
    elif query.data == "⬅️️":
        from_value = context.user_data.get("from", 'Not found')
        menu_text = f"{across_accounts_menu_text(from_value,to_value,amount)}"
        await query.edit_message_text(text=menu_text,reply_markup=edit_across_accounts_menu(from_value,to_value,amount))
        return ACROSS_ACCOUNTS
    

async def To_options(update: Update,context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    from_value = context.user_data.get("from", 'Not found')
    to_value = context.user_data.get("to", 'Not found')
    amount = context.user_data.get("amount", 'Not found')
    menu_text = f"{across_accounts_menu_text(from_value,to_value,amount)}"
    if query.data == "Main Account":
        context.user_data["to"] = "Main Account"
        context.user_data["to_id"] = MAIN_ACCOUNT_ID
        to_value = context.user_data.get("to", 'Not found') 
        menu_text = f"{across_accounts_menu_text(from_value,to_value,amount)}"
        await query.edit_message_text(text=menu_text,reply_markup=edit_across_accounts_menu(from_value,to_value,amount))
        return ACROSS_ACCOUNTS
    elif query.data == "Volume Flow":
        context.user_data["to"] = "Volume Flow"
        context.user_data["to_id"] = VOLUME_FLOW_ID
        to_value = context.user_data.get("to", 'Not found') 
        menu_text = f"{across_accounts_menu_text(from_value,to_value,amount)}"
        await query.edit_message_text(text=menu_text,reply_markup=edit_across_accounts_menu(from_value,to_value,amount))
        return ACROSS_ACCOUNTS
    elif query.data == "EmergencyFunds":
        context.user_data["to"] = "EmergencyFunds"
        context.user_data["to_id"] = EMERGENCYFUNDS_ID
        to_value = context.user_data.get("to", 'Not found') 
        menu_text = f"{across_accounts_menu_text(from_value,to_value,amount)}"
        await query.edit_message_text(text=menu_text,reply_markup=edit_across_accounts_menu(from_value,to_value,amount))
        return ACROSS_ACCOUNTS
    elif query.data == "⬅️️":
        menu_text = f"{across_accounts_menu_text(from_value,to_value,amount)}"
        await query.edit_message_text(text=menu_text,reply_markup=edit_across_accounts_menu(from_value,to_value,amount))
        return ACROSS_ACCOUNTS


async def amount_options(update: Update,context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    from_value = context.user_data.get("from", 'Not found')
    to_value = context.user_data.get("to", 'Not found')
    amount = context.user_data.get("amount", 'Not found')
    menu_text = f"{across_accounts_menu_text(from_value,to_value,amount)}"
    if query.data == "⬅️️":
        menu_text = f"{across_accounts_menu_text(from_value,to_value,amount)}"
        await query.edit_message_text(text=menu_text,reply_markup=edit_across_accounts_menu(from_value,to_value,amount))
        return ACROSS_ACCOUNTS
    elif query.data == "All":
        from_id = context.user_data.get("from_id", 'Not found')
        transferable_amount = float(get_balance_details(from_id,"UNIFIED")["transferBalance"])
        context.user_data["amount"] = transferable_amount
        amount = context.user_data.get("amount", 'Not found')
        menu_text = f"{across_accounts_menu_text(from_value,to_value,amount)}"
        await query.edit_message_text(text=menu_text,reply_markup=edit_across_accounts_menu(from_value,to_value,amount))
        return ACROSS_ACCOUNTS
    else:
        context.user_data["amount"] = query.data
        amount = context.user_data.get("amount", 'Not found')
        menu_text = f"{across_accounts_menu_text(from_value,to_value,amount)}"
        await query.edit_message_text(text=menu_text,reply_markup=edit_across_accounts_menu(from_value,to_value,amount))
        return ACROSS_ACCOUNTS


# Cancel handler
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

# Main function to start the bot
def main():
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .read_timeout(10)
        .write_timeout(10)
        .concurrent_updates(True)
        .build()
    )

    # ConversationHandler to handle the state machine
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [CallbackQueryHandler(main_menu_options)],
            BALANCE_MENU: [CallbackQueryHandler(balance_options)],
            PNL: [CallbackQueryHandler(pnl_options)],
            TRANSFER: [CallbackQueryHandler(transfer_options)],
            ACROSS_ACCOUNTS: [CallbackQueryHandler(across_accounts_options)],
            FROM: [CallbackQueryHandler(From_options)],
            TO: [CallbackQueryHandler(To_options)],
            AMOUNT: [CallbackQueryHandler(amount_options)],
            # PNL: [MessageHandler(filters.TEXT & ~filters.COMMAND, cancel)],
        },
        fallbacks=[CommandHandler("start", start)],
    )


    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()