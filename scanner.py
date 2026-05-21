import requests

from strategy import analyze

from logger import logger


BASE_URL = (
    "https://data-api.binance.vision"
)


# ================= EXCLUDED SYMBOLS =================
EXCLUDED_SYMBOLS = [

    "USDCUSDT",
    "BUSDUSDT",
    "TUSDUSDT",
    "FDUSDUSDT",

    "UPUSDT",
    "DOWNUSDT",
    "BULLUSDT",
    "BEARUSDT",

    "EURUSDT",
    "TRYUSDT",
    "BRLUSDT",

    "DODOUSDT",
    "HOTUSDT",
    "SCUSDT",
    "RNDRUSDT",
    "CHZUSDT",
    "APEUSDT"

]


# ================= GET TOP SYMBOLS =================
def get_top_symbols(limit=30):

    try:

        url = (
            "https://api.binance.com/api/v3/ticker/24hr"
        )

        response = requests.get(
            url,
            timeout=10
        )

        data = response.json()

        filtered = []

        for item in data:

            symbol = item["symbol"]

            if not symbol.endswith(
                "USDT"
            ):
                continue

            if symbol in EXCLUDED_SYMBOLS:
                continue

            try:

                volume = float(
                    item["quoteVolume"]
                )

                price_change = abs(
                    float(
                        item["priceChangePercent"]
                    )
                )

            except:
                continue

            # ================= QUALITY FILTERS =================
            if volume < 100000000:
                continue

            if price_change < 2:
                continue

            filtered.append({

                "symbol": symbol,

                "volume": volume,

                "change": price_change

            })

        # ================= SORT =================
        filtered = sorted(

            filtered,

            key=lambda x: (
                x["volume"],
                x["change"]
            ),

            reverse=True
        )

        symbols = [

            item["symbol"]

            for item in filtered[:limit]

        ]

        logger.info(
            f"🔥 SCANNING TOP "
            f"{len(symbols)} SYMBOLS"
        )

        return symbols

    except Exception as e:

        logger.error(
            f"❌ SYMBOL FETCH ERROR: {e}"
        )

        return [

            "BTCUSDT",
            "ETHUSDT",
            "BNBUSDT",
            "SOLUSDT",
            "XRPUSDT"
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

    symbols = get_top_symbols()

    for symbol in symbols:

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

                symbol,

                candles_5m,

                candles_15m,

                candles_1h

            )

            if signal:

                signals.append(
                    signal
                )

                logger.info(
                    f"✅ SIGNAL: "
                    f"{symbol}"
                )

        except Exception as e:

            logger.error(
                f"❌ SCAN ERROR: "
                f"{symbol} {e}"
            )

    logger.info(
        f"📊 FOUND "
        f"{len(signals)} SIGNALS"
    )

    return signals
