import requests

from logger import logger


# ================= BINANCE API =================
BASE_URL = "https://api.binance.com"


# ================= SYMBOLS =================
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
    "APEUSDT",
    "AAVEUSDT",
    "ICPUSDT",
    "INJUSDT",
    "APTUSDT",
    "CHIPUSDT",
    "TAOUSDT",
    "XLMUSDT",
    "FETUSDT",
    "FILUSDT",
    "ZECUSDT",
    "CHZUSDT",
    "SEIUSDT"

]


# ================= SAFE REQUEST =================
def safe_request(
    endpoint,
    params=None
):

    try:

        response = requests.get(

            f"{BASE_URL}{endpoint}",

            params=params,

            timeout=10

        )

        # STATUS CHECK
        if response.status_code != 200:

            logger.error(
                f"❌ BINANCE STATUS ERROR: "
                f"{response.status_code}"
            )

            return None

        return response.json()

    except Exception as e:

        logger.error(
            f"❌ REQUEST ERROR: {e}"
        )

        return None


# ================= GET KLINES =================
def get_klines(
    symbol,
    interval="15m",
    limit=100
):

    try:

        data = safe_request(

            "/api/v3/klines",

            {

                "symbol": symbol,

                "interval": interval,

                "limit": limit

            }

        )

        if data is None:
            return []

        candles = []

        for k in data:

            candles.append({

                "open": float(k[1]),

                "high": float(k[2]),

                "low": float(k[3]),

                "close": float(k[4]),

                "volume": float(k[5])

            })

        return candles

    except Exception as e:

        logger.error(
            f"❌ KLINES ERROR: "
            f"{symbol} {e}"
        )

        return []


# ================= BTC REGIME =================
def btc_regime():

    try:

        candles = get_klines(
            "BTCUSDT",
            "1h",
            50
        )

        if len(candles) < 50:

            return "NEUTRAL"

        closes = [

            c["close"]

            for c in candles

        ]

        current = closes[-1]

        old = closes[0]

        change = (
            (current - old)
            / old
        ) * 100

        logger.info(
            f"📊 BTC CHANGE: "
            f"{round(change, 2)}%"
        )

        # ================= BULL =================
        if change >= 2:

            return "BULL"

        # ================= BEAR =================
        elif change <= -2:

            return "BEAR"

        # ================= SIDEWAYS =================
        else:

            return "NEUTRAL"

    except Exception as e:

        logger.error(
            f"❌ BTC REGIME ERROR: {e}"
        )

        return "NEUTRAL"
