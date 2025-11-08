import customtkinter as ctk
from collections.abc import Callable
from src.models import VMInfo, VMState
from src.vm_service import VMService


class VMListWidget(ctk.CTkScrollableFrame):
    """Widget for displaying virtual machine list."""

    __slots__ = ("_service", "_on_select", "_buttons")

    _STATE_COLORS: dict[VMState, str] = {
        VMState.RUNNING: "green",
        VMState.SHUTOFF: "gray",
        VMState.PAUSED: "orange",
        VMState.UNKNOWN: "red",
    }

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        service: VMService,
        on_select: Callable[[VMInfo], None],
    ) -> None:
        super().__init__(master)
        self._service: VMService = service
        self._on_select: Callable[[VMInfo], None] = on_select
        self._buttons: list[ctk.CTkButton] = []

    def refresh(self) -> None:
        """Refresh VM list display."""
        self._clear_buttons()
        vms = self._service.list_vms()

        for vm in vms:
            self._create_vm_button(vm)

    def _clear_buttons(self) -> None:
        """Clear all VM buttons."""
        for btn in self._buttons:
            btn.destroy()
        self._buttons.clear()

    def _create_vm_button(self, vm: VMInfo) -> None:
        """Create button for VM."""
        color = self._STATE_COLORS.get(vm.state, "gray")
        btn = ctk.CTkButton(
            self,
            text=f"{vm.name} ({vm.state.value})",
            fg_color=color,
            command=lambda: self._on_select(vm),
        )
        btn.pack(pady=5, padx=10, fill="x")
        self._buttons.append(btn)
