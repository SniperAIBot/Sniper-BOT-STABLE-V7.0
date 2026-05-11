import os
import psycopg2

from datetime import datetime

from logger import logger


# ================= CONNECTION =================
def get_connection():

    return psycopg2.connect(
        os.getenv("DATABASE_URL"),
        sslmode="require"
    )


# ================= SAFE FLOAT =================
def safe_float(value):

    try:
        return float(value)

    except:
        return 0.0


# ================= SAFE INT =================
def safe_int(value):

    try:
        return int(value)

    except:
        return 0


# ================= INIT DATABASE =================
def init_db():

    try:

        conn = get_connection()

        cur = conn.cursor()

        cur.execute("""

        CREATE TABLE IF NOT EXISTS signals (

            id SERIAL PRIMARY KEY,

            time TEXT,

            symbol TEXT,

            trend TEXT,

            entry DOUBLE PRECISION,

            tp DOUBLE PRECISION,

            sl DOUBLE PRECISION,

            rr DOUBLE PRECISION,

            score INTEGER,

            rsi DOUBLE PRECISION,

            atr DOUBLE PRECISION,

            status TEXT DEFAULT 'OPEN',

            close_price DOUBLE PRECISION,

            close_time TEXT

        )

        """)

        conn.commit()

        cur.close()

        conn.close()

        logger.info(
            "✅ DATABASE INITIALIZED"
        )

    except Exception as e:

        logger.error(
            f"❌ DB INIT ERROR: {e}"
        )


# ================= SAVE SIGNAL =================
def save_signal(signal):

    try:

        conn = get_connection()

        cur = conn.cursor()

        cur.execute("""

        INSERT INTO signals (

            time,
            symbol,
            trend,
            entry,
            tp,
            sl,
            rr,
            score,
            rsi,
            atr,
            status

        )

        VALUES (

            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            'OPEN'

        )

        """, (

            str(datetime.now()),

            signal["symbol"],

            signal["trend"],

            safe_float(signal["entry"]),

            safe_float(signal["tp"]),

            safe_float(signal["sl"]),

            safe_float(signal["rr"]),

            safe_int(signal["score"]),

            safe_float(signal["rsi"]),

            safe_float(signal["atr"])

        ))

        conn.commit()

        cur.close()

        conn.close()

        logger.info(
            f"✅ SIGNAL SAVED: "
            f"{signal['symbol']}"
        )

    except Exception as e:

        logger.error(
            f"❌ SAVE SIGNAL ERROR: {e}"
        )


# ================= GET OPEN SIGNALS =================
def get_open_signals():

    try:

        conn = get_connection()

        cur = conn.cursor()

        cur.execute("""

        SELECT *

        FROM signals

        WHERE status = 'OPEN'

        """)

        rows = cur.fetchall()

        cur.close()

        conn.close()

        return rows

    except Exception as e:

        logger.error(
            f"❌ GET OPEN SIGNALS ERROR: {e}"
        )

        return []


# ================= CLOSE SIGNAL =================
def close_signal(signal_id, status, close_price):

    try:

        conn = get_connection()

        cur = conn.cursor()

        cur.execute("""

        UPDATE signals

        SET

            status = %s,

            close_price = %s,

            close_time = %s

        WHERE id = %s

        """, (

            status,

            safe_float(close_price),

            str(datetime.now()),

            signal_id

        ))

        conn.commit()

        cur.close()

        conn.close()

        logger.info(
            f"✅ SIGNAL CLOSED: "
            f"{signal_id}"
        )

    except Exception as e:

        logger.error(
            f"❌ CLOSE SIGNAL ERROR: {e}"
        )


# ================= GET STATS =================
def get_stats():

    try:

        conn = get_connection()

        cur = conn.cursor()

        cur.execute("""

        SELECT COUNT(*)

        FROM signals

        """)

        total = cur.fetchone()[0]

        cur.execute("""

        SELECT COUNT(*)

        FROM signals

        WHERE status='TP'

        """)

        wins = cur.fetchone()[0]

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
            f"❌ GET STATS ERROR: {e}"
        )

        return {
            "total": 0,
            "wins": 0,
            "losses": 0
        }
