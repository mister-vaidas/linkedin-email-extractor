# db/database.py

import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("PG_HOST"),
    "port": os.getenv("PG_PORT"),
    "dbname": os.getenv("PG_DATABASE"),
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PASSWORD"),
}

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Table for collected emails
    cur.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id SERIAL PRIMARY KEY,
            profile_url TEXT UNIQUE,
            email TEXT,
            extracted_at TIMESTAMP
        );
    """)

    # Table for UK-based connections
    cur.execute("""
        CREATE TABLE IF NOT EXISTS uk_connections (
            id SERIAL PRIMARY KEY,
            name TEXT,
            location TEXT,
            profile_url TEXT UNIQUE,
            fetched BOOLEAN DEFAULT FALSE,
            saved_at TIMESTAMP
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("[INFO] PostgreSQL tables initialized.")

def save_email(profile_url, email):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO emails (profile_url, email, extracted_at)
            VALUES (%s, %s, %s)
            ON CONFLICT (profile_url) DO NOTHING;
        """, (
            profile_url,
            email,
            datetime.utcnow(),
        ))
        conn.commit()
        print(f"[SAVE] {profile_url} → {email or 'No email'}")
    except Exception as e:
        print(f"[ERROR] Failed to save email: {e}")
    finally:
        cur.close()
        conn.close()

def save_uk_connection(conn):
    conn_db = get_connection()
    cur = conn_db.cursor()
    try:
        cur.execute("""
            INSERT INTO uk_connections (name, location, profile_url, saved_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (profile_url) DO NOTHING;
        """, (
            conn["name"],
            conn["location"],
            conn["profile_url"],
            datetime.utcnow()
        ))
        conn_db.commit()
        print(f"[UK SAVE] {conn['name']} - {conn['location']}")
    except Exception as e:
        print(f"[ERROR] Failed to save UK connection: {e}")
    finally:
        cur.close()
        conn_db.close()

def get_unfetched_uk_connections(limit=100):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, profile_url FROM uk_connections
        WHERE fetched = FALSE
        ORDER BY id ASC
        LIMIT %s;
    """, (limit,))
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

def mark_connection_as_fetched(conn_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE uk_connections SET fetched = TRUE WHERE id = %s;
    """, (conn_id,))
    conn.commit()
    cur.close()
    conn.close()
