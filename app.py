import os
import time
from datetime import datetime

from dotenv import load_dotenv

from config import PAIRS
from logger import logger

from database import (
    init_db,
    save_signal,
    get_open_signals,
    close_signal
)

from scanner import (
    get_klines,
    btc_regime
)

from strategy import analyze

from telegram_bot import send

from performance import get_win_rate


# ================= LOAD ENV =================
load_dotenv()


# ================= CHECK ENV =================
required_env = [
    "BOT_TOKEN",
    "VIP_CHAT_ID",
    "PUBLIC_CHAT_ID",
    "DATABASE_URL"
]

for var in required_env:
    if not os.getenv(var):
        raise Exception(f"❌ Missing environment variable: {var}")


# ================= START =================
logger.info("🚀 STARTING SNIPER PRO ENGINE")


# ================= INIT DATABASE =================
init_db()


# ================= COOLDOWN =================
last_signal_time = {}


# ================= UPDATE RESULTS =================
def update_results():

    try:

        open_signals = get_open_signals()

        for row in open_signals:

            signal_id = row[0]
            symbol = row[1]
            trend = row[2]
            entry = float(row[3])
            tp = float(row[4])
            sl = float(row[5])

            candles = get_klines(
                symbol,
                "5m",
                2
            )

            if not candles:
                continue

            price = candles[-1]["close"]

            # ================= BUY =================
            if trend == "UP":

                # TAKE PROFIT
                if price >= tp:

                    close_signal(
                        signal_id,
                        "TP",
                        price
                    )

                    logger.info(
                        f"✅ TP HIT: {symbol}"
                    )

                # STOP LOSS
                elif price <= sl:

                    close_signal(
                        signal_id,
                        "SL",
                        price
                    )

                    logger.info(
                        f"❌ SL HIT: {symbol}"
                    )

            # ================= SELL =================
            else:

                # TAKE PROFIT
                if price <= tp:

                    close_signal(
                        signal_id,
                        "TP",
                        price
                    )

                    logger.info(
                        f"✅ TP HIT: {symbol}"
                    )

                # STOP LOSS
                elif price >= sl:

                    close_signal(
                        signal_id,
                        "SL",
                        price
                    )

                    logger.info(
                        f"❌ SL HIT: {symbol}"
                    )

    except Exception as e:

        logger.error(
            f"❌ UPDATE RESULTS ERROR: {e}"
        )


# ================= MAIN LOOP =================
while True:

    try:

        logger.info(
            "🔁 SCANNING MARKET..."
        )

        # ================= UPDATE OLD SIGNALS =================
        update_results()

        # ================= MARKET REGIME =================
        regime = btc_regime()

        logger.info(
            f"📊 BTC REGIME: {regime}"
        )

        # ================= WIN RATE =================
        win_rate = get_win_rate()

        # ================= SCAN PAIRS =================
        for symbol in PAIRS:

            try:

                # ================= COOLDOWN =================
                if symbol in last_signal_time:

                    elapsed = (
                        time.time()
                        - last_signal_time[symbol]
                    )

                    # 1 HOUR COOLDOWN
                    if elapsed < 3600:
                        continue

                # ================= HIGHER TF =================
                htf = get_klines(
                    symbol,
                    "1h",
                    100
                )

                # ================= LOWER TF =================
                ltf = get_klines(
                    symbol,
                    "5m",
                    100
                )

                if not htf or not ltf:
                    continue

                # ================= ANALYZE =================
                signal = analyze(
                    symbol,
                    htf,
                    ltf,
                    regime
                )

                if not signal:
                    continue

                # ================= ADD METADATA =================
                signal["symbol"] = symbol
                signal["time"] = str(datetime.now())

                # ================= PUBLIC MESSAGE =================
                public_msg = f"""
🚨 فرصة تداول جديدة

💰 العملة:
{symbol}

📊 الاتجاه:
{signal['signal']}

🎯 نسبة النجاح:
{signal['score']}%

📈 السوق:
{regime}

🔥 تحليل لحظي بالذكاء الاصطناعي

🔒 التفاصيل الكاملة داخل VIP
https://t.me/+5fG1CslEcxdhNWQ6
"""

                # ================= VIP MESSAGE =================
                vip_msg = f"""
🚨 إشارة احترافية جديدة

💰 العملة:
{symbol}

📊 الاتجاه:
{signal['signal']}

💵 نقطة الدخول:
{signal['entry']:.6f}

🎯 الهدف:
{signal['tp']:.6f}

🛑 وقف الخسارة:
{signal['sl']:.6f}

📈 نسبة النجاح:
{signal['score']}%

📊 RSI:
{signal['rsi']:.2f}

⚡ ATR:
{signal['atr']:.6f}

🔥 حالة السوق:
{regime}

📉 نسبة نجاح النظام:
{win_rate}%
"""

                # ================= SEND TO TELEGRAM =================
                send(
                    "PUBLIC",
                    public_msg
                )

                send(
                    "VIP",
                    vip_msg
                )

                # ================= SAVE SIGNAL =================
                save_signal(signal)

                # ================= SAVE COOLDOWN =================
                last_signal_time[symbol] = (
                    time.time()
                )

                logger.info(
                    f"✅ SIGNAL SENT: {symbol}"
                )

            except Exception as e:

                logger.error(
                    f"❌ PAIR ERROR {symbol}: {e}"
                )

        # ================= WAIT =================
        logger.info(
            "⏳ Sleeping 300 seconds..."
        )

        time.sleep(300)

    except Exception as e:

        logger.error(
            f"❌ MAIN LOOP ERROR: {e}"
        )

        time.sleep(10)
