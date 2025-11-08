import sys
import customtkinter as ctk
from src.libvirt_adapter import LibvirtAdapter
from src.vm_service import VMService
from src.gui.main_window import MainWindow


def show_error(message: str) -> None:
    """Display error message in window."""
    root = ctk.CTk()
    root.title("Error")
    root.geometry("400x150")

    ctk.CTkLabel(root, text=message, font=("Arial", 14), text_color="red").pack(
        expand=True
    )

    ctk.CTkButton(root, text="Exit", command=root.destroy).pack(pady=10)
    root.mainloop()


def main() -> None:
    """Application entry point."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    adapter = LibvirtAdapter()
    if not adapter.connect():
        show_error(
            "Failed to connect to libvirt.\nEnsure libvirtd is running and you have permissions."
        )
        sys.exit(1)

    service = VMService(adapter)
    app = MainWindow(service)

    try:
        app.mainloop()
    finally:
        adapter.disconnect()


if __name__ == "__main__":
    main()
