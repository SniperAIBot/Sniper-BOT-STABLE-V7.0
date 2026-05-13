import pandas as pd
import numpy as np

from logger import logger


# ================= EMA =================
def ema(series, period):

    return series.ewm(
        span=period,
        adjust=False
    ).mean()


# ================= RSI =================
def rsi(series, period=14):

    delta = series.diff()

    gain = (
        delta.where(delta > 0, 0)
        .rolling(period)
        .mean()
    )

    loss = (
        -delta.where(delta < 0, 0)
        .rolling(period)
        .mean()
    )

    rs = gain / loss

    return 100 - (
        100 / (1 + rs)
    )


# ================= ATR =================
def atr(df, period=14):

    high_low = (
        df["high"] - df["low"]
    )

    high_close = np.abs(
        df["high"] -
        df["close"].shift()
    )

    low_close = np.abs(
        df["low"] -
        df["close"].shift()
    )

    tr = pd.concat(
        [
            high_low,
            high_close,
            low_close
        ],
        axis=1
    ).max(axis=1)

    return tr.rolling(period).mean()


# ================= ANALYZE =================
def analyze(
    candles_5m,
    candles_15m,
    candles_1h
):

    try:

        # ================= DATAFRAMES =================
        df5 = pd.DataFrame(candles_5m)
        df15 = pd.DataFrame(candles_15m)
        df1h = pd.DataFrame(candles_1h)

        for df in [df5, df15, df1h]:

            for col in [
                "open",
                "high",
                "low",
                "close",
                "volume"
            ]:

                df[col] = df[col].astype(float)

        # ================= INDICATORS =================
        df5["ema20"] = ema(
            df5["close"],
            20
        )

        df5["ema50"] = ema(
            df5["close"],
            50
        )

        df15["ema20"] = ema(
            df15["close"],
            20
        )

        df15["ema50"] = ema(
            df15["close"],
            50
        )

        df1h["ema20"] = ema(
            df1h["close"],
            20
        )

        df1h["ema50"] = ema(
            df1h["close"],
            50
        )

        df5["rsi"] = rsi(
            df5["close"]
        )

        df5["atr"] = atr(df5)

        # ================= CURRENT VALUES =================
        close = df5["close"].iloc[-1]

        ema20_5m = df5["ema20"].iloc[-1]
        ema50_5m = df5["ema50"].iloc[-1]

        ema20_15m = df15["ema20"].iloc[-1]
        ema50_15m = df15["ema50"].iloc[-1]

        ema20_1h = df1h["ema20"].iloc[-1]
        ema50_1h = df1h["ema50"].iloc[-1]

        current_rsi = df5["rsi"].iloc[-1]

        previous_rsi = df5["rsi"].iloc[-2]

        current_atr = df5["atr"].iloc[-1]

        # ================= VALIDATION =================
        if np.isnan(current_atr):

            return None

        atr_percent = (
            current_atr / close
        ) * 100

        # ================= ATR FILTER =================
        if atr_percent < 0.20:

            logger.info(
                "⚠️ LOW VOLATILITY"
            )

            return None

        # ================= TREND FILTER =================
        bullish_1h = (
            ema20_1h > ema50_1h
        )

        bearish_1h = (
            ema20_1h < ema50_1h
        )

        bullish_15m = (
            ema20_15m > ema50_15m
        )

        bearish_15m = (
            ema20_15m < ema50_15m
        )

        bullish_5m = (
            ema20_5m > ema50_5m
        )

        bearish_5m = (
            ema20_5m < ema50_5m
        )

        # ================= TREND STRENGTH =================
        ema_distance = abs(
            ema20_5m - ema50_5m
        ) / close * 100

        if ema_distance < 0.10:

            logger.info(
                "⚠️ WEAK TREND"
            )

            return None

        # ================= CANDLE MOMENTUM =================
        current_body = abs(
            df5["close"].iloc[-1] -
            df5["open"].iloc[-1]
        )

        previous_body = abs(
            df5["close"].iloc[-2] -
            df5["open"].iloc[-2]
        )

        momentum_confirmed = (
            current_body > previous_body
        )

        if not momentum_confirmed:

            return None

        # ================= BUY SIGNAL =================
        if (

            bullish_1h
            and bullish_15m
            and bullish_5m

            and current_rsi > 45
            and current_rsi > previous_rsi

        ):

            entry = close

            stop_loss = (
                entry - (current_atr * 1.2)
            )

            take_profit = (
                entry + (current_atr * 2.0)
            )

            rr = (
                (take_profit - entry) /
                (entry - stop_loss)
            )

            confidence = min(

                90,

                int(
                    55
                    + ema_distance * 100
                    + atr_percent * 10
                )

            )

            return {

                "direction": "BUY",

                "entry": round(entry, 6),

                "take_profit": round(
                    take_profit,
                    6
                ),

                "stop_loss": round(
                    stop_loss,
                    6
                ),

                "rsi": round(
                    current_rsi,
                    2
                ),

                "atr": round(
                    current_atr,
                    6
                ),

                "rr": round(
                    rr,
                    2
                ),

                "confidence": confidence,

                "market_regime": "BULL"

            }

        # ================= SELL SIGNAL =================
        if (

            bearish_1h
            and bearish_15m
            and bearish_5m

            and current_rsi < 55
            and current_rsi < previous_rsi

        ):

            entry = close

            stop_loss = (
                entry + (current_atr * 1.2)
            )

            take_profit = (
                entry - (current_atr * 2.0)
            )

            rr = (
                (entry - take_profit) /
                (stop_loss - entry)
            )

            confidence = min(

                90,

                int(
                    55
                    + ema_distance * 100
                    + atr_percent * 10
                )

            )

            return {

                "direction": "SELL",

                "entry": round(entry, 6),

                "take_profit": round(
                    take_profit,
                    6
                ),

                "stop_loss": round(
                    stop_loss,
                    6
                ),

                "rsi": round(
                    current_rsi,
                    2
                ),

                "atr": round(
                    current_atr,
                    6
                ),

                "rr": round(
                    rr,
                    2
                ),

                "confidence": confidence,

                "market_regime": "BEAR"

            }

        return None

    except Exception as e:

        logger.error(
            f"❌ STRATEGY ERROR: {e}"
        )

        return None
