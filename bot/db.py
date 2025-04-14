import sqlite3
from contextlib import closing
from typing import Any, List, Optional


class BaseDatabase:
    def __init__(self, db_path: str, schema: str) -> None:
        self.db_path = db_path
        self.schema = schema
        self._initialize_db()

    def _initialize_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn, closing(conn.cursor()) as cursor:
            cursor.executescript(self.schema)
            conn.commit()

    def execute(self, query: str, params: tuple = ()) -> None:
        with sqlite3.connect(self.db_path) as conn, closing(conn.cursor()) as cursor:
            cursor.execute(query, params)
            conn.commit()

    def fetchone(self, query: str, params: tuple = ()) -> Optional[tuple]:
        with sqlite3.connect(self.db_path) as conn, closing(conn.cursor()) as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

    def fetchall(self, query: str, params: tuple = ()) -> List[tuple]:
        with sqlite3.connect(self.db_path) as conn, closing(conn.cursor()) as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()


class UsersDatabase(BaseDatabase):
    def __init__(self) -> None:
        super().__init__(
            db_path="databases/botdb.db",
            schema="""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    quota INTEGER,
                    searched INTEGER
                );
            """,
        )

    def add_user(self, user_id: int, quota: int, searched: int) -> None:
        if not self.get_user(user_id):
            self.execute("INSERT INTO users VALUES (?, ?, ?)", (user_id, quota, searched))

    def get_user(self, user_id: int) -> tuple | None:
        return self.fetchone("SELECT * FROM users WHERE user_id = ? LIMIT 1", (user_id,))

    def get_all(self) -> List[tuple]:
        return self.fetchall("SELECT * FROM users")

    def update_user(self, user_id: int, key: str, new_value: Any) -> None:
        if key not in ("quota", "searched"):
            raise ValueError(f"Invalid column name: {key}")
        self.execute(f"UPDATE users SET {key} = ? WHERE user_id = ?", (new_value, user_id))


class ReferralsDatabase(BaseDatabase):
    def __init__(self) -> None:
        super().__init__(
            db_path="databases/botdb.db",
            schema="""
                CREATE TABLE IF NOT EXISTS refids (
                    ref_id TEXT PRIMARY KEY,
                    quota INTEGER
                );
            """,
        )

    def add_referral(self, ref_id: int, quota: int) -> None:
        if not self.get_referral(ref_id):
            self.execute("INSERT INTO refids VALUES (?, ?)", (ref_id, quota))

    def get_referral(self, ref_id: str) -> tuple | None:
        return self.fetchone("SELECT * FROM refids WHERE ref_id = ? LIMIT 1", (ref_id,))

    def delete_referral(self, ref_id: str) -> None:
        self.execute("DELETE FROM refids WHERE ref_id = ?", (ref_id,))


class HashesDatabase(BaseDatabase):
    def __init__(self) -> None:
        super().__init__(
            db_path="databases/hashes.db",
            schema="""
                CREATE TABLE IF NOT EXISTS hashes (
                    hash TEXT UNIQUE,
                    password TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_hash ON hashes(hash);
            """,
        )

    def add_hashes(self, hashes: list[str], passwords: list[str]) -> None:
        data_to_insert = list(zip(hashes, passwords))
        with sqlite3.connect(self.db_path) as conn, closing(conn.cursor()) as cursor:
            cursor.executemany("INSERT OR IGNORE INTO hashes (hash, password) VALUES (?, ?)", data_to_insert)
            conn.commit()

    def get_hash(self, hash: str, cursor=None) -> tuple | None:
        if cursor is not None:
            cursor.execute("SELECT * FROM hashes WHERE hash = ? LIMIT 1", (hash,))
            return cursor.fetchone()
        else:
            return self.fetchone("SELECT * FROM hashes WHERE hash = ? LIMIT 1", (hash,))


class BasesDatabase(BaseDatabase):
    def __init__(self) -> None:
        super().__init__(
            db_path="databases/bases.db",
            schema="""
                CREATE TABLE IF NOT EXISTS bases (
                    username TEXT,
                    password TEXT,
                    hash TEXT,
                    ip TEXT,
                    server TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_username_nocase ON bases(username COLLATE NOCASE);
                CREATE INDEX IF NOT EXISTS idx_ip ON bases(ip);
            """,
        )

    def get_user(self, username: str) -> List[tuple]:
        return self.fetchall("SELECT * FROM bases WHERE username COLLATE NOCASE = ?", (username,))

    def get_ip(self, ip: str) -> List[tuple]:
        return self.fetchall("SELECT * FROM bases WHERE ip = ?", (ip,))
