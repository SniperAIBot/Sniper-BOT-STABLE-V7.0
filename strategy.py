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

    gain = delta.where(delta > 0, 0).rolling(period).mean()

    loss = -delta.where(delta < 0, 0).rolling(period).mean()

    rs = gain / loss

    return 100 - (100 / (1 + rs))


# ================= ATR =================
def atr(df, period=14):

    high_low = df["high"] - df["low"]

    high_close = np.abs(df["high"] - df["close"].shift())

    low_close = np.abs(df["low"] - df["close"].shift())

    tr = pd.concat([
        high_low,
        high_close,
        low_close
    ], axis=1).max(axis=1)

    return tr.rolling(period).mean()


# ================= ANALYZE =================
def analyze(symbol, candles_5m, candles_15m, candles_1h):

    try:

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

        for df in [df5, df15, df1h]:

            df["ema20"] = ema(df["close"], 20)
            df["ema50"] = ema(df["close"], 50)

        df5["rsi"] = rsi(df5["close"])

        df5["atr"] = atr(df5)

        df5["volume_ma"] = df5["volume"].rolling(20).mean()

        close = df5["close"].iloc[-1]

        current_rsi = df5["rsi"].iloc[-1]

        previous_rsi = df5["rsi"].iloc[-2]

        current_atr = df5["atr"].iloc[-1]

        current_volume = df5["volume"].iloc[-1]

        average_volume = df5["volume_ma"].iloc[-1]

        if np.isnan(current_atr):
            return None

        atr_percent = (current_atr / close) * 100

        if atr_percent < 0.20:
            return None

        if current_volume < (average_volume * 1.10):
            return None

        bullish_1h = df1h["ema20"].iloc[-1] > df1h["ema50"].iloc[-1]
        bearish_1h = df1h["ema20"].iloc[-1] < df1h["ema50"].iloc[-1]

        bullish_15m = df15["ema20"].iloc[-1] > df15["ema50"].iloc[-1]
        bearish_15m = df15["ema20"].iloc[-1] < df15["ema50"].iloc[-1]

        bullish_5m = df5["ema20"].iloc[-1] > df5["ema50"].iloc[-1]
        bearish_5m = df5["ema20"].iloc[-1] < df5["ema50"].iloc[-1]

        ema_distance = abs(
            df5["ema20"].iloc[-1] -
            df5["ema50"].iloc[-1]
        ) / close * 100

        if ema_distance < 0.15:
            return None

        ema_slope = abs(
            df5["ema20"].iloc[-1] -
            df5["ema20"].iloc[-5]
        )

        if ema_slope < (close * 0.001):
            return None

        current_body = abs(
            df5["close"].iloc[-1] -
            df5["open"].iloc[-1]
        )

        candle_range = (
            df5["high"].iloc[-1] -
            df5["low"].iloc[-1]
        )

        if current_body < (candle_range * 0.35):
            return None

        # BUY
        if (
            bullish_1h
            and bullish_15m
            and bullish_5m
            and 55 < current_rsi < 70
            and current_rsi > previous_rsi
        ):

            entry = close

            stop_loss = entry - (current_atr * 1.4)

            take_profit = entry + (current_atr * 3.0)

            rr = (take_profit - entry) / (entry - stop_loss)

            confidence = min(
                95,
                int(65 + (ema_distance * 100))
            )

            if confidence < 70:
                return None

            return {
                "symbol": symbol,
                "direction": "BUY",
                "entry": round(entry, 6),
                "take_profit": round(take_profit, 6),
                "stop_loss": round(stop_loss, 6),
                "rsi": round(current_rsi, 2),
                "atr": round(current_atr, 6),
                "rr": round(rr, 2),
                "confidence": confidence,
                "market_regime": "TRENDING",
                "strategy_version": "v5_top10"
            }

        # SELL
        if (
            bearish_1h
            and bearish_15m
            and bearish_5m
            and 30 < current_rsi < 45
            and current_rsi < previous_rsi
        ):

            entry = close

            stop_loss = entry + (current_atr * 1.4)

            take_profit = entry - (current_atr * 3.0)

            rr = (entry - take_profit) / (stop_loss - entry)

            confidence = min(
                95,
                int(65 + (ema_distance * 100))
            )

            if confidence < 70:
                return None

            return {
                "symbol": symbol,
                "direction": "SELL",
                "entry": round(entry, 6),
                "take_profit": round(take_profit, 6),
                "stop_loss": round(stop_loss, 6),
                "rsi": round(current_rsi, 2),
                "atr": round(current_atr, 6),
                "rr": round(rr, 2),
                "confidence": confidence,
                "market_regime": "TRENDING",
                "strategy_version": "v5_top10"
            }

        return None

    except Exception as e:

        logger.error(f"❌ STRATEGY ERROR: {e}")

        return None
