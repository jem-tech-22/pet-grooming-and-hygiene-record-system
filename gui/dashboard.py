import sqlite3

import customtkinter as ctk

from database.database import DatabaseManager
from gui.pet_management import PetManagement


class Dashboard(ctk.CTkFrame):
	"""Sample-data Dashboard styled to match Pet Management."""

	COLORS = PetManagement.COLORS
	FONT_FAMILY = PetManagement.FONT_FAMILY
	NAVIGATION_ITEMS = PetManagement.NAVIGATION_ITEMS
	font = PetManagement.font
	create_nav_button = PetManagement.create_nav_button

	def __init__(self, master, on_navigate=None):
		super().__init__(master, fg_color=self.COLORS["canvas"])
		self.on_navigate = on_navigate
		self.summary_value_labels = {}
		self.pet_summary_value_labels = {}
		self.activity_table = None
		self.create_widgets()

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
		sidebar.grid_rowconfigure(8, weight=1)

		brand_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
		brand_frame.grid(row=0, column=0, padx=24, pady=(28, 40), sticky="w")
		ctk.CTkLabel(
			brand_frame, text="F", width=38, height=38, corner_radius=12,
			fg_color=self.COLORS["primary"], text_color="#FFFFFF",
			font=self.font(22, "bold")
		).grid(row=0, column=0, rowspan=2, padx=(0, 10))
		ctk.CTkLabel(
			brand_frame, text="FurLog", text_color="#FFFFFF",
			font=self.font(21, "bold")
		).grid(row=0, column=1, sticky="sw")
		ctk.CTkLabel(
			brand_frame, text="PET CARE RECORDS",
			text_color=self.COLORS["sidebar_muted"], font=self.font(9, "bold")
		).grid(row=1, column=1, sticky="nw")

		for row, label in enumerate(self.NAVIGATION_ITEMS, start=1):
			command = None
			if self.on_navigate and label in (
				"Dashboard", "Pet Management", "Grooming Records"
			):
				command = lambda target=label: self.on_navigate(target)
			self.create_nav_button(sidebar, label, label == "Dashboard", row, command)

	def create_content(self):
		content = ctk.CTkScrollableFrame(
			self,
			fg_color="transparent",
			scrollbar_button_color=self.COLORS["line"],
			scrollbar_button_hover_color="#B9CFC1"
		)
		content.grid(row=0, column=1, padx=(30, 34), pady=(26, 28), sticky="nsew")
		content.grid_columnconfigure(0, weight=1)

		header = ctk.CTkFrame(content, fg_color="transparent")
		header.grid(row=0, column=0, pady=(0, 25), sticky="ew")
		header.grid_columnconfigure(0, weight=1)
		ctk.CTkLabel(
			header, text="FURLOG OVERVIEW", text_color=self.COLORS["primary"],
			font=self.font(10, "bold")
		).grid(row=0, column=0, sticky="w")
		ctk.CTkLabel(
			header, text="Dashboard", text_color=self.COLORS["ink"],
			font=self.font(28, "bold")
		).grid(row=1, column=0, pady=(3, 0), sticky="w")
		ctk.CTkLabel(
			header, text="A quick overview of FurLog activity.",
			text_color=self.COLORS["muted"], font=self.font(12)
		).grid(row=2, column=0, pady=(3, 0), sticky="w")

		self.create_summary_cards(content)
		self.create_activity_and_pet_summary(content)

	def create_summary_cards(self, parent):
		cards = ctk.CTkFrame(parent, fg_color="transparent")
		cards.grid(row=1, column=0, pady=(0, 20), sticky="ew")
		for column in range(4):
			cards.grid_columnconfigure(column, weight=1, uniform="dashboard_cards")

		summary_data = (
			("total_pets", "TOTAL PETS", "0", "Registered profiles"),
			("grooming_records", "GROOMING RECORDS", "0", "Recorded activities"),
			("foods", "FOODS", "0", "Pets with food information"),
			("vitamins", "VITAMINS", "0", "Pets with vitamin information")
		)
		for column, (key, title, value, description) in enumerate(summary_data):
			card = ctk.CTkFrame(
				cards, fg_color=self.COLORS["surface"], border_width=1,
				border_color=self.COLORS["line"], corner_radius=12
			)
			card.grid(
				row=0, column=column,
				padx=(0 if column == 0 else 8, 8), sticky="ew"
			)
			card.grid_columnconfigure(0, weight=1)
			ctk.CTkLabel(
				card, text=title, text_color=self.COLORS["muted"],
				font=self.font(10, "bold")
			).grid(row=0, column=0, padx=16, pady=(14, 2), sticky="w")
			value_label = ctk.CTkLabel(
				card, text=value, text_color=self.COLORS["ink"],
				font=self.font(25, "bold")
			)
			value_label.grid(row=1, column=0, padx=16, sticky="w")
			self.summary_value_labels[key] = value_label
			ctk.CTkLabel(
				card, text=description, text_color=self.COLORS["muted"],
				font=self.font(10)
			).grid(row=2, column=0, padx=16, pady=(0, 14), sticky="w")

	def create_activity_and_pet_summary(self, parent):
		sections = ctk.CTkFrame(parent, fg_color="transparent")
		sections.grid(row=2, column=0, sticky="ew")
		sections.grid_columnconfigure(0, weight=3)
		sections.grid_columnconfigure(1, weight=1, minsize=190)

		self.create_recent_activities(sections)
		self.create_pet_summary(sections)

	def create_recent_activities(self, parent):
		card = ctk.CTkFrame(
			parent, fg_color=self.COLORS["surface"], border_width=1,
			border_color=self.COLORS["line"], corner_radius=12
		)
		card.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
		card.grid_columnconfigure(0, weight=1)
		ctk.CTkLabel(
			card, text="Recent grooming activities", text_color=self.COLORS["ink"],
			font=self.font(15, "bold")
		).grid(row=0, column=0, padx=18, pady=(16, 12), sticky="w")

		table = ctk.CTkFrame(card, fg_color="transparent")
		table.grid(row=1, column=0, padx=18, pady=(0, 18), sticky="ew")
		column_weights = (3, 1, 2)
		for column, weight in enumerate(column_weights):
			table.grid_columnconfigure(column, weight=weight)

		self.activity_table = table
		headings = ("DATE", "PET", "ACTIVITY")
		for column, heading in enumerate(headings):
			ctk.CTkLabel(
				table, text=heading, text_color=self.COLORS["muted"],
				fg_color=self.COLORS["soft_gray"], border_width=1,
				border_color=self.COLORS["line"], font=self.font(9, "bold"),
				anchor="center", height=40, corner_radius=0
			).grid(row=0, column=column, padx=(0, 1), pady=(0, 4), sticky="nsew")

		self.activity_empty_label = ctk.CTkLabel(
			table, text="No grooming activities yet.",
			text_color=self.COLORS["muted"], font=self.font(11)
		)
		self.activity_empty_label.grid(row=1, column=0, columnspan=3, pady=18)

	def create_pet_summary(self, parent):
		card = ctk.CTkFrame(
			parent, fg_color=self.COLORS["surface"], border_width=1,
			border_color=self.COLORS["line"], corner_radius=12
		)
		card.grid(row=0, column=1, sticky="nsew")
		card.grid_columnconfigure(0, weight=1)
		ctk.CTkLabel(
			card, text="Pet summary", text_color=self.COLORS["ink"],
			font=self.font(15, "bold")
		).grid(row=0, column=0, padx=18, pady=(16, 12), sticky="w")

		for row, (species, count) in enumerate((("Dogs", 0), ("Cats", 0), ("Other", 0)), start=1):
			item = ctk.CTkFrame(
				card,
				fg_color=self.COLORS["soft_gray"] if row % 2 else "#FAFCFA",
				corner_radius=8
			)
			item.grid(row=row, column=0, padx=14, pady=(0, 7), sticky="ew")
			item.grid_columnconfigure(0, weight=1)
			ctk.CTkLabel(
				item, text=species, text_color=self.COLORS["ink"],
				font=self.font(11), anchor="w"
			).grid(row=0, column=0, padx=12, pady=12, sticky="w")
			value_label = ctk.CTkLabel(
				item, text=str(count), text_color=self.COLORS["primary"],
				font=self.font(14, "bold"), anchor="e"
			)
			value_label.grid(row=0, column=1, padx=12, pady=12, sticky="e")
			self.pet_summary_value_labels[species.lower()] = value_label

	def refresh_data(self):
		"""Refresh visible Dashboard values from a short-lived read-only connection."""
		database_manager = None
		try:
			database_manager = DatabaseManager(read_only=True)
			summary = database_manager.get_dashboard_summary()
			activities = database_manager.get_recent_grooming_activities(limit=5)
		except (sqlite3.Error, OSError):
			summary = {
				"total_pets": 0,
				"grooming_records": 0,
				"foods": 0,
				"vitamins": 0,
				"dogs": 0,
				"cats": 0,
				"other": 0
			}
			activities = []
		finally:
			if database_manager is not None:
				database_manager.close()

		for key, label in self.summary_value_labels.items():
			label.configure(text=str(summary[key]))
		for species in ("dogs", "cats", "other"):
			self.pet_summary_value_labels[species].configure(text=str(summary[species]))
		self.render_recent_activities(activities)

	def render_recent_activities(self, activities):
		for widget in self.activity_table.grid_slaves():
			if widget is not self.activity_empty_label and int(widget.grid_info()["row"]) > 0:
				widget.destroy()

		if not activities:
			self.activity_empty_label.configure(text="No grooming activities yet.")
			self.activity_empty_label.grid(row=1, column=0, columnspan=3, pady=18)
			return

		self.activity_empty_label.grid_remove()
		for row, activity in enumerate(activities, start=1):
			row_color = self.COLORS["surface"] if row % 2 else "#FAFCFA"
			for column, value in enumerate(activity):
				ctk.CTkLabel(
					self.activity_table, text=str(value),
					text_color=self.COLORS["ink"], fg_color=row_color,
					border_width=1, border_color=self.COLORS["line"],
					font=self.font(10), anchor="center", height=42,
					corner_radius=0
				).grid(row=row, column=column, padx=(0, 1), pady=(0, 3), sticky="nsew")


if __name__ == "__main__":
	from main import FurLogApp

	app = FurLogApp()
	app.mainloop()
