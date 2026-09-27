import customtkinter as ctk
from tkinter import messagebox

from gui.pet_management import PetManagement
from managers.user_manager import UserManager


class UserManagement(ctk.CTkFrame):
	"""Administrator-only account management; credentials are never displayed."""

	COLORS = PetManagement.COLORS
	FONT_FAMILY = PetManagement.FONT_FAMILY
	NAVIGATION_ITEMS = PetManagement.NAVIGATION_ITEMS
	ROUTABLE_NAVIGATION_ITEMS = PetManagement.ROUTABLE_NAVIGATION_ITEMS
	font = PetManagement.font
	create_nav_button = PetManagement.create_nav_button
	get_navigation_items = PetManagement.get_navigation_items
	get_navigation_command = PetManagement.get_navigation_command
	create_action_button = PetManagement.create_action_button

	ROLES = UserManager.ROLES
	TABLE_COLUMNS = (("Full Name", 34), ("Username", 33), ("Role", 20))

	def __init__(self, master, user_manager, on_navigate=None):
		super().__init__(master, fg_color=self.COLORS["canvas"])
		self.user_manager = user_manager
		self.on_navigate = on_navigate
		self.selected_user_id = None
		self.user_rows = {}
		self.create_widgets()
		current_user = getattr(self.winfo_toplevel(), "current_user", None)
		if current_user is not None and current_user.role == "Administrator":
			self.refresh_users()

	def actor_id(self):
		current_user = getattr(self.winfo_toplevel(), "current_user", None)
		return current_user.id if current_user is not None else None

	def create_widgets(self):
		self.grid_columnconfigure(0, weight=0, minsize=224)
		self.grid_columnconfigure(1, weight=1)
		self.grid_rowconfigure(0, weight=1)
		self.create_sidebar()
		self.create_content()

	def create_sidebar(self):
		sidebar = ctk.CTkFrame(
			self, width=224, corner_radius=0, fg_color=self.COLORS["sidebar"]
		)
		sidebar.grid(row=0, column=0, sticky="nsew")
		sidebar.grid_propagate(False)
		sidebar.grid_columnconfigure(0, weight=1)
		brand = ctk.CTkFrame(sidebar, fg_color="transparent")
		brand.grid(row=0, column=0, padx=24, pady=(28, 40), sticky="w")
		ctk.CTkLabel(
			brand, text="F", width=38, height=38, corner_radius=12,
			fg_color=self.COLORS["primary"], text_color="#FFFFFF",
			font=self.font(22, "bold")
		).grid(row=0, column=0, rowspan=2, padx=(0, 10))
		ctk.CTkLabel(
			brand, text="FurLog", text_color="#FFFFFF", font=self.font(21, "bold")
		).grid(row=0, column=1, sticky="sw")
		ctk.CTkLabel(
			brand, text="PET CARE RECORDS",
			text_color=self.COLORS["sidebar_muted"], font=self.font(9, "bold")
		).grid(row=1, column=1, sticky="nw")
		navigation_items = self.get_navigation_items()
		logout_row = len(navigation_items) + 1
		sidebar.grid_rowconfigure(logout_row - 1, weight=1)
		for row, label in enumerate(
			(item for item in navigation_items if item != "Logout"), start=1
		):
			self.create_nav_button(
				sidebar, label, label == "User Management", row,
				self.get_navigation_command(label)
			)
		self.create_nav_button(
			sidebar, "Logout", False, logout_row,
			self.get_navigation_command("Logout")
		)

	def create_content(self):
		content = ctk.CTkScrollableFrame(
			self, fg_color="transparent",
			scrollbar_button_color=self.COLORS["line"],
			scrollbar_button_hover_color="#B9CFC1"
		)
		content.grid(row=0, column=1, padx=(30, 34), pady=(26, 28), sticky="nsew")
		content.grid_columnconfigure(0, weight=1)
		content.grid_rowconfigure(2, weight=1)
		header = ctk.CTkFrame(content, fg_color="transparent")
		header.grid(row=0, column=0, pady=(0, 25), sticky="ew")
		header.grid_columnconfigure(0, weight=1)
		ctk.CTkLabel(
			header, text="ADMINISTRATION", text_color=self.COLORS["primary"],
			font=self.font(10, "bold")
		).grid(row=0, column=0, sticky="w")
		ctk.CTkLabel(
			header, text="User Management", text_color=self.COLORS["ink"],
			font=self.font(28, "bold")
		).grid(row=1, column=0, pady=(3, 0), sticky="w")
		ctk.CTkLabel(
			header, text="Manage FurLog accounts and access roles.",
			text_color=self.COLORS["muted"], font=self.font(12)
		).grid(row=2, column=0, pady=(3, 0), sticky="w")
		self.create_user_form(content)
		self.create_user_table(content)

	def create_user_form(self, parent):
		card = ctk.CTkFrame(
			parent, fg_color=self.COLORS["surface"], border_width=1,
			border_color=self.COLORS["line"], corner_radius=12
		)
		card.grid(row=1, column=0, pady=(0, 18), sticky="ew")
		card.grid_columnconfigure(1, weight=1)
		card.grid_columnconfigure(3, weight=1)
		ctk.CTkLabel(
			card, text="Account details", text_color=self.COLORS["ink"],
			font=self.font(15, "bold")
		).grid(row=0, column=0, columnspan=4, padx=18, pady=(16, 4), sticky="w")
		ctk.CTkLabel(
			card,
			text="Password is required only when adding a user; use Change Password to reset one.",
			text_color=self.COLORS["muted"], font=self.font(10)
		).grid(row=1, column=0, columnspan=4, padx=18, pady=(0, 10), sticky="w")

		self.full_name_entry = self.create_entry(card, "Full Name", 2, 0)
		self.username_entry = self.create_entry(card, "Username", 2, 2)
		self.password_entry = self.create_entry(card, "Password", 3, 0, secret=True)
		self.confirm_entry = self.create_entry(card, "Confirm Password", 3, 2, secret=True)
		role_field = ctk.CTkFrame(card, fg_color="transparent")
		role_field.grid(row=4, column=0, columnspan=2, padx=(18, 8), pady=6, sticky="ew")
		role_field.grid_columnconfigure(0, weight=1)
		ctk.CTkLabel(
			role_field, text="Role", text_color=self.COLORS["ink"],
			font=self.font(10, "bold")
		).grid(row=0, column=0, pady=(0, 4), sticky="w")
		self.role_menu = ctk.CTkOptionMenu(
			role_field, values=list(self.ROLES), height=36, corner_radius=8,
			fg_color=self.COLORS["soft_gray"], button_color=self.COLORS["primary"],
			button_hover_color=self.COLORS["primary_hover"],
			text_color=self.COLORS["ink"], font=self.font(10),
			dropdown_font=self.font(10), anchor="w"
		)
		self.role_menu.grid(row=1, column=0, sticky="ew")
		self.role_menu.set("Staff")

		actions = ctk.CTkFrame(card, fg_color="transparent")
		actions.grid(row=5, column=0, columnspan=4, padx=18, pady=(12, 17), sticky="w")
		self.create_action_button(actions, "Add User", self.add_user, 0, True)
		self.create_action_button(actions, "Update", self.update_user, 1)
		self.create_action_button(actions, "Change Password", self.open_password_dialog, 2)
		self.create_action_button(actions, "Clear", self.clear_form, 3)
		self.create_action_button(actions, "Delete", self.delete_user, 4, danger=True)

	def create_entry(self, parent, label, row, column, secret=False):
		field = ctk.CTkFrame(parent, fg_color="transparent")
		field.grid(row=row, column=column, padx=(18, 8), pady=6, sticky="ew")
		field.grid_columnconfigure(0, weight=1)
		ctk.CTkLabel(
			field, text=label, text_color=self.COLORS["ink"],
			font=self.font(10, "bold")
		).grid(row=0, column=0, pady=(0, 4), sticky="w")
		entry = ctk.CTkEntry(
			field, height=36, corner_radius=8, border_width=1,
			border_color=self.COLORS["line"], fg_color="#FBFCFB",
			text_color=self.COLORS["ink"], font=self.font(11),
			show="*" if secret else ""
		)
		entry.grid(row=1, column=0, sticky="ew")
		return entry

	def create_user_table(self, parent):
		card = ctk.CTkFrame(
			parent, fg_color=self.COLORS["surface"], border_width=1,
			border_color=self.COLORS["line"], corner_radius=12
		)
		card.grid(row=2, column=0, sticky="nsew")
		card.configure(height=330)
		card.grid_propagate(False)
		card.grid_rowconfigure(1, weight=1)
		card.grid_columnconfigure(0, weight=1)
		header = ctk.CTkFrame(card, fg_color="transparent")
		header.grid(row=0, column=0, padx=18, pady=(16, 10), sticky="ew")
		header.grid_columnconfigure(0, weight=1)
		ctk.CTkLabel(
			header, text="Registered users", text_color=self.COLORS["ink"],
			font=self.font(15, "bold")
		).grid(row=0, column=0, sticky="w")
		self.count_label = ctk.CTkLabel(
			header, text="0 users", text_color=self.COLORS["muted"], font=self.font(10)
		)
		self.count_label.grid(row=1, column=0, pady=(2, 0), sticky="w")
		self.users_scroll = ctk.CTkScrollableFrame(
			card, fg_color=self.COLORS["surface"], corner_radius=0,
			scrollbar_button_color=self.COLORS["line"],
			scrollbar_button_hover_color="#B9CFC1"
		)
		self.users_scroll.grid(row=1, column=0, padx=18, pady=(0, 18), sticky="nsew")
		for column, (_, weight) in enumerate(self.TABLE_COLUMNS):
			self.users_scroll.grid_columnconfigure(column, weight=weight)
		for column, (heading, _) in enumerate(self.TABLE_COLUMNS):
			ctk.CTkLabel(
				self.users_scroll, text=heading.upper(),
				text_color=self.COLORS["muted"], fg_color=self.COLORS["soft_gray"],
				border_width=1, border_color=self.COLORS["line"],
				font=self.font(9, "bold"), anchor="center", height=42,
				corner_radius=0
			).grid(row=0, column=column, padx=(0, 1), pady=(0, 5), sticky="nsew")
		self.empty_label = ctk.CTkLabel(
			self.users_scroll, text="No user accounts are registered.",
			text_color=self.COLORS["muted"], font=self.font(11, "bold")
		)

	def refresh_users(self):
		try:
			users = self.user_manager.get_users(self.actor_id())
		except Exception as error:
			messagebox.showerror("Load users failed", str(error), parent=self)
			return
		self.render_users(users)

	def render_users(self, users):
		for row_widgets in self.user_rows.values():
			for widget in row_widgets:
				widget.destroy()
		self.user_rows.clear()
		self.count_label.configure(text=f"{len(users)} user" + ("s" if len(users) != 1 else ""))
		if not users:
			self.empty_label.grid(
				row=1, column=0, columnspan=len(self.TABLE_COLUMNS), padx=20, pady=36
			)
			return
		self.empty_label.grid_remove()
		for row_number, user in enumerate(users, start=1):
			row_color = self.COLORS["surface"] if row_number % 2 else "#FAFCFA"
			row_widgets = []
			for column, value in enumerate((user.full_name, user.username, user.role)):
				label = ctk.CTkLabel(
					self.users_scroll, text=value,
					text_color=self.COLORS["ink"], fg_color=row_color,
					border_width=1, border_color=self.COLORS["line"],
					font=self.font(11), anchor="center", height=46, corner_radius=0
				)
				label.grid(
					row=row_number, column=column,
					padx=(0, 1), pady=(0, 4), sticky="nsew"
				)
				label.bind(
					"<Button-1>", lambda event, user_id=user.id: self.select_user(user_id)
				)
				row_widgets.append(label)
			self.user_rows[user.id] = row_widgets

	def select_user(self, user_id):
		try:
			users = self.user_manager.get_users(self.actor_id())
		except Exception as error:
			messagebox.showerror("Load user failed", str(error), parent=self)
			return
		user = next((item for item in users if item.id == user_id), None)
		if user is None:
			messagebox.showerror("User not found", "That account no longer exists.", parent=self)
			self.refresh_users()
			return
		self.selected_user_id = user.id
		self.set_entry(self.full_name_entry, user.full_name)
		self.set_entry(self.username_entry, user.username)
		self.password_entry.delete(0, "end")
		self.confirm_entry.delete(0, "end")
		self.password_entry.configure(state="disabled")
		self.confirm_entry.configure(state="disabled")
		self.role_menu.set(user.role)
		for row_id, widgets in self.user_rows.items():
			color = self.COLORS["primary"] if row_id == user_id else self.COLORS["line"]
			for widget in widgets:
				widget.configure(border_color=color)

	@staticmethod
	def set_entry(entry, value):
		entry.configure(state="normal")
		entry.delete(0, "end")
		entry.insert(0, value)

	def add_user(self):
		if self.selected_user_id is not None:
			messagebox.showwarning(
				"Clear selection", "Clear the selected account before adding a new user.",
				parent=self
			)
			return
		password = self.password_entry.get()
		if password != self.confirm_entry.get():
			messagebox.showwarning(
				"Passwords do not match", "Enter the same password in both fields.", parent=self
			)
			return
		try:
			self.user_manager.create_user(
				self.actor_id(), self.full_name_entry.get(), self.username_entry.get(),
				password, self.role_menu.get()
			)
			self.refresh_users()
			self.clear_form()
		except Exception as error:
			messagebox.showerror("Add user failed", str(error), parent=self)

	def update_user(self):
		if self.selected_user_id is None:
			messagebox.showwarning("Select a user", "Select an account to update.", parent=self)
			return
		try:
			self.user_manager.update_user(
				self.actor_id(), self.selected_user_id,
				self.full_name_entry.get(), self.username_entry.get(), self.role_menu.get()
			)
			self.refresh_users()
			self.clear_form()
		except Exception as error:
			messagebox.showerror("Update user failed", str(error), parent=self)

	def open_password_dialog(self):
		if self.selected_user_id is None:
			messagebox.showwarning(
				"Select a user", "Select an account before changing its password.", parent=self
			)
			return
		dialog = ctk.CTkToplevel(self)
		dialog.title("Change user password")
		dialog.geometry("390x250")
		dialog.resizable(False, False)
		dialog.configure(fg_color=self.COLORS["canvas"])
		dialog.transient(self.winfo_toplevel())
		dialog.grab_set()
		card = ctk.CTkFrame(
			dialog, fg_color=self.COLORS["surface"], border_width=1,
			border_color=self.COLORS["line"], corner_radius=12
		)
		card.pack(fill="both", expand=True, padx=14, pady=14)
		card.grid_columnconfigure(0, weight=1)
		password_entry = self.create_dialog_password_field(card, "New password", 0)
		confirm_entry = self.create_dialog_password_field(card, "Confirm password", 1)

		def save_password():
			if password_entry.get() != confirm_entry.get():
				messagebox.showwarning(
					"Passwords do not match", "Enter the same password in both fields.",
					parent=dialog
				)
				return
			try:
				self.user_manager.change_password(
					self.actor_id(), self.selected_user_id, password_entry.get()
				)
			except Exception as error:
				messagebox.showerror("Change password failed", str(error), parent=dialog)
				return
			dialog.grab_release()
			dialog.destroy()
			messagebox.showinfo("Password changed", "The account password was updated.", parent=self)

		ctk.CTkButton(
			card, text="Save Password", command=save_password, height=36,
			corner_radius=8, fg_color=self.COLORS["primary"],
			hover_color=self.COLORS["primary_hover"], text_color="#FFFFFF",
			font=self.font(11, "bold")
		).grid(row=2, column=0, padx=16, pady=(8, 14), sticky="ew")
		dialog.update_idletasks()
		dialog.geometry(
			f"+{self.winfo_rootx() + 80}+{self.winfo_rooty() + 80}"
		)

	def create_dialog_password_field(self, parent, label, row):
		field = ctk.CTkFrame(parent, fg_color="transparent")
		field.grid(row=row, column=0, padx=16, pady=(12 if row == 0 else 4, 0), sticky="ew")
		field.grid_columnconfigure(0, weight=1)
		ctk.CTkLabel(
			field, text=label, text_color=self.COLORS["ink"],
			font=self.font(10, "bold")
		).grid(row=0, column=0, pady=(0, 4), sticky="w")
		entry = ctk.CTkEntry(
			field, height=34, corner_radius=8, border_width=1,
			border_color=self.COLORS["line"], fg_color="#FBFCFB",
			text_color=self.COLORS["ink"], font=self.font(11), show="*"
		)
		entry.grid(row=1, column=0, sticky="ew")
		return entry

	def delete_user(self):
		if self.selected_user_id is None:
			messagebox.showwarning("Select a user", "Select an account to delete.", parent=self)
			return
		if not messagebox.askyesno(
			"Delete user", "Delete the selected account? This cannot be undone.", parent=self
		):
			return
		try:
			self.user_manager.delete_user(self.actor_id(), self.selected_user_id)
			self.refresh_users()
			self.clear_form()
		except Exception as error:
			messagebox.showerror("Delete user failed", str(error), parent=self)

	def clear_form(self):
		self.selected_user_id = None
		for entry in (self.full_name_entry, self.username_entry):
			entry.configure(state="normal")
			entry.delete(0, "end")
		for entry in (self.password_entry, self.confirm_entry):
			entry.configure(state="normal")
			entry.delete(0, "end")
		self.role_menu.set("Staff")
		for widgets in self.user_rows.values():
			for widget in widgets:
				widget.configure(border_color=self.COLORS["line"])