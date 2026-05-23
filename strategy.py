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

        # ================= CLEAN =================
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
        for df in [df5, df15, df1h]:

            df["ema20"] = ema(
                df["close"],
                20
            )

            df["ema50"] = ema(
                df["close"],
                50
            )

        df5["rsi"] = rsi(
            df5["close"]
        )

        df5["atr"] = atr(df5)

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

        ema20_5m = float(
            df5["ema20"].iloc[-1]
        )

        ema50_5m = float(
            df5["ema50"].iloc[-1]
        )

        # ================= VALIDATION =================
        if np.isnan(current_atr):

            return None

        # ================= VOLATILITY =================
        atr_percent = (
            current_atr / close
        ) * 100

        if atr_percent < 0.25:

            logger.info(
                "⚠️ LOW VOLATILITY"
            )

            return None

        # ================= VOLUME FILTER =================
        if current_volume < (
            average_volume * 1.15
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
            ema20_5m >
            ema50_5m
        )

        bearish_5m = (
            ema20_5m <
            ema50_5m
        )

        # ================= TREND STRENGTH =================
        ema_distance = abs(
            ema20_5m -
            ema50_5m
        ) / close * 100

        if ema_distance < 0.15:

            logger.info(
                "⚠️ WEAK TREND"
            )

            return None

        # ================= PULLBACK DETECTION =================
        distance_from_ema = abs(
            close - ema20_5m
        ) / close * 100

        # avoid chasing huge candles
        if distance_from_ema > 0.60:

            logger.info(
                "⚠️ OVEREXTENDED"
            )

            return None

        # ================= CANDLE STRUCTURE =================
        current_body = abs(
            df5["close"].iloc[-1] -
            df5["open"].iloc[-1]
        )

        candle_range = (
            df5["high"].iloc[-1] -
            df5["low"].iloc[-1]
        )

        if candle_range == 0:

            return None

        body_ratio = (
            current_body /
            candle_range
        )

        if body_ratio < 0.45:

            logger.info(
                "⚠️ WEAK CANDLE"
            )

            return None

        # ================= MARKET REGIME =================
        if atr_percent > 1.2:

            market_regime = "VOLATILE"

        else:

            market_regime = "TRENDING"

        # =====================================================
        # ================= BUY SIGNAL ========================
        # =====================================================
        if (

            bullish_1h
            and bullish_15m
            and bullish_5m

            # pullback zone
            and 48 < current_rsi < 62

            # momentum recovery
            and current_rsi > previous_rsi

            # close above EMA20
            and close > ema20_5m
        ):

            entry = close

            # structure-based SL
            recent_low = min(
                df5["low"].tail(5)
            )

            stop_loss = min(
                recent_low,
                entry - (current_atr * 1.2)
            )

            risk = (
                entry - stop_loss
            )

            if risk <= 0:

                return None

            take_profit = (
                entry + (risk * 2.5)
            )

            rr = (
                (take_profit - entry) /
                risk
            )

            confidence = min(

                95,

                int(
                    60
                    + (ema_distance * 120)
                    + (atr_percent * 8)
                )
            )

            if confidence < 75:

                return None

            return {

                "symbol": symbol,

                "direction": "BUY",

                "entry": round(
                    entry,
                    6
                ),

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

                "strategy_version": "v4_pullback"
            }

        # =====================================================
        # ================= SELL SIGNAL =======================
        # =====================================================
        if (

            bearish_1h
            and bearish_15m
            and bearish_5m

            # pullback zone
            and 38 < current_rsi < 52

            # momentum recovery downward
            and current_rsi < previous_rsi

            # close below EMA20
            and close < ema20_5m
        ):

            entry = close

            recent_high = max(
                df5["high"].tail(5)
            )

            stop_loss = max(
                recent_high,
                entry + (current_atr * 1.2)
            )

            risk = (
                stop_loss - entry
            )

            if risk <= 0:

                return None

            take_profit = (
                entry - (risk * 2.5)
            )

            rr = (
                (entry - take_profit) /
                risk
            )

            confidence = min(

                95,

                int(
                    60
                    + (ema_distance * 120)
                    + (atr_percent * 8)
                )
            )

            if confidence < 75:

                return None

            return {

                "symbol": symbol,

                "direction": "SELL",

                "entry": round(
                    entry,
                    6
                ),

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

                "strategy_version": "v4_pullback"
            }

        return None

    except Exception as e:

        logger.error(
            f"❌ STRATEGY ERROR: {e}"
        )

        return None
