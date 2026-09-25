from datetime import date


class GroomingRecord:
    """Represents one grooming or hygiene activity for a pet."""

    def __init__(
        self,
        id=None,
        pet_id=None,
        activity="",
        grooming_date=None,
        notes="",
        created_by=None
    ):
        self.id = id
        self.pet_id = pet_id
        self.activity = activity
        self.grooming_date = grooming_date or date.today().isoformat()
        self.notes = notes
        self.created_by = created_by

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def pet_id(self):
        return self._pet_id

    @pet_id.setter
    def pet_id(self, value):
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Pet ID must be a positive whole number")
        self._pet_id = value

    @property
    def activity(self):
        return self._activity

    @activity.setter
    def activity(self, value):
        self._activity = self._require_text(value, "Activity")

    @property
    def grooming_date(self):
        return self._grooming_date

    @grooming_date.setter
    def grooming_date(self, value):
        self._grooming_date = self._require_text(value, "Grooming date")

    @property
    def notes(self):
        return self._notes

    @notes.setter
    def notes(self, value):
        if value is None:
            self._notes = ""
        elif isinstance(value, str):
            self._notes = value.strip()
        else:
            raise ValueError("Notes must be text")

    @property
    def created_by(self):
        return self._created_by

    @created_by.setter
    def created_by(self, value):
        if value is not None and (not isinstance(value, int) or value <= 0):
            raise ValueError("Created-by ID must be a positive whole number")
        self._created_by = value

    @staticmethod
    def _require_text(value, field_name):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} cannot be empty")
        return value.strip()