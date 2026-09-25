from datetime import datetime


class Pet:
    """Represents a pet registered in FurLog."""

    def __init__(
        self,
        id=None,
        name="",
        species="",
        breed="",
        age=None,
        owner="",
        created_at=None
    ):
        self.id = id
        self.name = name
        self.species = species
        self.breed = breed
        self.age = age
        self.owner = owner
        self.created_at = created_at or datetime.now().isoformat(timespec="seconds")

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = self._require_text(value, "Name")

    @property
    def species(self):
        return self._species

    @species.setter
    def species(self, value):
        self._species = self._require_text(value, "Species")

    @property
    def breed(self):
        return self._breed

    @breed.setter
    def breed(self, value):
        if value is None:
            self._breed = ""
        elif isinstance(value, str):
            self._breed = value.strip()
        else:
            raise ValueError("Breed must be text")

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value):
        if value is not None and (not isinstance(value, int) or value < 0):
            raise ValueError("Age must be a non-negative whole number")
        self._age = value

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, value):
        self._owner = self._require_text(value, "Owner")

    @property
    def created_at(self):
        return self._created_at

    @created_at.setter
    def created_at(self, value):
        self._created_at = self._require_text(value, "Created at")

    @staticmethod
    def _require_text(value, field_name):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} cannot be empty")
        return value.strip()