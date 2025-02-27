import sqlite3


def clear_server_in_db(db_file: str, server_name: str) -> None:
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE bases
        SET server = NULL
        WHERE server = ?
    """,
        (server_name,),
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    clear_server_in_db("bases.db", " FreeDB_CM_?1")
