import os
import pandas as pd
import psycopg2

from psycopg2.extras import RealDictCursor


DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():

    return psycopg2.connect(DATABASE_URL)


def initialize_database():

    conn = get_connection()

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
            strategy_version TEXT,
            status TEXT DEFAULT 'OPEN',
            result TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            closed_at TIMESTAMP
        );
        """
    )

    conn.commit()

    conn.close()


def save_signal(signal):

    conn = get_connection()

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
            strategy_version,
            status
        )
        VALUES (
            %s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,
            %s,%s
        )
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
            signal["strategy_version"],
            "OPEN"
        )
    )

    conn.commit()

    conn.close()


def get_open_signals():

    conn = get_connection()

    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        "SELECT * FROM signals WHERE status='OPEN'"
    )

    data = cur.fetchall()

    conn.close()

    return data


def close_signal(signal_id, result):

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        UPDATE signals
        SET
            status='CLOSED',
            result=%s,
            closed_at=CURRENT_TIMESTAMP
        WHERE id=%s
        """,
        (result, signal_id)
    )

    conn.commit()

    conn.close()


def get_all_signals():

    conn = get_connection()

    df = pd.read_sql(
        "SELECT * FROM signals ORDER BY id DESC",
        conn
    )

    conn.close()

    return df
