import customtkinter as ctk
from src.gui import LibvirtGUI

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = LibvirtGUI()
    app.mainloop()
