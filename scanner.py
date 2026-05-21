import requests

from strategy import analyze

from logger import logger


BASE_URL = (
    "https://data-api.binance.vision"
)


SYMBOLS = [

    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "ATOMUSDT",
    "ADAUSDT",
    "LINKUSDT",
    "AVAXUSDT",
    "LTCUSDT",
    "DOTUSDT",
    "UNIUSDT",
    "AAVEUSDT",
    "ICPUSDT",
    "INJUSDT",
    "APTUSDT",
    "TAOUSDT",
    "XLMUSDT",
    "FETUSDT",
    "FILUSDT",
    "ZECUSDT",
    "SEIUSDT"

]


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


# ================= SCAN MARKET =================
def scan_market():

    signals = []

    for symbol in SYMBOLS:

        try:

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

            signal = analyze(

                candles_5m,
                candles_15m,
                candles_1h

            )

            if signal:

                signal["symbol"] = symbol

                signals.append(signal)

                logger.info(
                    f"✅ SIGNAL: "
                    f"{symbol}"
                )

        except Exception as e:

            logger.error(
                f"❌ SCAN ERROR: "
                f"{symbol} {e}"
            )

    return signals
