import customtkinter as ctk
from typing import Any
from collections.abc import Callable
from src.control import LibvirtManager, VMInfo, VMState


class VMListFrame(ctk.CTkScrollableFrame):
    """Frame displaying list of virtual machines."""

    __slots__ = ("_manager", "_on_vm_select", "_vm_buttons")

    def __init__(
        self,
        master: Any,
        manager: LibvirtManager,
        on_vm_select: Callable[[VMInfo], None],
    ) -> None:
        super().__init__(master)
        self._manager: LibvirtManager = manager
        self._on_vm_select: Callable[[VMInfo], None] = on_vm_select
        self._vm_buttons: list[ctk.CTkButton] = []

    def refresh(self) -> None:
        """Refresh VM list display."""
        for btn in self._vm_buttons:
            btn.destroy()
        self._vm_buttons.clear()

        vms: list[VMInfo] = self._manager.list_vms()
        for vm in vms:
            color: str = self._get_state_color(vm.state)
            btn = ctk.CTkButton(
                self,
                text=f"{vm.name} ({vm.state.value})",
                fg_color=color,
                command=lambda v=vm: self._on_vm_select(v),
            )
            btn.pack(pady=5, padx=10, fill="x")
            self._vm_buttons.append(btn)

    @staticmethod
    def _get_state_color(state: VMState) -> str:
        """Get color for VM state."""
        colors: dict[VMState, str] = {
            VMState.RUNNING: "green",
            VMState.SHUTOFF: "gray",
            VMState.PAUSED: "orange",
            VMState.UNKNOWN: "red",
        }
        return colors.get(state, "gray")


class VMControlFrame(ctk.CTkFrame):
    """Frame with VM control buttons."""

    def __init__(
        self, master: Any, manager: LibvirtManager, on_action: Callable[[], None]
    ) -> None:
        super().__init__(master)
        self._manager: LibvirtManager = manager
        self._on_action: Callable[[], None] = on_action
        self._selected_vm: VMInfo | None = None

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create control buttons."""
        ctk.CTkButton(self, text="Start", command=self._start_vm).pack(
            pady=5, padx=10, fill="x"
        )

        ctk.CTkButton(self, text="Shutdown", command=self._shutdown_vm).pack(
            pady=5, padx=10, fill="x"
        )

        ctk.CTkButton(self, text="Force Stop", command=self._force_stop_vm).pack(
            pady=5, padx=10, fill="x"
        )

        ctk.CTkButton(
            self, text="Delete", command=self._delete_vm, fg_color="red"
        ).pack(pady=5, padx=10, fill="x")

    def set_selected_vm(self, vm: VMInfo) -> None:
        """Set currently selected VM."""
        self._selected_vm = vm

    def _start_vm(self) -> None:
        if self._selected_vm:
            self._manager.start_vm(self._selected_vm.name)
            self._on_action()

    def _shutdown_vm(self) -> None:
        if self._selected_vm:
            self._manager.shutdown_vm(self._selected_vm.name)
            self._on_action()

    def _force_stop_vm(self) -> None:
        if self._selected_vm:
            self._manager.force_stop_vm(self._selected_vm.name)
            self._on_action()

    def _delete_vm(self) -> None:
        if self._selected_vm:
            self._manager.delete_vm(self._selected_vm.name)
            self._on_action()


class CreateVMDialog(ctk.CTkToplevel):
    """Dialog for creating new virtual machines."""

    def __init__(
        self, master: Any, manager: LibvirtManager, on_create: Callable[[], None]
    ) -> None:
        super().__init__(master)
        self._manager: LibvirtManager = manager
        self._on_create: Callable[[], None] = on_create

        self.title("Create Virtual Machine")
        self.geometry("400x400")

        self._create_widgets()

    def _create_widgets(self) -> None:
        """Create dialog widgets."""
        ctk.CTkLabel(self, text="VM Name:").pack(pady=5)
        self.name_entry: ctk.CTkEntry = ctk.CTkEntry(self, width=300)
        self.name_entry.pack(pady=5)

        ctk.CTkLabel(self, text="Memory (MB):").pack(pady=5)
        self.memory_entry: ctk.CTkEntry = ctk.CTkEntry(self, width=300)
        self.memory_entry.insert(0, "2048")
        self.memory_entry.pack(pady=5)

        ctk.CTkLabel(self, text="vCPUs:").pack(pady=5)
        self.vcpu_entry: ctk.CTkEntry = ctk.CTkEntry(self, width=300)
        self.vcpu_entry.insert(0, "2")
        self.vcpu_entry.pack(pady=5)

        ctk.CTkLabel(self, text="Disk Path:").pack(pady=5)
        self.disk_entry: ctk.CTkEntry = ctk.CTkEntry(self, width=300)
        self.disk_entry.pack(pady=5)

        ctk.CTkLabel(self, text="ISO Path (optional):").pack(pady=5)
        self.iso_entry: ctk.CTkEntry = ctk.CTkEntry(self, width=300)
        self.iso_entry.pack(pady=5)

        ctk.CTkButton(self, text="Create", command=self._create_vm).pack(pady=20)

    def _create_vm(self) -> None:
        """Create VM with specified parameters."""
        name: str = self.name_entry.get()
        memory: int = int(self.memory_entry.get())
        vcpus: int = int(self.vcpu_entry.get())
        disk: str = self.disk_entry.get()
        iso: str | None = self.iso_entry.get() or None

        if self._manager.create_vm(name, memory, vcpus, disk, iso):
            self._on_create()
            self.destroy()


class LibvirtGUI(ctk.CTk):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()

        self.title("Libvirt VM Manager")
        self.geometry("800x600")

        self.manager: LibvirtManager = LibvirtManager()

        if not self.manager.connect():
            self._show_connection_error()
            return

        self._create_widgets()
        self._refresh_vm_list()

    def _create_widgets(self) -> None:
        """Create main window widgets."""
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header: ctk.CTkFrame = ctk.CTkFrame(self)
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

        # VM List
        self.vm_list: VMListFrame = VMListFrame(
            self, self.manager, self._on_vm_selected
        )
        self.vm_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Control Panel
        self.control_panel: VMControlFrame = VMControlFrame(
            self, self.manager, self._refresh_vm_list
        )
        self.control_panel.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

    def _refresh_vm_list(self) -> None:
        """Refresh VM list display."""
        self.vm_list.refresh()

    def _on_vm_selected(self, vm: VMInfo) -> None:
        """Handle VM selection."""
        self.control_panel.set_selected_vm(vm)

    def _open_create_dialog(self) -> None:
        """Open VM creation dialog."""
        CreateVMDialog(self, self.manager, self._refresh_vm_list)

    def _show_connection_error(self) -> None:
        """Display connection error message."""
        ctk.CTkLabel(
            self,
            text="Failed to connect to libvirt",
            font=("Arial", 16),
            text_color="red",
        ).pack(expand=True)

    def destroy(self) -> None:
        """Clean up on application exit."""
        self.manager.disconnect()
        super().destroy()


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app: LibvirtGUI = LibvirtGUI()
    app.mainloop()
