from dependencies import *

def get_balance_details(account_id,type):
    account_balance_details = session.get_coin_balance(
        accountType=type,
        coin="USDT",
        memberId=account_id,
        
    )['result']['balance']
    return account_balance_details

# transferable_balance = ["transferBalance"]

def new_across_account_transfer(from_account,to_account,from_type,to_type,amount):
    RANDOM_UUID = str(uuid.uuid4())
    transfer_details = session.create_universal_transfer(
        transferId=RANDOM_UUID,
        coin="USDT",
        amount=str(amount),
        fromMemberId=from_account,
        toMemberId=to_account,
        fromAccountType=from_type,
        toAccountType=to_type,
    )
    return transfer_details



transferable_balance = float(get_balance_details(MAIN_ACCOUNT_ID,"UNIFIED")["transferBalance"])

# transfer_details = new_across_account_transfer(MAIN_ACCOUNT_ID,VOLUME_FLOW_ID,"UNIFIED","UNIFIED",transferable_balance)

# pprint(transfer_details)