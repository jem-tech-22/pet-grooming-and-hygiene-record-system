import sqlite3
from pathlib import Path


class DatabaseManager:
    """Creates and manages the FurLog SQLite database."""

    def __init__(self, database_name="furlog.db", read_only=False):
        project_folder = Path(__file__).resolve().parent.parent
        self.database_path = project_folder / database_name
        if read_only:
            database_uri = f"{self.database_path.as_uri()}?mode=ro"
            self.connection = sqlite3.connect(database_uri, uri=True)
        else:
            self.connection = sqlite3.connect(self.database_path)
        self.connection.execute("PRAGMA foreign_keys = ON")
        if not read_only:
            self.create_tables()

    def get_dashboard_summary(self):
        """Return read-only pet, grooming, food, vitamin, and species counts."""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT
                (SELECT COUNT(*) FROM pets),
                (SELECT COUNT(*) FROM grooming_records),
                (SELECT COUNT(*) FROM pets
                 WHERE foods IS NOT NULL AND TRIM(foods) <> ''),
                (SELECT COUNT(*) FROM pets
                 WHERE vitamins IS NOT NULL AND TRIM(vitamins) <> ''),
                (SELECT COUNT(*) FROM pets
                 WHERE LOWER(TRIM(COALESCE(species, ''))) IN ('dog', 'dogs')),
                (SELECT COUNT(*) FROM pets
                 WHERE LOWER(TRIM(COALESCE(species, ''))) IN ('cat', 'cats')),
                (SELECT COUNT(*) FROM pets
                 WHERE LOWER(TRIM(COALESCE(species, '')))
                       NOT IN ('dog', 'dogs', 'cat', 'cats'))
        """)
        row = cursor.fetchone()
        return {
            "total_pets": row[0],
            "grooming_records": row[1],
            "foods": row[2],
            "vitamins": row[3],
            "dogs": row[4],
            "cats": row[5],
            "other": row[6]
        }

    def get_recent_grooming_activities(self, limit=5):
        """Return the latest grooming dates, pet names, and activity names."""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT gr.grooming_date,
                   COALESCE(NULLIF(TRIM(p.name), ''), 'Unknown pet'),
                   gr.activity
            FROM grooming_records AS gr
            LEFT JOIN pets AS p ON p.id = gr.pet_id
            ORDER BY gr.grooming_date DESC, gr.id DESC
            LIMIT ?
        """, (limit,))
        return cursor.fetchall()

    def create_tables(self):
        """Create the required tables if they do not already exist."""
        cursor = self.connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                species TEXT NOT NULL,
                breed TEXT,
                age INTEGER,
                owner TEXT NOT NULL,
                vitamins TEXT,
                foods TEXT,
                needs TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        pet_columns = {
            row[1] for row in cursor.execute("PRAGMA table_info(pets)").fetchall()
        }
        for column_name in ("vitamins", "foods", "needs"):
            if column_name not in pet_columns:
                cursor.execute(f"ALTER TABLE pets ADD COLUMN {column_name} TEXT")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grooming_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                activity TEXT NOT NULL,
                grooming_date TEXT NOT NULL,
                notes TEXT,
                created_by INTEGER,
                FOREIGN KEY (pet_id) REFERENCES pets (id) ON DELETE CASCADE,
                FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE SET NULL
            )
        """)

        self.connection.commit()

    def get_table_names(self):
        """Return the application table names for a simple database check."""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name IN ('users', 'pets', 'grooming_records')
            ORDER BY name
        """)
        return [row[0] for row in cursor.fetchall()]

    def close(self):
        """Close the database connection."""
        self.connection.close()


if __name__ == "__main__":
    database_manager = DatabaseManager()
    table_names = database_manager.get_table_names()
    print(f"Database created: {database_manager.database_path}")
    print(f"Tables found: {', '.join(table_names)}")
    database_manager.close()