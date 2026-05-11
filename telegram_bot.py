import os
import requests

from logger import logger


# ================= ENV =================
BOT_TOKEN = os.getenv("BOT_TOKEN")

VIP_CHAT_ID = os.getenv("VIP_CHAT_ID")

PUBLIC_CHAT_ID = os.getenv("PUBLIC_CHAT_ID")


# ================= SEND =================
def send(target, message):

    try:

        # ================= TARGET =================
        if target == "VIP":

            chat_id = VIP_CHAT_ID

        else:

            chat_id = PUBLIC_CHAT_ID

        # ================= API URL =================
        url = (
            f"https://api.telegram.org/"
            f"bot{BOT_TOKEN}/sendMessage"
        )

        payload = {

            "chat_id": chat_id,

            "text": message

        }

        response = requests.post(
            url,
            data=payload,
            timeout=15
        )

        logger.info(
            f"📨 TELEGRAM STATUS: "
            f"{response.status_code}"
        )

        logger.info(
            f"📨 TELEGRAM RESPONSE: "
            f"{response.text}"
        )

    except Exception as e:

        logger.error(
            f"❌ TELEGRAM ERROR: {e}"
        )
