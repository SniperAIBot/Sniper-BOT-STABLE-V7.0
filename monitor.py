import time

from scanner import get_klines

from database import (
    get_open_signals,
    close_signal
)

from logger import logger


# ================= CONFIG =================
MAX_TRADE_DURATION = 14400

BREAKEVEN_TRIGGER = 0.75


# ================= MONITOR =================
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

                signal_id = signal.get("id")

                symbol = signal.get("symbol")

                direction = signal.get("direction")

                entry = float(
                    signal.get("entry")
                )

                tp = float(
                    signal.get("take_profit")
                )

                sl = float(
                    signal.get("stop_loss")
                )

                created_at = signal.get(
                    "created_at"
                )

                if (
                    not symbol
                    or not direction
                ):

                    continue

                candles = get_klines(
                    symbol=symbol,
                    interval="5m",
                    limit=2
                )

                if not candles:

                    continue

                current_price = candles[-1]["close"]

                # ================= RISK =================
                if direction == "BUY":

                    risk = (
                        entry - sl
                    )

                    current_profit = (
                        current_price - entry
                    )

                else:

                    risk = (
                        sl - entry
                    )

                    current_profit = (
                        entry - current_price
                    )

                if risk <= 0:

                    continue

                rr_progress = (
                    current_profit / risk
                )

                # ================= TIMEOUT EXIT =================
                if created_at:

                    try:

                        trade_age = (
                            time.time() -
                            created_at.timestamp()
                        )

                        if trade_age > MAX_TRADE_DURATION:

                            close_signal(
                                signal_id,
                                "TIMEOUT"
                            )

                            logger.info(
                                f"⌛ TIMEOUT EXIT: "
                                f"{symbol}"
                            )

                            continue

                    except:

                        pass

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

                        continue

                    # BREAKEVEN EXIT
                    if (
                        rr_progress >=
                        BREAKEVEN_TRIGGER
                        and current_price <= entry
                    ):

                        close_signal(
                            signal_id,
                            "BREAKEVEN"
                        )

                        logger.info(
                            f"⚖️ BREAKEVEN: "
                            f"{symbol}"
                        )

                        continue

                    # STOP LOSS
                    if current_price <= sl:

                        close_signal(
                            signal_id,
                            "LOSS"
                        )

                        logger.info(
                            f"💀 SL HIT: "
                            f"{symbol}"
                        )

                        continue

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

                        continue

                    # BREAKEVEN EXIT
                    if (
                        rr_progress >=
                        BREAKEVEN_TRIGGER
                        and current_price >= entry
                    ):

                        close_signal(
                            signal_id,
                            "BREAKEVEN"
                        )

                        logger.info(
                            f"⚖️ BREAKEVEN: "
                            f"{symbol}"
                        )

                        continue

                    # STOP LOSS
                    if current_price >= sl:

                        close_signal(
                            signal_id,
                            "LOSS"
                        )

                        logger.info(
                            f"💀 SL HIT: "
                            f"{symbol}"
                        )

                        continue

            except Exception as signal_error:

                logger.error(
                    f"❌ MONITOR SIGNAL ERROR: "
                    f"{signal_error}"
                )

    except Exception as e:

        logger.error(
            f"❌ MONITOR ERROR: {e}"
        )
