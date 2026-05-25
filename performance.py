from database import get_connection
from logger import logger


# ================= WIN RATE =================
def get_win_rate():

    try:

        conn = get_connection()

        if conn is None:
            return 0

        cur = conn.cursor()

        # ================= WINS =================
        cur.execute(
            """
            SELECT COUNT(*)
            FROM signals
            WHERE result='WIN'
            """
        )

        wins = cur.fetchone()[0]

        # ================= LOSSES =================
        cur.execute(
            """
            SELECT COUNT(*)
            FROM signals
            WHERE result='LOSS'
            """
        )

        losses = cur.fetchone()[0]

        cur.close()
        conn.close()

        total = wins + losses

        if total == 0:
            return 0

        return round(
            (wins / total) * 100,
            2
        )

    except Exception as e:

        logger.error(
            f"❌ WIN RATE ERROR: {e}"
        )

        return 0


# ================= EXPECTANCY =================
def get_expectancy():

    try:

        conn = get_connection()

        if conn is None:
            return 0

        cur = conn.cursor()

        # ================= WINS =================
        cur.execute(
            """
            SELECT COUNT(*)
            FROM signals
            WHERE result='WIN'
            """
        )

        wins = cur.fetchone()[0]

        # ================= LOSSES =================
        cur.execute(
            """
            SELECT COUNT(*)
            FROM signals
            WHERE result='LOSS'
            """
        )

        losses = cur.fetchone()[0]

        # ================= AVG RR WIN =================
        cur.execute(
            """
            SELECT AVG(rr)
            FROM signals
            WHERE result='WIN'
            """
        )

        avg_rr_win = cur.fetchone()[0]

        if avg_rr_win is None:
            avg_rr_win = 0

        cur.close()
        conn.close()

        total_closed = wins + losses

        if total_closed == 0:
            return 0

        win_rate = wins / total_closed
        loss_rate = losses / total_closed

        expectancy = (
            (win_rate * avg_rr_win)
            - loss_rate
        )

        return round(
            expectancy,
            2
        )

    except Exception as e:

        logger.error(
            f"❌ EXPECTANCY ERROR: {e}"
        )

        return 0


# ================= DASHBOARD STATS =================
def get_statistics():

    try:

        conn = get_connection()

        if conn is None:

            return {
                "total_trades": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0,
                "expectancy": 0,
                "avg_rr_win": 0
            }

        cur = conn.cursor()

        # ================= TOTAL =================
        cur.execute(
            """
            SELECT COUNT(*)
            FROM signals
            """
        )

        total_trades = cur.fetchone()[0]

        # ================= WINS =================
        cur.execute(
            """
            SELECT COUNT(*)
            FROM signals
            WHERE result='WIN'
            """
        )

        wins = cur.fetchone()[0]

        # ================= LOSSES =================
        cur.execute(
            """
            SELECT COUNT(*)
            FROM signals
            WHERE result='LOSS'
            """
        )

        losses = cur.fetchone()[0]

        # ================= AVG RR WIN =================
        cur.execute(
            """
            SELECT AVG(rr)
            FROM signals
            WHERE result='WIN'
            """
        )

        avg_rr_win = cur.fetchone()[0]

        if avg_rr_win is None:
            avg_rr_win = 0

        cur.close()
        conn.close()

        total_closed = wins + losses

        if total_closed > 0:

            win_rate = round(
                (wins / total_closed) * 100,
                2
            )

            expectancy = round(
                (
                    (wins / total_closed)
                    * avg_rr_win
                )
                -
                (losses / total_closed),
                2
            )

        else:

            win_rate = 0
            expectancy = 0

        return {

            "total_trades": total_trades,

            "wins": wins,

            "losses": losses,

            "win_rate": win_rate,

            "expectancy": expectancy,

            "avg_rr_win": round(
                avg_rr_win,
                2
            )
        }

    except Exception as e:

        logger.error(
            f"❌ STATISTICS ERROR: {e}"
        )

        return {

            "total_trades": 0,

            "wins": 0,

            "losses": 0,

            "win_rate": 0,

            "expectancy": 0,

            "avg_rr_win": 0
        }
