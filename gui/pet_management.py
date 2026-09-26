import customtkinter as ctk
from datetime import datetime
from tkinter import messagebox

from managers.pet_manager import PetManager
from models.pet import Pet


class PetManagement(ctk.CTkFrame):
    """Polished FurLog pet-management page backed by PetManager."""

    COLORS = {
        "canvas": "#F4F7F4",
        "sidebar": "#173B2F",
        "sidebar_muted": "#A7C5B7",
        "sidebar_active": "#2E7354",
        "primary": "#2F8F63",
        "primary_hover": "#267650",
        "ink": "#17231E",
        "muted": "#718079",
        
        "line": "#DDE6E0",
        "surface": "#FFFFFF",
        "soft_green": "#E7F3EC",
        "soft_gray": "#EEF2EF",
        "danger": "#B95050"
    }
    FONT_FAMILY = "Quicksand"
    TABLE_COLUMNS = (
        ("No.", 5),
        ("Pet name", 15),
        ("Species", 10),
        ("Breed", 13),
        ("Age", 6),
        ("Owner", 12),
        ("Vitamins", 13),
        ("Foods", 13),
        ("Needs", 13),
        ("Action", 15)
    )
    TABLE_ROW_HEIGHT = 52

    def __init__(self, master, pet_manager=None):
        super().__init__(master, fg_color=self.COLORS["canvas"])
        self.pet_manager = pet_manager or PetManager()
        self.selected_pet_id = None
        self.entries = {}
        self.metric_labels = {}
        self.pet_rows = {}

        self.create_widgets()
        try:
            self.load_pets()
        except Exception as error:
            messagebox.showerror("Load pets failed", str(error))

    def font(self, size, weight="normal"):
        return ctk.CTkFont(family=self.FONT_FAMILY, size=size, weight=weight)

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
        sidebar.grid_rowconfigure(5, weight=0)

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

        self.create_nav_button(sidebar, "Dashboard", False, 1)
        self.create_nav_button(sidebar, "Pet Record", True, 2)
        self.create_nav_button(sidebar, "Owners", False, 3)
        self.create_nav_button(sidebar, "Grooming Records", False, 4)
        self.create_nav_button(sidebar, "Reports & History", False, 5)
        sidebar.grid_rowconfigure(6, weight=1)

    def create_nav_button(self, parent, text, active, row):
        button = ctk.CTkButton(
            parent, text=f"   {text}", anchor="w", height=40, corner_radius=9,
            fg_color=self.COLORS["sidebar_active"] if active else "transparent",
            hover_color="#255A45",
            text_color="#FFFFFF" if active else self.COLORS["sidebar_muted"],
            font=self.font(12, "bold" if active else "normal"),
            state="normal" if active else "disabled"
        )
        button.grid(row=row, column=0, padx=14, pady=2, sticky="ew")

    def create_content(self):
        content = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=self.COLORS["line"],
            scrollbar_button_hover_color="#B9CFC1"
        )
        content.grid(row=0, column=1, padx=(30, 34), pady=(26, 28), sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(4, weight=1)

        header = ctk.CTkFrame(content, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            header, text="PET RECORDS", text_color=self.COLORS["primary"],
            font=self.font(10, "bold")
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            header, text="Manage your furry clients", text_color=self.COLORS["ink"],
            font=self.font(28, "bold")
        ).grid(row=1, column=0, pady=(3, 0), sticky="w")
        ctk.CTkLabel(
            header,
            text="Keep every pet profile accurate and ready for their next visit.",
            text_color=self.COLORS["muted"], font=self.font(12)
        ).grid(row=2, column=0, pady=(3, 0), sticky="w")
        ctk.CTkButton(
            header, text="+  Add pet", command=self.focus_new_pet, width=118,
            height=38, corner_radius=9, fg_color=self.COLORS["primary"],
            hover_color=self.COLORS["primary_hover"], text_color="#FFFFFF",
            font=self.font(12, "bold")
        ).grid(row=1, column=1, rowspan=2, padx=(20, 0), sticky="e")

        self.create_metrics(content)
        self.create_form_card(content)
        self.create_table_card(content)

    def create_metrics(self, parent):
        metrics = ctk.CTkFrame(parent, fg_color="transparent")
        metrics.grid(row=1, column=0, pady=(25, 20), sticky="ew")
        for column in range(3):
            metrics.grid_columnconfigure(column, weight=1)

        metric_data = [
            ("total", "TOTAL PETS", "0", "All registered profiles"),
            ("species", "SPECIES", "0", "Distinct pet types"),
            ("owners", "OWNERS", "0", "People represented")
        ]
        for column, (key, title, value, description) in enumerate(metric_data):
            card = ctk.CTkFrame(
                metrics, fg_color=self.COLORS["surface"], border_width=1,
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
            self.metric_labels[key] = value_label
            ctk.CTkLabel(
                card, text=description, text_color=self.COLORS["muted"],
                font=self.font(10)
            ).grid(row=2, column=0, padx=16, pady=(0, 14), sticky="w")

    def create_form_card(self, parent):
        form_card = ctk.CTkFrame(
            parent, fg_color=self.COLORS["surface"], border_width=1,
            border_color=self.COLORS["line"], corner_radius=12
        )
        form_card.grid(row=2, column=0, pady=(0, 18), sticky="ew")
        form_card.grid_columnconfigure(1, weight=1)
        form_card.grid_columnconfigure(3, weight=1)
        ctk.CTkLabel(
            form_card, text="Pet information", text_color=self.COLORS["ink"],
            font=self.font(15, "bold")
        ).grid(row=0, column=0, columnspan=4, padx=18, pady=(16, 3), sticky="w")
        ctk.CTkLabel(
            form_card, text="Select a row below to edit an existing profile.",
            text_color=self.COLORS["muted"], font=self.font(11)
        ).grid(row=1, column=0, columnspan=4, padx=18, pady=(0, 12), sticky="w")

        fields = [
            ("Name", 2, 0, "Pet name"), ("Species", 2, 2, "e.g. Dog"),
            ("Breed", 3, 0, "Breed or mix"), ("Age", 3, 2, "Years"),
            ("Owner", 4, 0, "Owner name"),
            ("Vitamins", 4, 2, "Vitamins or supplements"),
            ("Foods", 5, 0, "Food information"),
            ("Needs", 5, 2, "Special care needs")
        ]
        for field_name, row, column, placeholder in fields:
            ctk.CTkLabel(
                form_card, text=field_name, text_color=self.COLORS["ink"],
                font=self.font(11, "bold")
            ).grid(row=row, column=column, padx=(18, 8), pady=6, sticky="e")
            entry = ctk.CTkEntry(
                form_card, height=36, corner_radius=8, border_width=1,
                border_color=self.COLORS["line"], fg_color="#FBFCFB",
                text_color=self.COLORS["ink"], placeholder_text=placeholder,
                placeholder_text_color="#A1ADA6", font=self.font(11)
            )
            entry.grid(row=row, column=column + 1, padx=(0, 18), pady=6, sticky="ew")
            self.entries[field_name.lower()] = entry

        actions = ctk.CTkFrame(form_card, fg_color="transparent")
        actions.grid(row=6, column=0, columnspan=4, padx=18, pady=(12, 17), sticky="w")
        self.create_action_button(actions, "Add pet", self.add_pet, 0, True)
        self.create_action_button(actions, "Update", self.update_pet, 1)
        self.create_action_button(actions, "Clear", self.clear_fields, 2)
        self.create_action_button(actions, "Delete", self.delete_pet, 3, danger=True)

    def create_action_button(self, parent, text, command, column, primary=False, danger=False):
        if primary:
            fg_color, hover_color, text_color = (
                self.COLORS["primary"], self.COLORS["primary_hover"], "#FFFFFF"
            )
        elif danger:
            fg_color, hover_color, text_color = "#FFF7F7", "#FBE8E8", self.COLORS["danger"]
        else:
            fg_color, hover_color, text_color = (
                self.COLORS["soft_gray"], "#E1E9E3", self.COLORS["ink"]
            )
        ctk.CTkButton(
            parent, text=text, command=command, height=34, width=94,
            corner_radius=8, fg_color=fg_color, hover_color=hover_color,
            text_color=text_color, font=self.font(11, "bold")
        ).grid(row=0, column=column, padx=(0, 8))

    def create_table_card(self, parent):
        table_card = ctk.CTkFrame(
            parent, fg_color=self.COLORS["surface"], border_width=1,
            border_color=self.COLORS["line"], corner_radius=12
        )
        table_card.grid(row=4, column=0, sticky="nsew")
        table_card.configure(height=300)
        table_card.grid_propagate(False)
        table_card.grid_rowconfigure(2, weight=1)
        table_card.grid_columnconfigure(0, weight=1)

        table_header = ctk.CTkFrame(table_card, fg_color="transparent")
        table_header.grid(row=0, column=0, padx=18, pady=(16, 10), sticky="ew")
        table_header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            table_header, text="Registered pets", text_color=self.COLORS["ink"],
            font=self.font(15, "bold")
        ).grid(row=0, column=0, sticky="w")
        self.result_label = ctk.CTkLabel(
            table_header, text="0 profiles", text_color=self.COLORS["muted"],
            font=self.font(10)
        )
        self.result_label.grid(row=1, column=0, pady=(2, 0), sticky="w")

        search_box = ctk.CTkFrame(table_header, fg_color="transparent")
        search_box.grid(row=0, column=1, rowspan=2, sticky="e")
        self.search_entry = ctk.CTkEntry(
            search_box, width=190, height=34, corner_radius=8, border_width=1,
            border_color=self.COLORS["line"], fg_color="#FBFCFB",
            placeholder_text="Search pets...", placeholder_text_color="#A1ADA6",
            font=self.font(11)
        )
        self.search_entry.grid(row=0, column=0, padx=(0, 7))
        self.search_entry.bind("<Return>", lambda event: self.search_pets())
        ctk.CTkButton(
            search_box, text="Search", command=self.search_pets, width=74,
            height=34, corner_radius=8, fg_color=self.COLORS["soft_green"],
            hover_color="#D8EBDD", text_color=self.COLORS["primary_hover"],
            font=self.font(11, "bold")
        ).grid(row=0, column=1)

        self.results_scroll = ctk.CTkScrollableFrame(
            table_card,
            fg_color=self.COLORS["surface"],
            corner_radius=0,
            scrollbar_button_color=self.COLORS["line"],
            scrollbar_button_hover_color="#B9CFC1"
        )
        self.results_scroll.grid(row=2, column=0, padx=18, pady=(0, 18), sticky="nsew")
        for column, (_, weight) in enumerate(self.TABLE_COLUMNS):
            self.results_scroll.grid_columnconfigure(column, weight=weight)

        for column, (heading, _) in enumerate(self.TABLE_COLUMNS):
            ctk.CTkLabel(
                self.results_scroll,
                text=heading.upper(),
                text_color=self.COLORS["muted"],
                fg_color=self.COLORS["soft_gray"],
                border_width=1,
                border_color=self.COLORS["line"],
                font=self.font(9, "bold"),
                anchor="center",
                height=48,
                corner_radius=0
            ).grid(
                row=0,
                column=column,
                padx=(0, 1),
                pady=(0, 5),
                sticky="nsew"
            )
        self.empty_state_label = ctk.CTkLabel(
            self.results_scroll,
            text="No pets found",
            text_color=self.COLORS["muted"],
            font=self.font(12, "bold")
        )

    def focus_new_pet(self):
        self.clear_fields()
        self.entries["name"].focus_set()

    def load_pets(self, pets=None):
        """Load pets into the table and refresh the summary metrics."""
        if pets is None:
            pets = self.pet_manager.get_all_pets()
        pets = list(pets)
        for row_widgets in self.pet_rows.values():
            for widget in row_widgets:
                widget.destroy()
        self.pet_rows.clear()

        for row_number, pet in enumerate(pets):
            self.create_pet_row(row_number, pet)
        if pets:
            self.empty_state_label.grid_remove()
        else:
            self.empty_state_label.grid(
                row=1, column=0, columnspan=len(self.TABLE_COLUMNS), padx=20, pady=38
            )
        self.update_metrics(pets)
        result_text = (
            f"{len(pets)} profile{'s' if len(pets) != 1 else ''}"
            if pets else "No pets found"
        )
        self.result_label.configure(text=result_text)

    def create_pet_row(self, row_number, pet):
        row_color = self.COLORS["surface"] if row_number % 2 == 0 else "#FAFCFA"
        values = (
            row_number + 1,
            self.truncate_text(pet.name, 18),
            self.truncate_text(pet.species, 14),
            self.truncate_text(pet.breed or "-", 20),
            pet.age,
            self.truncate_text(pet.owner, 20),
            self.truncate_text(pet.vitamins or "-", 18),
            self.truncate_text(pet.foods or "-", 18),
            self.truncate_text(pet.needs or "-", 18)
        )
        row_widgets = []
        for column, value in enumerate(values):
            is_centered = column in (3, 4, 5)
            value_label = ctk.CTkLabel(
                self.results_scroll,
                text=str(value),
                text_color=self.COLORS["ink"],
                fg_color=row_color,
                border_width=1,
                border_color=self.COLORS["line"],
                font=self.font(11),
                anchor="center" if is_centered else "center",
                height=self.TABLE_ROW_HEIGHT,
                corner_radius=0
            )
            value_label.grid(
                row=row_number + 1,
                column=column,
                padx=(0, 1),
                pady=(0, 5),
                sticky="nsew"
            )
            value_label.bind(
                "<Button-1>",
                lambda event, pet_id=pet.id: self.select_pet(pet_id)
            )
            value_label.bind(
                "<Enter>",
                lambda event, target=row_widgets: self.set_row_hover(target, True)
            )
            value_label.bind(
                "<Leave>",
                lambda event, target=row_widgets: self.set_row_hover(target, False)
            )
            row_widgets.append(value_label)

        action_button = ctk.CTkButton(
            self.results_scroll,
            text="View Details",
            command=lambda pet_id=pet.id: self.open_details_modal(pet_id),
            width=116,
            height=29,
            corner_radius=7,
            fg_color=self.COLORS["soft_green"],
            hover_color="#D8EBDD",
            text_color=self.COLORS["primary_hover"],
            font=self.font(10, "bold")
        )
        action_button.grid(
            row=row_number + 1,
            column=len(self.TABLE_COLUMNS) - 1,
            padx=(0, 1),
            pady=(0, 5),
            sticky="nsew"
        )
        row_widgets.append(action_button)
        self.pet_rows[pet.id] = row_widgets

    @staticmethod
    def truncate_text(value, max_length):
        value = str(value)
        if len(value) <= max_length:
            return value
        return f"{value[:max_length - 3]}..."

    def set_row_hover(self, row_widgets, is_hovered):
        for widget in row_widgets:
            if widget.winfo_exists() and isinstance(widget, ctk.CTkLabel):
                widget.configure(
                    fg_color="#F1F8F3" if is_hovered else self.COLORS["surface"]
                )

    def update_metrics(self, pets):
        self.metric_labels["total"].configure(text=str(len(pets)))
        self.metric_labels["species"].configure(
            text=str(len({pet.species.lower() for pet in pets}))
        )
        self.metric_labels["owners"].configure(
            text=str(len({pet.owner.lower() for pet in pets}))
        )

    def get_form_values(self):
        """Return validated form values or None when validation fails."""
        name = self.entries["name"].get().strip()
        species = self.entries["species"].get().strip()
        breed = self.entries["breed"].get().strip()
        age_text = self.entries["age"].get().strip()
        owner = self.entries["owner"].get().strip()
        vitamins = self.entries["vitamins"].get().strip()
        foods = self.entries["foods"].get().strip()
        needs = self.entries["needs"].get().strip()
        if not name or not species or not owner:
            messagebox.showwarning(
                "Missing information", "Name, Species, and Owner are required."
            )
            return None
        if not age_text:
            messagebox.showwarning("Invalid age", "Please enter a pet age.")
            return None
        try:
            age = int(age_text)
            if age < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Invalid age", "Age must be a non-negative whole number."
            )
            return None
        return name, species, breed, age, owner, vitamins, foods, needs

    def add_pet(self):
        values = self.get_form_values()
        if values is None:
            return
        try:
            pet = Pet(
                name=values[0], species=values[1], breed=values[2],
                age=values[3], owner=values[4], vitamins=values[5],
                foods=values[6], needs=values[7]
            )
            self.pet_manager.create_pet(pet)
            self.load_pets()
            self.clear_fields()
            messagebox.showinfo("Pet added", "The pet profile was added successfully.")
        except Exception as error:
            messagebox.showerror("Add pet failed", str(error))

    def update_pet(self):
        if self.selected_pet_id is None:
            messagebox.showwarning("No pet selected", "Select a pet to update.")
            return
        values = self.get_form_values()
        if values is None:
            return
        try:
            pet = Pet(
                id=self.selected_pet_id, name=values[0], species=values[1],
                breed=values[2], age=values[3], owner=values[4],
                vitamins=values[5], foods=values[6], needs=values[7]
            )
            if self.pet_manager.update_pet(pet):
                self.load_pets()
                self.clear_fields()
                messagebox.showinfo("Pet updated", "The pet profile was updated successfully.")
            else:
                messagebox.showerror("Update failed", "The selected pet was not found.")
        except Exception as error:
            messagebox.showerror("Update pet failed", str(error))

    def delete_pet(self):
        if self.selected_pet_id is None:
            messagebox.showwarning("No pet selected", "Select a pet to delete.")
            return
        if not messagebox.askyesno(
            "Delete pet", "Are you sure you want to delete this pet profile?"
        ):
            return
        try:
            if self.pet_manager.delete_pet(self.selected_pet_id):
                self.load_pets()
                self.clear_fields()
                messagebox.showinfo("Pet deleted", "The pet profile was deleted.")
            else:
                messagebox.showerror("Delete failed", "The selected pet was not found.")
        except Exception as error:
            messagebox.showerror("Delete pet failed", str(error))

    def search_pets(self):
        search_term = self.search_entry.get().strip()
        try:
            pets = (
                self.pet_manager.search_pets(search_term)
                if search_term else self.pet_manager.get_all_pets()
            )
            self.clear_fields()
            self.load_pets(pets)
        except Exception as error:
            messagebox.showerror("Search failed", str(error))

    @staticmethod
    def format_ph_time(value):
        if value is None or value == "":
            return "Not available"

        try:
            if isinstance(value, datetime):
                dt = value
            else:
                normalized = str(value).strip()
                dt = datetime.fromisoformat(normalized.replace("Z", "+00:00"))

            if dt.tzinfo is not None:
                dt = dt.astimezone()
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                dt = datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S")
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                return str(value)

    def open_details_modal(self, pet_id):
        """Open complete details for the pet identified by its database ID."""
        try:
            pet = self.pet_manager.get_pet_by_id(pet_id)
            if pet is None:
                messagebox.showerror("Selection failed", "The selected pet was not found.")
                return

            modal = ctk.CTkToplevel(self)
            modal.title(f"{pet.name} - Pet details")
            modal.geometry("500x590")
            modal.minsize(440, 500)
            modal.configure(fg_color=self.COLORS["canvas"])
            modal.transient(self.winfo_toplevel())
            modal.grab_set()
            modal.protocol("WM_DELETE_WINDOW", lambda: self.close_details_modal(modal))
            modal.grid_columnconfigure(0, weight=1)
            modal.grid_rowconfigure(0, weight=1)

            modal_card = ctk.CTkFrame(
                modal,
                fg_color=self.COLORS["surface"],
                border_width=1,
                border_color=self.COLORS["line"],
                corner_radius=18
            )
            modal_card.grid(row=0, column=0, padx=18, pady=18, sticky="nsew")
            modal_card.grid_columnconfigure(0, weight=1)
            modal_card.grid_rowconfigure(2, weight=1)

            accent = ctk.CTkFrame(
                modal_card, height=7, corner_radius=4,
                fg_color=self.COLORS["primary"]
            )
            accent.grid(row=0, column=0, padx=22, pady=(20, 18), sticky="ew")

            heading = ctk.CTkFrame(modal_card, fg_color="transparent")
            heading.grid(row=1, column=0, padx=24, sticky="ew")
            ctk.CTkLabel(
                heading,
                text="PET PROFILE",
                text_color=self.COLORS["primary"],
                font=self.font(10, "bold")
            ).grid(row=0, column=0, sticky="w")
            ctk.CTkLabel(
                heading,
                text=pet.name,
                text_color=self.COLORS["ink"],
                font=self.font(25, "bold")
            ).grid(row=1, column=0, pady=(3, 0), sticky="w")
            ctk.CTkLabel(
                heading,
                text="Complete information from the local record",
                text_color=self.COLORS["muted"],
                font=self.font(11)
            ).grid(row=2, column=0, pady=(3, 0), sticky="w")

            details = ctk.CTkScrollableFrame(
                modal_card,
                fg_color="transparent",
                scrollbar_button_color=self.COLORS["line"],
                scrollbar_button_hover_color="#B9CFC1"
            )
            details.grid(row=2, column=0, padx=24, pady=(18, 10), sticky="nsew")
            detail_values = [
                ("Species", pet.species),
                ("Breed", pet.breed or "Not specified"),
                ("Age", f"{pet.age} year{'s' if pet.age != 1 else ''}"),
                ("Owner", pet.owner),
                ("Vitamins", pet.vitamins or "Not specified"),
                ("Foods", pet.foods or "Not specified"),
                ("Needs", pet.needs or "Not specified"),
                ("Created at", self.format_ph_time(pet.created_at))
            ]
            for row_number, (label, value) in enumerate(detail_values):
                detail_row = ctk.CTkFrame(
                    details,
                    fg_color=self.COLORS["soft_gray"] if row_number % 2 == 0 else "#FAFCFA",
                    corner_radius=8
                )
                detail_row.grid(row=row_number, column=0, pady=(0, 7), sticky="ew")
                detail_row.grid_columnconfigure(0, weight=1)
                detail_row.grid_columnconfigure(1, weight=2)

                ctk.CTkLabel(
                    detail_row,
                    text=label.upper(),
                    text_color=self.COLORS["muted"],
                    font=self.font(9, "bold"),
                    anchor="center",
                    justify="center"
                ).grid(row=0, column=0, padx=12, pady=11, sticky="ew")

                value_label = ctk.CTkLabel(
                    detail_row,
                    text=str(value),
                    text_color=self.COLORS["ink"],
                    font=self.font(11, "bold"),
                    anchor="center",
                    justify="center",
                    width=210
                )
                value_label.grid(row=0, column=1, padx=12, pady=11, sticky="ew")

            actions = ctk.CTkFrame(modal_card, fg_color="transparent")
            actions.grid(row=3, column=0, padx=24, pady=(8, 24), sticky="ew")
            actions.grid_columnconfigure(0, weight=1)
            actions.grid_columnconfigure(1, weight=1)
            actions.grid_columnconfigure(2, weight=1)
            ctk.CTkButton(
                actions,
                text="Edit pet",
                command=lambda: self.edit_from_modal(modal, pet.id),
                height=36,
                corner_radius=8,
                fg_color=self.COLORS["primary"],
                hover_color=self.COLORS["primary_hover"],
                text_color="#FFFFFF",
                font=self.font(11, "bold")
            ).grid(row=0, column=0, padx=(0, 6), sticky="ew")
            ctk.CTkButton(
                actions,
                text="Delete pet",
                command=lambda: self.delete_from_modal(modal, pet.id),
                height=36,
                corner_radius=8,
                fg_color="#FFF7F7",
                hover_color="#FBE8E8",
                text_color=self.COLORS["danger"],
                font=self.font(11, "bold")
            ).grid(row=0, column=1, padx=6, sticky="ew")
            ctk.CTkButton(
                actions,
                text="Close",
                command=lambda: self.close_details_modal(modal),
                height=36,
                corner_radius=8,
                fg_color=self.COLORS["soft_gray"],
                hover_color="#E1E9E3",
                text_color=self.COLORS["ink"],
                font=self.font(11, "bold")
            ).grid(row=0, column=2, padx=(6, 0), sticky="ew")

            modal.update_idletasks()
            parent = self.winfo_toplevel()
            x_position = parent.winfo_rootx() + max(
                (parent.winfo_width() - modal.winfo_width()) // 2, 0
            )
            y_position = parent.winfo_rooty() + max(
                (parent.winfo_height() - modal.winfo_height()) // 2, 0
            )
            modal.geometry(f"+{x_position}+{y_position}")
        except Exception as error:
            messagebox.showerror("View details failed", str(error))

    def close_details_modal(self, modal):
        if modal.winfo_exists():
            modal.grab_release()
            modal.destroy()

    def edit_from_modal(self, modal, pet_id):
        self.close_details_modal(modal)
        self.load_pet_into_form(pet_id)

    def delete_from_modal(self, modal, pet_id):
        self.close_details_modal(modal)
        self.selected_pet_id = pet_id
        self.delete_pet()

    def load_pet_into_form(self, pet_id):
        try:
            pet = self.pet_manager.get_pet_by_id(pet_id)
            if pet is None:
                messagebox.showerror("Selection failed", "The selected pet was not found.")
                return
            self.selected_pet_id = pet.id
            self.set_entry_value("name", pet.name)
            self.set_entry_value("species", pet.species)
            self.set_entry_value("breed", pet.breed)
            self.set_entry_value("age", pet.age)
            self.set_entry_value("owner", pet.owner)
            self.set_entry_value("vitamins", pet.vitamins)
            self.set_entry_value("foods", pet.foods)
            self.set_entry_value("needs", pet.needs)
            for row_widgets in self.pet_rows.values():
                self.set_row_border(row_widgets, self.COLORS["line"])
            self.set_row_border(self.pet_rows[pet.id], self.COLORS["primary"])
            self.entries["name"].focus_set()
        except Exception as error:
            messagebox.showerror("Selection failed", str(error))

    def select_pet(self, pet_id):
        """Load a pet into the form using its database ID."""
        self.load_pet_into_form(pet_id)

    def set_entry_value(self, field_name, value):
        entry = self.entries[field_name]
        entry.delete(0, "end")
        entry.insert(0, str(value))

    @staticmethod
    def set_row_border(row_widgets, color):
        for widget in row_widgets:
            if isinstance(widget, ctk.CTkLabel):
                widget.configure(border_color=color)

    def clear_fields(self):
        self.selected_pet_id = None
        for entry in self.entries.values():
            entry.delete(0, "end")
        for row_widgets in self.pet_rows.values():
            self.set_row_border(row_widgets, self.COLORS["line"])


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")
    root = ctk.CTk()
    root.title("FurLog - Pet Records")
    root.geometry("1180x800")
    root.minsize(900, 650)
    pet_management = PetManagement(root)
    pet_management.pack(fill="both", expand=True)
    root.mainloop()