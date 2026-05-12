import os
import requests

from logger import logger


# ================= ENV VARIABLES =================
BOT_TOKEN = os.getenv("BOT_TOKEN")

PUBLIC_CHAT_ID = os.getenv(
    "PUBLIC_CHAT_ID"
)

VIP_CHAT_ID = os.getenv(
    "VIP_CHAT_ID"
)


# ================= TELEGRAM URL =================
BASE_URL = (
    f"https://api.telegram.org/bot"
    f"{BOT_TOKEN}/sendMessage"
)


# ================= SEND MESSAGE =================
def send_message(
    chat_id,
    text
):

    try:

        response = requests.post(

            BASE_URL,

            json={

                "chat_id": chat_id,

                "text": text

            },

            timeout=10

        )

        logger.info(
            f"📨 TELEGRAM STATUS: "
            f"{response.status_code}"
        )

        logger.info(
            f"📨 TELEGRAM RESPONSE: "
            f"{response.text}"
        )

        return response.json()

    except Exception as e:

        logger.error(
            f"❌ TELEGRAM ERROR: {e}"
        )

        return None


# ================= PUBLIC SIGNAL =================
def send_public_signal(signal):

    try:

        direction_emoji = (
            "📈"
            if signal["direction"] == "BUY"
            else "📉"
        )

        message = f"""
🚨 فرصة تداول جديدة

💰 العملة:
{signal['symbol']}

📊 الاتجاه:
{signal['direction']} {direction_emoji}

🎯 نسبة النجاح:
{signal['confidence']}%

📈 السوق:
{signal['market_regime']}

🔥 تحليل لحظي بالذكاء الاصطناعي

🔒 التفاصيل الكاملة داخل VIP
https://t.me/+5fG1CslEcxdhNWQ6
"""

        send_message(
            PUBLIC_CHAT_ID,
            message
        )

    except Exception as e:

        logger.error(
            f"❌ PUBLIC SIGNAL ERROR: {e}"
        )


# ================= VIP SIGNAL =================
def send_vip_signal(
    signal,
    win_rate=0
):

    try:

        direction_emoji = (
            "📈"
            if signal["direction"] == "BUY"
            else "📉"
        )

        message = f"""
🚨 إشارة احترافية جديدة

💰 العملة:
{signal['symbol']}

📊 الاتجاه:
{signal['direction']} {direction_emoji}

💵 نقطة الدخول:
{signal['entry']}

🎯 الهدف:
{signal['take_profit']}

🛑 وقف الخسارة:
{signal['stop_loss']}

📈 نسبة النجاح:
{signal['confidence']}%

📊 RSI:
{signal['rsi']}

⚡ ATR:
{signal['atr']}

🔥 حالة السوق:
{signal['market_regime']}

📉 نسبة نجاح النظام:
{win_rate}%
"""

        send_message(
            VIP_CHAT_ID,
            message
        )

    except Exception as e:

        logger.error(
            f"❌ VIP SIGNAL ERROR: {e}"
        )
