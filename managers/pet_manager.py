from database.database import DatabaseManager
from models.pet import Pet


class PetManager:
	"""Handles CRUD and search operations for pets."""

	def __init__(self, database_manager=None):
		self.database_manager = database_manager or DatabaseManager()
		self.connection = self.database_manager.connection

	def create_pet(self, pet):
		"""Insert a Pet object and return it with its new database ID."""
		cursor = self.connection.cursor()
		cursor.execute(
			"""
			INSERT INTO pets (name, species, breed, age, owner, created_at, vitamins, foods, needs, age_unit)
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
			""",
			(pet.name, pet.species, pet.breed, pet.age, pet.owner, pet.created_at,
			 pet.vitamins, pet.foods, pet.needs, pet.age_unit)
		)
		self.connection.commit()
		pet.id = cursor.lastrowid
		return pet

	def get_all_pets(self):
		"""Return all pets as a list of Pet objects sorted alphabetically by name."""
		cursor = self.connection.cursor()
		cursor.execute(
			"""
			SELECT id, name, species, breed, age, owner, created_at, vitamins, foods, needs, age_unit
			FROM pets
			ORDER BY name COLLATE NOCASE ASC
			"""
		)
		return [self._row_to_pet(row) for row in cursor.fetchall()]

	def get_pet_by_id(self, pet_id):
		"""Return one Pet object by ID, or None when it is not found."""
		cursor = self.connection.cursor()
		cursor.execute(
			"""
			SELECT id, name, species, breed, age, owner, created_at, vitamins, foods, needs, age_unit
			FROM pets
			WHERE id = ?
			""",
			(pet_id,)
		)
		row = cursor.fetchone()
		return self._row_to_pet(row) if row else None

	def update_pet(self, pet):
		"""Update an existing pet and return whether a row was changed."""
		if pet.id is None:
			raise ValueError("A pet ID is required to update a pet")

		cursor = self.connection.cursor()
		cursor.execute(
			"""
			UPDATE pets
			SET name = ?, species = ?, breed = ?, age = ?, owner = ?,
			    vitamins = ?, foods = ?, needs = ?, age_unit = ?
			WHERE id = ?
			""",
			(pet.name, pet.species, pet.breed, pet.age, pet.owner,
			 pet.vitamins, pet.foods, pet.needs, pet.age_unit, pet.id)
		)
		self.connection.commit()
		return cursor.rowcount > 0

	def delete_pet(self, pet_id):
		"""Delete a pet by ID and return whether a row was deleted."""
		cursor = self.connection.cursor()
		cursor.execute("DELETE FROM pets WHERE id = ?", (pet_id,))
		self.connection.commit()
		return cursor.rowcount > 0

	def search_pets(self, search_term):
		"""Search pet names, species, breeds, and owners in alphabetical order."""
		search_pattern = f"%{search_term}%"
		cursor = self.connection.cursor()
		cursor.execute(
			"""
			SELECT id, name, species, breed, age, owner, created_at, vitamins, foods, needs, age_unit
			FROM pets
			WHERE name LIKE ?
			   OR species LIKE ?
			   OR breed LIKE ?
			   OR owner LIKE ?
			ORDER BY name COLLATE NOCASE ASC
			""",
			(search_pattern, search_pattern, search_pattern, search_pattern)
		)
		return [self._row_to_pet(row) for row in cursor.fetchall()]

	@staticmethod
	def _row_to_pet(row):
		return Pet(
			id=row[0],
			name=row[1],
			species=row[2],
			breed=row[3],
			age=row[4],
			owner=row[5],
			created_at=row[6],
			vitamins=row[7],
			foods=row[8],
			needs=row[9],
			age_unit=row[10]
		)
