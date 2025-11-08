"""Main application window."""

from __future__ import annotations
import customtkinter as ctk
from src.gui.create_vm_dialog import CreateVMDialog
from src.gui.control_panel_widget import ControlPanelWidget
from src.gui.vm_list_widget import VMListWidget
from src.models import VMInfo
from src.vm_service import VMService


class MainWindow(ctk.CTk):
    """Modern main application window."""

    __slots__ = ("_service", "_vm_list", "_control_panel")

    def __init__(
        self, service: VMService, width: int = 1000, height: int = 700
    ) -> None:
        super().__init__()
        self._service: VMService = service

        self.title("Libvirt Manager")
        self.geometry(f"{width}x{height}")
        self.configure(fg_color="#ffffff")

        # Initialize widgets
        self._vm_list: VMListWidget
        self._control_panel: ControlPanelWidget

        self._build_ui()
        self._refresh_vm_list()

    def _build_ui(self) -> None:
        """Build modern main window UI."""
        self._configure_grid()
        self._create_header()
        self._create_vm_list()
        self._create_control_panel()

    def _configure_grid(self) -> None:
        """Configure grid layout."""
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def _create_header(self) -> None:
        """Create modern header."""
        header = ctk.CTkFrame(self, fg_color="#f9fafb", height=80, corner_radius=0)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        header.grid_propagate(False)

        # Title
        ctk.CTkLabel(
            header,
            text="🖥️  Virtual Machines",
            font=("SF Pro Display", 28, "bold"),
            text_color="#111827",
        ).pack(side="left", padx=30, pady=20)

        # Buttons
        button_frame = ctk.CTkFrame(header, fg_color="transparent")
        button_frame.pack(side="right", padx=30)

        ctk.CTkButton(
            button_frame,
            text="+ Create VM",
            font=("SF Pro Display", 13, "bold"),
            fg_color="#3b82f6",
            hover_color="#2563eb",
            height=40,
            corner_radius=10,
            command=self._open_create_dialog,
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            button_frame,
            text="↻ Refresh",
            font=("SF Pro Display", 13),
            fg_color="#e5e7eb",
            hover_color="#d1d5db",
            text_color="#374151",
            height=40,
            corner_radius=10,
            command=self._refresh_vm_list,
        ).pack(side="right", padx=5)

    def _create_vm_list(self) -> None:
        """Create VM list widget."""
        container = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=0)
        container.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

        self._vm_list = VMListWidget(container, self._service, self._on_vm_selected)
        self._vm_list.pack(fill="both", expand=True, padx=20, pady=20)

    def _create_control_panel(self) -> None:
        """Create control panel widget."""
        container = ctk.CTkFrame(self, fg_color="#f9fafb", corner_radius=0)
        container.grid(row=1, column=1, sticky="nsew", padx=0, pady=0)

        self._control_panel = ControlPanelWidget(
            container, self._service, self._refresh_vm_list
        )
        self._control_panel.pack(fill="both", expand=True, padx=20, pady=20)

    def _refresh_vm_list(self) -> None:
        """Refresh VM list."""
        self._vm_list.refresh()

    def _on_vm_selected(self, vm: VMInfo) -> None:
        """Handle VM selection."""
        self._control_panel.set_selected_vm(vm)

    def _open_create_dialog(self) -> None:
        """Open VM creation dialog."""
        dialog = CreateVMDialog(self, self._service, self._refresh_vm_list)
        dialog.focus()
