import sqlite3
from pathlib import Path


def test_required_tables():
    database_path = Path(__file__).resolve().parent.parent / "furlog.db"
    required_tables = ["users", "pets", "grooming_records"]
    connection = None

    try:
        connection = sqlite3.connect(database_path)
        cursor = connection.cursor()

        for table_name in required_tables:
            cursor.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table' AND name = ?
                """,
                (table_name,)
            )
            table_exists = cursor.fetchone() is not None

            if table_exists:
                print(f"PASS: {table_name} table exists")
            else:
                print(f"FAIL: {table_name} table does not exist")
    except sqlite3.Error as error:
        print(f"FAIL: Could not test the database: {error}")
    finally:
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    test_required_tables()