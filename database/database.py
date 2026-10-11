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
                (SELECT COUNT(*) FROM inventory_items WHERE category = 'Food'),
                (SELECT COUNT(*) FROM inventory_items WHERE category = 'Vitamin'),
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
                age_unit TEXT NOT NULL DEFAULT 'years',
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
        if "age_unit" not in pet_columns:
            cursor.execute(
                "ALTER TABLE pets ADD COLUMN age_unit TEXT NOT NULL DEFAULT 'years'"
            )
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

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pet_care (
                pet_id INTEGER PRIMARY KEY,
                special_care_needs TEXT NOT NULL DEFAULT '',
                care_notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pet_id) REFERENCES pets (id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL CHECK (category IN ('Food', 'Vitamin')),
                quantity INTEGER CHECK (quantity IS NULL OR quantity >= 0),
                unit TEXT NOT NULL DEFAULT '',
                reorder_level INTEGER NOT NULL DEFAULT 0 CHECK (reorder_level >= 0),
                expiration_date TEXT,
                notes TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_inventory_category_name
            ON inventory_items(category, name COLLATE NOCASE)
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pet_inventory_assignments (
                pet_id INTEGER NOT NULL,
                inventory_item_id INTEGER NOT NULL,
                assigned_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (pet_id, inventory_item_id),
                FOREIGN KEY (pet_id) REFERENCES pets (id) ON DELETE CASCADE,
                FOREIGN KEY (inventory_item_id)
                    REFERENCES inventory_items (id) ON DELETE CASCADE
            )
        """)

        self.connection.commit()
        self._migrate_legacy_pet_care_data()

    def _migrate_legacy_pet_care_data(self):
        """Copy old Foods, Vitamins, and Needs values without deleting them."""
        cursor = self.connection.cursor()
        if cursor.execute("PRAGMA user_version").fetchone()[0] >= 1:
            return

        cursor.execute("BEGIN IMMEDIATE")
        try:
            cursor.execute("SELECT id, foods, vitamins, needs FROM pets ORDER BY id")
            for pet_id, foods, vitamins, needs in cursor.fetchall():
                needs_value = (needs or "").strip()
                if needs_value:
                    cursor.execute("""
                        INSERT OR IGNORE INTO pet_care
                            (pet_id, special_care_needs, care_notes)
                        VALUES (?, ?, '')
                    """, (pet_id, needs_value))

                for category, legacy_value in (("Food", foods), ("Vitamin", vitamins)):
                    item_name = (legacy_value or "").strip()
                    if not item_name:
                        continue
                    cursor.execute("""
                        INSERT OR IGNORE INTO inventory_items
                            (name, category, quantity, unit, reorder_level,
                             expiration_date, notes)
                        VALUES (?, ?, NULL, '', 0, NULL, ?)
                    """, (
                        item_name,
                        category,
                        "Migrated from legacy pet field; stock quantity unknown."
                    ))
                    cursor.execute("""
                        SELECT id FROM inventory_items
                        WHERE category = ? AND name = ? COLLATE NOCASE
                    """, (category, item_name))
                    item_row = cursor.fetchone()
                    if item_row is None:
                        raise sqlite3.IntegrityError(
                            f"Could not migrate legacy {category.lower()} value for pet {pet_id}"
                        )
                    cursor.execute("""
                        INSERT OR IGNORE INTO pet_inventory_assignments
                            (pet_id, inventory_item_id)
                        VALUES (?, ?)
                    """, (pet_id, item_row[0]))

            cursor.execute("PRAGMA user_version = 1")
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

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