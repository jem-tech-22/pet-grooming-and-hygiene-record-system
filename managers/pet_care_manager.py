from database.database import DatabaseManager
from models.pet_care import PetCare


class PetCareManager:
	"""Reads and writes care information associated with a pet."""

	def __init__(self, database_manager=None):
		self.database_manager = database_manager or DatabaseManager()
		self.connection = self.database_manager.connection

	def get_for_pet(self, pet_id):
		cursor = self.connection.cursor()
		cursor.execute(
			"SELECT pet_id, special_care_needs, care_notes FROM pet_care WHERE pet_id = ?",
			(pet_id,)
		)
		row = cursor.fetchone()
		return PetCare(*row) if row else None

	def get_pet_options(self):
		cursor = self.connection.cursor()
		cursor.execute("""
			SELECT id, name, species, owner FROM pets
			ORDER BY name COLLATE NOCASE, id
		""")
		return cursor.fetchall()

	def get_all_report_rows(self):
		"""Return pet care details and names of assigned Food/Vitamin items."""
		cursor = self.connection.cursor()
		cursor.execute("""
			SELECT p.id, p.name,
			       COALESCE(pc.special_care_needs, ''),
			       COALESCE(pc.care_notes, ''),
			       COALESCE((
			           SELECT GROUP_CONCAT(i.name, ', ')
			           FROM pet_inventory_assignments AS a
			           JOIN inventory_items AS i ON i.id = a.inventory_item_id
			           WHERE a.pet_id = p.id AND i.category = 'Food'
			       ), ''),
			       COALESCE((
			           SELECT GROUP_CONCAT(i.name, ', ')
			           FROM pet_inventory_assignments AS a
			           JOIN inventory_items AS i ON i.id = a.inventory_item_id
			           WHERE a.pet_id = p.id AND i.category = 'Vitamin'
			       ), '')
			FROM pets AS p
			LEFT JOIN pet_care AS pc ON pc.pet_id = p.id
			ORDER BY p.name COLLATE NOCASE, p.id
		""")
		return cursor.fetchall()

	def save_for_pet(self, care):
		cursor = self.connection.cursor()
		cursor.execute("""
			INSERT INTO pet_care (pet_id, special_care_needs, care_notes)
			VALUES (?, ?, ?)
			ON CONFLICT(pet_id) DO UPDATE SET
				special_care_needs = excluded.special_care_needs,
				care_notes = excluded.care_notes,
				updated_at = CURRENT_TIMESTAMP
		""", (care.pet_id, care.special_care_needs, care.care_notes))
		self.connection.commit()
		return care

	def delete_for_pet(self, pet_id):
		cursor = self.connection.cursor()
		cursor.execute("DELETE FROM pet_care WHERE pet_id = ?", (pet_id,))
		self.connection.commit()
		return cursor.rowcount > 0
