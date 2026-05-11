import requests
from indicators import ema


# ================= BINANCE =================
BASE_URL = "https://data-api.binance.vision"


# ================= REQUEST =================
def get_json(url):

    try:

        response = requests.get(
            url,
            timeout=10
        )

        return response.json()

    except Exception as e:

        print(f"SCANNER ERROR: {e}")

        return None


# ================= KLINES =================
def get_klines(
    symbol,
    interval="5m",
    limit=100
):

    try:

        url = (
            f"{BASE_URL}/api/v3/klines"
            f"?symbol={symbol}"
            f"&interval={interval}"
            f"&limit={limit}"
        )

        data = get_json(url)

        if not isinstance(data, list):

            return None

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

        print(f"KLINES ERROR: {e}")

        return None


# ================= BTC REGIME =================
def btc_regime():

    try:

        candles = get_klines(
            "BTCUSDT",
            "1h",
            100
        )

        if not candles:

            return "UNKNOWN"

        closes = [
            c["close"]
            for c in candles
        ]

        ema20 = ema(closes, 20)

        ema50 = ema(closes, 50)

        if ema20 > ema50:

            return "BULL"

        elif ema20 < ema50:

            return "BEAR"

        return "RANGE"

    except Exception as e:

        print(f"BTC REGIME ERROR: {e}")

        return "UNKNOWN"
