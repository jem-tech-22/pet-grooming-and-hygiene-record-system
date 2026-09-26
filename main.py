import customtkinter as ctk

from gui.dashboard import Dashboard
from gui.grooming_records import GroomingRecords
from gui.grooming_history import GroomingHistory
from gui.pet_management import PetManagement
from gui.reports import Reports


class FurLogApp(ctk.CTk):
	"""Hosts the existing Dashboard, Pet Management, and Grooming Records screens."""

	def __init__(self):
		ctk.set_appearance_mode("light")
		ctk.set_default_color_theme("green")
		super().__init__()
		self.title("FurLog")
		self.geometry("1180x800")
		self.minsize(900, 650)
		self.grid_rowconfigure(0, weight=1)
		self.grid_columnconfigure(0, weight=1)

		self.pages = {
			"Dashboard": Dashboard(self, on_navigate=self.show_page),
			"Pet Management": PetManagement(self, on_navigate=self.show_page),
			"Grooming Records": GroomingRecords(self, on_navigate=self.show_page),
			"Grooming History": GroomingHistory(self, on_navigate=self.show_page),
			"Reports": Reports(self, on_navigate=self.show_page)
		}
		for page in self.pages.values():
			page.grid(row=0, column=0, sticky="nsew")
		self.protocol("WM_DELETE_WINDOW", self.close_app)
		self.show_page("Dashboard")

	def show_page(self, page_name):
		page = self.pages.get(page_name)
		if page is None:
			return
		if page_name in (
			"Dashboard", "Grooming Records", "Grooming History", "Reports"
		):
			page.refresh_data()
		page.tkraise()
		self.title(f"FurLog - {page_name}")

	def close_app(self):
		for page in self.pages.values():
			manager = getattr(page, "pet_manager", None)
			if manager is None:
				manager = getattr(page, "grooming_manager", None)
			if manager is not None:
				database_manager = getattr(manager, "database_manager", None)
				if database_manager is not None:
					database_manager.close()
				elif hasattr(manager, "close"):
					manager.close()
		self.destroy()


if __name__ == "__main__":
	app = FurLogApp()
	app.mainloop()
