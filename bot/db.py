import sqlite3
from typing import Any, Optional, Literal
from contextlib import closing


class BaseDatabase:
    def __init__(self, db_path: str, schema: str) -> None:
        self.db_path = db_path
        self.schema = schema
        self._initialize_db()

    def _initialize_db(self) -> None:
        """Creates table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn, closing(conn.cursor()) as cursor:
            cursor.execute(self.schema)
            conn.commit()

    def execute(self, query: str, params: tuple = ()) -> None:
        """Executes a query that does not return data (INSERT, UPDATE, DELETE)."""
        with sqlite3.connect(self.db_path) as conn, closing(conn.cursor()) as cursor:
            cursor.execute(query, params)
            conn.commit()

    def fetchone(self, query: str, params: tuple = ()) -> Optional[tuple]:
        """Executes a query that returns a single row."""
        with sqlite3.connect(self.db_path) as conn, closing(conn.cursor()) as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

    def fetchall(self, query: str, params: tuple = ()) -> list[tuple]:
        """Executes a query that returns multiple rows."""
        with sqlite3.connect(self.db_path) as conn, closing(conn.cursor()) as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()


class UsersDatabase(BaseDatabase):
    def __init__(self) -> None:
        super().__init__(
            db_path="bot_databases/usersdb.db",
            schema="""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER,
                    subscription TEXT,
                    subscription_until DATETIME DEFAULT NULL,
                    quota INTEGER,
                    invited INTEGER
                )
            """,
        )

    def add_user(self, user_id: int, subscription: str, subscription_until: str, quota: int, invited: int) -> None:
        if not self.get_user(user_id):
            self.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (user_id, subscription, subscription_until, quota, invited))

    def get_user(self, user_id: int) -> Optional[tuple]:
        return self.fetchone("SELECT * FROM users WHERE user_id = ? LIMIT 1", (user_id,))

    def get_all(self) -> list[tuple]:
        return self.fetchall("SELECT * FROM users")

    def update_user(self, user_id: int, key: str, value: Any) -> None:
        if key not in ("subscription", "subscription_until", "quota", "invited"):
            raise ValueError(f"Invalid column name: {key}")
        self.execute(f"UPDATE users SET {key} = ? WHERE user_id = ?", (value, user_id))


class RefIDsDatabase(BaseDatabase):
    def __init__(self) -> None:
        super().__init__(
            db_path="bot_databases/refids.db",
            schema="""
                CREATE TABLE IF NOT EXISTS refids (
                    ref_id TEXT,
                    uses_left INTEGER,
                    subscription TEXT,
                    time TEXT
                )
            """,
        )

    def add_refid(self, ref_id: str, uses_left: int, subscription: Literal["premium", "premium+"], time: str) -> None:
        if not self.get_refid(ref_id):
            self.execute("INSERT INTO refids VALUES (?, ?, ?, ?)", (ref_id, uses_left, subscription, time))

    def get_refid(self, ref_id: str) -> Optional[tuple]:
        return self.fetchone("SELECT * FROM refids WHERE ref_id = ? LIMIT 1", (ref_id,))

    def use_refid(self, ref_id: str) -> None:
        if self.get_refid(ref_id):
            self.execute("UPDATE refids SET uses_left = uses_left - 1 WHERE ref_id = ?", (ref_id,))
            if self.get_refid(ref_id)[1] == 0:
                self.execute("DELETE FROM refids WHERE ref_id = ?", (ref_id,))


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
                )
            """,
        )
        self.execute("CREATE INDEX IF NOT EXISTS idx_username ON bases (username)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_ip ON bases (ip)")

    def get_user(self, username: str) -> Optional[tuple]:
        return self.fetchall("SELECT * FROM bases WHERE username = ?", (username,))

    def get_by_ip(self, ip: str) -> Optional[tuple]:
        return self.fetchall("SELECT * FROM bases WHERE ip = ?", (ip,))


# Usage:
# users_db = UsersDatabase()
# refids_db = RefIDsDatabase()
# bases_db = BasesDatabase()
