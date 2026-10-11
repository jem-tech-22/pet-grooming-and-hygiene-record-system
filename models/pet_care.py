class PetCare:
	"""Care requirements and notes belonging to one pet."""

	def __init__(self, pet_id, special_care_needs="", care_notes=""):
		self.pet_id = pet_id
		self.special_care_needs = special_care_needs
		self.care_notes = care_notes

	@property
	def pet_id(self):
		return self._pet_id

	@pet_id.setter
	def pet_id(self, value):
		if not isinstance(value, int) or value <= 0:
			raise ValueError("Pet ID must be a positive whole number")
		self._pet_id = value

	@property
	def special_care_needs(self):
		return self._optional_text(self._special_care_needs, "Special care needs")

	@special_care_needs.setter
	def special_care_needs(self, value):
		self._special_care_needs = self._optional_text(value, "Special care needs")

	@property
	def care_notes(self):
		return self._optional_text(self._care_notes, "Care notes")

	@care_notes.setter
	def care_notes(self, value):
		self._care_notes = self._optional_text(value, "Care notes")

	@staticmethod
	def _optional_text(value, label):
		if value is None:
			return ""
		if not isinstance(value, str):
			raise ValueError(f"{label} must be text")
		return value.strip()
