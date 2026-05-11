import numpy as np


def ema(values, period):

    weights = np.exp(np.linspace(-1., 0., period))
    weights /= weights.sum()

    return np.convolve(values, weights, mode='valid')[-1]


def rsi(closes, period=14):

    deltas = np.diff(closes)

    seed = deltas[:period]

    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period

    rs = up / down if down != 0 else 0

    return 100 - (100 / (1 + rs))


def atr(candles, period=14):

    trs = []

    for i in range(1, len(candles)):

        high = candles[i]["high"]
        low = candles[i]["low"]
        prev_close = candles[i - 1]["close"]

        tr = max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close)
        )

        trs.append(tr)

    return sum(trs[-period:]) / period
