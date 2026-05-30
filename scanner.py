import time
import requests

from strategy import analyze
from logger import logger


BINANCE_URL = "https://api.binance.com"


SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "DOGEUSDT",
    "TRXUSDT",
    "AVAXUSDT",
    "LINKUSDT",
]


LAST_SIGNAL_TIME = {}
COOLDOWN_MINUTES = 90


def get_klines(symbol, interval, limit=200):
    url = f"{BINANCE_URL}/api/v3/klines"

    try:
        response = requests.get(
            url,
            params={
                "symbol": symbol,
                "interval": interval,
                "limit": limit,
            },
            timeout=15,
        )

        logger.info(
            f"{symbol} {interval} STATUS={response.status_code}"
        )

        if response.status_code != 200:
            logger.warning(
                f"⚠️ BINANCE ERROR: {symbol} STATUS={response.status_code}"
            )

            logger.warning(response.text[:300])

            return None

        data = response.json()

        candles = []

        for candle in data:
            candles.append(
                {
                    "open": float(candle[1]),
                    "high": float(candle[2]),
                    "low": float(candle[3]),
                    "close": float(candle[4]),
                    "volume": float(candle[5]),
                }
            )

        return candles

    except Exception as e:
        logger.error(
            f"❌ KLINES ERROR {symbol}: {e}"
        )

        return None


def in_cooldown(symbol):
    if symbol not in LAST_SIGNAL_TIME:
        return False

    elapsed = time.time() - LAST_SIGNAL_TIME[symbol]

    return elapsed < (COOLDOWN_MINUTES * 60)


def correlation_filter(signals, new_signal):
    if not signals:
        return True

    same_direction = sum(
        1
        for signal in signals
        if signal["direction"] == new_signal["direction"]
    )

    if same_direction >= 3:
        logger.info("⚠️ CORRELATION BLOCKED")
        return False

    return True


def scan_market():
    signals = []

    logger.info("🔍 SCANNING MARKET")

    for symbol in SYMBOLS:

        try:

            if in_cooldown(symbol):
                logger.info(
                    f"⏳ COOLDOWN: {symbol}"
                )
                continue

            candles_5m = get_klines(symbol, "5m")
            candles_15m = get_klines(symbol, "15m")
            candles_1h = get_klines(symbol, "1h")

            if (
                candles_5m is None
                or candles_15m is None
                or candles_1h is None
            ):
                logger.warning(
                    f"⚠️ NO DATA: {symbol}"
                )
                continue

            signal = analyze(
                symbol,
                candles_5m,
                candles_15m,
                candles_1h,
            )

            if signal is None:
                logger.info(
                    f"❌ NO SETUP: {symbol}"
                )
                continue

            if not correlation_filter(
                signals,
                signal,
            ):
                continue

            LAST_SIGNAL_TIME[symbol] = time.time()

            signals.append(signal)

            logger.info(
                f"🔥 SIGNAL FOUND {symbol} "
                f"{signal['direction']}"
            )

        except Exception as e:
            logger.error(
                f"❌ SCAN ERROR {symbol}: {e}"
            )

    logger.info(
        f"📊 FOUND {len(signals)} SIGNALS"
    )

    return signals
