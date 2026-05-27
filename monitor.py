from scanner import get_klines

from database import (
    get_open_signals,
    close_signal
)

from logger import logger


# ================= MONITOR =================
def monitor_signals():

    try:

        signals = get_open_signals()

        if not signals:

            logger.info("📭 NO OPEN SIGNALS")

            return

        for signal in signals:

            try:

                candles = get_klines(
                    signal["symbol"],
                    "5m",
                    2
                )

                if not candles:
                    continue

                current_price = candles[-1]["close"]

                if signal["direction"] == "BUY":

                    if current_price >= signal["take_profit"]:

                        close_signal(signal["id"], "WIN")

                    elif current_price <= signal["stop_loss"]:

                        close_signal(signal["id"], "LOSS")

                elif signal["direction"] == "SELL":

                    if current_price <= signal["take_profit"]:

                        close_signal(signal["id"], "WIN")

                    elif current_price >= signal["stop_loss"]:

                        close_signal(signal["id"], "LOSS")

            except Exception as e:

                logger.error(f"❌ MONITOR SIGNAL ERROR: {e}")

    except Exception as e:

        logger.error(f"❌ MONITOR ERROR: {e}")
