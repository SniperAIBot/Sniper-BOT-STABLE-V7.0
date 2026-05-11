from indicators import (
    ema,
    rsi,
    atr
)


# ================= ANALYZE =================
def analyze(symbol, htf, ltf, regime):

    try:

        closes = [
            c["close"]
            for c in ltf
        ]

        current_price = closes[-1]

        ema20 = ema(closes, 20)

        ema50 = ema(closes, 50)

        rsi_value = rsi(closes)

        atr_value = atr(ltf)

        if atr_value <= 0:
            return None

        # ================= TREND =================
        trend = None

        # BUY TREND
        if (
            ema20 > ema50
            and closes[-1] > closes[-2]
        ):

            trend = "UP"

        # SELL TREND
        elif (
            ema20 < ema50
            and closes[-1] < closes[-2]
        ):

            trend = "DOWN"

        else:

            return None

        # ================= BUY =================
        if trend == "UP":

            entry = current_price

            sl = entry - atr_value

            tp = entry + (
                atr_value * 1.5
            )

            signal = "شراء 📈"

        # ================= SELL =================
        else:

            entry = current_price

            sl = entry + atr_value

            tp = entry - (
                atr_value * 1.5
            )

            signal = "بيع 📉"

        # ================= RR =================
        rr = abs(
            tp - entry
        ) / abs(
            entry - sl
        )

        # ================= SCORE =================
        score = 30

        # EMA POWER
        ema_gap = abs(
            ema20 - ema50
        ) / current_price

        if ema_gap > 0.002:
            score += 15

        # RSI STRENGTH
        if trend == "UP":

            if rsi_value > 55:
                score += 20

            if rsi_value > 65:
                score += 10

        else:

            if rsi_value < 45:
                score += 20

            if rsi_value < 35:
                score += 10

        # MOMENTUM
        momentum = abs(
            closes[-1] - closes[-3]
        ) / current_price

        if momentum > 0.003:
            score += 10

        # LIMITS
        if score > 85:
            score = 85

        if score < 30:
            score = 30

        return {

            "symbol": symbol,

            "trend": trend,

            "signal": signal,

            "entry": float(entry),

            "tp": float(tp),

            "sl": float(sl),

            "rr": float(rr),

            "score": int(score),

            "rsi": float(rsi_value),

            "atr": float(atr_value)

        }

    except Exception as e:

        print(
            f"STRATEGY ERROR: {e}"
        )

        return None
