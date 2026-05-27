import requests
import time

from strategy import analyze
from logger import logger


BASE_URL = "https://api.binance.com"


# ================= TOP MARKET CAP COINS =================
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


# ================= COOLDOWN SYSTEM =================
LAST_SIGNAL_TIME = {}

COOLDOWN_MINUTES = 90


# ================= GET KLINES =================
def get_klines(symbol, interval, limit=200):

    try:

        url = f"{BASE_URL}/api/v3/klines"

        response = requests.get(
            url,
            params={
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            },
            timeout=10
        )

        if response.status_code != 200:
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

        logger.error(f"❌ KLINES ERROR: {symbol} {e}")

        return None


# ================= 24H STATS =================
def get_ticker_stats(symbol):

    try:

        url = f"{BASE_URL}/api/v3/ticker/24hr"

        response = requests.get(
            url,
            params={"symbol": symbol},
            timeout=10
        )

        if response.status_code != 200:
            return None

        return response.json()

    except Exception:
        return None


# ================= LIQUIDITY FILTER =================
def is_valid_market(symbol):

    stats = get_ticker_stats(symbol)

    if not stats:
        return False

    quote_volume = float(stats["quoteVolume"])

    price_change = abs(float(stats["priceChangePercent"]))

    # Strong liquidity
    if quote_volume < 150000000:
        return False

    # Must be moving
    if price_change < 2:
        return False

    return True


# ================= COOLDOWN =================
def in_cooldown(symbol):

    if symbol not in LAST_SIGNAL_TIME:
        return False

    elapsed = time.time() - LAST_SIGNAL_TIME[symbol]

    return elapsed < (COOLDOWN_MINUTES * 60)


# ================= CORRELATION FILTER =================
def correlation_filter(signals, new_signal):

    if not signals:
        return True

    directions = [s["direction"] for s in signals]

    same_direction = directions.count(new_signal["direction"])

    if same_direction >= 3:
        return False

    return True


# ================= SCAN MARKET =================
def scan_market():

    signals = []

    for symbol in SYMBOLS:

        try:

            if in_cooldown(symbol):
                continue

            if not is_valid_market(symbol):

                logger.info(f"⚠️ MARKET FILTERED: {symbol}")

                continue

            candles_5m = get_klines(symbol, "5m")
            candles_15m = get_klines(symbol, "15m")
            candles_1h = get_klines(symbol, "1h")

            if not candles_5m or not candles_15m or not candles_1h:
                continue

            signal = analyze(
                symbol,
                candles_5m,
                candles_15m,
                candles_1h
            )

            if signal:

                if not correlation_filter(signals, signal):

                    logger.info("⚠️ CORRELATION BLOCKED")

                    continue

                LAST_SIGNAL_TIME[symbol] = time.time()

                signals.append(signal)

                logger.info(f"✅ SIGNAL: {symbol}")

        except Exception as e:

            logger.error(f"❌ SCAN ERROR: {symbol} {e}")

    return signals
