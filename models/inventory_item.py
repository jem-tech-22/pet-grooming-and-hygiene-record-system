class InventoryItem:
	"""A simple Food or Vitamin catalog item with current quantity."""

	CATEGORIES = ("Food", "Vitamin")

	def __init__(self, name, category, quantity, unit, item_id=None):
		self.id = item_id
		self.name = name
		self.category = category
		self.quantity = quantity
		self.unit = unit

	@property
	def id(self):
		return self._id

	@id.setter
	def id(self, value):
		if value is not None and (not isinstance(value, int) or value <= 0):
			raise ValueError("Inventory item ID must be a positive whole number")
		self._id = value

	@property
	def name(self):
		return self._name

	@name.setter
	def name(self, value):
		if not isinstance(value, str) or not value.strip():
			raise ValueError("Item name cannot be empty")
		self._name = value.strip()

	@property
	def category(self):
		return self._category

	@category.setter
	def category(self, value):
		if not isinstance(value, str) or value.strip().title() not in self.CATEGORIES:
			raise ValueError("Type must be Food or Vitamin")
		self._category = value.strip().title()

	@property
	def quantity(self):
		return self._quantity

	@quantity.setter
	def quantity(self, value):
		if value is not None and (
			not isinstance(value, int) or isinstance(value, bool) or value < 0
		):
			raise ValueError("Quantity must be a non-negative whole number")
		self._quantity = value

	@property
	def unit(self):
		return self._unit

	@unit.setter
	def unit(self, value):
		if not isinstance(value, str):
			raise ValueError("Unit must be text")
		self._unit = value.strip()
