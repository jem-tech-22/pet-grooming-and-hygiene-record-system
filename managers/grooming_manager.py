from database.database import DatabaseManager
from models.grooming_record import GroomingRecord


class GroomingManager:
	"""Handles database operations for grooming records."""

	def __init__(self, database_manager=None):
		self.database_manager = database_manager or DatabaseManager()
		self.connection = self.database_manager.connection

	def get_pet_options(self):
		"""Return registered pet IDs, names, and owners for the selector."""
		cursor = self.connection.cursor()
		cursor.execute("""
			SELECT id, name, owner
			FROM pets
			ORDER BY name COLLATE NOCASE ASC, id ASC
		""")
		return cursor.fetchall()

	def get_all_records(self):
		"""Return grooming rows joined with their pet name and owner."""
		cursor = self.connection.cursor()
		cursor.execute("""
			SELECT gr.id, gr.pet_id, p.name, p.owner,
			       gr.grooming_date, gr.activity, COALESCE(gr.notes, '')
			FROM grooming_records AS gr
			JOIN pets AS p ON p.id = gr.pet_id
			ORDER BY gr.grooming_date DESC, gr.id DESC
		""")
		return cursor.fetchall()

	def get_record_by_id(self, record_id):
		"""Return one GroomingRecord by its database ID, or None."""
		cursor = self.connection.cursor()
		cursor.execute("""
			SELECT id, pet_id, activity, grooming_date, notes, created_by
			FROM grooming_records
			WHERE id = ?
		""", (record_id,))
		row = cursor.fetchone()
		return self._row_to_record(row) if row else None

	def create_record(self, record):
		"""Insert a grooming record and assign its generated database ID."""
		cursor = self.connection.cursor()
		cursor.execute("""
			INSERT INTO grooming_records
			    (pet_id, activity, grooming_date, notes, created_by)
			VALUES (?, ?, ?, ?, ?)
		""", (
			record.pet_id,
			record.activity,
			record.grooming_date,
			record.notes,
			record.created_by
		))
		self.connection.commit()
		record.id = cursor.lastrowid
		return record

	def update_record(self, record):
		"""Update an existing grooming record by ID."""
		if record.id is None:
			raise ValueError("A record ID is required to update a grooming record")
		cursor = self.connection.cursor()
		cursor.execute("""
			UPDATE grooming_records
			SET pet_id = ?, activity = ?, grooming_date = ?, notes = ?
			WHERE id = ?
		""", (
			record.pet_id,
			record.activity,
			record.grooming_date,
			record.notes,
			record.id
		))
		self.connection.commit()
		return cursor.rowcount > 0

	def delete_record(self, record_id):
		"""Delete one grooming record by ID."""
		cursor = self.connection.cursor()
		cursor.execute("DELETE FROM grooming_records WHERE id = ?", (record_id,))
		self.connection.commit()
		return cursor.rowcount > 0

	@staticmethod
	def _row_to_record(row):
		return GroomingRecord(
			id=row[0],
			pet_id=row[1],
			activity=row[2],
			grooming_date=row[3],
			notes=row[4],
			created_by=row[5]
		)

	def close(self):
		self.database_manager.close()