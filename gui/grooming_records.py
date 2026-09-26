import calendar
from datetime import date, datetime
from tkinter import messagebox

import customtkinter as ctk

from gui.pet_management import PetManagement
from managers.grooming_manager import GroomingManager
from models.grooming_record import GroomingRecord


class GroomingRecords(ctk.CTkFrame):
	"""Grooming-record CRUD screen styled like Pet Management."""

	COLORS = PetManagement.COLORS
	FONT_FAMILY = PetManagement.FONT_FAMILY
	NAVIGATION_ITEMS = PetManagement.NAVIGATION_ITEMS
	ROUTABLE_NAVIGATION_ITEMS = PetManagement.ROUTABLE_NAVIGATION_ITEMS
	font = PetManagement.font
	create_nav_button = PetManagement.create_nav_button
	create_action_button = PetManagement.create_action_button

	TABLE_COLUMNS = (("Date", 18), ("Pet", 18), ("Activity", 20), ("Notes", 44))
	ACTIVITIES = (
		"Bathing",
		"Hair Grooming",
		"Nail Trimming",
		"Ear Cleaning",
		"Other"
	)

	def __init__(self, master, grooming_manager=None, on_navigate=None):
		super().__init__(master, fg_color=self.COLORS["canvas"])
		self.grooming_manager = grooming_manager or GroomingManager()
		self.on_navigate = on_navigate
		self.selected_record_id = None
		self.pet_id_by_option = {}
		self.pet_option_by_id = {}
		self.record_rows = {}
		self.create_widgets()
		try:
			self.refresh_data()
		except Exception as error:
			messagebox.showerror("Load grooming records failed", str(error))

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
			if self.on_navigate and label in self.ROUTABLE_NAVIGATION_ITEMS + ("Grooming Records",):
				command = lambda target=label: self.on_navigate(target)
			self.create_nav_button(
				sidebar, label, label == "Grooming Records", row, command
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
			header, text="Grooming Records", text_color=self.COLORS["ink"],
			font=self.font(28, "bold")
		).grid(row=1, column=0, pady=(3, 0), sticky="w")
		ctk.CTkLabel(
			header, text="Record and manage each pet's grooming visits.",
			text_color=self.COLORS["muted"], font=self.font(12)
		).grid(row=2, column=0, pady=(3, 0), sticky="w")
		ctk.CTkButton(
			header, text="+  Add record", command=self.focus_new_record, width=128,
			height=38, corner_radius=9, fg_color=self.COLORS["primary"],
			hover_color=self.COLORS["primary_hover"], text_color="#FFFFFF",
			font=self.font(12, "bold")
		).grid(row=1, column=1, rowspan=2, padx=(20, 0), sticky="e")

		self.create_form_card(content)
		self.create_table_card(content)

	def create_form_card(self, parent):
		card = ctk.CTkFrame(
			parent, fg_color=self.COLORS["surface"], border_width=1,
			border_color=self.COLORS["line"], corner_radius=12
		)
		card.grid(row=1, column=0, pady=(0, 18), sticky="ew")
		card.grid_columnconfigure(1, weight=1)
		card.grid_columnconfigure(3, weight=2)
		ctk.CTkLabel(
			card, text="Grooming information", text_color=self.COLORS["ink"],
			font=self.font(15, "bold")
		).grid(row=0, column=0, columnspan=4, padx=18, pady=(16, 3), sticky="w")
		ctk.CTkLabel(
			card, text="Select a saved record below to update or delete it.",
			text_color=self.COLORS["muted"], font=self.font(11)
		).grid(row=1, column=0, columnspan=4, padx=18, pady=(0, 12), sticky="w")

		ctk.CTkLabel(
			card, text="Pet", text_color=self.COLORS["ink"], font=self.font(11, "bold")
		).grid(row=2, column=0, padx=(18, 8), pady=6, sticky="e")
		self.pet_menu = ctk.CTkOptionMenu(
			card, values=["No pets registered"], height=36, corner_radius=8,
			fg_color=self.COLORS["soft_gray"], button_color=self.COLORS["primary"],
			button_hover_color=self.COLORS["primary_hover"],
			text_color=self.COLORS["ink"], font=self.font(11),
			dropdown_font=self.font(11), anchor="w"
		)
		self.pet_menu.grid(row=2, column=1, padx=(0, 18), pady=6, sticky="ew")

		ctk.CTkLabel(
			card, text="Grooming Date", text_color=self.COLORS["ink"],
			font=self.font(11, "bold")
		).grid(row=2, column=2, padx=(18, 8), pady=6, sticky="e")
		date_input = ctk.CTkFrame(card, fg_color="transparent")
		date_input.grid(row=2, column=3, padx=(0, 18), pady=6, sticky="ew")
		date_input.grid_columnconfigure(0, weight=1)
		self.date_entry = ctk.CTkEntry(
			date_input, height=36, corner_radius=8, border_width=1,
			border_color=self.COLORS["line"], fg_color="#FBFCFB",
			text_color=self.COLORS["ink"], placeholder_text="YYYY-MM-DD",
			placeholder_text_color="#A1ADA6", font=self.font(11), state="readonly"
		)
		self.date_entry.grid(row=0, column=0, sticky="ew")
		self.date_entry.bind("<Button-1>", self.open_date_picker)
		ctk.CTkButton(
			date_input, text="Choose", command=self.open_date_picker, width=72,
			height=36, corner_radius=8, fg_color=self.COLORS["soft_green"],
			hover_color="#D8EBDD", text_color=self.COLORS["primary_hover"],
			font=self.font(10, "bold")
		).grid(row=0, column=1, padx=(6, 0))

		ctk.CTkLabel(
			card, text="Activity", text_color=self.COLORS["ink"],
			font=self.font(11, "bold")
		).grid(row=3, column=0, padx=(18, 8), pady=6, sticky="e")
		self.activity_menu = ctk.CTkOptionMenu(
			card, values=list(self.ACTIVITIES), height=36, corner_radius=8,
			fg_color=self.COLORS["soft_gray"], button_color=self.COLORS["primary"],
			button_hover_color=self.COLORS["primary_hover"],
			text_color=self.COLORS["ink"], font=self.font(11),
			dropdown_font=self.font(11), anchor="w"
		)
		self.activity_menu.grid(row=3, column=1, padx=(0, 18), pady=6, sticky="ew")

		ctk.CTkLabel(
			card, text="Notes", text_color=self.COLORS["ink"],
			font=self.font(11, "bold")
		).grid(row=3, column=2, padx=(18, 8), pady=6, sticky="e")
		self.notes_textbox = ctk.CTkTextbox(
			card, height=74, corner_radius=8, border_width=1,
			border_color=self.COLORS["line"], fg_color="#FBFCFB",
			text_color=self.COLORS["ink"], font=self.font(11), wrap="word"
		)
		self.notes_textbox.grid(row=3, column=3, padx=(0, 18), pady=6, sticky="ew")

		actions = ctk.CTkFrame(card, fg_color="transparent")
		actions.grid(row=4, column=0, columnspan=4, padx=18, pady=(12, 17), sticky="w")
		self.create_action_button(actions, "Add", self.add_record, 0, True)
		self.create_action_button(actions, "Update", self.update_record, 1)
		self.create_action_button(actions, "Clear", self.clear_form, 2)
		self.create_action_button(actions, "Delete", self.delete_record, 3, danger=True)

	def open_date_picker(self, event=None):
		"""Open a small calendar and place its selected date in the form."""
		current_value = self.date_entry.get().strip()
		try:
			selected_date = datetime.strptime(current_value, "%Y-%m-%d").date()
		except ValueError:
			selected_date = date.today()

		picker = ctk.CTkToplevel(self)
		picker.title("Choose grooming date")
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
		month_header.grid(row=0, column=0, columnspan=7, padx=10, pady=(10, 6), sticky="ew")
		month_header.grid_columnconfigure(1, weight=1)
		month_label = ctk.CTkLabel(
			month_header, text="", text_color=self.COLORS["ink"],
			font=self.font(14, "bold")
		)
		month_label.grid(row=0, column=1, sticky="ew")

		weekday_names = ("Mo", "Tu", "We", "Th", "Fr", "Sa", "Su")
		for column, weekday in enumerate(weekday_names):
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
			self.set_grooming_date(chosen.isoformat())
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
					button = ctk.CTkButton(
						calendar_card, text=str(day),
						command=lambda selected_day=day: choose_day(selected_day),
						width=34, height=32, corner_radius=7,
						fg_color=(
							self.COLORS["primary"]
							if (month_state["year"], month_state["month"], day)
							== (selected_date.year, selected_date.month, selected_date.day)
							else "transparent"
						),
						hover_color=self.COLORS["soft_green"],
						text_color=(
							"#FFFFFF"
							if (month_state["year"], month_state["month"], day)
							== (selected_date.year, selected_date.month, selected_date.day)
							else self.COLORS["ink"]
						),
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

	def set_grooming_date(self, value):
		self.date_entry.configure(state="normal")
		self.date_entry.delete(0, "end")
		self.date_entry.insert(0, value)
		self.date_entry.configure(state="readonly")

	def create_table_card(self, parent):
		card = ctk.CTkFrame(
			parent, fg_color=self.COLORS["surface"], border_width=1,
			border_color=self.COLORS["line"], corner_radius=12
		)
		card.grid(row=2, column=0, sticky="nsew")
		card.configure(height=310)
		card.grid_propagate(False)
		card.grid_rowconfigure(1, weight=1)
		card.grid_columnconfigure(0, weight=1)
		ctk.CTkLabel(
			card, text="Saved grooming records", text_color=self.COLORS["ink"],
			font=self.font(15, "bold")
		).grid(row=0, column=0, padx=18, pady=(16, 10), sticky="w")

		self.records_scroll = ctk.CTkScrollableFrame(
			card, fg_color=self.COLORS["surface"], corner_radius=0,
			scrollbar_button_color=self.COLORS["line"],
			scrollbar_button_hover_color="#B9CFC1"
		)
		self.records_scroll.grid(row=1, column=0, padx=18, pady=(0, 18), sticky="nsew")
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
			self.records_scroll, text="No grooming records yet.",
			text_color=self.COLORS["muted"], font=self.font(12, "bold")
		)

	def refresh_data(self):
		"""Reload pet choices and saved grooming records from SQLite."""
		try:
			pet_options = self.grooming_manager.get_pet_options()
			records = self.grooming_manager.get_all_records()
		except Exception as error:
			messagebox.showerror("Load grooming records failed", str(error))
			return

		self.pet_id_by_option.clear()
		self.pet_option_by_id.clear()
		for pet_id, name, owner in pet_options:
			option = f"{name} (Owner: {owner}) - ID: {pet_id}"
			self.pet_id_by_option[option] = pet_id
			self.pet_option_by_id[pet_id] = option

		options = list(self.pet_id_by_option) or ["No pets registered"]
		self.pet_menu.configure(values=options)
		if self.pet_menu.get() not in options:
			self.pet_menu.set(options[0])
		self.render_records(records)

	def render_records(self, records):
		for row_widgets in self.record_rows.values():
			for widget in row_widgets:
				widget.destroy()
		self.record_rows.clear()

		if not records:
			self.empty_state_label.grid(
				row=1, column=0, columnspan=len(self.TABLE_COLUMNS),
				padx=20, pady=38
			)
			return
		self.empty_state_label.grid_remove()

		for row_number, record in enumerate(records):
			record_id, pet_id, pet_name, owner, grooming_date, activity, notes = record
			pet_display = f"{pet_name} ({owner})"
			values = (grooming_date, pet_display, activity, notes or "-")
			row_color = self.COLORS["surface"] if row_number % 2 == 0 else "#FAFCFA"
			row_widgets = []
			for column, value in enumerate(values):
				label = ctk.CTkLabel(
					self.records_scroll, text=self.truncate_text(value, 48),
					text_color=self.COLORS["ink"], fg_color=row_color,
					border_width=1, border_color=self.COLORS["line"],
					font=self.font(11), anchor="center", height=48,
					corner_radius=0
				)
				label.grid(
					row=row_number + 1, column=column,
					padx=(0, 1), pady=(0, 5), sticky="nsew"
				)
				label.bind(
					"<Button-1>",
					lambda event, selected_id=record_id: self.select_record(selected_id)
				)
				row_widgets.append(label)
			self.record_rows[record_id] = row_widgets

	def truncate_text(self, value, max_length):
		value = str(value)
		if len(value) <= max_length:
			return value
		return f"{value[:max_length - 3]}..."

	def focus_new_record(self):
		self.clear_form()
		if self.pet_id_by_option:
			self.pet_menu.focus_set()

	def get_form_values(self):
		pet_option = self.pet_menu.get()
		pet_id = self.pet_id_by_option.get(pet_option)
		grooming_date = self.date_entry.get().strip()
		activity = self.activity_menu.get().strip()
		notes = self.notes_textbox.get("1.0", "end-1c").strip()

		if pet_id is None:
			messagebox.showwarning("Select a pet", "Register a pet and select it first.")
			return None
		try:
			parsed_date = datetime.strptime(grooming_date, "%Y-%m-%d")
			if parsed_date.date().isoformat() != grooming_date:
				raise ValueError
		except ValueError:
			messagebox.showwarning(
				"Invalid date", "Enter the grooming date as YYYY-MM-DD."
			)
			return None
		if not activity or activity not in self.ACTIVITIES:
			messagebox.showwarning("Select an activity", "Choose a grooming activity.")
			return None
		return pet_id, grooming_date, activity, notes

	def add_record(self):
		values = self.get_form_values()
		if values is None:
			return
		try:
			self.grooming_manager.create_record(GroomingRecord(
				pet_id=values[0], grooming_date=values[1],
				activity=values[2], notes=values[3]
			))
			self.refresh_data()
			self.clear_form()
		except Exception as error:
			messagebox.showerror("Add grooming record failed", str(error))

	def update_record(self):
		if self.selected_record_id is None:
			messagebox.showwarning("No record selected", "Select a record to update.")
			return
		values = self.get_form_values()
		if values is None:
			return
		try:
			record = GroomingRecord(
				id=self.selected_record_id, pet_id=values[0],
				grooming_date=values[1], activity=values[2], notes=values[3]
			)
			if self.grooming_manager.update_record(record):
				self.refresh_data()
				self.clear_form()
		except Exception as error:
			messagebox.showerror("Update grooming record failed", str(error))

	def delete_record(self):
		if self.selected_record_id is None:
			messagebox.showwarning("No record selected", "Select a record to delete.")
			return
		if not messagebox.askyesno(
			"Delete grooming record", "Are you sure you want to delete this record?"
		):
			return
		try:
			if self.grooming_manager.delete_record(self.selected_record_id):
				self.refresh_data()
				self.clear_form()
		except Exception as error:
			messagebox.showerror("Delete grooming record failed", str(error))

	def select_record(self, record_id):
		record = self.grooming_manager.get_record_by_id(record_id)
		if record is None:
			messagebox.showerror("Record not found", "The selected record no longer exists.")
			self.refresh_data()
			return
		self.selected_record_id = record.id
		self.pet_menu.set(self.pet_option_by_id.get(record.pet_id, "No pets registered"))
		self.set_grooming_date(record.grooming_date)
		self.activity_menu.set(record.activity)
		self.notes_textbox.delete("1.0", "end")
		self.notes_textbox.insert("1.0", record.notes)
		for row_id, row_widgets in self.record_rows.items():
			color = self.COLORS["primary"] if row_id == record.id else self.COLORS["line"]
			for widget in row_widgets:
				widget.configure(border_color=color)

	def clear_form(self):
		self.selected_record_id = None
		if self.pet_id_by_option:
			self.pet_menu.set(next(iter(self.pet_id_by_option)))
		else:
			self.pet_menu.set("No pets registered")
		self.set_grooming_date("")
		self.activity_menu.set(self.ACTIVITIES[0])
		self.notes_textbox.delete("1.0", "end")
		for row_widgets in self.record_rows.values():
			for widget in row_widgets:
				widget.configure(border_color=self.COLORS["line"])
