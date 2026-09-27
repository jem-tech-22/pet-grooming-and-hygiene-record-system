from tkinter import messagebox

import customtkinter as ctk

from gui.pet_management import PetManagement


class LoginScreen(ctk.CTkFrame):
	"""Log into FurLog or securely create its first administrator account."""

	COLORS = PetManagement.COLORS
	FONT_FAMILY = PetManagement.FONT_FAMILY

	def __init__(self, master, user_manager, on_authenticated):
		super().__init__(master, fg_color=self.COLORS["canvas"])
		self.user_manager = user_manager
		self.on_authenticated = on_authenticated
		self.setup_mode = not self.user_manager.has_users()
		self.create_widgets()

	def font(self, size, weight="normal"):
		return ctk.CTkFont(family=self.FONT_FAMILY, size=size, weight=weight)

	def create_widgets(self):
		self.grid_columnconfigure(0, weight=1)
		self.grid_rowconfigure(0, weight=1)
		card = ctk.CTkFrame(
			self, width=440, height=560 if self.setup_mode else 360,
			fg_color=self.COLORS["surface"], border_width=1,
			border_color=self.COLORS["line"], corner_radius=12
		)
		card.grid(row=0, column=0, padx=24, pady=24)
		card.grid_propagate(False)
		card.grid_columnconfigure(0, weight=1)

		title = "Create Administrator" if self.setup_mode else "Welcome back"
		description = (
			"Set up the first account to secure this FurLog installation."
			if self.setup_mode else "Sign in to continue to FurLog."
		)
		ctk.CTkLabel(
			card, text=title, text_color=self.COLORS["ink"],
			font=self.font(21, "bold"), anchor="center", justify="center"
		).grid(row=0, column=0, padx=30, pady=(34, 0), sticky="ew")
		ctk.CTkLabel(
			card, text=description, text_color=self.COLORS["muted"],
			font=self.font(11), wraplength=370, anchor="center", justify="center"
		).grid(row=1, column=0, padx=30, pady=(5, 18), sticky="ew")

		row = 2
		if self.setup_mode:
			self.full_name_entry = self.create_field(card, "Full Name", row)
			row += 1
		self.username_entry = self.create_field(card, "Username", row)
		row += 1
		self.password_entry = self.create_field(card, "Password", row, secret=True)
		row += 1
		if self.setup_mode:
			self.confirm_entry = self.create_field(card, "Confirm Password", row, secret=True)
			row += 1

		button_text = "Create Administrator" if self.setup_mode else "Log In"
		ctk.CTkButton(
			card, text=button_text, command=self.submit, height=38,
			corner_radius=8, fg_color=self.COLORS["primary"],
			hover_color=self.COLORS["primary_hover"], text_color="#FFFFFF",
			font=self.font(12, "bold")
		).grid(row=row, column=0, padx=30, pady=(16, 30), sticky="ew")
		self.username_entry.bind("<Return>", lambda event: self.password_entry.focus_set())
		self.password_entry.bind("<Return>", lambda event: self.submit())
		if self.setup_mode:
			self.confirm_entry.bind("<Return>", lambda event: self.submit())

	def create_field(self, parent, label, row, secret=False):
		field = ctk.CTkFrame(parent, fg_color="transparent")
		field.grid(row=row, column=0, padx=30, pady=(0, 10), sticky="ew")
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

	def submit(self):
		try:
			if self.setup_mode:
				password = self.password_entry.get()
				if password != self.confirm_entry.get():
					messagebox.showwarning(
						"Passwords do not match", "Enter the same password in both fields.",
						parent=self
					)
					return
				user = self.user_manager.create_initial_admin(
					self.full_name_entry.get(), self.username_entry.get(), password
				)
			else:
				user = self.user_manager.authenticate(
					self.username_entry.get(), self.password_entry.get()
				)
				if user is None:
					messagebox.showerror(
						"Login failed", "The username or password is incorrect.", parent=self
					)
					self.password_entry.delete(0, "end")
					return
		except (ValueError, PermissionError) as error:
			messagebox.showwarning("Account setup failed", str(error), parent=self)
			return
		except Exception as error:
			messagebox.showerror("Login failed", str(error), parent=self)
			return
		self.password_entry.delete(0, "end")
		self.on_authenticated(user)