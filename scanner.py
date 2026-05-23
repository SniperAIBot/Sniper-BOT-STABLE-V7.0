import requests
import time
import pandas as pd

from strategy import analyze
from logger import logger

# ================= CONFIG =================
BASE_URL = "https://data-api.binance.vision"

# ================= ELITE SYMBOLS ONLY =================
SYMBOLS = [

    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "DOGEUSDT",
    "ADAUSDT",
    "LINKUSDT",
    "AVAXUSDT",
    "AAVEUSDT",
    "INJUSDT",
    "ATOMUSDT",
    "APTUSDT",
    "FILUSDT",
    "SEIUSDT"

]

# ================= COOLDOWN =================
LAST_SIGNAL_TIME = {}

COOLDOWN_SECONDS = 7200

# ================= CORRELATION GROUPS =================
CORRELATION_GROUPS = {

    "BTC": [
        "BTCUSDT",
        "ETHUSDT",
        "SOLUSDT",
        "BNBUSDT"
    ],

    "ALT": [
        "AVAXUSDT",
        "ADAUSDT",
        "ATOMUSDT",
        "APTUSDT",
        "SEIUSDT",
        "FILUSDT"
    ]
}

MAX_SIGNALS_PER_GROUP = 1


# ================= GET GROUP =================
def get_group(symbol):

    for group, symbols in CORRELATION_GROUPS.items():

        if symbol in symbols:

            return group

    return None


# ================= GET KLINES =================
def get_klines(
    symbol,
    interval,
    limit=200
):

    try:

        url = (
            f"{BASE_URL}/api/v3/klines"
        )

        params = {

            "symbol": symbol,
            "interval": interval,
            "limit": limit

        }

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code != 200:

            logger.error(
                f"❌ BINANCE STATUS ERROR: "
                f"{response.status_code}"
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
            f"❌ KLINES ERROR: "
            f"{symbol} {e}"
        )

        return None


# ================= LIQUIDITY FILTER =================
def passes_liquidity_filter(candles):

    try:

        df = pd.DataFrame(candles)

        avg_volume = (
            df["volume"]
            .astype(float)
            .tail(20)
            .mean()
        )

        return avg_volume > 100000

    except:

        return False


# ================= MOMENTUM FILTER =================
def passes_momentum_filter(candles):

    try:

        df = pd.DataFrame(candles)

        close_now = float(
            df["close"].iloc[-1]
        )

        close_before = float(
            df["close"].iloc[-12]
        )

        move_percent = abs(
            (
                close_now -
                close_before
            ) / close_before
        ) * 100

        return move_percent > 1.0

    except:

        return False


# ================= SCAN MARKET =================
def scan_market():

    signals = []

    active_groups = {}

    logger.info(
        "🔍 STARTING ELITE MARKET SCAN"
    )

    for symbol in SYMBOLS:

        try:

            # ================= COOLDOWN =================
            last_signal = LAST_SIGNAL_TIME.get(symbol)

            if last_signal:

                elapsed = (
                    time.time() -
                    last_signal
                )

                if elapsed < COOLDOWN_SECONDS:

                    logger.info(
                        f"⏳ COOLDOWN: {symbol}"
                    )

                    continue

            # ================= GET DATA =================
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

            # ================= LIQUIDITY =================
            if not passes_liquidity_filter(
                candles_5m
            ):

                logger.info(
                    f"⚠️ LOW LIQUIDITY: "
                    f"{symbol}"
                )

                continue

            # ================= MOMENTUM =================
            if not passes_momentum_filter(
                candles_15m
            ):

                logger.info(
                    f"⚠️ NO MOMENTUM: "
                    f"{symbol}"
                )

                continue

            # ================= ANALYZE =================
            signal = analyze(

                symbol,
                candles_5m,
                candles_15m,
                candles_1h

            )

            if not signal:

                continue

            # ================= CORRELATION FILTER =================
            group = get_group(symbol)

            if group:

                active_count = active_groups.get(
                    group,
                    0
                )

                if active_count >= MAX_SIGNALS_PER_GROUP:

                    logger.info(
                        f"⚠️ CORRELATED SKIP: "
                        f"{symbol}"
                    )

                    continue

                active_groups[group] = (
                    active_count + 1
                )

            # ================= SAVE COOLDOWN =================
            LAST_SIGNAL_TIME[symbol] = time.time()

            # ================= ADD SIGNAL =================
            signals.append(signal)

            logger.info(
                f"✅ ELITE SIGNAL: "
                f"{symbol} | "
                f"{signal['direction']} | "
                f"CONFIDENCE "
                f"{signal['confidence']}"
            )

        except Exception as e:

            logger.error(
                f"❌ SCAN ERROR: "
                f"{symbol} {e}"
            )

    logger.info(
        f"📊 FOUND "
        f"{len(signals)} ELITE SIGNALS"
    )

    return signals
