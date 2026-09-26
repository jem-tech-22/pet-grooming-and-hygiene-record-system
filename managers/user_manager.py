import bcrypt

from database.database import DatabaseManager
from models.user import User


class UserManager:
	"""Authenticates users and enforces account-management permissions."""

	ROLES = ("Administrator", "Staff")
	MIN_PASSWORD_LENGTH = 8
	MAX_PASSWORD_BYTES = 72

	def __init__(self, database_manager=None):
		self.database_manager = database_manager or DatabaseManager()
		self.connection = self.database_manager.connection

	def has_users(self):
		cursor = self.connection.cursor()
		cursor.execute("SELECT EXISTS(SELECT 1 FROM users)")
		return bool(cursor.fetchone()[0])

	def create_initial_admin(self, full_name, username, password):
		full_name = self._required_text(full_name, "Full name")
		username = self._required_text(username, "Username")
		self._validate_password(password)
		password_hash = self._hash_password(password)
		cursor = self.connection.cursor()
		cursor.execute("BEGIN IMMEDIATE")
		try:
			cursor.execute("SELECT COUNT(*) FROM users")
			if cursor.fetchone()[0] != 0:
				raise PermissionError("The initial administrator has already been created.")
			cursor.execute(
				"INSERT INTO users (username, password, full_name, role) VALUES (?, ?, ?, ?)",
				(username, password_hash, full_name, "Administrator")
			)
			user_id = cursor.lastrowid
			self.connection.commit()
		except Exception:
			self.connection.rollback()
			raise
		return User(user_id, username, full_name, "Administrator")

	def authenticate(self, username, password):
		username = self._required_text(username, "Username")
		if not isinstance(password, str) or not password:
			return None
		cursor = self.connection.cursor()
		cursor.execute(
			"SELECT id, username, password, full_name, role FROM users "
			"WHERE username = ? COLLATE NOCASE",
			(username,)
		)
		row = cursor.fetchone()
		if (
			row is None or row[4] not in self.ROLES
			or not self._verify_password(password, row[2])
		):
			return None
		return User(row[0], row[1], row[3], row[4])

	def get_users(self, actor_id):
		self._require_administrator(actor_id)
		cursor = self.connection.cursor()
		cursor.execute("SELECT id, username, full_name, role FROM users ORDER BY full_name COLLATE NOCASE, id")
		return [User(row[0], row[1], row[2], row[3]) for row in cursor.fetchall()]

	def create_user(self, actor_id, full_name, username, password, role):
		full_name = self._required_text(full_name, "Full name")
		username = self._required_text(username, "Username")
		role = self._validate_role(role)
		self._validate_password(password)
		password_hash = self._hash_password(password)
		cursor = self.connection.cursor()
		cursor.execute("BEGIN IMMEDIATE")
		try:
			self._require_administrator(actor_id, cursor)
			self._ensure_username_available(cursor, username)
			cursor.execute(
				"INSERT INTO users (username, password, full_name, role) VALUES (?, ?, ?, ?)",
				(username, password_hash, full_name, role)
			)
			user_id = cursor.lastrowid
			self.connection.commit()
		except Exception:
			self.connection.rollback()
			raise
		return User(user_id, username, full_name, role)

	def update_user(self, actor_id, user_id, full_name, username, role):
		full_name = self._required_text(full_name, "Full name")
		username = self._required_text(username, "Username")
		role = self._validate_role(role)
		cursor = self.connection.cursor()
		cursor.execute("BEGIN IMMEDIATE")
		try:
			self._require_administrator(actor_id, cursor)
			cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
			current = cursor.fetchone()
			if current is None:
				raise ValueError("The selected user no longer exists.")
			if user_id == actor_id and role != current[0]:
				raise PermissionError("You cannot change your own administrator role.")
			self._ensure_username_available(cursor, username, user_id)
			if current[0] == "Administrator" and role != "Administrator":
				self._ensure_another_administrator(cursor, user_id)
			cursor.execute(
				"UPDATE users SET full_name = ?, username = ?, role = ? WHERE id = ?",
				(full_name, username, role, user_id)
			)
			self.connection.commit()
		except Exception:
			self.connection.rollback()
			raise
		return User(user_id, username, full_name, role)

	def change_password(self, actor_id, user_id, password):
		self._validate_password(password)
		password_hash = self._hash_password(password)
		cursor = self.connection.cursor()
		cursor.execute("BEGIN IMMEDIATE")
		try:
			self._require_administrator(actor_id, cursor)
			cursor.execute("UPDATE users SET password = ? WHERE id = ?", (password_hash, user_id))
			if cursor.rowcount == 0:
				raise ValueError("The selected user no longer exists.")
			self.connection.commit()
		except Exception:
			self.connection.rollback()
			raise

	def delete_user(self, actor_id, user_id):
		cursor = self.connection.cursor()
		cursor.execute("BEGIN IMMEDIATE")
		try:
			self._require_administrator(actor_id, cursor)
			if user_id == actor_id:
				raise PermissionError("You cannot delete your own active account.")
			cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
			current = cursor.fetchone()
			if current is None:
				raise ValueError("The selected user no longer exists.")
			if current[0] == "Administrator":
				self._ensure_another_administrator(cursor, user_id)
			cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
			self.connection.commit()
		except Exception:
			self.connection.rollback()
			raise

	def _require_administrator(self, actor_id, cursor=None):
		cursor = cursor or self.connection.cursor()
		cursor.execute("SELECT role FROM users WHERE id = ?", (actor_id,))
		row = cursor.fetchone()
		if row is None or row[0] != "Administrator":
			raise PermissionError("Administrator access is required for user management.")

	@staticmethod
	def _ensure_username_available(cursor, username, excluded_user_id=None):
		query = "SELECT 1 FROM users WHERE username = ? COLLATE NOCASE"
		parameters = [username]
		if excluded_user_id is not None:
			query += " AND id <> ?"
			parameters.append(excluded_user_id)
		cursor.execute(query, parameters)
		if cursor.fetchone() is not None:
			raise ValueError("That username is already in use.")

	@staticmethod
	def _ensure_another_administrator(cursor, excluded_user_id):
		cursor.execute(
			"SELECT COUNT(*) FROM users WHERE role = 'Administrator' AND id <> ?",
			(excluded_user_id,)
		)
		if cursor.fetchone()[0] == 0:
			raise PermissionError("The last administrator account cannot be removed or demoted.")

	@classmethod
	def _validate_password(cls, password):
		if not isinstance(password, str) or len(password) < cls.MIN_PASSWORD_LENGTH:
			raise ValueError("Password must contain at least 8 characters.")
		if len(password.encode("utf-8")) > cls.MAX_PASSWORD_BYTES:
			raise ValueError("Password must be no longer than 72 UTF-8 bytes.")

	@classmethod
	def _hash_password(cls, password):
		cls._validate_password(password)
		return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("ascii")

	@classmethod
	def _verify_password(cls, password, password_hash):
		try:
			return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("ascii"))
		except (AttributeError, UnicodeEncodeError, ValueError):
			return False

	@staticmethod
	def _required_text(value, field_name):
		if not isinstance(value, str) or not value.strip():
			raise ValueError(f"{field_name} cannot be empty.")
		return value.strip()

	@classmethod
	def _validate_role(cls, role):
		if role not in cls.ROLES:
			raise ValueError("Choose Administrator or Staff as the role.")
		return role

	def close(self):
		self.database_manager.close()