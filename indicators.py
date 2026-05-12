import pandas as pd


# ================= EMA =================
def calculate_ema(
    closes,
    period=20
):

    try:

        series = pd.Series(closes)

        ema = series.ewm(
            span=period,
            adjust=False
        ).mean()

        return float(ema.iloc[-1])

    except Exception:

        return None


# ================= RSI =================
def calculate_rsi(
    closes,
    period=14
):

    try:

        series = pd.Series(closes)

        delta = series.diff()

        gain = delta.clip(
            lower=0
        )

        loss = -delta.clip(
            upper=0
        )

        avg_gain = gain.rolling(
            window=period
        ).mean()

        avg_loss = loss.rolling(
            window=period
        ).mean()

        rs = avg_gain / avg_loss

        rsi = (
            100
            - (
                100
                / (1 + rs)
            )
        )

        return float(rsi.iloc[-1])

    except Exception:

        return None


# ================= ATR =================
def calculate_atr(
    highs,
    lows,
    closes,
    period=14
):

    try:

        high = pd.Series(highs)

        low = pd.Series(lows)

        close = pd.Series(closes)

        tr1 = high - low

        tr2 = (
            high - close.shift()
        ).abs()

        tr3 = (
            low - close.shift()
        ).abs()

        tr = pd.concat(

            [

                tr1,
                tr2,
                tr3

            ],

            axis=1

        ).max(axis=1)

        atr = tr.rolling(
            window=period
        ).mean()

        return float(
            atr.iloc[-1]
        )

    except Exception:

        return None
