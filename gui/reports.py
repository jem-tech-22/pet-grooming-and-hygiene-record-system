import calendar
from datetime import date, datetime
from tkinter import filedialog, messagebox

import customtkinter as ctk

from database.database import DatabaseManager
from gui.pet_management import PetManagement
from managers.grooming_manager import GroomingManager
from managers.pet_manager import PetManager
from reports.pdf_exporter import export_report_pdf


class Reports(ctk.CTkFrame):
	"""Generate read-only previews and PDF exports from FurLog records."""

	COLORS = PetManagement.COLORS
	FONT_FAMILY = PetManagement.FONT_FAMILY
	NAVIGATION_ITEMS = PetManagement.NAVIGATION_ITEMS
	ROUTABLE_NAVIGATION_ITEMS = PetManagement.ROUTABLE_NAVIGATION_ITEMS
	font = PetManagement.font
	create_nav_button = PetManagement.create_nav_button
	get_navigation_items = PetManagement.get_navigation_items
	get_navigation_command = PetManagement.get_navigation_command

	PET_REGISTRY = "Pet Registry Report"
	GROOMING_ACTIVITY = "Grooming Activity Report"
	PET_CARE = "Pet Care Report"
	ALL_PETS = "All Pets"
	REPORT_TYPES = (PET_REGISTRY, GROOMING_ACTIVITY, PET_CARE)

	def __init__(self, master, on_navigate=None):
		super().__init__(master, fg_color=self.COLORS["canvas"])
		self.on_navigate = on_navigate
		self.pet_id_by_option = {self.ALL_PETS: None}
		self.preview_headers = []
		self.preview_rows = []
		self.applied_filters = {}
		self.current_report_type = None
		self.preview_widgets = []
		self.create_widgets()
		self.update_filter_visibility()

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
				sidebar, label, label == "Reports", row, command
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
			header, text="FURLOG INSIGHTS", text_color=self.COLORS["primary"],
			font=self.font(10, "bold")
		).grid(row=0, column=0, sticky="w")
		ctk.CTkLabel(
			header, text="Reports", text_color=self.COLORS["ink"],
			font=self.font(28, "bold")
		).grid(row=1, column=0, pady=(3, 0), sticky="w")
		ctk.CTkLabel(
			header, text="Build a report from your saved pet care records.",
			text_color=self.COLORS["muted"], font=self.font(12)
		).grid(row=2, column=0, pady=(3, 0), sticky="w")

		self.create_controls_card(content)
		self.create_preview_card(content)

	def create_controls_card(self, parent):
		card = ctk.CTkFrame(
			parent, fg_color=self.COLORS["surface"], border_width=1,
			border_color=self.COLORS["line"], corner_radius=12
		)
		card.grid(row=1, column=0, pady=(0, 18), sticky="ew")
		card.grid_columnconfigure(0, weight=1)
		ctk.CTkLabel(
			card, text="Report setup", text_color=self.COLORS["ink"],
			font=self.font(15, "bold")
		).grid(row=0, column=0, padx=18, pady=(16, 10), sticky="w")

		type_field = ctk.CTkFrame(card, fg_color="transparent")
		type_field.grid(row=1, column=0, padx=18, pady=(0, 10), sticky="ew")
		type_field.grid_columnconfigure(0, weight=1)
		ctk.CTkLabel(
			type_field, text="Report type", text_color=self.COLORS["ink"],
			font=self.font(10, "bold")
		).grid(row=0, column=0, pady=(0, 4), sticky="w")
		self.report_type_menu = ctk.CTkOptionMenu(
			type_field, values=list(self.REPORT_TYPES), height=36, corner_radius=8,
			fg_color=self.COLORS["soft_gray"],
			button_color=self.COLORS["primary"],
			button_hover_color=self.COLORS["primary_hover"],
			text_color=self.COLORS["ink"], font=self.font(11),
			dropdown_font=self.font(11), anchor="w",
			command=lambda _value: self.on_report_type_change()
		)
		self.report_type_menu.grid(row=1, column=0, sticky="ew")
		self.report_type_menu.set(self.PET_REGISTRY)

		self.grooming_filters = ctk.CTkFrame(card, fg_color="transparent")
		self.grooming_filters.grid(row=2, column=0, padx=18, pady=(0, 8), sticky="ew")
		for column in range(3):
			self.grooming_filters.grid_columnconfigure(column, weight=1)
		self.pet_menu = self.create_option_menu(
			self.grooming_filters, "Pet", [self.ALL_PETS], row=0, column=0
		)
		self.start_date_entry = self.create_date_filter(
			self.grooming_filters, "From date", row=0, column=1
		)
		self.end_date_entry = self.create_date_filter(
			self.grooming_filters, "To date", row=0, column=2
		)

		actions = ctk.CTkFrame(card, fg_color="transparent")
		actions.grid(row=3, column=0, padx=18, pady=(4, 16), sticky="e")
		ctk.CTkButton(
			actions, text="Generate Report", command=self.generate_report,
			height=36, width=142, corner_radius=8,
			fg_color=self.COLORS["primary"],
			hover_color=self.COLORS["primary_hover"], text_color="#FFFFFF",
			font=self.font(11, "bold")
		).grid(row=0, column=0, padx=(0, 8))
		self.export_button = ctk.CTkButton(
			actions, text="Export PDF", command=self.export_pdf,
			height=36, width=112, corner_radius=8,
			fg_color=self.COLORS["soft_green"], hover_color="#D8EBDD",
			text_color=self.COLORS["primary_hover"], font=self.font(11, "bold"),
			state="disabled"
		)
		self.export_button.grid(row=0, column=1, padx=(0, 8))
		ctk.CTkButton(
			actions, text="Clear Filters", command=self.clear_filters,
			height=36, width=112, corner_radius=8,
			fg_color=self.COLORS["soft_gray"], hover_color="#E1E9E3",
			text_color=self.COLORS["ink"], font=self.font(11, "bold")
		).grid(row=0, column=2)

	def create_option_menu(self, parent, label, values, row, column):
		field = ctk.CTkFrame(parent, fg_color="transparent")
		field.grid(row=row, column=column, padx=(0, 10), sticky="ew")
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

	def create_date_filter(self, parent, label, row, column):
		field = ctk.CTkFrame(parent, fg_color="transparent")
		field.grid(row=row, column=column, padx=(0, 10), sticky="ew")
		field.grid_columnconfigure(0, weight=1)
		ctk.CTkLabel(
			field, text=label, text_color=self.COLORS["ink"],
			font=self.font(10, "bold")
		).grid(row=0, column=0, columnspan=2, pady=(0, 4), sticky="w")
		controls = ctk.CTkFrame(field, fg_color="transparent")
		controls.grid(row=1, column=0, columnspan=2, sticky="ew")
		controls.grid_columnconfigure(0, weight=1)
		entry = ctk.CTkEntry(
			controls, height=36, corner_radius=8, border_width=1,
			border_color=self.COLORS["line"], fg_color="#FBFCFB",
			text_color=self.COLORS["ink"], placeholder_text="YYYY-MM-DD",
			placeholder_text_color="#A1ADA6", font=self.font(11), state="readonly"
		)
		entry.grid(row=0, column=0, sticky="ew")
		entry.bind(
			"<Button-1>", lambda event, target=entry: self.open_date_picker(target)
		)
		ctk.CTkButton(
			controls, text="Choose", command=lambda: self.open_date_picker(entry),
			width=72, height=36, corner_radius=8,
			fg_color=self.COLORS["soft_green"], hover_color="#D8EBDD",
			text_color=self.COLORS["primary_hover"], font=self.font(10, "bold")
		).grid(row=0, column=1, padx=(6, 0))
		return entry

	def open_date_picker(self, target_entry):
		"""Open a calendar and write the selected day to the requested filter."""
		try:
			selected_date = datetime.strptime(
				target_entry.get().strip(), "%Y-%m-%d"
			).date()
		except ValueError:
			selected_date = date.today()

		picker = ctk.CTkToplevel(self)
		picker.title("Choose report date")
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
			self.set_date_entry(
				target_entry, date(month_state["year"], month_state["month"], day).isoformat()
			)
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
					if not day:
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
		picker.geometry(f"+{parent.winfo_rootx() + 100}+{parent.winfo_rooty() + 100}")
		return picker

	@staticmethod
	def set_date_entry(entry, value):
		entry.configure(state="normal")
		entry.delete(0, "end")
		if value:
			entry.insert(0, value)
		entry.configure(state="readonly")

	def on_report_type_change(self):
		self.update_filter_visibility()
		self.clear_preview("Generate the selected report to preview its records.")

	def update_filter_visibility(self):
		if self.report_type_menu.get() == self.GROOMING_ACTIVITY:
			self.grooming_filters.grid()
			self.refresh_data()
		else:
			self.grooming_filters.grid_remove()

	def refresh_data(self):
		"""Refresh registered pet choices when Reports is opened or selected."""
		database_manager = None
		try:
			database_manager = DatabaseManager(read_only=True)
			pet_options = GroomingManager(database_manager).get_pet_options()
			self.update_pet_options(pet_options)
		except Exception as error:
			messagebox.showerror("Load report filters failed", str(error))
		finally:
			if database_manager is not None:
				database_manager.close()

	def update_pet_options(self, pet_options):
		selected_option = self.pet_menu.get()
		self.pet_id_by_option = {self.ALL_PETS: None}
		for pet_id, name, owner in pet_options:
			option = f"{name} (Owner: {owner}) - ID: {pet_id}"
			self.pet_id_by_option[option] = pet_id
		values = list(self.pet_id_by_option)
		self.pet_menu.configure(values=values)
		self.pet_menu.set(
			selected_option if selected_option in self.pet_id_by_option else self.ALL_PETS
		)

	def generate_report(self):
		report_type = self.report_type_menu.get()
		self.clear_preview("Correct the filters and generate the report again.")
		filters = {}
		if report_type == self.GROOMING_ACTIVITY:
			filters = self.get_grooming_filters()
			if filters is None:
				return

		self.clear_preview("Generating report...")
		database_manager = None
		try:
			database_manager = DatabaseManager(read_only=True)
			pet_manager = PetManager(database_manager)
			grooming_manager = GroomingManager(database_manager)
			if report_type == self.PET_REGISTRY:
				pets = pet_manager.get_all_pets()
				headers = ("Pet Name", "Species", "Breed", "Age", "Owner")
				rows = [
					(
						pet.name, pet.species, pet.breed or "-",
						f"{pet.age} {pet.age_unit}" if pet.age is not None else "-",
						pet.owner
					)
					for pet in pets
				]
			elif report_type == self.GROOMING_ACTIVITY:
				pet_options = grooming_manager.get_pet_options()
				self.update_pet_options(pet_options)
				selected_pet_id = self.pet_id_by_option.get(self.pet_menu.get())
				filters["pet_id"] = selected_pet_id
				filters["Pet"] = self.pet_menu.get()
				records = grooming_manager.get_all_records(
					pet_id=selected_pet_id,
					start_date=filters["start_date"],
					end_date=filters["end_date"]
				)
				headers = ("Grooming Date", "Pet Name", "Activity", "Notes")
				rows = [
					(record[4], record[2], record[5], record[6] or "-")
					for record in records
				]
				filters = {
					key: value for key, value in filters.items()
					if key != "pet_id" and value
				}
			else:
				pets = pet_manager.get_all_pets()
				headers = ("Pet Name", "Vitamins", "Foods", "Needs")
				rows = [
					(pet.name, pet.vitamins or "-", pet.foods or "-", pet.needs or "-")
					for pet in pets
				]
		except Exception as error:
			messagebox.showerror("Generate report failed", str(error))
			self.clear_preview("The report could not be generated.")
			return
		finally:
			if database_manager is not None:
				database_manager.close()

		self.current_report_type = report_type
		self.preview_headers = list(headers)
		self.preview_rows = [tuple(str(value) for value in row) for row in rows]
		self.applied_filters = filters
		self.render_preview()

	def get_grooming_filters(self):
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
		return {
			"start_date": start_date,
			"end_date": end_date,
			"Pet": self.pet_menu.get()
		}

	@staticmethod
	def parse_date(value, label):
		if not value:
			return None
		try:
			parsed = datetime.strptime(value, "%Y-%m-%d").date()
			if parsed.isoformat() != value:
				raise ValueError
			return value
		except ValueError:
			messagebox.showwarning(
				"Invalid date",
				f"Choose a valid {label.lower()} in YYYY-MM-DD format."
			)
			return False

	def create_preview_card(self, parent):
		card = ctk.CTkFrame(
			parent, fg_color=self.COLORS["surface"], border_width=1,
			border_color=self.COLORS["line"], corner_radius=12
		)
		card.grid(row=2, column=0, sticky="nsew")
		card.configure(height=380)
		card.grid_propagate(False)
		card.grid_rowconfigure(1, weight=1)
		card.grid_columnconfigure(0, weight=1)
		header = ctk.CTkFrame(card, fg_color="transparent")
		header.grid(row=0, column=0, padx=18, pady=(16, 10), sticky="ew")
		header.grid_columnconfigure(0, weight=1)
		ctk.CTkLabel(
			header, text="Report preview", text_color=self.COLORS["ink"],
			font=self.font(15, "bold")
		).grid(row=0, column=0, sticky="w")
		self.result_label = ctk.CTkLabel(
			header, text="Generate a report to preview its records.",
			text_color=self.COLORS["muted"], font=self.font(10)
		)
		self.result_label.grid(row=1, column=0, pady=(2, 0), sticky="w")
		self.preview_scroll = ctk.CTkScrollableFrame(
			card, fg_color=self.COLORS["surface"], corner_radius=0,
			scrollbar_button_color=self.COLORS["line"],
			scrollbar_button_hover_color="#B9CFC1"
		)
		self.preview_scroll.grid_columnconfigure(0, weight=1)
		self.preview_scroll.grid(
			row=1, column=0, padx=18, pady=(0, 18), sticky="nsew"
		)
		self.show_preview_message("Generate a report to preview its records.")

	def show_preview_message(self, message):
		self.preview_message = ctk.CTkLabel(
			self.preview_scroll, text=message,
			text_color=self.COLORS["muted"], font=self.font(12, "bold"),
			anchor="center", justify="center", wraplength=540
		)
		self.preview_message.grid(
			row=0, column=0, columnspan=5, padx=20, pady=40, sticky="ew"
		)

	def clear_preview(self, message):
		self.current_report_type = None
		self.preview_headers = []
		self.preview_rows = []
		self.applied_filters = {}
		self.export_button.configure(state="disabled")
		for widget in self.preview_widgets:
			widget.destroy()
		self.preview_widgets.clear()
		for widget in self.preview_scroll.winfo_children():
			widget.destroy()
		self.show_preview_message(message)
		self.result_label.configure(text="0 records")

	def render_preview(self):
		for widget in self.preview_scroll.winfo_children():
			widget.destroy()
		self.preview_widgets.clear()
		count = len(self.preview_rows)
		self.result_label.configure(
			text=f"{count} record" + ("s" if count != 1 else "")
		)
		if not self.preview_rows:
			filters_active = bool(self.applied_filters)
			message = (
				"No records match the selected filters."
				if filters_active else "No records are available for this report."
			)
			self.show_preview_message(message)
			self.export_button.configure(state="disabled")
			return

		for column in range(len(self.preview_headers)):
			self.preview_scroll.grid_columnconfigure(column, weight=1, uniform="report_columns")
		for column, heading in enumerate(self.preview_headers):
			label = ctk.CTkLabel(
				self.preview_scroll, text=heading.upper(),
				text_color=self.COLORS["muted"], fg_color=self.COLORS["soft_gray"],
				border_width=1, border_color=self.COLORS["line"],
				font=self.font(9, "bold"), anchor="center", height=42,
				corner_radius=0, wraplength=150
			)
			label.grid(row=0, column=column, padx=(0, 1), pady=(0, 5), sticky="nsew")
			self.preview_widgets.append(label)

		for row_number, values in enumerate(self.preview_rows, start=1):
			line_count = max(
				max(1, sum(max(1, (len(line) + 27) // 28) for line in value.splitlines()))
				for value in values
			)
			row_height = max(48, line_count * 18 + 12)
			row_color = self.COLORS["surface"] if row_number % 2 else "#FAFCFA"
			for column, value in enumerate(values):
				label = ctk.CTkLabel(
					self.preview_scroll, text=value,
					text_color=self.COLORS["ink"], fg_color=row_color,
					border_width=1, border_color=self.COLORS["line"],
					font=self.font(10), anchor="center", justify="center",
					height=row_height, corner_radius=0, wraplength=180
				)
				label.grid(
					row=row_number, column=column,
					padx=(0, 1), pady=(0, 4), sticky="nsew"
				)
				self.preview_widgets.append(label)
		self.export_button.configure(state="normal")

	def export_pdf(self):
		if not self.preview_rows or self.current_report_type is None:
			messagebox.showinfo("No report to export", "Generate a report before exporting.")
			return
		filename = f"furlog_{self.current_report_type.lower().replace(' ', '_')}_{date.today().isoformat()}.pdf"
		file_path = filedialog.asksaveasfilename(
			title="Save FurLog report",
			defaultextension=".pdf",
			initialfile=filename,
			filetypes=(("PDF files", "*.pdf"), ("All files", "*.*"))
		)
		if not file_path:
			return
		from pathlib import Path
		if Path(file_path).exists() and not messagebox.askyesno(
			"Confirm overwrite",
			"That file already exists. Do you want to replace it?"
		):
			return
		try:
			export_report_pdf(
				file_path=file_path,
				report_type=self.current_report_type,
				headers=self.preview_headers,
				rows=self.preview_rows,
				filters=self.applied_filters
			)
		except Exception as error:
			messagebox.showerror("Export PDF failed", str(error))
			return
		messagebox.showinfo("PDF exported", f"Report saved to:\n{file_path}")

	def clear_filters(self):
		self.report_type_menu.set(self.PET_REGISTRY)
		self.pet_menu.set(self.ALL_PETS)
		self.set_date_entry(self.start_date_entry, "")
		self.set_date_entry(self.end_date_entry, "")
		self.update_filter_visibility()
		self.clear_preview("Generate a report to preview its records.")
