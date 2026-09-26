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
        created_at=None,
        vitamins="",
        foods="",
        needs=""
    ):
        self.id = id
        self.name = name
        self.species = species
        self.breed = breed
        self.age = age
        self.owner = owner
        self.created_at = created_at or self._default_created_at()
        self.vitamins = vitamins
        self.foods = foods
        self.needs = needs

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
    def vitamins(self):
        return self._vitamins

    @vitamins.setter
    def vitamins(self, value):
        self._vitamins = self._optional_text(value, "Vitamins")

    @property
    def foods(self):
        return self._foods

    @foods.setter
    def foods(self, value):
        self._foods = self._optional_text(value, "Foods")

    @property
    def needs(self):
        return self._needs

    @needs.setter
    def needs(self, value):
        self._needs = self._optional_text(value, "Needs")

    @property
    def created_at(self):
        return self._created_at

    @created_at.setter
    def created_at(self, value):
        self._created_at = self._normalize_created_at(value)

    @classmethod
    def _default_created_at(cls):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def _normalize_created_at(cls, value):
        if value is None:
            return cls._default_created_at()

        if isinstance(value, datetime):
            dt = value
            if dt.tzinfo is not None:
                dt = dt.astimezone()
            return dt.strftime("%Y-%m-%d %H:%M:%S")

        if isinstance(value, str):
            value = value.strip()
            if not value:
                raise ValueError("Created at cannot be empty")

            parsed = None
            for candidate in (value, value.replace("Z", "+00:00")):
                try:
                    parsed = datetime.fromisoformat(candidate)
                    break
                except ValueError:
                    continue

            if parsed is None:
                for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
                    try:
                        parsed = datetime.strptime(value, fmt)
                        break
                    except ValueError:
                        continue

            if parsed is None:
                raise ValueError("Created at has an invalid date format")

            if parsed.tzinfo is not None:
                parsed = parsed.astimezone()
            return parsed.strftime("%Y-%m-%d %H:%M:%S")

        raise ValueError("Created at must be a datetime or text value")

    @staticmethod
    def _require_text(value, field_name):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} cannot be empty")
        return value.strip()

    @staticmethod
    def _optional_text(value, field_name):
        if value is None:
            return ""
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be text")
        return value.strip()