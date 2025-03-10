import sqlite3
from contextlib import closing
from typing import Any, List, Literal, Optional


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


class User:
    def __init__(self, user_id: int, subscription: str, subscription_until: Optional[str], quota: int, invited: int) -> None:
        self.user_id = user_id
        self.subscription = subscription
        self.subscription_until = subscription_until
        self.quota = quota
        self.invited = invited

    @classmethod
    def from_tuple(cls, data: tuple) -> "User":
        return cls(*data)


class Referral:
    def __init__(self, ref_id: str, uses_left: int, subscription: Literal["premium", "premium+"], time: str) -> None:
        self.ref_id = ref_id
        self.uses_left = uses_left
        self.subscription = subscription
        self.time = time

    @classmethod
    def from_tuple(cls, data: tuple) -> "Referral":
        return cls(*data)


class UsersDatabase(BaseDatabase):
    def __init__(self) -> None:
        super().__init__(
            db_path="databases/botdb.db",
            schema="""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    subscription TEXT,
                    subscription_until DATETIME DEFAULT NULL,
                    quota INTEGER,
                    invited INTEGER
                );
            """,
        )

    def add_user(self, user: User) -> None:
        if not self.get_user(user.user_id):
            self.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (user.user_id, user.subscription, user.subscription_until, user.quota, user.invited))

    def get_user(self, user_id: int) -> Optional[User]:
        data = self.fetchone("SELECT * FROM users WHERE user_id = ? LIMIT 1", (user_id,))
        return User.from_tuple(data) if data else None

    def get_all(self) -> list[User]:
        data = self.fetchall("SELECT * FROM users")
        return [User.from_tuple(row) for row in data]

    def update_user(self, user_id: int, key: str, value: Any) -> None:
        if key not in ("subscription", "subscription_until", "quota", "invited"):
            raise ValueError(f"Invalid column name: {key}")
        self.execute(f"UPDATE users SET {key} = ? WHERE user_id = ?", (value, user_id))


class ReferralsDatabase(BaseDatabase):
    def __init__(self) -> None:
        super().__init__(
            db_path="databases/botdb.db",
            schema="""
                CREATE TABLE IF NOT EXISTS refids (
                    ref_id TEXT PRIMARY KEY,
                    uses_left INTEGER,
                    subscription TEXT,
                    time TEXT
                );
            """,
        )

    def add_referral(self, referral: Referral) -> None:
        if not self.get_referral(referral.ref_id):
            self.execute("INSERT INTO refids VALUES (?, ?, ?, ?)", (referral.ref_id, referral.uses_left, referral.subscription, referral.time))

    def get_referral(self, ref_id: str) -> Optional[Referral]:
        data = self.fetchone("SELECT * FROM refids WHERE ref_id = ? LIMIT 1", (ref_id,))
        return Referral.from_tuple(data) if data else None

    def use_referral(self, ref_id: str) -> None:
        referral = self.get_referral(ref_id)
        if referral:
            self.execute("UPDATE refids SET uses_left = uses_left - 1 WHERE ref_id = ?", (ref_id,))
            if referral.uses_left == 1:
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
                );
                CREATE INDEX IF NOT EXISTS idx_username_nocase ON bases(username COLLATE NOCASE);
                CREATE INDEX IF NOT EXISTS idx_ip ON bases(ip);
            """,
        )

    def get_user(self, username: str) -> List[tuple]:
        return self.fetchall("SELECT * FROM bases WHERE username COLLATE NOCASE = ?", (username,))

    def get_by_ip(self, ip: str) -> List[tuple]:
        return self.fetchall("SELECT * FROM bases WHERE ip = ?", (ip,))
