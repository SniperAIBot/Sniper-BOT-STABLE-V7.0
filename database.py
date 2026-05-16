import os
import psycopg2
from psycopg2.extras import RealDictCursor

from logger import logger


# ================= DATABASE URL =================
DATABASE_URL = os.getenv(
    "DATABASE_URL"
)


# ================= CONNECT =================
def get_connection():

    try:

        conn = psycopg2.connect(
            DATABASE_URL
        )

        return conn

    except Exception as e:

        logger.error(
            f"❌ DATABASE CONNECTION ERROR: {e}"
        )

        return None


# ================= INITIALIZE DATABASE =================
def initialize_database():

    conn = get_connection()

    if conn is None:
        return

    try:

        cur = conn.cursor()

        cur.execute(

            """
            CREATE TABLE IF NOT EXISTS signals (

                id SERIAL PRIMARY KEY,

                symbol TEXT,

                direction TEXT,

                entry DOUBLE PRECISION,

                take_profit DOUBLE PRECISION,

                stop_loss DOUBLE PRECISION,

                confidence DOUBLE PRECISION,

                rsi DOUBLE PRECISION,

                atr DOUBLE PRECISION,

                rr DOUBLE PRECISION,

                market_regime TEXT,

                status TEXT DEFAULT 'OPEN',

                result TEXT DEFAULT '',

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                closed_at TIMESTAMP

            );
            """

        )

        conn.commit()

        cur.close()

        conn.close()

        logger.info(
            "✅ DATABASE INITIALIZED"
        )

    except Exception as e:

        logger.error(
            f"❌ DATABASE INIT ERROR: {e}"
        )


# ================= SAVE SIGNAL =================
def save_signal(signal):

    conn = get_connection()

    if conn is None:
        return

    try:

        cur = conn.cursor()

        cur.execute(

            """
            INSERT INTO signals (

                symbol,
                direction,
                entry,
                take_profit,
                stop_loss,
                confidence,
                rsi,
                atr,
                rr,
                market_regime,
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
                %s

            );
            """,

            (

                signal["symbol"],
                signal["direction"],
                signal["entry"],
                signal["take_profit"],
                signal["stop_loss"],
                signal["confidence"],
                signal["rsi"],
                signal["atr"],
                signal["rr"],
                signal["market_regime"],
                "OPEN"

            )

        )

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

    conn = get_connection()

    if conn is None:
        return []

    try:

        cur = conn.cursor(
            cursor_factory=RealDictCursor
        )

        cur.execute(

            """
            SELECT *
            FROM signals
            WHERE status = 'OPEN';
            """

        )

        signals = cur.fetchall()

        cur.close()

        conn.close()

        return signals

    except Exception as e:

        logger.error(
            f"❌ GET OPEN SIGNALS ERROR: {e}"
        )

        return []


# ================= CLOSE SIGNAL =================
def close_signal(
    signal_id,
    result
):

    conn = get_connection()

    if conn is None:
        return

    try:

        cur = conn.cursor()

        cur.execute(

            """
            UPDATE signals

            SET

                status = 'CLOSED',
                result = %s,
                closed_at = CURRENT_TIMESTAMP

            WHERE id = %s;
            """,

            (

                result,
                signal_id

            )

        )

        conn.commit()

        cur.close()

        conn.close()

        logger.info(
            f"✅ SIGNAL CLOSED: "
            f"{signal_id} {result}"
        )

    except Exception as e:

        logger.error(
            f"❌ CLOSE SIGNAL ERROR: {e}"
        )

import pandas as pd


# ================= GET ALL SIGNALS =================
def get_all_signals():

    conn = get_connection()

    query = """
        SELECT *
        FROM signals
        ORDER BY id DESC
    """

    df = pd.read_sql(
        query,
        conn
    )

    conn.close()

    return df


# ================= GET RECENT SIGNALS =================
def get_recent_signals(limit=20):

    conn = get_connection()

    query = f"""
        SELECT
            symbol,
            direction,
            entry,
            take_profit,
            stop_loss,
            result,
            market_regime,
            created_at
        FROM signals
        ORDER BY id DESC
        LIMIT {limit}
    """

    df = pd.read_sql(
        query,
        conn
    )

    conn.close()

    return df


# ================= GET STATISTICS =================
def get_statistics():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*) FROM signals
        """
    )

    total = cursor.fetchone()[0]


    cursor.execute(
        """
        SELECT COUNT(*)
        FROM signals
        WHERE result = 'WIN'
        """
    )

    wins = cursor.fetchone()[0]


    cursor.execute(
        """
        SELECT COUNT(*)
        FROM signals
        WHERE result = 'LOSS'
        """
    )

    losses = cursor.fetchone()[0]


    winrate = 0

    if total > 0:

        winrate = round(
            (wins / total) * 100,
            2
        )


    conn.close()

    return {
        "total": total,
        "wins": wins,
        "losses": losses,
        "winrate": winrate
    }


# ================= SYMBOL PERFORMANCE =================
def get_symbol_performance():

    conn = get_connection()

    query = """
        SELECT
            symbol,
            COUNT(*) FILTER (
                WHERE result = 'WIN'
            ) AS wins,

            COUNT(*) FILTER (
                WHERE result = 'LOSS'
            ) AS losses

        FROM signals

        GROUP BY symbol

        ORDER BY wins DESC
    """

    df = pd.read_sql(
        query,
        conn
    )

    conn.close()

    return df
