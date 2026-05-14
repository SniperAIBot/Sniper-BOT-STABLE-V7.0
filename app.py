import time

from logger import logger

from scanner import (
    SYMBOLS,
    get_klines
)

from strategy import (
    analyze
)

from telegram_bot import (
    send_public_signal,
    send_vip_signal
)

from database import (
    initialize_database,
    save_signal
)

from performance import (
    get_win_rate
)

from monitor import (
    monitor_signals
)


# ================= START ENGINE =================
logger.info(
    "🚀 STARTING SNIPER PRO ENGINE"
)


# ================= INIT DATABASE =================
initialize_database()

logger.info(
    "✅ DATABASE INITIALIZED"
)


# ================= MAIN LOOP =================
while True:

    try:

        logger.info(
            "🔁 SCANNING MARKET..."
        )

        signals_found = 0


        # ================= LOOP SYMBOLS =================
        for symbol in SYMBOLS:

            try:

                logger.info(
                    f"🔍 SCANNING {symbol}"
                )


                # ================= GET 5M DATA =================
                candles_5m = get_klines(
                    symbol=symbol,
                    interval="5m",
                    limit=120
                )


                # ================= GET 15M DATA =================
                candles_15m = get_klines(
                    symbol=symbol,
                    interval="15m",
                    limit=120
                )


                # ================= GET 1H DATA =================
                candles_1h = get_klines(
                    symbol=symbol,
                    interval="1h",
                    limit=120
                )


                # ================= VALIDATION =================
                if (

                    not candles_5m
                    or not candles_15m
                    or not candles_1h

                ):

                    logger.warning(
                        f"⚠️ NO DATA: {symbol}"
                    )

                    continue


                # ================= ANALYZE =================
                signal = analyze(

                    symbol=symbol,

                    candles_5m=candles_5m,

                    candles_15m=candles_15m,

                    candles_1h=candles_1h
                )


                # ================= NO SIGNAL =================
                if signal is None:

                    continue


                # ================= SEND TELEGRAM =================
                send_public_signal(signal)

                send_vip_signal(
                    signal,
                    get_win_rate()
                )


                # ================= SAVE DATABASE =================
                save_signal(signal)


                signals_found += 1


                logger.info(
                    f"✅ SIGNAL SENT: "
                    f"{symbol}"
                )


                # ================= ANTI SPAM =================
                time.sleep(1)


            except Exception as symbol_error:

                logger.error(
                    f"❌ SCAN ERROR: "
                    f"{symbol} "
                    f"{symbol_error}"
                )


        # ================= SIGNAL SUMMARY =================
        logger.info(
            f"📊 FOUND "
            f"{signals_found} SIGNALS"
        )


        # ================= MONITOR SIGNALS =================
        try:

            monitor_signals()

        except Exception as monitor_error:

            logger.error(
                f"❌ MONITOR ERROR: "
                f"{monitor_error}"
            )


        # ================= LOOP DELAY =================
        logger.info(
            "⏳ Sleeping 300 seconds..."
        )

        time.sleep(300)


    except Exception as main_error:

        logger.error(
            f"❌ MAIN LOOP ERROR: "
            f"{main_error}"
        )

        time.sleep(60)
