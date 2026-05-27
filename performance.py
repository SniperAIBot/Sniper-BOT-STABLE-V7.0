from database import get_connection


def get_statistics():

    conn = get_connection()

    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM signals")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM signals WHERE result='WIN'")
    wins = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM signals WHERE result='LOSS'")
    losses = cur.fetchone()[0]

    cur.execute("SELECT AVG(rr) FROM signals WHERE result='WIN'")

    avg_rr = cur.fetchone()[0]

    if avg_rr is None:
        avg_rr = 0

    closed = wins + losses

    if closed > 0:

        win_rate = (wins / closed) * 100

        expectancy = (
            (wins / closed) * avg_rr
        ) - (
            losses / closed)

    else:

        win_rate = 0
        expectancy = 0

    conn.close()

    return {
        "total_trades": total,
        "wins": wins,
        "losses": losses,
        "win_rate": round(win_rate, 2),
        "expectancy": round(expectancy, 2),
        "avg_rr": round(avg_rr, 2)
    }
