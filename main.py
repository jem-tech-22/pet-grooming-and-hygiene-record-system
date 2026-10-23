import customtkinter as ctk
from tkinter import messagebox

from database.database import DatabaseManager
from gui.dashboard import Dashboard
from gui.grooming_records import GroomingRecords
from gui.grooming_history import GroomingHistory
from gui.login import LoginScreen
from gui.pet_management import PetManagement
from gui.reports import Reports
from gui.user_management import UserManagement
from managers.user_manager import UserManager


class FurLogApp(ctk.CTk):
	"""Hosts FurLog authentication and the authorized application screens."""

	def __init__(self):
		ctk.set_appearance_mode("light")
		ctk.set_default_color_theme("green")
		super().__init__()
		self.title("FurLog")
		self.geometry("1180x800")
		self.minsize(900, 650)
		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(0, weight=1)
		self.user_manager = UserManager(DatabaseManager())
		self.current_user = None
		self.pages = {}
		self.page_factories = {}
		self._navigation_skeleton = None
		self._navigation_generation = 0
		self.show_login()
		self.protocol("WM_DELETE_WINDOW", self.close_app)

	def show_login(self):
		self.login_screen = LoginScreen(
			self, self.user_manager, self.start_session
		)
		self.login_screen.grid(row=0, column=0, sticky="nsew")
		self.title("FurLog - Login")

	def start_session(self, user):
		self.current_user = user
		self.login_screen.destroy()
		self.login_screen = None
		self.pages = {}
		self.page_factories = {
			"Dashboard": lambda: Dashboard(self, on_navigate=self.show_page),
			"Pet Management": lambda: PetManagement(self, on_navigate=self.show_page),
			"Grooming Records": lambda: GroomingRecords(
				self, on_navigate=self.show_page
			),
			"Grooming History": lambda: GroomingHistory(
				self, on_navigate=self.show_page
			),
			"Reports": lambda: Reports(self, on_navigate=self.show_page)
		}
		if user.role == "Administrator":
			self.page_factories["User Management"] = lambda: UserManagement(
				self, self.user_manager, on_navigate=self.show_page
			)
		self.show_page("Dashboard")

	def show_page(self, page_name):
		if page_name == "Logout":
			if self.current_user is not None:
				self.confirm_logout()
			return
		if self.current_user is None:
			return
		if page_name == "User Management" and self.current_user.role != "Administrator":
			messagebox.showwarning(
				"Access denied", "Administrator access is required.", parent=self
			)
			return
		page = self.pages.get(page_name)
		created = page is None
		if page is None:
			factory = self.page_factories.get(page_name)
			if factory is None:
				return
			self._navigation_generation += 1
			generation = self._navigation_generation
			self.title(f"FurLog - {page_name}")
			self._show_navigation_skeleton(page_name)
			self.after_idle(
				self._create_page_after_skeleton, page_name, factory, generation
			)
			return
		self._navigation_generation += 1
		generation = self._navigation_generation
		if self._navigation_skeleton is not None:
			self._hide_navigation_skeleton()
		page.tkraise()
		self.title(f"FurLog - {page_name}")
		self.after_idle(
			self._refresh_page_data, page_name, page, generation,
			not created or page_name in ("Dashboard", "Reports")
		)

	def _show_navigation_skeleton(self, page_name):
		self._hide_navigation_skeleton()
		colors = PetManagement.COLORS
		skeleton = ctk.CTkFrame(
			self, fg_color=colors["canvas"], corner_radius=0
		)
		skeleton.grid_columnconfigure(1, weight=1)
		skeleton.grid_rowconfigure(0, weight=1)

		sidebar = ctk.CTkFrame(
			skeleton, width=224, corner_radius=0,
			fg_color=colors["sidebar"]
		)
		sidebar.grid(row=0, column=0, sticky="nsew")
		sidebar.grid_propagate(False)

		content = ctk.CTkFrame(skeleton, fg_color="transparent")
		content.grid(
			row=0, column=1, padx=(30, 34), pady=(30, 28), sticky="nsew"
		)
		content.grid_columnconfigure(0, weight=1)
		self._add_skeleton_block(
			content, width=108, height=10, color=colors["line"],
			row=0, column=0, sticky="w", pady=(2, 12)
		)
		self._add_skeleton_block(
			content, width=280, height=28, color=colors["soft_gray"],
			row=1, column=0, sticky="w", pady=(0, 10)
		)
		self._add_skeleton_block(
			content, width=390, height=12, color=colors["line"],
			row=2, column=0, sticky="w", pady=(0, 28)
		)

		cards = ctk.CTkFrame(content, fg_color="transparent")
		cards.grid(row=3, column=0, pady=(0, 20), sticky="ew")
		for column in range(4):
			cards.grid_columnconfigure(column, weight=1, uniform="skeleton_cards")
			card = ctk.CTkFrame(
				cards, fg_color=colors["surface"], corner_radius=12,
				border_width=1, border_color=colors["line"]
			)
			card.grid(row=0, column=column, padx=(0, 10), sticky="ew")
			self._add_skeleton_block(
				card, width=74, height=10, color=colors["line"],
				padx=14, pady=(16, 10)
			)
			self._add_skeleton_block(
				card, width=106, height=22, color=colors["soft_gray"],
				padx=14, pady=(0, 16)
			)

		panel = ctk.CTkFrame(
			content, fg_color=colors["canvas"], corner_radius=12
		)
		panel.grid(row=4, column=0, sticky="nsew")
		panel.grid_columnconfigure(0, weight=1)
		self._add_skeleton_block(
			panel, width=200, height=16, color=colors["soft_gray"],
			padx=18, pady=(18, 20)
		)
		for row in range(5):
			self._add_skeleton_block(
				panel, width=570 if row % 2 == 0 else 430, height=12,
				color=colors["line"], padx=18, pady=(0, 16)
			)

		skeleton.place(relx=0, rely=0, relwidth=1, relheight=1)
		skeleton.lift()
		self._navigation_skeleton = skeleton
		self.update_idletasks()

	def _add_skeleton_block(
		self, parent, width, height, color, row=None, column=0,
		padx=0, pady=0, sticky=None
	):
		block = ctk.CTkFrame(
			parent, width=width, height=height, fg_color=color,
			corner_radius=max(4, height // 2)
		)
		if row is None:
			block.pack(anchor="w", padx=padx, pady=pady)
		else:
			block.grid(row=row, column=column, padx=padx, pady=pady, sticky=sticky)
		block.pack_propagate(False)
		block.grid_propagate(False)
		return block

	def _create_page_after_skeleton(self, page_name, factory, generation):
		if generation != self._navigation_generation or self.current_user is None:
			return
		try:
			page = factory()
			self.pages[page_name] = page
			page.grid(row=0, column=0, sticky="nsew")
			self._navigation_skeleton.lift()
			self._refresh_page_data(
				page_name, page, generation,
				page_name in ("Dashboard", "Reports")
			)
			self.update_idletasks()
			self._hide_navigation_skeleton()
			page.tkraise()
		except Exception:
			self._hide_navigation_skeleton()
			raise

	def _hide_navigation_skeleton(self):
		if self._navigation_skeleton is not None:
			self._navigation_skeleton.destroy()
			self._navigation_skeleton = None

	def _refresh_page_data(self, page_name, page, generation, refresh_page=True):
		if generation != self._navigation_generation:
			return
		if not refresh_page:
			return
		if page_name in (
			"Dashboard", "Pet Management", "Grooming Records",
			"Grooming History", "Reports"
		):
			page.refresh_data()
		elif page_name == "User Management":
			page.refresh_users()

	def confirm_logout(self):
		dialog = ctk.CTkToplevel(self)
		dialog.title("Confirm Logout")
		dialog.geometry("360x170")
		dialog.resizable(False, False)
		dialog.transient(self)
		dialog.grab_set()
		dialog.grid_columnconfigure(0, weight=1)

		ctk.CTkLabel(
			dialog, text="Are you sure you want to log out?",
			text_color=PetManagement.COLORS["ink"],
			font=ctk.CTkFont(family=PetManagement.FONT_FAMILY, size=13, weight="bold")
		).grid(row=0, column=0, padx=24, pady=(30, 22))

		buttons = ctk.CTkFrame(dialog, fg_color="transparent")
		buttons.grid(row=1, column=0, padx=24, pady=(0, 22), sticky="e")
		ctk.CTkButton(
			buttons, text="Cancel", command=dialog.destroy,
			width=96, height=34, corner_radius=8,
			fg_color=PetManagement.COLORS["soft_gray"],
			hover_color="#E1E9E3", text_color=PetManagement.COLORS["ink"],
			font=ctk.CTkFont(family=PetManagement.FONT_FAMILY, size=11, weight="bold")
		).grid(row=0, column=0, padx=(0, 8))
		ctk.CTkButton(
			buttons, text="Yes", command=lambda: self.confirmed_logout(dialog),
			width=96, height=34, corner_radius=8,
			fg_color=PetManagement.COLORS["primary"],
			hover_color=PetManagement.COLORS["primary_hover"], text_color="#FFFFFF",
			font=ctk.CTkFont(family=PetManagement.FONT_FAMILY, size=11, weight="bold")
		).grid(row=0, column=1)
		dialog.bind("<Escape>", lambda event: dialog.destroy())
		dialog.update_idletasks()
		dialog.geometry(f"+{self.winfo_rootx() + 120}+{self.winfo_rooty() + 120}")

	def confirmed_logout(self, dialog):
		dialog.grab_release()
		dialog.destroy()
		self.logout()

	def logout(self):
		self._navigation_generation += 1
		self._hide_navigation_skeleton()
		self._destroy_pages()
		self.current_user = None
		self.page_factories = {}
		self.show_login()

	def _destroy_pages(self):
		closed_database_managers = set()
		for page in self.pages.values():
			database_managers = getattr(page, "database_managers", None)
			if database_managers is None:
				manager = getattr(page, "pet_manager", None)
				if manager is None:
					manager = getattr(page, "grooming_manager", None)
				database_manager = getattr(manager, "database_manager", None)
				database_managers = [database_manager] if database_manager else []
			for database_manager in database_managers:
				if id(database_manager) not in closed_database_managers:
					database_manager.close()
					closed_database_managers.add(id(database_manager))
			page.destroy()
		self.pages = {}

	def close_app(self):
		self._navigation_generation += 1
		self._destroy_pages()
		self.user_manager.close()
		self.destroy()


if __name__ == "__main__":
	app = FurLogApp()
	app.mainloop()
