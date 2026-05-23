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


# ================= ENGINE START =================
logger.info(
    "🚀 STARTING SNIPER PRO ENGINE v4"
)


# ================= INIT DATABASE =================
try:

    initialize_database()

    logger.info(
        "✅ DATABASE INITIALIZED"
    )

except Exception as db_error:

    logger.error(
        f"❌ DATABASE INIT ERROR: "
        f"{db_error}"
    )


# ================= MAIN LOOP =================
while True:

    try:

        logger.info(
            "🔁 STARTING MARKET CYCLE"
        )

        # =====================================================
        # ================= SCAN MARKET =======================
        # =====================================================
        try:

            signals = scan_market()

        except Exception as scan_error:

            logger.error(
                f"❌ MARKET SCAN ERROR: "
                f"{scan_error}"
            )

            signals = []


        # =====================================================
        # ================= PROCESS SIGNALS ===================
        # =====================================================
        signals_sent = 0

        for signal in signals:

            try:

                symbol = signal.get(
                    "symbol",
                    "UNKNOWN"
                )

                logger.info(
                    f"📨 PROCESSING SIGNAL: "
                    f"{symbol}"
                )

                # ================= SEND PUBLIC =================
                send_public_signal(signal)

                # ================= SEND VIP =================
                send_vip_signal(

                    signal,

                    get_win_rate()

                )

                # ================= SAVE DATABASE =================
                save_signal(signal)

                signals_sent += 1

                logger.info(
                    f"✅ SIGNAL DEPLOYED: "
                    f"{symbol}"
                )

                # ================= ANTI-SPAM =================
                time.sleep(1)

            except Exception as signal_error:

                logger.error(
                    f"❌ SIGNAL PROCESS ERROR: "
                    f"{signal_error}"
                )


        # =====================================================
        # ================= SUMMARY ===========================
        # =====================================================
        logger.info(
            f"📊 CYCLE COMPLETE | "
            f"SIGNALS SENT: "
            f"{signals_sent}"
        )


        # =====================================================
        # ================= MONITOR SIGNALS ===================
        # =====================================================
        try:

            monitor_signals()

        except Exception as monitor_error:

            logger.error(
                f"❌ MONITOR ERROR: "
                f"{monitor_error}"
            )


        # =====================================================
        # ================= SLEEP =============================
        # =====================================================
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
