from indicators import (
    calculate_ema,
    calculate_rsi,
    calculate_atr
)

from logger import logger


# ================= STRATEGY ENGINE =================
def generate_signal(
    symbol,
    candles,
    market_regime="NEUTRAL"
):

    try:

        # ================= SAFETY =================
        if len(candles) < 60:

            logger.warning(
                f"⚠️ NOT ENOUGH DATA: {symbol}"
            )

            return None

        # ================= CLOSE PRICES =================
        closes = [

            c["close"]

            for c in candles

        ]

        highs = [

            c["high"]

            for c in candles

        ]

        lows = [

            c["low"]

            for c in candles

        ]

        volumes = [

            c["volume"]

            for c in candles

        ]


        # ================= INDICATORS =================
        ema20 = calculate_ema(
            closes,
            20
        )

        ema50 = calculate_ema(
            closes,
            50
        )

        rsi = calculate_rsi(
            closes,
            14
        )

        atr = calculate_atr(
            highs,
            lows,
            closes,
            14
        )

        # SAFETY
        if (
            ema20 is None
            or ema50 is None
            or rsi is None
            or atr is None
        ):

            logger.warning(
                f"⚠️ INDICATOR FAILURE: {symbol}"
            )

            return None


        # ================= CURRENT DATA =================
        price = closes[-1]

        volume_now = volumes[-1]

        avg_volume = (
            sum(volumes[-20:])
            / 20
        )

        atr_percent = (
            atr / price
        ) * 100


        # ================= FILTER DEAD MARKET =================
        if atr_percent < 0.25:

            logger.info(
                f"⏭️ LOW VOLATILITY SKIP: {symbol}"
            )

            return None


        # ================= TREND =================
        bullish_trend = ema20 > ema50
        bearish_trend = ema20 < ema50


        # ================= MOMENTUM =================
        bullish_momentum = rsi >= 55
        bearish_momentum = rsi <= 45


        # ================= VOLUME =================
        strong_volume = volume_now > avg_volume


        # ================= SCORE ENGINE =================
        buy_score = 0
        sell_score = 0


        # ================= EMA =================
        if bullish_trend:
            buy_score += 25

        if bearish_trend:
            sell_score += 25


        # ================= RSI =================
        if bullish_momentum:
            buy_score += 25

        if bearish_momentum:
            sell_score += 25


        # ================= MARKET REGIME =================
        if market_regime == "BULL":
            buy_score += 20
            sell_score -= 10

        elif market_regime == "BEAR":
            sell_score += 20
            buy_score -= 10


        # ================= ATR =================
        if atr_percent >= 0.5:
            buy_score += 10
            sell_score += 10


        # ================= VOLUME =================
        if strong_volume:
            buy_score += 15
            sell_score += 15


        # ================= DETERMINE DIRECTION =================
        direction = None
        confidence = 0


        if buy_score > sell_score:

            direction = "BUY"
            confidence = buy_score

        elif sell_score > buy_score:

            direction = "SELL"
            confidence = sell_score

        else:

            logger.info(
                f"⚖️ NO CLEAR DIRECTION: {symbol}"
            )

            return None


        # ================= MINIMUM CONFIDENCE =================
        if confidence < 30:

            logger.info(
                f"❌ LOW CONFIDENCE: "
                f"{symbol} {confidence}%"
            )

            return None


        # ================= ENTRY =================
        entry = price


        # ================= TP / SL =================
        if direction == "BUY":

            take_profit = (
                entry + (atr * 1.5)
            )

            stop_loss = (
                entry - atr
            )

        else:

            take_profit = (
                entry - (atr * 1.5)
            )

            stop_loss = (
                entry + atr
            )


        # ================= RISK REWARD =================
        risk = abs(
            entry - stop_loss
        )

        reward = abs(
            take_profit - entry
        )

        rr = round(
            reward / risk,
            2
        )


        # ================= FINAL SIGNAL =================
        signal = {

            "symbol": symbol,

            "direction": direction,

            "entry": round(entry, 6),

            "take_profit": round(
                take_profit,
                6
            ),

            "stop_loss": round(
                stop_loss,
                6
            ),

            "confidence": max(
                30,
                min(confidence, 85)
            ),

            "rsi": round(rsi, 2),

            "atr": round(atr, 6),

            "atr_percent": round(
                atr_percent,
                2
            ),

            "ema20": round(
                ema20,
                6
            ),

            "ema50": round(
                ema50,
                6
            ),

            "rr": rr,

            "market_regime": market_regime

        }


        logger.info(
            f"✅ SIGNAL GENERATED: "
            f"{symbol} "
            f"{direction} "
            f"{confidence}%"
        )

        return signal


    except Exception as e:

        logger.error(
            f"❌ STRATEGY ERROR: "
            f"{symbol} {e}"
        )

        return None
