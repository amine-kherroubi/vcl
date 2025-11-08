from __future__ import annotations
import sys
import customtkinter as ctk
from pathlib import Path
from config.settings import AppConfig
from src.utils.logger import AppLogger
from src.libvirt_adapter import LibvirtAdapter
from src.vm_service import VMService
from src.gui.main_window import MainWindow


def show_error(message: str) -> None:
    root = ctk.CTk()
    root.title("Connection Error")
    root.geometry("450x200")
    root.configure(fg_color="#FFFFFF")

    ctk.CTkLabel(
        root,
        text="Connection Error",
        font=("Inter", 20, "bold"),
        text_color="#EF4444",
    ).pack(pady=(30, 10))

    ctk.CTkLabel(
        root,
        text=message,
        font=("Inter", 13),
        text_color="#6B7280",
        wraplength=350,
    ).pack(pady=10)

    ctk.CTkButton(
        root,
        text="Exit",
        font=("Inter", 13, "bold"),
        fg_color="#EF4444",
        hover_color="#DC2626",
        height=40,
        corner_radius=8,
        command=root.destroy,
    ).pack(pady=20)

    root.mainloop()


def main() -> None:
    config_path = Path.home() / ".config" / "libvirt-manager" / "config.json"
    config = AppConfig.load(config_path)

    logger = AppLogger.setup(config.log_file, config.log_level)
    logger.info("Starting Libvirt Manager")

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    adapter = LibvirtAdapter(config.libvirt_uri)
    if not adapter.connect():
        logger.error("Failed to connect to libvirt")
        show_error(
            f"Failed to connect to libvirt.\nEnsure libvirtd is running and you have proper permissions.\nURI: {config.libvirt_uri}"
        )
        sys.exit(1)

    service = VMService(adapter)
    app = MainWindow(service, config.window_width, config.window_height)

    try:
        logger.info("Application started successfully")
        app.mainloop()
    except Exception as e:
        logger.exception("Application error: %s", e)
    finally:
        logger.info("Shutting down application")
        adapter.disconnect()
        config.save(config_path)


if __name__ == "__main__":
    main()
