import calendar
from datetime import date, datetime
from tkinter import messagebox

import customtkinter as ctk

from database.database import DatabaseManager
from gui.pet_management import PetManagement
from managers.grooming_manager import GroomingManager


class GroomingHistory(ctk.CTkFrame):
	"""Read-only, filterable history of saved grooming records."""

	COLORS = PetManagement.COLORS
	FONT_FAMILY = PetManagement.FONT_FAMILY
	NAVIGATION_ITEMS = PetManagement.NAVIGATION_ITEMS
	ROUTABLE_NAVIGATION_ITEMS = PetManagement.ROUTABLE_NAVIGATION_ITEMS
	font = PetManagement.font
	create_nav_button = PetManagement.create_nav_button
	get_navigation_items = PetManagement.get_navigation_items
	get_navigation_command = PetManagement.get_navigation_command

	ALL_PETS = "All Pets"
	ALL_ACTIVITIES = "All Activities"
	TABLE_COLUMNS = (("Grooming Date", 16), ("Pet Name", 20), ("Activity", 20), ("Notes", 44))

	def __init__(self, master, grooming_manager=None, on_navigate=None):
		super().__init__(master, fg_color=self.COLORS["canvas"])
		self.grooming_manager = grooming_manager
		self.on_navigate = on_navigate
		self.pet_id_by_option = {self.ALL_PETS: None}
		self.record_rows = {}
		self.create_widgets()
		try:
			if self.grooming_manager is None:
				self.grooming_manager = GroomingManager(DatabaseManager(read_only=True))
			self.refresh_data()
		except Exception as error:
			messagebox.showerror("Load grooming history failed", str(error))

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

		navigation_items = self.get_navigation_items()
		logout_row = len(navigation_items) + 1
		sidebar.grid_rowconfigure(logout_row - 1, weight=1)
		for row, label in enumerate(
			(item for item in navigation_items if item != "Logout"), start=1
		):
			command = self.get_navigation_command(label)
			self.create_nav_button(
				sidebar, label, label == "Grooming History", row, command
			)
		self.create_nav_button(
			sidebar, "Logout", False, logout_row,
			self.get_navigation_command("Logout")
		)

	def create_content(self):
		content = ctk.CTkScrollableFrame(
			self,
			fg_color="transparent",
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
			header, text="GROOMING", text_color=self.COLORS["primary"],
			font=self.font(10, "bold")
		).grid(row=0, column=0, sticky="w")
		ctk.CTkLabel(
			header, text="Grooming History", text_color=self.COLORS["ink"],
			font=self.font(28, "bold")
		).grid(row=1, column=0, pady=(3, 0), sticky="w")
		ctk.CTkLabel(
			header, text="Review past grooming activities and visits.",
			text_color=self.COLORS["muted"], font=self.font(12)
		).grid(row=2, column=0, pady=(3, 0), sticky="w")

		self.create_filter_card(content)
		self.create_table_card(content)

	def create_filter_card(self, parent):
		card = ctk.CTkFrame(
			parent, fg_color=self.COLORS["surface"], border_width=1,
			border_color=self.COLORS["line"], corner_radius=12
		)
		card.grid(row=1, column=0, pady=(0, 18), sticky="ew")
		for column in range(4):
			card.grid_columnconfigure(column, weight=1)
		ctk.CTkLabel(
			card, text="Search and filters", text_color=self.COLORS["ink"],
			font=self.font(15, "bold")
		).grid(row=0, column=0, columnspan=4, padx=18, pady=(16, 10), sticky="w")

		self.search_entry = self.create_entry(
			card, "Pet name", "Search pet names...", row=1, column=0, columnspan=2
		)
		self.pet_menu = self.create_option_menu(
			card, "Registered pet", [self.ALL_PETS], row=1, column=2,
			columnspan=2
		)
		self.activity_menu = self.create_option_menu(
			card, "Grooming activity", [self.ALL_ACTIVITIES], row=2, column=0
		)
		self.start_date_entry = self.create_date_entry(
			card, "From date", row=2, column=1
		)
		self.end_date_entry = self.create_date_entry(
			card, "To date", row=2, column=2
		)

		actions = ctk.CTkFrame(card, fg_color="transparent")
		actions.grid(row=2, column=3, padx=(8, 18), pady=(8, 15), sticky="sew")
		ctk.CTkButton(
			actions, text="Apply", command=self.refresh_data, height=34, width=82,
			corner_radius=8, fg_color=self.COLORS["primary"],
			hover_color=self.COLORS["primary_hover"], text_color="#FFFFFF",
			font=self.font(11, "bold")
		).grid(row=0, column=0, padx=(0, 6), sticky="ew")
		ctk.CTkButton(
			actions, text="Clear", command=self.clear_filters, height=34, width=72,
			corner_radius=8, fg_color=self.COLORS["soft_gray"],
			hover_color="#E1E9E3", text_color=self.COLORS["ink"],
			font=self.font(11, "bold")
		).grid(row=0, column=1, sticky="ew")
		self.search_entry.bind("<Return>", lambda event: self.refresh_data())

	def create_entry(self, parent, label, placeholder, row, column, columnspan=1):
		field = ctk.CTkFrame(parent, fg_color="transparent")
		field.grid(
			row=row, column=column, columnspan=columnspan,
			padx=(18, 8), pady=(0, 8), sticky="ew"
		)
		field.grid_columnconfigure(0, weight=1)
		ctk.CTkLabel(
			field, text=label, text_color=self.COLORS["ink"],
			font=self.font(10, "bold")
		).grid(row=0, column=0, pady=(0, 4), sticky="w")
		entry = ctk.CTkEntry(
			field, height=36, corner_radius=8, border_width=1,
			border_color=self.COLORS["line"], fg_color="#FBFCFB",
			text_color=self.COLORS["ink"], placeholder_text=placeholder,
			placeholder_text_color="#A1ADA6", font=self.font(11)
		)
		entry.grid(row=1, column=0, sticky="ew")
		return entry

	def create_date_entry(self, parent, label, row, column):
		field = ctk.CTkFrame(parent, fg_color="transparent")
		field.grid(row=row, column=column, padx=(18, 8), pady=(0, 8), sticky="ew")
		field.grid_columnconfigure(0, weight=1)
		ctk.CTkLabel(
			field, text=label, text_color=self.COLORS["ink"],
			font=self.font(10, "bold")
		).grid(row=0, column=0, columnspan=2, pady=(0, 4), sticky="w")

		date_controls = ctk.CTkFrame(field, fg_color="transparent")
		date_controls.grid(row=1, column=0, columnspan=2, sticky="ew")
		date_controls.grid_columnconfigure(0, weight=1)
		entry = ctk.CTkEntry(
			date_controls, height=36, corner_radius=8, border_width=1,
			border_color=self.COLORS["line"], fg_color="#FBFCFB",
			text_color=self.COLORS["ink"], placeholder_text="YYYY-MM-DD",
			placeholder_text_color="#A1ADA6", font=self.font(11), state="readonly"
		)
		entry.grid(row=0, column=0, sticky="ew")
		entry.bind(
			"<Button-1>",
			lambda event, target=entry: self.open_date_picker(target)
		)
		ctk.CTkButton(
			date_controls, text="Choose", command=lambda: self.open_date_picker(entry),
			width=72, height=36, corner_radius=8,
			fg_color=self.COLORS["soft_green"], hover_color="#D8EBDD",
			text_color=self.COLORS["primary_hover"], font=self.font(10, "bold")
		).grid(row=0, column=1, padx=(6, 0))
		return entry

	def open_date_picker(self, target_entry):
		"""Open the FurLog calendar and place its selection in a date filter."""
		try:
			selected_date = datetime.strptime(
				target_entry.get().strip(), "%Y-%m-%d"
			).date()
		except ValueError:
			selected_date = date.today()

		picker = ctk.CTkToplevel(self)
		picker.title("Choose date")
		picker.geometry("340x350")
		picker.resizable(False, False)
		picker.configure(fg_color=self.COLORS["canvas"])
		picker.transient(self.winfo_toplevel())
		picker.grab_set()

		calendar_card = ctk.CTkFrame(
			picker, fg_color=self.COLORS["surface"], border_width=1,
			border_color=self.COLORS["line"], corner_radius=12
		)
		calendar_card.pack(fill="both", expand=True, padx=14, pady=14)
		calendar_card.grid_columnconfigure(tuple(range(7)), weight=1)

		month_state = {"year": selected_date.year, "month": selected_date.month}
		month_header = ctk.CTkFrame(calendar_card, fg_color="transparent")
		month_header.grid(
			row=0, column=0, columnspan=7, padx=10, pady=(10, 6), sticky="ew"
		)
		month_header.grid_columnconfigure(1, weight=1)
		month_label = ctk.CTkLabel(
			month_header, text="", text_color=self.COLORS["ink"],
			font=self.font(14, "bold")
		)
		month_label.grid(row=0, column=1, sticky="ew")

		for column, weekday in enumerate(("Mo", "Tu", "We", "Th", "Fr", "Sa", "Su")):
			ctk.CTkLabel(
				calendar_card, text=weekday, text_color=self.COLORS["muted"],
				font=self.font(10, "bold"), height=28
			).grid(row=1, column=column, padx=2, pady=2, sticky="nsew")

		day_buttons = []

		def change_month(offset):
			month_index = month_state["month"] - 1 + offset
			month_state["year"] += month_index // 12
			month_state["month"] = month_index % 12 + 1
			render_month()

		ctk.CTkButton(
			month_header, text="<", command=lambda: change_month(-1),
			width=32, height=30, corner_radius=7,
			fg_color=self.COLORS["soft_gray"], hover_color="#E1E9E3",
			text_color=self.COLORS["ink"], font=self.font(12, "bold")
		).grid(row=0, column=0, sticky="w")
		ctk.CTkButton(
			month_header, text=">", command=lambda: change_month(1),
			width=32, height=30, corner_radius=7,
			fg_color=self.COLORS["soft_gray"], hover_color="#E1E9E3",
			text_color=self.COLORS["ink"], font=self.font(12, "bold")
		).grid(row=0, column=2, sticky="e")

		def choose_day(day):
			chosen = date(month_state["year"], month_state["month"], day)
			self.set_date_entry(target_entry, chosen.isoformat())
			picker.grab_release()
			picker.destroy()

		def render_month():
			month_label.configure(
				text=f"{calendar.month_name[month_state['month']]} {month_state['year']}"
			)
			for button in day_buttons:
				button.destroy()
			day_buttons.clear()
			for week_index, week in enumerate(
				calendar.monthcalendar(month_state["year"], month_state["month"]),
				start=2
			):
				for weekday_index, day in enumerate(week):
					if day == 0:
						continue
					is_selected = (
						month_state["year"], month_state["month"], day
					) == (selected_date.year, selected_date.month, selected_date.day)
					button = ctk.CTkButton(
						calendar_card, text=str(day),
						command=lambda selected_day=day: choose_day(selected_day),
						width=34, height=32, corner_radius=7,
						fg_color=self.COLORS["primary"] if is_selected else "transparent",
						hover_color=self.COLORS["soft_green"],
						text_color="#FFFFFF" if is_selected else self.COLORS["ink"],
						font=self.font(10)
					)
					button.grid(
						row=week_index, column=weekday_index,
						padx=2, pady=2, sticky="nsew"
					)
					day_buttons.append(button)

		render_month()
		picker.update_idletasks()
		parent = self.winfo_toplevel()
		picker.geometry(
			f"+{parent.winfo_rootx() + 100}+{parent.winfo_rooty() + 100}"
		)
		return picker

	@staticmethod
	def set_date_entry(entry, value):
		entry.configure(state="normal")
		entry.delete(0, "end")
		entry.insert(0, value)
		entry.configure(state="readonly")

	def create_option_menu(self, parent, label, values, row, column, columnspan=1):
		field = ctk.CTkFrame(parent, fg_color="transparent")
		field.grid(
			row=row, column=column, columnspan=columnspan,
			padx=(18, 8), pady=(0, 8), sticky="ew"
		)
		field.grid_columnconfigure(0, weight=1)
		ctk.CTkLabel(
			field, text=label, text_color=self.COLORS["ink"],
			font=self.font(10, "bold")
		).grid(row=0, column=0, pady=(0, 4), sticky="w")
		menu = ctk.CTkOptionMenu(
			field, values=values, height=36, corner_radius=8,
			fg_color=self.COLORS["soft_gray"],
			button_color=self.COLORS["primary"],
			button_hover_color=self.COLORS["primary_hover"],
			text_color=self.COLORS["ink"], font=self.font(10),
			dropdown_font=self.font(10), anchor="w"
		)
		menu.grid(row=1, column=0, sticky="ew")
		menu.set(values[0])
		return menu

	def create_table_card(self, parent):
		card = ctk.CTkFrame(
			parent, fg_color=self.COLORS["surface"], border_width=1,
			border_color=self.COLORS["line"], corner_radius=12
		)
		card.grid(row=2, column=0, sticky="nsew")
		card.configure(height=410)
		card.grid_propagate(False)
		card.grid_rowconfigure(1, weight=1)
		card.grid_columnconfigure(0, weight=1)

		header = ctk.CTkFrame(card, fg_color="transparent")
		header.grid(row=0, column=0, padx=18, pady=(16, 10), sticky="ew")
		header.grid_columnconfigure(0, weight=1)
		ctk.CTkLabel(
			header, text="Past grooming activities", text_color=self.COLORS["ink"],
			font=self.font(15, "bold")
		).grid(row=0, column=0, sticky="w")
		self.result_label = ctk.CTkLabel(
			header, text="0 records", text_color=self.COLORS["muted"],
			font=self.font(10)
		)
		self.result_label.grid(row=1, column=0, pady=(2, 0), sticky="w")

		self.records_scroll = ctk.CTkScrollableFrame(
			card, fg_color=self.COLORS["surface"], corner_radius=0,
			scrollbar_button_color=self.COLORS["line"],
			scrollbar_button_hover_color="#B9CFC1"
		)
		self.records_scroll.grid(
			row=1, column=0, padx=18, pady=(0, 18), sticky="nsew"
		)
		for column, (_, weight) in enumerate(self.TABLE_COLUMNS):
			self.records_scroll.grid_columnconfigure(column, weight=weight)
		for column, (heading, _) in enumerate(self.TABLE_COLUMNS):
			ctk.CTkLabel(
				self.records_scroll, text=heading.upper(),
				text_color=self.COLORS["muted"], fg_color=self.COLORS["soft_gray"],
				border_width=1, border_color=self.COLORS["line"],
				font=self.font(9, "bold"), anchor="center", height=44,
				corner_radius=0
			).grid(row=0, column=column, padx=(0, 1), pady=(0, 5), sticky="nsew")
		self.empty_state_label = ctk.CTkLabel(
			self.records_scroll, text="No grooming records have been saved yet.",
			text_color=self.COLORS["muted"], font=self.font(12, "bold")
		)

	def refresh_data(self):
		"""Reload reference choices and current history from the read-only database."""
		try:
			pet_options = self.grooming_manager.get_pet_options()
			activities = self.grooming_manager.get_activity_options()
			self.update_filter_options(pet_options, activities)
			filters = self.get_filter_values()
			if filters is None:
				return
			records = self.grooming_manager.get_all_records(**filters)
		except Exception as error:
			messagebox.showerror("Load grooming history failed", str(error))
			return

		self.render_records(records, filters)

	def update_filter_options(self, pet_options, activities):
		selected_pet = self.pet_menu.get()
		self.pet_id_by_option = {self.ALL_PETS: None}
		for pet_id, name, owner in pet_options:
			option = f"{name} (Owner: {owner}) - ID: {pet_id}"
			self.pet_id_by_option[option] = pet_id
		pet_values = list(self.pet_id_by_option)
		self.pet_menu.configure(values=pet_values)
		self.pet_menu.set(selected_pet if selected_pet in pet_values else self.ALL_PETS)

		selected_activity = self.activity_menu.get()
		activity_values = [self.ALL_ACTIVITIES, *activities]
		self.activity_menu.configure(values=activity_values)
		self.activity_menu.set(
			selected_activity if selected_activity in activity_values
			else self.ALL_ACTIVITIES
		)

	def get_filter_values(self):
		start_date = self.parse_date(self.start_date_entry.get().strip(), "From date")
		end_date = self.parse_date(self.end_date_entry.get().strip(), "To date")
		if start_date is False or end_date is False:
			return None
		if start_date and end_date and start_date > end_date:
			messagebox.showwarning(
				"Invalid date range",
				"The From date must be on or before the To date."
			)
			return None

		activity = self.activity_menu.get()
		pet_option = self.pet_menu.get()
		return {
			"search_term": self.search_entry.get().strip(),
			"activity": None if activity == self.ALL_ACTIVITIES else activity,
			"start_date": start_date or None,
			"end_date": end_date or None,
			"pet_id": self.pet_id_by_option.get(pet_option)
		}

	def parse_date(self, value, label):
		if not value:
			return None
		try:
			parsed_date = datetime.strptime(value, "%Y-%m-%d").date()
			if parsed_date.isoformat() != value:
				raise ValueError
			return value
		except ValueError:
			messagebox.showwarning(
				"Invalid date",
				f"Enter {label.lower()} as a real date in YYYY-MM-DD format."
			)
			return False

	def render_records(self, records, filters):
		for row_widgets in self.record_rows.values():
			for widget in row_widgets:
				widget.destroy()
		self.record_rows.clear()
		self.result_label.configure(
			text=f"{len(records)} record" + ("s" if len(records) != 1 else "")
		)

		if not records:
			active_filters = any((
				filters["search_term"], filters["activity"], filters["start_date"],
				filters["end_date"], filters["pet_id"] is not None
			))
			self.empty_state_label.configure(
				text=(
					"No grooming records match the selected filters."
					if active_filters else "No grooming records have been saved yet."
				)
			)
			self.empty_state_label.grid(
				row=1, column=0, columnspan=len(self.TABLE_COLUMNS),
				padx=20, pady=38
			)
			return
		self.empty_state_label.grid_remove()

		for row_number, record in enumerate(records):
			record_id, pet_id, pet_name, owner, grooming_date, activity, notes = record
			values = (grooming_date, pet_name, activity, notes or "-")
			row_color = self.COLORS["surface"] if row_number % 2 == 0 else "#FAFCFA"
			row_widgets = []
			for column, value in enumerate(values):
				label = ctk.CTkLabel(
					self.records_scroll, text=self.truncate_text(value, 72),
					text_color=self.COLORS["ink"], fg_color=row_color,
					border_width=1, border_color=self.COLORS["line"],
					font=self.font(11), anchor="center", height=48,
					corner_radius=0
				)
				label.grid(
					row=row_number + 1, column=column,
					padx=(0, 1), pady=(0, 5), sticky="nsew"
				)
				row_widgets.append(label)
			self.record_rows[record_id] = row_widgets

	def clear_filters(self):
		self.search_entry.delete(0, "end")
		self.set_date_entry(self.start_date_entry, "")
		self.set_date_entry(self.end_date_entry, "")
		self.activity_menu.set(self.ALL_ACTIVITIES)
		self.pet_menu.set(self.ALL_PETS)
		self.refresh_data()

	@staticmethod
	def truncate_text(value, max_length):
		value = str(value)
		if len(value) <= max_length:
			return value
		return f"{value[:max_length - 3]}..."
