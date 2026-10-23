import customtkinter as ctk
from tkinter import messagebox

from managers.inventory_manager import InventoryManager
from managers.pet_care_manager import PetCareManager
from models.pet_care import PetCare


class PetCareSection(ctk.CTkFrame):
	"""Internal Pet Management section for pet-specific care information."""

	def __init__(
		self, master, colors, font, care_manager=None, inventory_manager=None
	):
		super().__init__(master, fg_color="transparent")
		self.colors = colors
		self.font = font
		self.care_manager = care_manager or PetCareManager()
		self.inventory_manager = inventory_manager or InventoryManager(
			self.care_manager.database_manager
		)
		self.pet_id_by_option = {}
		self.selected_pet_id = None
		self.has_saved_care = False
		self.assignment_menus = {}
		self.supply_option_to_id = {"Food": {}, "Vitamin": {}}
		self.assigned_item_frames = {}
		self.create_widgets()
		self.refresh_data()

	def create_widgets(self):
		self.grid_columnconfigure(0, weight=1)
		card = ctk.CTkFrame(
			self, fg_color=self.colors["surface"], border_width=1,
			border_color=self.colors["line"], corner_radius=12
		)
		card.grid(row=0, column=0, sticky="ew")
		card.grid_columnconfigure(1, weight=1)
		card.grid_columnconfigure(3, weight=1)
		ctk.CTkLabel(
			card, text="Pet care information", text_color=self.colors["ink"],
			font=self.font(15, "bold")
		).grid(row=0, column=0, columnspan=4, padx=18, pady=(16, 4), sticky="w")
		ctk.CTkLabel(
			card, text="Care details are saved for the selected pet.",
			text_color=self.colors["muted"], font=self.font(11)
		).grid(row=1, column=0, columnspan=4, padx=18, pady=(0, 12), sticky="w")

		ctk.CTkLabel(
			card, text="Selected Pet", text_color=self.colors["ink"],
			font=self.font(11, "bold")
		).grid(row=2, column=0, padx=(18, 8), pady=6, sticky="e")
		self.pet_menu = ctk.CTkOptionMenu(
			card, values=["No pets registered"], height=36, corner_radius=8,
			fg_color=self.colors["soft_gray"], button_color=self.colors["primary"],
			button_hover_color=self.colors["primary_hover"],
			text_color=self.colors["ink"], font=self.font(11),
			dropdown_font=self.font(11), anchor="w",
			command=self.on_pet_selected
		)
		self.pet_menu.grid(row=2, column=1, columnspan=3, padx=(0, 18), pady=6, sticky="ew")

		self.create_supply_assignment(card, "Food", 3)
		self.create_supply_assignment(card, "Vitamin", 5)

		ctk.CTkLabel(
			card, text="Special Care Needs", text_color=self.colors["ink"],
			font=self.font(11, "bold")
		).grid(row=7, column=0, padx=(18, 8), pady=6, sticky="e")
		self.needs_textbox = ctk.CTkTextbox(
			card, height=92, corner_radius=8, border_width=1,
			border_color=self.colors["line"], fg_color="#FBFCFB",
			text_color=self.colors["ink"], font=self.font(11), wrap="word"
		)
		self.needs_textbox.grid(row=7, column=1, columnspan=3, padx=(0, 18), pady=6, sticky="ew")

		ctk.CTkLabel(
			card, text="Care Notes", text_color=self.colors["ink"],
			font=self.font(11, "bold")
		).grid(row=8, column=0, padx=(18, 8), pady=6, sticky="e")
		self.notes_textbox = ctk.CTkTextbox(
			card, height=112, corner_radius=8, border_width=1,
			border_color=self.colors["line"], fg_color="#FBFCFB",
			text_color=self.colors["ink"], font=self.font(11), wrap="word"
		)
		self.notes_textbox.grid(row=8, column=1, columnspan=3, padx=(0, 18), pady=6, sticky="ew")

		actions = ctk.CTkFrame(card, fg_color="transparent")
		actions.grid(row=9, column=0, columnspan=4, padx=18, pady=(12, 10), sticky="w")
		self.create_action_button(actions, "Add", self.add_care, 0, primary=True)
		self.create_action_button(actions, "Update", self.update_care, 1)
		self.create_action_button(actions, "Clear", self.clear_form, 2)
		self.create_action_button(actions, "Delete", self.delete_care, 3, danger=True)
		self.status_label = ctk.CTkLabel(
			card, text="", text_color=self.colors["muted"], font=self.font(10)
		)
		self.status_label.grid(row=10, column=0, columnspan=4, padx=18, pady=(0, 14), sticky="w")

	def create_supply_assignment(self, card, category, row):
		plural = "Foods" if category == "Food" else "Vitamins"
		ctk.CTkLabel(
			card, text=f"Assigned {plural}", text_color=self.colors["ink"],
			font=self.font(11, "bold")
		).grid(row=row, column=0, padx=(18, 8), pady=6, sticky="e")
		menu = ctk.CTkOptionMenu(
			card, values=[f"No {category.lower()} items available"],
			height=36, corner_radius=8,
			fg_color=self.colors["soft_gray"], button_color=self.colors["primary"],
			button_hover_color=self.colors["primary_hover"],
			text_color=self.colors["ink"], font=self.font(10),
			dropdown_font=self.font(10), anchor="w"
		)
		menu.grid(row=row, column=1, columnspan=2, padx=(0, 8), pady=6, sticky="ew")
		self.assignment_menus[category] = menu
		ctk.CTkButton(
			card, text="Assign", command=lambda kind=category: self.assign_supply(kind),
			height=34, width=86, corner_radius=8,
			fg_color=self.colors["soft_green"], hover_color="#D8EBDD",
			text_color=self.colors["primary_hover"], font=self.font(10, "bold")
		).grid(row=row, column=3, padx=(0, 18), pady=6, sticky="e")
		items_frame = ctk.CTkFrame(card, fg_color="transparent")
		items_frame.grid(
			row=row + 1, column=1, columnspan=3,
			padx=(0, 18), pady=(0, 5), sticky="ew"
		)
		items_frame.grid_columnconfigure(0, weight=1)
		self.assigned_item_frames[category] = items_frame

	def create_action_button(self, parent, text, command, column, primary=False, danger=False):
		if primary:
			fg_color, hover_color, text_color = (
				self.colors["primary"], self.colors["primary_hover"], "#FFFFFF"
			)
		elif danger:
			fg_color, hover_color, text_color = "#FFF7F7", "#FBE8E8", self.colors["danger"]
		else:
			fg_color, hover_color, text_color = (
				self.colors["soft_gray"], "#E1E9E3", self.colors["ink"]
			)
		ctk.CTkButton(
			parent, text=text, command=command, height=34, width=94,
			corner_radius=8, fg_color=fg_color, hover_color=hover_color,
			text_color=text_color, font=self.font(11, "bold")
		).grid(row=0, column=column, padx=(0, 8))

	def refresh_data(self):
		try:
			pet_options = self.care_manager.get_pet_options()
		except Exception as error:
			messagebox.showerror("Load pets failed", str(error), parent=self)
			return
		self.pet_id_by_option = {
			f"{species} - {name} (Owner: {owner}) - ID: {pet_id}": pet_id
			for pet_id, name, species, owner in pet_options
		}
		options = list(self.pet_id_by_option) or ["No pets registered"]
		self.refresh_supply_dropdowns()
		previous_id = self.selected_pet_id
		self.pet_menu.configure(values=options)
		if previous_id in self.pet_id_by_option.values():
			option = next(key for key, value in self.pet_id_by_option.items() if value == previous_id)
			self.pet_menu.set(option)
			self.load_selected_pet(previous_id)
		else:
			self.selected_pet_id = None
			self.pet_menu.set(options[0])
			self.clear_values()
			self.refresh_assigned_supplies()
			self.status_label.configure(
				text="Register a pet first to add care information."
				if not pet_options else "Select a pet to view its care information."
			)

	def on_pet_selected(self, option):
		self.selected_pet_id = self.pet_id_by_option.get(option)
		self.load_selected_pet(self.selected_pet_id)
		self.refresh_supply_dropdowns()

	def load_selected_pet(self, pet_id):
		if pet_id is None:
			self.has_saved_care = False
			self.clear_values()
			self.refresh_assigned_supplies()
			return
		try:
			care = self.care_manager.get_for_pet(pet_id)
		except Exception as error:
			messagebox.showerror("Load care information failed", str(error), parent=self)
			return
		self.has_saved_care = care is not None
		self._set_text(self.needs_textbox, care.special_care_needs if care else "")
		self._set_text(self.notes_textbox, care.care_notes if care else "")
		self.status_label.configure(
			text="Care information loaded." if care else "No care information saved for this pet yet."
		)
		self.refresh_assigned_supplies()

	def refresh_supply_dropdowns(self):
		try:
			for category in ("Food", "Vitamin"):
				items = self.inventory_manager.get_items(category=category)
				assigned_ids = {
					row[0] for row in self.inventory_manager.get_pet_assignments(
						self.selected_pet_id, category
					)
				} if self.selected_pet_id is not None else set()
				available_items = [item for item in items if item.id not in assigned_ids]
				previous_option = self.assignment_menus[category].get()
				self.supply_option_to_id[category] = {
					f"{item.name} - ID: {item.id}": item.id
					for item in available_items
				}
				placeholder = f"No {category.lower()} items available"
				options = list(self.supply_option_to_id[category]) or [placeholder]
				menu = self.assignment_menus[category]
				menu.configure(values=options)
				menu.set(previous_option if previous_option in options else options[0])
		except Exception as error:
			messagebox.showerror("Load available supplies failed", str(error), parent=self)

	def refresh_assigned_supplies(self):
		for category, frame in self.assigned_item_frames.items():
			for widget in frame.winfo_children():
				widget.destroy()
			if self.selected_pet_id is None:
				message = "Select a pet to view assigned supplies."
				ctk.CTkLabel(
					frame, text=message, text_color=self.colors["muted"],
					font=self.font(10)
				).grid(row=0, column=0, sticky="w")
				continue
			try:
				items = self.inventory_manager.get_pet_assignments(
					self.selected_pet_id, category
				)
			except Exception as error:
				messagebox.showerror("Load assigned supplies failed", str(error), parent=self)
				continue
			if not items:
				ctk.CTkLabel(
					frame, text=f"No {category.lower()} assigned.",
					text_color=self.colors["muted"], font=self.font(10)
				).grid(row=0, column=0, sticky="w")
				continue
			for row_number, (item_id, name, _item_category, _quantity, _unit) in enumerate(items):
				ctk.CTkLabel(
					frame, text=name, text_color=self.colors["ink"],
					font=self.font(10), anchor="w"
				).grid(row=row_number, column=0, pady=2, sticky="w")
				ctk.CTkButton(
					frame, text="Remove",
					command=lambda selected_id=item_id, kind=category: self.remove_supply(kind, selected_id),
					width=76, height=28, corner_radius=7,
					fg_color=self.colors["soft_gray"], hover_color="#E1E9E3",
					text_color=self.colors["ink"], font=self.font(9, "bold")
				).grid(row=row_number, column=1, padx=(8, 0), pady=2)

	def assign_supply(self, category):
		if self.selected_pet_id is None:
			messagebox.showwarning("Select a pet", "Select a registered pet first.", parent=self)
			return
		item_id = self.supply_option_to_id[category].get(
			self.assignment_menus[category].get()
		)
		if item_id is None:
			messagebox.showwarning(
				"No available supply", f"Add a {category.lower()} item in Supplies & Inventory first.",
				parent=self
			)
			return
		try:
			created = self.inventory_manager.assign_item(
				self.selected_pet_id, item_id, category
			)
			self.refresh_supply_dropdowns()
			self.refresh_assigned_supplies()
			self.status_label.configure(
				text=f"{category} assigned to this pet." if created
				else f"This {category.lower()} is already assigned."
			)
		except Exception as error:
			messagebox.showerror("Assign supply failed", str(error), parent=self)

	def remove_supply(self, category, item_id):
		if not messagebox.askyesno(
			f"Remove assigned {category.lower()}",
			f"Remove this {category.lower()} from the selected pet? The inventory item and quantity will remain unchanged.",
			parent=self
		):
			return
		try:
			self.inventory_manager.unassign_item(self.selected_pet_id, item_id)
			self.refresh_supply_dropdowns()
			self.refresh_assigned_supplies()
			self.status_label.configure(text=f"{category} removed from this pet.")
		except Exception as error:
			messagebox.showerror("Remove supply assignment failed", str(error), parent=self)

	def add_care(self):
		if self.selected_pet_id is None:
			messagebox.showwarning("Select a pet", "Select a registered pet first.", parent=self)
			return
		if self.has_saved_care:
			messagebox.showwarning("Already exists", "Use Update to change this pet's care information.", parent=self)
			return
		self.save_care()

	def update_care(self):
		if self.selected_pet_id is None or not self.has_saved_care:
			messagebox.showwarning("No care information", "Select a pet with saved care information to update.", parent=self)
			return
		self.save_care()

	def save_care(self):
		try:
			care = PetCare(
				self.selected_pet_id,
				self.needs_textbox.get("1.0", "end-1c"),
				self.notes_textbox.get("1.0", "end-1c")
			)
			self.care_manager.save_for_pet(care)
			self.has_saved_care = True
			self.status_label.configure(text="Care information saved.")
		except Exception as error:
			messagebox.showerror("Save care information failed", str(error), parent=self)

	def delete_care(self):
		if self.selected_pet_id is None or not self.has_saved_care:
			messagebox.showwarning("No care information", "Select a pet with saved care information first.", parent=self)
			return
		if not messagebox.askyesno(
			"Delete care information", "Delete the saved care information for this pet?", parent=self
		):
			return
		try:
			self.care_manager.delete_for_pet(self.selected_pet_id)
			self.has_saved_care = False
			self.clear_values()
			self.status_label.configure(text="Care information deleted.")
		except Exception as error:
			messagebox.showerror("Delete care information failed", str(error), parent=self)

	def clear_form(self):
		self.clear_values()
		self.status_label.configure(text="Care form cleared. Choose another pet or reload this pet.")

	def clear_values(self):
		self._set_text(self.needs_textbox, "")
		self._set_text(self.notes_textbox, "")

	@staticmethod
	def _set_text(textbox, value):
		textbox.delete("1.0", "end")
		if value:
			textbox.insert("1.0", value)
