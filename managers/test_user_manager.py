import sqlite3
import unittest

from managers.user_manager import UserManager


class DatabaseStub:
	def __init__(self):
		self.connection = sqlite3.connect(":memory:")
		self.connection.execute("""
			CREATE TABLE users (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				username TEXT NOT NULL UNIQUE,
				password TEXT NOT NULL,
				full_name TEXT NOT NULL,
				role TEXT NOT NULL
			)
		""")
		self.connection.commit()

	def close(self):
		self.connection.close()


class UserManagerTests(unittest.TestCase):
	def setUp(self):
		self.database = DatabaseStub()
		self.manager = UserManager(self.database)
		self.admin = self.manager.create_initial_admin(
			"Admin Person", "admin", "secure-password"
		)

	def tearDown(self):
		self.database.close()

	def test_password_is_hashed_and_login_returns_credential_free_user(self):
		stored_password = self.database.connection.execute(
			"SELECT password FROM users WHERE id = ?", (self.admin.id,)
		).fetchone()[0]
		self.assertTrue(stored_password.startswith("$2"))
		self.assertNotEqual(stored_password, "secure-password")
		user = self.manager.authenticate("ADMIN", "secure-password")
		self.assertEqual(user.id, self.admin.id)
		self.assertFalse(hasattr(user, "password"))
		self.assertIsNone(self.manager.authenticate("admin", "incorrect"))

	def test_first_admin_can_only_be_created_once(self):
		with self.assertRaises(PermissionError):
			self.manager.create_initial_admin("Other Admin", "other", "other-password")

	def test_duplicate_usernames_are_case_insensitive(self):
		with self.assertRaisesRegex(ValueError, "already in use"):
			self.manager.create_user(
				self.admin.id, "Second Person", "ADMIN", "another-password", "Staff"
			)

	def test_staff_cannot_manage_users(self):
		staff = self.manager.create_user(
			self.admin.id, "Staff Person", "staff", "staff-password", "Staff"
		)
		with self.assertRaises(PermissionError):
			self.manager.create_user(
				staff.id, "Another Person", "another", "another-password", "Staff"
			)

	def test_last_administrator_cannot_be_demoted_or_deleted(self):
		with self.assertRaises(PermissionError):
			self.manager.update_user(
				self.admin.id, self.admin.id, "Admin Person", "admin", "Staff"
			)
		with self.assertRaises(PermissionError):
			self.manager.delete_user(self.admin.id, self.admin.id)
		users = self.manager.get_users(self.admin.id)
		self.assertEqual(len(users), 1)
		self.assertEqual(users[0].role, "Administrator")

	def test_password_changes_do_not_run_during_profile_updates(self):
		self.manager.update_user(
			self.admin.id, self.admin.id, "Updated Admin", "admin", "Administrator"
		)
		self.assertIsNotNone(self.manager.authenticate("admin", "secure-password"))
		self.manager.change_password(self.admin.id, self.admin.id, "updated-password")
		self.assertIsNone(self.manager.authenticate("admin", "secure-password"))
		self.assertIsNotNone(self.manager.authenticate("admin", "updated-password"))


if __name__ == "__main__":
	unittest.main()