import time

from logger import logger

from scanner import (
    SYMBOLS,
    get_klines,
    btc_regime
)

from strategy import (
    generate_signal
)

from telegram_bot import (
    send_public_signal,
    send_vip_signal
)

from database import (
    initialize_database,
    save_signal,
    get_open_signals,
    close_signal
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

        # ================= BTC REGIME =================
        market_regime = btc_regime()

        logger.info(
            f"📊 BTC REGIME: "
            f"{market_regime}"
        )

        # ================= SCAN SYMBOLS =================
        for symbol in SYMBOLS:

            try:

                candles = get_klines(
                    symbol=symbol,
                    interval="15m",
                    limit=120
                )

                if not candles:

                    logger.warning(
                        f"⚠️ NO DATA: {symbol}"
                    )

                    continue


                # ================= GENERATE SIGNAL =================
                signal = generate_signal(
                    symbol=symbol,
                    candles=candles,
                    market_regime=market_regime
                )

                if signal is None:
                    continue


                # ================= TELEGRAM =================
                send_public_signal(signal)

                send_vip_signal(
                    signal,
                    get_win_rate()
                )


                # ================= SAVE DATABASE =================
                save_signal(signal)


                logger.info(
                    f"✅ SIGNAL SENT: "
                    f"{symbol}"
                )

                time.sleep(1)


            except Exception as symbol_error:

                logger.error(
                    f"❌ SYMBOL ERROR: "
                    f"{symbol} "
                    f"{symbol_error}"
                )


        # ================= MONITOR OPEN SIGNALS =================
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
