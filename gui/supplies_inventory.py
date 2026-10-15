from tkinter import messagebox

import customtkinter as ctk

from managers.inventory_manager import InventoryManager
from models.inventory_item import InventoryItem


class SuppliesInventorySection(ctk.CTkFrame):
	"""Internal inventory and pet-supply assignment section."""

	ALL_CATEGORIES = "All Categories"
	UNIT_OPTIONS = ("pieces", "packs", "bottles", "cans", "kg", "Others")

	def __init__(self, master, colors, font, inventory_manager=None):
		super().__init__(master, fg_color="transparent")
		self.colors = colors
		self.font = font
		self.inventory_manager = inventory_manager or InventoryManager()
		self.selected_item_id = None
		self.item_rows = {}
		self.create_widgets()
		self.refresh_data()

	def create_widgets(self):
		self.grid_columnconfigure(0, weight=1)
		self.create_item_form(self)
		self.create_inventory_table(self)

	def create_item_form(self, parent):
		card = ctk.CTkFrame(
			parent, fg_color=self.colors["surface"], border_width=1,
			border_color=self.colors["line"], corner_radius=12
		)
		card.grid(row=0, column=0, pady=(0, 16), sticky="ew")
		for column in (1, 3):
			card.grid_columnconfigure(column, weight=1)
		ctk.CTkLabel(
			card, text="Supply and inventory item", text_color=self.colors["ink"],
			font=self.font(15, "bold")
		).grid(row=0, column=0, columnspan=4, padx=18, pady=(16, 3), sticky="w")
		ctk.CTkLabel(
			card, text="Manage Food and Vitamin catalog items.",
			text_color=self.colors["muted"], font=self.font(11)
		).grid(row=1, column=0, columnspan=4, padx=18, pady=(0, 10), sticky="w")

		self.name_entry = self.create_entry(card, "Item Name", 2, 0, "Supply name")
		self.category_menu = self.create_option_menu(
			card, "Type", ["Food", "Vitamin"], 2, 2
		)
		self.quantity_entry = self.create_entry(card, "Quantity / Stock", 3, 0, "Whole number")
		self.create_unit_picker(card)

		actions = ctk.CTkFrame(card, fg_color="transparent")
		actions.grid(row=4, column=0, columnspan=4, padx=18, pady=(10, 16), sticky="w")
		self.create_action_button(actions, "Add Item", self.add_item, 0, primary=True)
		self.create_action_button(actions, "Update", self.update_item, 1)
		self.create_action_button(actions, "Clear", self.clear_form, 2)
		self.create_action_button(actions, "Delete", self.delete_item, 3, danger=True)

	def create_unit_picker(self, parent):
		field = ctk.CTkFrame(parent, fg_color="transparent")
		field.grid(row=3, column=2, columnspan=2, padx=(10, 18), pady=5, sticky="ew")
		field.grid_columnconfigure(0, weight=1)
		field.grid_columnconfigure(1, weight=1)
		ctk.CTkLabel(
			field, text="Unit", text_color=self.colors["ink"],
			font=self.font(10, "bold")
		).grid(row=0, column=0, columnspan=2, pady=(0, 4), sticky="w")
		self.unit_menu = ctk.CTkOptionMenu(
			field, values=list(self.UNIT_OPTIONS), height=36, corner_radius=8,
			fg_color=self.colors["soft_gray"], button_color=self.colors["primary"],
			button_hover_color=self.colors["primary_hover"],
			text_color=self.colors["ink"], font=self.font(10),
			dropdown_font=self.font(10), anchor="w", command=self.on_unit_selected
		)
		self.unit_menu.grid(row=1, column=0, sticky="ew")
		self.unit_menu.set(self.UNIT_OPTIONS[0])
		self.unit_other_entry = ctk.CTkEntry(
			field, height=36, corner_radius=8, border_width=1,
			border_color=self.colors["line"], fg_color="#FBFCFB",
			text_color=self.colors["ink"], placeholder_text="Specify unit",
			placeholder_text_color="#A1ADA6", font=self.font(11)
		)
		self.unit_other_entry.grid(row=1, column=1, padx=(6, 0), sticky="ew")
		self.unit_other_entry.grid_remove()

	def on_unit_selected(self, value):
		if value == "Others":
			self.unit_other_entry.grid()
		else:
			self.unit_other_entry.delete(0, "end")
			self.unit_other_entry.grid_remove()

	def create_entry(self, parent, label, row, column, placeholder):
		field = ctk.CTkFrame(parent, fg_color="transparent")
		field.grid(
			row=row, column=column, columnspan=2,
			padx=(18 if column == 0 else 10, 8), pady=5, sticky="ew"
		)
		field.grid_columnconfigure(0, weight=1)
		ctk.CTkLabel(
			field, text=label, text_color=self.colors["ink"],
			font=self.font(10, "bold")
		).grid(row=0, column=0, pady=(0, 4), sticky="w")
		entry = ctk.CTkEntry(
			field, height=36, corner_radius=8, border_width=1,
			border_color=self.colors["line"], fg_color="#FBFCFB",
			text_color=self.colors["ink"], placeholder_text=placeholder,
			placeholder_text_color="#A1ADA6", font=self.font(11)
		)
		entry.grid(row=1, column=0, sticky="ew")
		return entry

	def create_option_menu(self, parent, label, values, row, column):
		field = ctk.CTkFrame(parent, fg_color="transparent")
		field.grid(
			row=row, column=column,
			padx=(18 if column == 0 else 10, 18), pady=5, sticky="ew"
		)
		field.grid_columnconfigure(0, weight=1)
		ctk.CTkLabel(
			field, text=label, text_color=self.colors["ink"],
			font=self.font(10, "bold")
		).grid(row=0, column=0, pady=(0, 4), sticky="w")
		menu = ctk.CTkOptionMenu(
			field, values=values, height=36, corner_radius=8,
			fg_color=self.colors["soft_gray"], button_color=self.colors["primary"],
			button_hover_color=self.colors["primary_hover"],
			text_color=self.colors["ink"], font=self.font(10),
			dropdown_font=self.font(10), anchor="w"
		)
		menu.grid(row=1, column=0, sticky="ew")
		menu.set(values[0])
		return menu

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

	def create_inventory_table(self, parent):
		card = ctk.CTkFrame(
			parent, fg_color=self.colors["surface"], border_width=1,
			border_color=self.colors["line"], corner_radius=12
		)
		card.grid(row=1, column=0, pady=(0, 16), sticky="nsew")
		card.configure(height=320)
		card.grid_propagate(False)
		card.grid_rowconfigure(2, weight=1)
		card.grid_columnconfigure(0, weight=1)
		header = ctk.CTkFrame(card, fg_color="transparent")
		header.grid(row=0, column=0, padx=18, pady=(14, 8), sticky="ew")
		header.grid_columnconfigure(0, weight=1)
		ctk.CTkLabel(
			header, text="Inventory items", text_color=self.colors["ink"],
			font=self.font(15, "bold")
		).grid(row=0, column=0, sticky="w")
		self.count_label = ctk.CTkLabel(
			header, text="0 items", text_color=self.colors["muted"], font=self.font(10)
		)
		self.count_label.grid(row=1, column=0, pady=(2, 0), sticky="w")

		filters = ctk.CTkFrame(header, fg_color="transparent")
		filters.grid(row=0, column=1, rowspan=2, sticky="e")
		self.search_entry = ctk.CTkEntry(
			filters, width=180, height=34, corner_radius=8, border_width=1,
			border_color=self.colors["line"], fg_color="#FBFCFB",
			text_color=self.colors["ink"], placeholder_text="Search inventory...",
			placeholder_text_color="#A1ADA6", font=self.font(10)
		)
		self.search_entry.grid(row=0, column=0, padx=(0, 6))
		self.search_entry.bind("<Return>", lambda _event: self.refresh_items())
		self.category_filter = ctk.CTkOptionMenu(
			filters, values=[self.ALL_CATEGORIES, "Food", "Vitamin"],
			width=132, height=34, corner_radius=8,
			fg_color=self.colors["soft_gray"], button_color=self.colors["primary"],
			button_hover_color=self.colors["primary_hover"],
			text_color=self.colors["ink"], font=self.font(10),
			dropdown_font=self.font(10), command=lambda _value: self.refresh_items()
		)
		self.category_filter.grid(row=0, column=1)
		self.category_filter.set(self.ALL_CATEGORIES)

		self.items_scroll = ctk.CTkScrollableFrame(
			card, fg_color=self.colors["surface"], corner_radius=0,
			scrollbar_button_color=self.colors["line"],
			scrollbar_button_hover_color="#B9CFC1"
		)
		self.items_scroll.grid(row=2, column=0, padx=18, pady=(0, 16), sticky="nsew")
		self.item_columns = (("Item Name", 40), ("Type", 20), ("Quantity", 20), ("Unit", 20))
		for column, (_, weight) in enumerate(self.item_columns):
			self.items_scroll.grid_columnconfigure(column, weight=weight)
		for column, (heading, _) in enumerate(self.item_columns):
			ctk.CTkLabel(
				self.items_scroll, text=heading.upper(),
				text_color=self.colors["muted"], fg_color=self.colors["soft_gray"],
				border_width=1, border_color=self.colors["line"],
				font=self.font(9, "bold"), anchor="center", height=40,
				corner_radius=0
			).grid(row=0, column=column, padx=(0, 1), pady=(0, 4), sticky="nsew")
		self.items_empty_label = ctk.CTkLabel(
			self.items_scroll, text="No inventory items found.",
			text_color=self.colors["muted"], font=self.font(11, "bold")
		)

	def refresh_data(self):
		self.refresh_items(error_title="Load inventory failed")

	def refresh_items(self, error_title="Search inventory failed"):
		category = self.category_filter.get()
		if category == self.ALL_CATEGORIES:
			category = None
		try:
			items = self.inventory_manager.get_items(self.search_entry.get(), category)
		except Exception as error:
			messagebox.showerror(error_title, str(error), parent=self)
			return
		for row_widgets in self.item_rows.values():
			for widget in row_widgets:
				widget.destroy()
		self.item_rows.clear()
		self.count_label.configure(text=f"{len(items)} item" + ("s" if len(items) != 1 else ""))
		if not items:
			self.items_empty_label.grid(row=1, column=0, columnspan=len(self.item_columns), padx=16, pady=30)
		else:
			self.items_empty_label.grid_remove()
		for row, item in enumerate(items, start=1):
			quantity = "Unknown" if item.quantity is None else f"{item.quantity} {item.unit}".strip()
			values = (item.name, item.category, quantity, item.unit)
			widgets = []
			for column, value in enumerate(values):
				label = ctk.CTkLabel(
					self.items_scroll, text=str(value),
					text_color=self.colors["ink"],
					fg_color=self.colors["surface"] if row % 2 else "#FAFCFA",
					border_width=1, border_color=self.colors["line"],
					font=self.font(10),
					anchor="center", height=42, corner_radius=0
				)
				label.grid(row=row, column=column, padx=(0, 1), pady=(0, 3), sticky="nsew")
				label.bind("<Button-1>", lambda _event, selected=item.id: self.select_item(selected))
				widgets.append(label)
			self.item_rows[item.id] = widgets

	def get_form_item(self):
		name = self.name_entry.get().strip()
		category = self.category_menu.get()
		quantity_text = self.quantity_entry.get().strip()
		unit_choice = self.unit_menu.get()
		unit = (
			self.unit_other_entry.get().strip()
			if unit_choice == "Others" else unit_choice
		)
		if not name:
			messagebox.showwarning("Missing item name", "Enter an item name.", parent=self)
			return None
		if not unit and self.selected_item_id is None:
			messagebox.showwarning("Missing unit", "Enter a unit such as bottles, bags, or kg.", parent=self)
			return None
		try:
			quantity = int(quantity_text) if quantity_text else None
			if self.selected_item_id is None and quantity is None:
				raise ValueError("Enter a non-negative quantity for a new item.")
			return InventoryItem(
				item_id=self.selected_item_id, name=name, category=category,
				quantity=quantity, unit=unit
			)
		except ValueError as error:
			messagebox.showwarning("Invalid inventory values", str(error), parent=self)
			return None

	def add_item(self):
		if self.selected_item_id is not None:
			messagebox.showwarning("Clear selection", "Clear the selected item before adding another.", parent=self)
			return
		item = self.get_form_item()
		if item is None:
			return
		try:
			self.inventory_manager.create_item(item)
			self.clear_form()
			self.refresh_data()
		except Exception as error:
			messagebox.showerror("Add inventory item failed", str(error), parent=self)

	def update_item(self):
		if self.selected_item_id is None:
			messagebox.showwarning("Select an item", "Select an inventory item to update.", parent=self)
			return
		item = self.get_form_item()
		if item is None:
			return
		try:
			if self.inventory_manager.update_item(item):
				self.refresh_data()
				self.select_item(item.id)
		except Exception as error:
			messagebox.showerror("Update item failed", str(error), parent=self)

	def select_item(self, item_id):
		item = self.inventory_manager.get_item_by_id(item_id)
		if item is None:
			messagebox.showerror("Item not found", "This inventory item no longer exists.", parent=self)
			self.refresh_data()
			return
		self.selected_item_id = item.id
		self.name_entry.delete(0, "end")
		self.name_entry.insert(0, item.name)
		self.category_menu.set(item.category)
		self.quantity_entry.delete(0, "end")
		if item.quantity is not None:
			self.quantity_entry.insert(0, str(item.quantity))
		if item.unit in self.UNIT_OPTIONS and item.unit != "Others":
			self.unit_menu.set(item.unit)
			self.on_unit_selected(item.unit)
		else:
			self.unit_menu.set("Others")
			self.on_unit_selected("Others")
			self.unit_other_entry.delete(0, "end")
			self.unit_other_entry.insert(0, item.unit)

	def delete_item(self):
		if self.selected_item_id is None:
			messagebox.showwarning("Select an item", "Select an inventory item to delete.", parent=self)
			return
		if not messagebox.askyesno(
			"Delete inventory item",
			"Delete this inventory item? This cannot be undone.",
			parent=self
		):
			return
		try:
			self.inventory_manager.delete_item(self.selected_item_id)
			self.clear_form()
			self.refresh_data()
		except Exception as error:
			messagebox.showerror("Delete inventory item failed", str(error), parent=self)

	def clear_form(self):
		self.selected_item_id = None
		for entry in (self.name_entry, self.quantity_entry, self.unit_other_entry):
			entry.delete(0, "end")
		self.category_menu.set("Food")
		self.unit_menu.set(self.UNIT_OPTIONS[0])
		self.unit_other_entry.grid_remove()
