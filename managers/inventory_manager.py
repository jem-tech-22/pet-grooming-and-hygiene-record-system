import sqlite3

from database.database import DatabaseManager
from models.inventory_item import InventoryItem


class InventoryManager:
	"""Simple Food/Vitamin catalog CRUD and search/filter operations."""

	def __init__(self, database_manager=None):
		self.database_manager = database_manager or DatabaseManager()
		self.connection = self.database_manager.connection

	def get_items(self, search_text="", category=None):
		conditions = []
		parameters = []
		if search_text.strip():
			conditions.append("LOWER(name) LIKE LOWER(?)")
			parameters.append(f"%{search_text.strip()}%")
		if category in InventoryItem.CATEGORIES:
			conditions.append("category = ?")
			parameters.append(category)
		where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
		cursor = self.connection.cursor()
		cursor.execute(f"""
			SELECT id, name, category, quantity, unit
			FROM inventory_items
			{where}
			ORDER BY category, name COLLATE NOCASE, id
		""", parameters)
		return [self._row_to_item(row) for row in cursor.fetchall()]

	def get_item_by_id(self, item_id):
		cursor = self.connection.cursor()
		cursor.execute("""
			SELECT id, name, category, quantity, unit
			FROM inventory_items WHERE id = ?
		""", (item_id,))
		row = cursor.fetchone()
		return self._row_to_item(row) if row else None

	def create_item(self, item):
		if item.quantity is None:
			raise ValueError("Enter a quantity when adding a new item.")
		cursor = self.connection.cursor()
		try:
			cursor.execute("""
				INSERT INTO inventory_items (name, category, quantity, unit)
				VALUES (?, ?, ?, ?)
			""", self._item_values(item))
			self.connection.commit()
		except sqlite3.IntegrityError as error:
			self.connection.rollback()
			if "idx_inventory_category_name" in str(error) or "UNIQUE constraint failed" in str(error):
				raise ValueError("An item with this name and type already exists.") from error
			raise
		item.id = cursor.lastrowid
		return item

	def update_item(self, item):
		if item.id is None:
			raise ValueError("An item ID is required to update inventory")
		cursor = self.connection.cursor()
		try:
			cursor.execute("""
				UPDATE inventory_items
				SET name = ?, category = ?, quantity = ?, unit = ?
				WHERE id = ?
			""", (*self._item_values(item), item.id))
			self.connection.commit()
		except sqlite3.IntegrityError as error:
			self.connection.rollback()
			if "idx_inventory_category_name" in str(error) or "UNIQUE constraint failed" in str(error):
				raise ValueError("An item with this name and type already exists.") from error
			raise
		return cursor.rowcount > 0

	def delete_item(self, item_id):
		cursor = self.connection.cursor()
		cursor.execute("DELETE FROM inventory_items WHERE id = ?", (item_id,))
		self.connection.commit()
		return cursor.rowcount > 0

	def get_pet_assignments(self, pet_id, category=None):
		conditions = ["a.pet_id = ?"]
		parameters = [pet_id]
		if category in InventoryItem.CATEGORIES:
			conditions.append("i.category = ?")
			parameters.append(category)
		cursor = self.connection.cursor()
		cursor.execute(f"""
			SELECT i.id, i.name, i.category, i.quantity, i.unit
			FROM pet_inventory_assignments AS a
			JOIN inventory_items AS i ON i.id = a.inventory_item_id
			WHERE {' AND '.join(conditions)}
			ORDER BY i.name COLLATE NOCASE, i.id
		""", parameters)
		return cursor.fetchall()

	def assign_item(self, pet_id, item_id, category):
		if category not in InventoryItem.CATEGORIES:
			raise ValueError("Type must be Food or Vitamin")
		cursor = self.connection.cursor()
		cursor.execute("SELECT 1 FROM pets WHERE id = ?", (pet_id,))
		if cursor.fetchone() is None:
			raise ValueError("The selected pet no longer exists.")
		cursor.execute(
			"SELECT category FROM inventory_items WHERE id = ?", (item_id,)
		)
		row = cursor.fetchone()
		if row is None:
			raise ValueError("The selected supply no longer exists.")
		if row[0] != category:
			raise ValueError(f"Select an inventory item with type {category}.")
		cursor.execute("""
			INSERT OR IGNORE INTO pet_inventory_assignments (pet_id, inventory_item_id)
			VALUES (?, ?)
		""", (pet_id, item_id))
		created = cursor.rowcount > 0
		self.connection.commit()
		return created

	def unassign_item(self, pet_id, item_id):
		cursor = self.connection.cursor()
		cursor.execute("""
			DELETE FROM pet_inventory_assignments
			WHERE pet_id = ? AND inventory_item_id = ?
		""", (pet_id, item_id))
		self.connection.commit()
		return cursor.rowcount > 0

	@staticmethod
	def _item_values(item):
		return item.name, item.category, item.quantity, item.unit

	@staticmethod
	def _row_to_item(row):
		return InventoryItem(
			item_id=row[0], name=row[1], category=row[2], quantity=row[3], unit=row[4]
		)
