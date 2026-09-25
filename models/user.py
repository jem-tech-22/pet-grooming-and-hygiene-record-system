class User:
    """Represents a FurLog application user."""

    def __init__(self, id=None, username="", password="", full_name="", role=""):
        self.id = id
        self.username = username
        self.password = password
        self.full_name = full_name
        self.role = role

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = self._require_text(value, "Username")

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = self._require_text(value, "Password")

    @property
    def full_name(self):
        return self._full_name

    @full_name.setter
    def full_name(self, value):
        self._full_name = self._require_text(value, "Full name")

    @property
    def role(self):
        return self._role

    @role.setter
    def role(self, value):
        self._role = self._require_text(value, "Role")

    @staticmethod
    def _require_text(value, field_name):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} cannot be empty")
        return value.strip()