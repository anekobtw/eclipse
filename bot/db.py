import os
import sqlite3
from typing import Literal

import pandas as pd

# Bases from "databases" folder
# Short name: bases
# username | password | hash | ip | server


def _load_databases(directory: str) -> pd.DataFrame:
    parquet_files = ["database.parquet"]
    # parquet_files = [f for f in os.listdir(directory) if f.endswith(".parquet")]
    dfs = [pd.read_parquet(os.path.join(directory, f), engine="fastparquet") for f in parquet_files]
    return pd.concat(dfs, ignore_index=True)


bases = _load_databases("databases")  # Yes, it preloads


def bases_get_user(username: str) -> dict | None:
    user = bases[bases["username"] == username]
    return None if user.empty else user.to_dict()


def bases_get_ip(ip: str) -> dict | None:
    user = bases[bases["ip"] == ip]
    return None if user.empty else user.to_dict()


# Database "bot_databases/users.parquet"
# id | subscription | subscription_until | quota | invited
# Short name: usersdb

usersdb_conn = sqlite3.connect("bot_databases/usersdb.db")
usersdb_cursor = usersdb_conn.cursor()

usersdb_cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        subscription TEXT,
        subscription_until DATETIME DEFAULT NULL,
        quota INTEGER,
        invited INTEGER
    )
"""
)
usersdb_conn.commit()


def usersdb_add(user_id: int, subscription: str, subscription_until: str, quota: int, invited: int) -> None:
    if usersdb_get(user_id) is None:
        usersdb_cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (user_id, subscription, subscription_until, quota, invited))
        usersdb_conn.commit()


def usersdb_get(user_id: int) -> tuple | None:
    usersdb_cursor.execute("SELECT * FROM users WHERE user_id = ? LIMIT 1", (user_id,))
    return usersdb_cursor.fetchone()


def usersdb_update(user_id: int, key: str, value: str) -> None:
    if key not in ("subscription", "subscription_until", "quota", "invited"):
        raise ValueError(f"Invalid column name: {key}")
    usersdb_cursor.execute(f"UPDATE users SET {key} = ? WHERE user_id = ?", (value, user_id))
    usersdb_conn.commit()


# Database "bot_databases/refids.parquet"
# ref_id | uses_left | subscription | time
# Short name: refids


refids_conn = sqlite3.connect("bot_databases/refids.db")
refids_cursor = refids_conn.cursor()

refids_cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS refids(
        ref_id TEXT,
        uses_left INTEGER,
        subscription TEXT,
        time TEXT
    )
"""
)
refids_conn.commit()


def refids_add(ref_id: str, uses_left: int, subscription: Literal["premium", "premium+"], time: str) -> None:
    if refids_get(ref_id) is None:
        refids_cursor.execute("INSERT INTO refids VALUES (?, ?, ?, ?)", (ref_id, uses_left, subscription, time))
        refids_conn.commit()


def refids_delete(ref_id: str) -> None:
    refids_cursor.execute("DELETE FROM refids WHERE ref_id = ?", (ref_id,))
    refids_conn.commit()


def refids_get(ref_id: str) -> tuple | None:
    refids_cursor.execute("SELECT * FROM refids WHERE ref_id = ? LIMIT 1", (ref_id,))
    return refids_cursor.fetchone()


def refids_use(ref_id: str) -> None:
    if refids_get(ref_id) is not None:
        refids_cursor.execute(f"UPDATE refids SET uses_left = uses_left - 1 WHERE ref_id = ?", (ref_id,))
        refids_conn.commit()
    if refids_get(ref_id)[1] == 0:
        refids_delete(ref_id)
