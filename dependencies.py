from pybit.unified_trading import HTTP
import json
from pathlib import Path
import uuid
from pprint import pprint

BOT_TOKEN = "8223616346:AAGfZBgE8UJQL29nl5kp2MFGtOpRxT6X9VI"

script_dir = Path(__file__).parent
session = HTTP(
    testnet=False,
    api_key="DYagNLt8eh6FKFCsbn",
    api_secret="bVvLdk08q84VdpO5s6oDoHD4diPeUHv9la9z",
)


def save_json(data,file_name):
    script_dir = Path(__file__).parent
    with open(f'{script_dir}/{file_name}.json', 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


MAIN_ACCOUNT_ID = 75062656
VOLUME_FLOW_ID = 464131066
EMERGENCYFUNDS_ID = 460119889
