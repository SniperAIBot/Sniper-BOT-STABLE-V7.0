import time

from logger import logger

from scanner import scan_market

from database import (
    initialize_database,
    save_signal
)

from monitor import monitor_signals

from telegram_bot import (
    send_public_signal,
    send_vip_signal
)

from performance import get_statistics


logger.info("🚀 STARTING ENGINE")

initialize_database()


while True:

    try:

        logger.info("🔍 SCANNING MARKET")

        signals = scan_market()

        logger.info(f"📊 FOUND {len(signals)} SIGNALS")

        for signal in signals:

            try:

                save_signal(signal)

                stats = get_statistics()

                send_public_signal(signal)

                send_vip_signal(
                    signal,
                    stats["win_rate"]
                )

                logger.info(
                    f"✅ SIGNAL SENT: {signal['symbol']}"
                )

                time.sleep(1)

            except Exception as e:

                logger.error(f"❌ SIGNAL ERROR: {e}")

        monitor_signals()

        logger.info("⏳ SLEEPING 300 SECONDS")

        time.sleep(300)

    except Exception as e:

        logger.error(f"❌ MAIN LOOP ERROR: {e}")

        time.sleep(60)
