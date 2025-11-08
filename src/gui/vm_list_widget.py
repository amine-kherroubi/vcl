from __future__ import annotations
from typing import TYPE_CHECKING
import customtkinter as ctk
from collections.abc import Callable
from src.models import VMInfo, VMState

if TYPE_CHECKING:
    from src.vm_service import VMService


class VMListWidget(ctk.CTkScrollableFrame):
    __slots__ = ("_service", "_on_select", "_widgets")

    _STATE_COLORS: dict[VMState, str] = {
        VMState.RUNNING: "#10B981",
        VMState.SHUTOFF: "#737373",
        VMState.PAUSED: "#F97316",
        VMState.UNKNOWN: "#EF4444",
    }

    _HOVER_COLORS: dict[str, str] = {
        "#10B981": "#059669",
        "#737373": "#525252",
        "#F97316": "#EA580C",
        "#EF4444": "#DC2626",
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
        self._widgets: list[ctk.CTkButton | ctk.CTkLabel] = []

    def refresh(self) -> None:
        self._clear_buttons()
        vms = self._service.list_vms()

        if not vms:
            self._show_empty_state()
        else:
            for vm in vms:
                self._create_vm_button(vm)

    def _clear_buttons(self) -> None:
        for widget in self._widgets:
            widget.destroy()
        self._widgets.clear()

    def _show_empty_state(self) -> None:
        label = ctk.CTkLabel(
            self,
            text="No virtual machines found\nCreate one to get started",
            font=("Inter", 14),
            text_color="#A3A3A3",
        )
        label.pack(pady=50)
        self._widgets.append(label)

    def _create_vm_button(self, vm: VMInfo) -> None:
        color = self._STATE_COLORS.get(vm.state, "#737373")
        hover_color = self._HOVER_COLORS.get(color, color)

        display_text = (
            f"{vm.name}\n{vm.memory}MB · {vm.vcpus} vCPU · {vm.state.value.upper()}"
        )

        btn = ctk.CTkButton(
            self,
            text=display_text,
            font=("Inter", 14, "bold"),
            fg_color=color,
            hover_color=hover_color,
            height=50,
            corner_radius=8,
            anchor="w",
            command=lambda v=vm: self._on_select(v),
        )

        btn.pack(pady=8, padx=15, fill="x")
        self._widgets.append(btn)
