from scanner import get_klines

from database import (
    get_open_signals,
    close_signal
)

from logger import logger


# ================= MONITOR SIGNALS =================
def monitor_signals():

    try:

        signals = get_open_signals()

        if not signals:

            logger.info(
                "📭 NO OPEN SIGNALS"
            )

            return


        logger.info(
            f"👀 MONITORING "
            f"{len(signals)} SIGNALS"
        )


        for signal in signals:

            try:

                symbol = signal["symbol"]

                direction = signal["direction"]

                tp = float(
                    signal["take_profit"]
                )

                sl = float(
                    signal["stop_loss"]
                )

                signal_id = signal["id"]


                candles = get_klines(
                    symbol=symbol,
                    interval="5m",
                    limit=2
                )

                if not candles:
                    continue


                current_price = candles[-1]["close"]


                # ================= BUY =================
                if direction == "BUY":

                    # TAKE PROFIT
                    if current_price >= tp:

                        close_signal(
                            signal_id,
                            "WIN"
                        )

                        logger.info(
                            f"🏆 TP HIT: "
                            f"{symbol}"
                        )

                    # STOP LOSS
                    elif current_price <= sl:

                        close_signal(
                            signal_id,
                            "LOSS"
                        )

                        logger.info(
                            f"💀 SL HIT: "
                            f"{symbol}"
                        )


                # ================= SELL =================
                elif direction == "SELL":

                    # TAKE PROFIT
                    if current_price <= tp:

                        close_signal(
                            signal_id,
                            "WIN"
                        )

                        logger.info(
                            f"🏆 TP HIT: "
                            f"{symbol}"
                        )

                    # STOP LOSS
                    elif current_price >= sl:

                        close_signal(
                            signal_id,
                            "LOSS"
                        )

                        logger.info(
                            f"💀 SL HIT: "
                            f"{symbol}"
                        )


            except Exception as signal_error:

                logger.error(
                    f"❌ MONITOR SIGNAL ERROR: "
                    f"{signal_error}"
                )


    except Exception as e:

        logger.error(
            f"❌ MONITOR ERROR: {e}"
        )
