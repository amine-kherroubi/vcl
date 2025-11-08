from __future__ import annotations
import customtkinter as ctk
from src.gui.create_vm_dialog import CreateVMDialog
from src.gui.control_panel_widget import ControlPanelWidget
from src.gui.vm_list_widget import VMListWidget
from src.models import VMInfo
from src.vm_service import VMService


class MainWindow(ctk.CTk):
    __slots__ = ("_service", "_vm_list", "_control_panel", "_status_label")

    def __init__(
        self, service: VMService, width: int = 1000, height: int = 700
    ) -> None:
        super().__init__()
        self._service: VMService = service

        self.title("Libvirt Manager")
        self.geometry(f"{width}x{height}")
        self.configure(fg_color="#FFFFFF")

        self._vm_list: VMListWidget
        self._control_panel: ControlPanelWidget
        self._status_label: ctk.CTkLabel

        self._build_ui()
        self._refresh_vm_list()

    def _build_ui(self) -> None:
        self._configure_grid()
        self._create_header()
        self._create_status_bar()
        self._create_vm_list()
        self._create_control_panel()

    def _configure_grid(self) -> None:
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

    def _create_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="#FAFAFA", height=70, corner_radius=0)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        header.grid_propagate(False)

        ctk.CTkLabel(
            header,
            text="Virtual Machines",
            font=("Inter", 24, "bold"),
            text_color="#0F0F0F",
        ).pack(side="left", padx=30, pady=20)

        button_frame = ctk.CTkFrame(header, fg_color="transparent")
        button_frame.pack(side="right", padx=30)

        ctk.CTkButton(
            button_frame,
            text="Create VM",
            font=("Inter", 13, "bold"),
            fg_color="#0F0F0F",
            hover_color="#262626",
            height=38,
            corner_radius=6,
            command=self._open_create_dialog,
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Refresh",
            font=("Inter", 13),
            fg_color="#E5E5E5",
            hover_color="#D4D4D4",
            text_color="#0F0F0F",
            height=38,
            corner_radius=6,
            command=self._refresh_vm_list,
        ).pack(side="right", padx=5)

    def _create_vm_list(self) -> None:
        container = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=0)
        container.grid(row=2, column=0, sticky="nsew", padx=0, pady=0)

        self._vm_list = VMListWidget(container, self._service, self._on_vm_selected)
        self._vm_list.pack(fill="both", expand=True, padx=20, pady=20)

    def _create_control_panel(self) -> None:
        container = ctk.CTkFrame(self, fg_color="#FAFAFA", corner_radius=0)
        container.grid(row=2, column=1, sticky="nsew", padx=0, pady=0)

        self._control_panel = ControlPanelWidget(
            container, self._service, self._refresh_vm_list
        )
        self._control_panel.pack(fill="both", expand=True, padx=20, pady=20)

    def _create_status_bar(self) -> None:
        status = ctk.CTkFrame(self, fg_color="#F5F5F5", height=32, corner_radius=0)
        status.grid(row=1, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
        status.grid_propagate(False)

        self._status_label = ctk.CTkLabel(
            status,
            text="Ready",
            font=("Inter", 11),
            text_color="#737373",
            anchor="w",
        )
        self._status_label.pack(side="left", padx=20)

    def _refresh_vm_list(self) -> None:
        self._status_label.configure(text="Refreshing...")
        self.update_idletasks()
        self._vm_list.refresh()
        vm_count = len(self._service.list_vms())
        self._status_label.configure(text=f"Ready - {vm_count} VMs")

    def _on_vm_selected(self, vm: VMInfo) -> None:
        self._control_panel.set_selected_vm(vm)

    def _open_create_dialog(self) -> None:
        dialog = CreateVMDialog(self, self._service, self._refresh_vm_list)
        dialog.focus()
