import customtkinter as ctk
from collections.abc import Callable
from src.models import VMInfo
from src.vm_service import VMService


class ControlPanelWidget(ctk.CTkFrame):
    """Widget for VM control operations."""

    __slots__ = ("_service", "_on_action", "_selected_vm")

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        service: VMService,
        on_action: Callable[[], None],
    ) -> None:
        super().__init__(master)
        self._service: VMService = service
        self._on_action: Callable[[], None] = on_action
        self._selected_vm: VMInfo | None = None
        self._build_ui()

    def set_selected_vm(self, vm: VMInfo) -> None:
        """Set currently selected VM."""
        self._selected_vm = vm

    def _build_ui(self) -> None:
        """Build control panel UI."""
        buttons = [
            ("Start", self._start_vm, None),
            ("Shutdown", self._shutdown_vm, None),
            ("Force Stop", self._force_stop_vm, None),
            ("Delete", self._delete_vm, "red"),
        ]

        for text, command, color in buttons:
            kwargs = {"fg_color": color} if color else {}
            ctk.CTkButton(self, text=text, command=command, **kwargs).pack(
                pady=5, padx=10, fill="x"
            )

    def _start_vm(self) -> None:
        """Start selected VM."""
        if self._selected_vm:
            self._service.start_vm(self._selected_vm.name)
            self._on_action()

    def _shutdown_vm(self) -> None:
        """Shutdown selected VM."""
        if self._selected_vm:
            self._service.shutdown_vm(self._selected_vm.name)
            self._on_action()

    def _force_stop_vm(self) -> None:
        """Force stop selected VM."""
        if self._selected_vm:
            self._service.force_stop_vm(self._selected_vm.name)
            self._on_action()

    def _delete_vm(self) -> None:
        """Delete selected VM."""
        if self._selected_vm:
            self._service.delete_vm(self._selected_vm.name)
            self._on_action()
