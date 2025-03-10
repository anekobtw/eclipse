import sqlite3


def clear_server_in_db(db_file: str) -> None:
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute("SELECT hash FROM bases")
    f = open("hashes.txt", "w")
    for i in cursor.fetchall():
        try:
            if i[0].startswith("$SHA$"):
                f.write(i[0] + "\n")
        except Exception as e:
            continue

    # cursor.execute("UPDATE bases SET server = NULL WHERE server = ?", (server_name,))
    # conn.commit()
    # conn.close()


if __name__ == "__main__":
    clear_server_in_db("bases.db")
