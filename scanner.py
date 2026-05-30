import requests
import time

from strategy import analyze
from logger import logger


BASE_URL = "https://data-api.binance.com"


# ================= TOP 10 COINS =================
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
    "LINKUSDT"
]


# ================= COOLDOWN =================
LAST_SIGNAL_TIME = {}

COOLDOWN_MINUTES = 90


# ================= GET KLINES =================
def get_klines(
    symbol,
    interval,
    limit=200
):

    try:

        response = requests.get(
            f"{BASE_URL}/api/v3/klines",
            params={
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            },
            timeout=10
        )

        if response.status_code != 200:

            logger.warning(
                f"⚠️ BINANCE ERROR: {symbol}"
            )

            return None

        data = response.json()

        candles = []

        for candle in data:

            candles.append({

                "open": float(candle[1]),
                "high": float(candle[2]),
                "low": float(candle[3]),
                "close": float(candle[4]),
                "volume": float(candle[5])

            })

        return candles

    except Exception as e:

        logger.error(
            f"❌ KLINES ERROR {symbol}: {e}"
        )

        return None


# ================= MARKET FILTER =================
# Disabled intentionally.
# Strategy.py already performs the real filtering.
def is_valid_market(symbol):

    return True


# ================= COOLDOWN =================
def in_cooldown(symbol):

    if symbol not in LAST_SIGNAL_TIME:

        return False

    elapsed = (
        time.time()
        -
        LAST_SIGNAL_TIME[symbol]
    )

    return elapsed < (
        COOLDOWN_MINUTES * 60
    )


# ================= CORRELATION FILTER =================
def correlation_filter(
    signals,
    new_signal
):

    if not signals:

        return True

    same_direction = sum(

        1

        for signal in signals

        if signal["direction"]
        ==
        new_signal["direction"]

    )

    if same_direction >= 3:

        logger.info(
            "⚠️ CORRELATION BLOCKED"
        )

        return False

    return True


# ================= SCAN MARKET =================
def scan_market():

    signals = []

    logger.info(
        "🔍 SCANNING MARKET"
    )

    for symbol in SYMBOLS:

        try:

            if in_cooldown(symbol):

                logger.info(
                    f"⏳ COOLDOWN: {symbol}"
                )

                continue


            candles_5m = get_klines(
                symbol,
                "5m"
            )

            candles_15m = get_klines(
                symbol,
                "15m"
            )

            candles_1h = get_klines(
                symbol,
                "1h"
            )

            if (
                not candles_5m
                or not candles_15m
                or not candles_1h
            ):

                logger.warning(
                    f"⚠️ NO DATA: {symbol}"
                )

                continue


            logger.info(
                f"📈 ANALYZING {symbol}"
            )


            signal = analyze(

                symbol,

                candles_5m,

                candles_15m,

                candles_1h

            )


            if signal is None:

                logger.info(
                    f"❌ NO SETUP: {symbol}"
                )

                continue


            logger.info(
                f"🔥 SIGNAL FOUND "
                f"{symbol} "
                f"{signal['direction']}"
            )


            if not correlation_filter(
                signals,
                signal
            ):

                continue


            LAST_SIGNAL_TIME[
                symbol
            ] = time.time()


            signals.append(
                signal
            )

            logger.info(
                f"✅ SIGNAL ADDED: "
                f"{symbol}"
            )


        except Exception as e:

            logger.error(
                f"❌ SCAN ERROR "
                f"{symbol}: {e}"
            )


    logger.info(
        f"📊 FOUND "
        f"{len(signals)} SIGNALS"
    )

    return signals
