from database import (
    get_connection
)

from logger import logger


# ================= WIN RATE =================
def get_win_rate():

    try:

        conn = get_connection()

        cur = conn.cursor()

        # ================= WINS =================
        cur.execute("""

        SELECT COUNT(*)

        FROM signals

        WHERE status='WIN'

        """)

        wins = cur.fetchone()[0]

        # ================= LOSSES =================
        cur.execute("""

        SELECT COUNT(*)

        FROM signals

        WHERE status='LOSS'

        """)

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


# ================= ADVANCED STATISTICS =================
def get_statistics():

    try:

        conn = get_connection()

        cur = conn.cursor()

        # ================= TOTAL =================
        cur.execute("""

        SELECT COUNT(*)

        FROM signals

        """)

        total = cur.fetchone()[0]

        # ================= WINS =================
        cur.execute("""

        SELECT COUNT(*)

        FROM signals

        WHERE status='WIN'

        """)

        wins = cur.fetchone()[0]

        # ================= LOSSES =================
        cur.execute("""

        SELECT COUNT(*)

        FROM signals

        WHERE status='LOSS'

        """)

        losses = cur.fetchone()[0]

        # ================= BREAKEVEN =================
        cur.execute("""

        SELECT COUNT(*)

        FROM signals

        WHERE status='BREAKEVEN'

        """)

        breakeven = cur.fetchone()[0]

        # ================= TIMEOUT =================
        cur.execute("""

        SELECT COUNT(*)

        FROM signals

        WHERE status='TIMEOUT'

        """)

        timeout = cur.fetchone()[0]

        # ================= AVG RR =================
        cur.execute("""

        SELECT AVG(rr)

        FROM signals

        WHERE status='WIN'

        """)

        avg_rr_win = cur.fetchone()[0]

        if avg_rr_win is None:

            avg_rr_win = 0

        # ================= EXPECTANCY =================
        total_closed = wins + losses

        if total_closed > 0:

            win_rate = wins / total_closed

            loss_rate = losses / total_closed

            expectancy = (
                (win_rate * avg_rr_win)
                -
                loss_rate
            )

        else:

            win_rate = 0

            expectancy = 0

        cur.close()

        conn.close()

        return {

            "total": total,

            "wins": wins,

            "losses": losses,

            "breakeven": breakeven,

            "timeout": timeout,

            "win_rate": round(
                win_rate * 100,
                2
            ),

            "expectancy": round(
                expectancy,
                2
            ),

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

            "total": 0,

            "wins": 0,

            "losses": 0,

            "breakeven": 0,

            "timeout": 0,

            "win_rate": 0,

            "expectancy": 0,

            "avg_rr_win": 0
        }
