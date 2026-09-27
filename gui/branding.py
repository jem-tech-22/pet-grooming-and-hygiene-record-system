from functools import lru_cache
from pathlib import Path

import customtkinter as ctk
from PIL import Image


LOGO_PATH = Path(__file__).resolve().parent.parent / "assets" / "images" / "furlog-logo.png"


@lru_cache(maxsize=4)
def get_furlog_logo(max_width=176, max_height=45):
	"""Load the FurLog logo scaled within the requested bounds, preserving its ratio."""
	with Image.open(LOGO_PATH) as source:
		logo = source.convert("RGBA")
		logo.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
	return ctk.CTkImage(
		light_image=logo,
		dark_image=logo,
		size=logo.size
	)