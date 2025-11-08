import customtkinter as ctk
from src.gui.create_vm_dialog import CreateVMDialog
from src.gui.control_panel_widget import ControlPanelWidget
from src.gui.vm_list_widget import VMListWidget
from src.models import VMInfo
from src.vm_service import VMService


class MainWindow(ctk.CTk):
    """Main application window."""

    __slots__ = ("_service", "_vm_list", "_control_panel")

    def __init__(self, service: VMService) -> None:
        super().__init__()
        self._service: VMService = service

        self.title("Libvirt VM Manager")
        self.geometry("800x600")

        self._build_ui()
        self._refresh_vm_list()

    def _build_ui(self) -> None:
        """Build main window UI."""
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
        """Create header with title and buttons."""
        header = ctk.CTkFrame(self)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        ctk.CTkLabel(
            header, text="Virtual Machine Manager", font=("Arial", 20, "bold")
        ).pack(side="left", padx=10)

        ctk.CTkButton(header, text="Create VM", command=self._open_create_dialog).pack(
            side="right", padx=10
        )

        ctk.CTkButton(header, text="Refresh", command=self._refresh_vm_list).pack(
            side="right", padx=10
        )

    def _create_vm_list(self) -> None:
        """Create VM list widget."""
        self._vm_list = VMListWidget(self, self._service, self._on_vm_selected)
        self._vm_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    def _create_control_panel(self) -> None:
        """Create control panel widget."""
        self._control_panel = ControlPanelWidget(
            self, self._service, self._refresh_vm_list
        )
        self._control_panel.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

    def _refresh_vm_list(self) -> None:
        """Refresh VM list."""
        self._vm_list.refresh()

    def _on_vm_selected(self, vm: VMInfo) -> None:
        """Handle VM selection."""
        self._control_panel.set_selected_vm(vm)

    def _open_create_dialog(self) -> None:
        """Open VM creation dialog."""
        CreateVMDialog(self, self._service, self._refresh_vm_list)
