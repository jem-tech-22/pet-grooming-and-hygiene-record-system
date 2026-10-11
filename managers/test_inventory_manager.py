import sqlite3
import unittest

from managers.inventory_manager import InventoryManager
from models.inventory_item import InventoryItem


class InventoryDatabaseStub:
	def __init__(self):
		self.connection = sqlite3.connect(":memory:")
		self.connection.execute("PRAGMA foreign_keys = ON")
		self.connection.executescript("""
			CREATE TABLE pets (
				id INTEGER PRIMARY KEY,
				name TEXT NOT NULL,
				owner TEXT NOT NULL
			);
			CREATE TABLE inventory_items (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				name TEXT NOT NULL,
				category TEXT NOT NULL,
				quantity INTEGER,
				unit TEXT NOT NULL DEFAULT '',
				reorder_level INTEGER NOT NULL DEFAULT 0,
				expiration_date TEXT,
				notes TEXT NOT NULL DEFAULT ''
			);
			CREATE UNIQUE INDEX idx_inventory_category_name
			ON inventory_items(category, name COLLATE NOCASE);
			CREATE TABLE pet_inventory_assignments (
				pet_id INTEGER NOT NULL,
				inventory_item_id INTEGER NOT NULL,
				PRIMARY KEY (pet_id, inventory_item_id),
				FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE,
				FOREIGN KEY (inventory_item_id) REFERENCES inventory_items(id) ON DELETE CASCADE
			);
		""")
		self.connection.executemany(
			"INSERT INTO pets (id, name, owner) VALUES (?, ?, ?)",
			((1, "Bruno", "Alex"), (2, "Milo", "Sam"))
		)

	def close(self):
		self.connection.close()


class InventoryManagerTests(unittest.TestCase):
	def setUp(self):
		self.database = InventoryDatabaseStub()
		self.manager = InventoryManager(self.database)

	def tearDown(self):
		self.database.close()

	def test_add_search_filter_update_and_delete(self):
		food = self.manager.create_item(
			InventoryItem("Royal Canin", "Food", 10, "packs")
		)
		self.manager.create_item(InventoryItem("Vitamin C", "Vitamin", 5, "bottles"))

		self.assertEqual(len(self.manager.get_items(category="Food")), 1)
		self.assertEqual(self.manager.get_items(search_text="royal")[0].id, food.id)

		food.quantity = 8
		self.assertTrue(self.manager.update_item(food))
		self.assertEqual(self.manager.get_item_by_id(food.id).quantity, 8)
		self.assertTrue(self.manager.delete_item(food.id))
		self.assertEqual(self.manager.get_items(category="Food"), [])

	def test_negative_quantity_is_rejected(self):
		with self.assertRaisesRegex(ValueError, "non-negative"):
			InventoryItem("Food", "Food", -1, "packs")

	def test_pet_assignments_use_ids_allow_many_to_many_and_do_not_change_quantity(self):
		food = self.manager.create_item(
			InventoryItem("Royal Canin", "Food", 10, "packs")
		)
		vitamin = self.manager.create_item(
			InventoryItem("Vitamin C", "Vitamin", 5, "bottles")
		)
		self.assertTrue(self.manager.assign_item(1, food.id, "Food"))
		self.assertTrue(self.manager.assign_item(1, vitamin.id, "Vitamin"))
		self.assertTrue(self.manager.assign_item(2, food.id, "Food"))
		self.assertFalse(self.manager.assign_item(1, food.id, "Food"))

		bruno_assignments = self.manager.get_pet_assignments(1)
		self.assertEqual({row[0] for row in bruno_assignments}, {food.id, vitamin.id})
		self.assertEqual(self.manager.get_pet_assignments(1, "Food")[0][0], food.id)
		self.assertEqual(self.manager.get_pet_assignments(2, "Food")[0][0], food.id)
		self.assertEqual(self.manager.get_item_by_id(food.id).quantity, 10)
		self.assertEqual(self.manager.get_item_by_id(vitamin.id).quantity, 5)

		self.assertTrue(self.manager.unassign_item(1, food.id))
		self.assertEqual(self.manager.get_pet_assignments(1, "Food"), [])
		self.assertEqual(self.manager.get_pet_assignments(2, "Food")[0][0], food.id)
		self.assertEqual(self.manager.get_item_by_id(food.id).quantity, 10)

	def test_unknown_legacy_quantity_can_be_set_without_overwriting_old_metadata(self):
		cursor = self.database.connection.cursor()
		cursor.execute("""
			INSERT INTO inventory_items (name, category, quantity, unit, notes)
			VALUES ('Migrated Food', 'Food', NULL, '', 'legacy marker')
		""")
		self.database.connection.commit()
		item = self.manager.get_items()[0]
		self.assertIsNone(item.quantity)
		item.quantity = 6
		item.unit = "bags"
		self.manager.update_item(item)
		stored = self.database.connection.execute(
			"SELECT quantity, unit, notes FROM inventory_items WHERE id = ?",
			(item.id,)
		).fetchone()
		self.assertEqual(stored, (6, "bags", "legacy marker"))

if __name__ == "__main__":
	unittest.main()
