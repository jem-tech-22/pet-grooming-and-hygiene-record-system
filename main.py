import customtkinter as ctk

from gui.dashboard import Dashboard
from gui.pet_management import PetManagement


class FurLogApp(ctk.CTk):
	"""Hosts the existing Dashboard and Pet Management screens."""

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
			"Pet Management": PetManagement(self, on_navigate=self.show_page)
		}
		for page in self.pages.values():
			page.grid(row=0, column=0, sticky="nsew")
		self.show_page("Dashboard")

	def show_page(self, page_name):
		page = self.pages.get(page_name)
		if page is None:
			return
		if page_name == "Dashboard":
			page.refresh_data()
		page.tkraise()
		self.title(f"FurLog - {page_name}")


if __name__ == "__main__":
	app = FurLogApp()
	app.mainloop()
