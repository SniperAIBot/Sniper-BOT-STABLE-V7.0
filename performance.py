from database import (
    get_connection
)

from logger import logger


# ================= WIN RATE =================
def get_win_rate():

    try:

        conn = get_connection()

        cur = conn.cursor()

        # TOTAL TP
        cur.execute("""

        SELECT COUNT(*)

        FROM signals

        WHERE status='TP'

        """)

        tp = cur.fetchone()[0]

        # TOTAL SL
        cur.execute("""

        SELECT COUNT(*)

        FROM signals

        WHERE status='SL'

        """)

        sl = cur.fetchone()[0]

        cur.close()

        conn.close()

        total = tp + sl

        if total == 0:
            return 0

        return int(
            (tp / total) * 100
        )

    except Exception as e:

        logger.error(
            f"❌ WIN RATE ERROR: {e}"
        )

        return 0


# ================= STATS =================
def get_statistics():

    try:

        conn = get_connection()

        cur = conn.cursor()

        # TOTAL SIGNALS
        cur.execute("""

        SELECT COUNT(*)

        FROM signals

        """)

        total = cur.fetchone()[0]

        # WINS
        cur.execute("""

        SELECT COUNT(*)

        FROM signals

        WHERE status='TP'

        """)

        wins = cur.fetchone()[0]

        # LOSSES
        cur.execute("""

        SELECT COUNT(*)

        FROM signals

        WHERE status='SL'

        """)

        losses = cur.fetchone()[0]

        cur.close()

        conn.close()

        return {
            "total": total,
            "wins": wins,
            "losses": losses
        }

    except Exception as e:

        logger.error(
            f"❌ STATISTICS ERROR: {e}"
        )

        return {
            "total": 0,
            "wins": 0,
            "losses": 0
        }
