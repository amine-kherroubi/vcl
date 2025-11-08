"""Application entry point."""

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
    """Display error message in modern window."""
    root = ctk.CTk()
    root.title("Connection Error")
    root.geometry("450x200")
    root.configure(fg_color="#ffffff")

    ctk.CTkLabel(
        root,
        text="⚠️ Connection Error",
        font=("SF Pro Display", 20, "bold"),
        text_color="#ef4444",
    ).pack(pady=(30, 10))

    ctk.CTkLabel(
        root,
        text=message,
        font=("SF Pro Display", 13),
        text_color="#6b7280",
        wraplength=350,
    ).pack(pady=10)

    ctk.CTkButton(
        root,
        text="Exit",
        font=("SF Pro Display", 13, "bold"),
        fg_color="#ef4444",
        hover_color="#dc2626",
        height=40,
        corner_radius=10,
        command=root.destroy,
    ).pack(pady=20)

    root.mainloop()


def main() -> None:
    """Application entry point."""
    # Load configuration
    config_path = Path.home() / ".config" / "libvirt-manager" / "config.json"
    config = AppConfig.load(config_path)

    # Setup logging
    logger = AppLogger.setup(config.log_file, config.log_level)
    logger.info("Starting Libvirt Manager")

    # Setup UI theme
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    # Connect to libvirt
    adapter = LibvirtAdapter(config.libvirt_uri)
    if not adapter.connect():
        logger.error("Failed to connect to libvirt")
        show_error(
            "Failed to connect to libvirt.\n"
            "Ensure libvirtd is running and you have proper permissions.\n"
            f"URI: {config.libvirt_uri}"
        )
        sys.exit(1)

    # Create service and run app
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
