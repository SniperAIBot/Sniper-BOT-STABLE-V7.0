import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
VIP_CHAT_ID = os.getenv("CHAT_ID")
PUBLIC_CHAT_ID = os.getenv("PUBLIC_CHAT_ID")
DATABASE_URL = os.getenv("DATABASE_URL")
VIP_LINK = os.getenv("VIP_LINK")

BASE_URL = "https://data-api.binance.vision"

SCAN_INTERVAL = 300
COOLDOWN_SECONDS = 7200

PAIRS = [

    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "BNBUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "AVAXUSDT",
    "LINKUSDT",
    "DOTUSDT",
    "TRXUSDT",
    "MATICUSDT",
    "SUIUSDT",
    "APTUSDT",
    "ARBUSDT",
    "OPUSDT",
    "ATOMUSDT",
    "NEARUSDT",
    "INJUSDT",
    "SEIUSDT",
    "FILUSDT",
    "TIAUSDT",
    "WIFUSDT",
    "PEPEUSDT",
    "ORDIUSDT",
    "LTCUSDT",
    "ETCUSDT",
    "AAVEUSDT",
    "APEUSDT",
    "UNIUSDT",
    "ICPUSDT"
]
