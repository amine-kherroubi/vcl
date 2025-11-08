"""Widget for displaying virtual machine list."""

from __future__ import annotations
from typing import TYPE_CHECKING
import customtkinter as ctk
from collections.abc import Callable
from src.models import VMInfo, VMState

if TYPE_CHECKING:
    from src.vm_service import VMService


class VMListWidget(ctk.CTkScrollableFrame):
    """Modern widget for displaying virtual machine list."""

    __slots__ = ("_service", "_on_select", "_buttons")

    _STATE_COLORS: dict[VMState, str] = {
        VMState.RUNNING: "#10b981",
        VMState.SHUTOFF: "#6b7280",
        VMState.PAUSED: "#f59e0b",
        VMState.UNKNOWN: "#ef4444",
    }

    _HOVER_COLORS: dict[str, str] = {
        "#10b981": "#34d399",
        "#6b7280": "#9ca3af",
        "#f59e0b": "#fbbf24",
        "#ef4444": "#f87171",
    }

    def __init__(
        self,
        master: ctk.CTkFrame | ctk.CTk,
        service: VMService,
        on_select: Callable[[VMInfo], None],
    ) -> None:
        super().__init__(master, fg_color="transparent")
        self._service: VMService = service
        self._on_select: Callable[[VMInfo], None] = on_select
        self._buttons: list[ctk.CTkButton] = []

    def refresh(self) -> None:
        """Refresh VM list display."""
        self._clear_buttons()
        vms = self._service.list_vms()

        if not vms:
            self._show_empty_state()
        else:
            for vm in vms:
                self._create_vm_button(vm)

    def _clear_buttons(self) -> None:
        """Clear all VM buttons."""
        for btn in self._buttons:
            btn.destroy()
        self._buttons.clear()

    def _show_empty_state(self) -> None:
        """Show empty state message."""
        label = ctk.CTkLabel(
            self,
            text="No virtual machines found\nCreate one to get started",
            font=("SF Pro Display", 14),
            text_color="#9ca3af",
        )
        label.pack(pady=50)

    def _create_vm_button(self, vm: VMInfo) -> None:
        """Create modern button for VM."""
        color = self._STATE_COLORS.get(vm.state, "#6b7280")
        hover_color = self._HOVER_COLORS.get(color, color)

        display_text = (
            f"{vm.name}\n{vm.memory}MB · {vm.vcpus} vCPU · {vm.state.value.upper()}"
        )

        btn = ctk.CTkButton(
            self,
            text=display_text,
            font=("SF Pro Display", 14, "bold"),
            fg_color=color,
            hover_color=hover_color,
            height=50,
            corner_radius=12,
            anchor="w",
            command=lambda v=vm: self._on_select(v),
        )

        btn.pack(pady=8, padx=15, fill="x")
        self._buttons.append(btn)
