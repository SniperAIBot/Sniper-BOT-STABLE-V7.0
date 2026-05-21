```python
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
    symbol,
    candles_5m,
    candles_15m,
    candles_1h
):

    try:

        # ================= DATAFRAMES =================
        df5 = pd.DataFrame(candles_5m)
        df15 = pd.DataFrame(candles_15m)
        df1h = pd.DataFrame(candles_1h)

        # ================= CLEAN DATA =================
        for df in [df5, df15, df1h]:

            for col in [
                "open",
                "high",
                "low",
                "close",
                "volume"
            ]:

                df[col] = df[col].astype(float)

        # ================= EMAS =================
        for df in [df5, df15, df1h]:

            df["ema20"] = ema(
                df["close"],
                20
            )

            df["ema50"] = ema(
                df["close"],
                50
            )

        # ================= RSI =================
        df5["rsi"] = rsi(
            df5["close"]
        )

        # ================= ATR =================
        df5["atr"] = atr(df5)

        # ================= VOLUME =================
        df5["volume_ma"] = (
            df5["volume"]
            .rolling(20)
            .mean()
        )

        # ================= CURRENT VALUES =================
        close = float(
            df5["close"].iloc[-1]
        )

        current_rsi = float(
            df5["rsi"].iloc[-1]
        )

        previous_rsi = float(
            df5["rsi"].iloc[-2]
        )

        current_atr = float(
            df5["atr"].iloc[-1]
        )

        current_volume = float(
            df5["volume"].iloc[-1]
        )

        average_volume = float(
            df5["volume_ma"].iloc[-1]
        )

        # ================= VALIDATION =================
        if np.isnan(current_atr):

            return None

        # ================= ATR FILTER =================
        atr_percent = (
            current_atr / close
        ) * 100

        if atr_percent < 0.35:

            logger.info(
                "⚠️ LOW VOLATILITY"
            )

            return None

        # ================= VOLUME FILTER =================
        if current_volume < (
            average_volume * 1.5
        ):

            logger.info(
                "⚠️ LOW VOLUME"
            )

            return None

        # ================= TREND FILTER =================
        bullish_1h = (
            df1h["ema20"].iloc[-1] >
            df1h["ema50"].iloc[-1]
        )

        bearish_1h = (
            df1h["ema20"].iloc[-1] <
            df1h["ema50"].iloc[-1]
        )

        bullish_15m = (
            df15["ema20"].iloc[-1] >
            df15["ema50"].iloc[-1]
        )

        bearish_15m = (
            df15["ema20"].iloc[-1] <
            df15["ema50"].iloc[-1]
        )

        bullish_5m = (
            df5["ema20"].iloc[-1] >
            df5["ema50"].iloc[-1]
        )

        bearish_5m = (
            df5["ema20"].iloc[-1] <
            df5["ema50"].iloc[-1]
        )

        # ================= TREND STRENGTH =================
        ema_distance = abs(
            df5["ema20"].iloc[-1] -
            df5["ema50"].iloc[-1]
        ) / close * 100

        if ema_distance < 0.25:

            logger.info(
                "⚠️ WEAK TREND"
            )

            return None

        # ================= EMA MOMENTUM =================
        ema_slope = abs(
            df5["ema20"].iloc[-1] -
            df5["ema20"].iloc[-5]
        )

        if ema_slope < (
            close * 0.002
        ):

            logger.info(
                "⚠️ WEAK MOMENTUM"
            )

            return None

        # ================= CANDLE STRENGTH =================
        current_body = abs(
            df5["close"].iloc[-1] -
            df5["open"].iloc[-1]
        )

        candle_range = (
            df5["high"].iloc[-1] -
            df5["low"].iloc[-1]
        )

        if current_body < (
            candle_range * 0.5
        ):

            logger.info(
                "⚠️ WEAK CANDLE"
            )

            return None

        # ================= MARKET REGIME =================
        if atr_percent > 1.2:

            market_regime = "VOLATILE"

        else:

            market_regime = "TRENDING"

        # ================= BUY =================
        if (

            bullish_1h
            and bullish_15m
            and bullish_5m

            and 55 < current_rsi < 70

            and current_rsi > previous_rsi

        ):

            entry = close

            stop_loss = (
                entry -
                (current_atr * 1.5)
            )

            take_profit = (
                entry +
                (current_atr * 3.5)
            )

            rr = (
                (take_profit - entry) /
                (entry - stop_loss)
            )

            confidence = min(

                95,

                int(
                    65
                    + (ema_distance * 100)
                    + (atr_percent * 10)
                )
            )

            if confidence < 80:

                return None

            return {

                "symbol": symbol,

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

                "market_regime": market_regime,

                "strategy_version": "v3_precision"
            }

        # ================= SELL =================
        if (

            bearish_1h
            and bearish_15m
            and bearish_5m

            and 30 < current_rsi < 45

            and current_rsi < previous_rsi

        ):

            entry = close

            stop_loss = (
                entry +
                (current_atr * 1.5)
            )

            take_profit = (
                entry -
                (current_atr * 3.5)
            )

            rr = (
                (entry - take_profit) /
                (stop_loss - entry)
            )

            confidence = min(

                95,

                int(
                    65
                    + (ema_distance * 100)
                    + (atr_percent * 10)
                )
            )

            if confidence < 80:

                return None

            return {

                "symbol": symbol,

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

                "market_regime": market_regime,

                "strategy_version": "v3_precision"
            }

        return None

    except Exception as e:

        logger.error(
            f"❌ STRATEGY ERROR: {e}"
        )

        return None
```
