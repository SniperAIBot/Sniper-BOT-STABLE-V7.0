import time

from logger import logger

from scanner import (
    scan_market
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


        # ================= GET SIGNALS =================
        signals = scan_market()


        logger.info(
            f"📊 FOUND {len(signals)} SIGNALS"
        )


        # ================= PROCESS SIGNALS =================
        for signal in signals:

            try:

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
                    f"{signal['symbol']}"
                )

                time.sleep(1)


            except Exception as signal_error:

                logger.error(
                    f"❌ SIGNAL ERROR: "
                    f"{signal_error}"
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
