"""Widget for VM control operations."""

from __future__ import annotations
from typing import TYPE_CHECKING
import customtkinter as ctk
from collections.abc import Callable
from src.models import VMInfo

if TYPE_CHECKING:
    from src.vm_service import VMService


class ControlPanelWidget(ctk.CTkFrame):
    """Modern widget for VM control operations."""

    __slots__ = ("_service", "_on_action", "_selected_vm", "_vm_info_label")

    def __init__(
        self,
        master: ctk.CTkFrame | ctk.CTk,
        service: VMService,
        on_action: Callable[[], None],
    ) -> None:
        super().__init__(master, fg_color="#f9fafb", corner_radius=15)
        self._service: VMService = service
        self._on_action: Callable[[], None] = on_action
        self._selected_vm: VMInfo | None = None
        self._vm_info_label: ctk.CTkLabel
        self._build_ui()

    def set_selected_vm(self, vm: VMInfo) -> None:
        """Set currently selected VM."""
        self._selected_vm = vm
        self._update_info_display()

    def _build_ui(self) -> None:
        """Build modern control panel UI."""
        # Title
        ctk.CTkLabel(
            self,
            text="VM Controls",
            font=("SF Pro Display", 18, "bold"),
            text_color="#111827",
        ).pack(pady=(20, 10), padx=20)

        # VM Info Display
        self._vm_info_label = ctk.CTkLabel(
            self,
            text="No VM selected",
            font=("SF Pro Display", 12),
            text_color="#6b7280",
            wraplength=200,
        )
        self._vm_info_label.pack(pady=10, padx=20)

        # Separator
        ctk.CTkFrame(self, height=1, fg_color="#e5e7eb").pack(
            fill="x", padx=20, pady=15
        )

        # Control buttons
        buttons: list[tuple[str, Callable[[], None], str, str]] = [
            ("▶  Start", self._start_vm, "#10b981", "#059669"),
            ("⏸  Shutdown", self._shutdown_vm, "#3b82f6", "#2563eb"),
            ("⏹  Force Stop", self._force_stop_vm, "#f59e0b", "#d97706"),
            ("🗑  Delete", self._delete_vm, "#ef4444", "#dc2626"),
        ]

        for text, command, color, hover in buttons:
            ctk.CTkButton(
                self,
                text=text,
                font=("SF Pro Display", 13, "bold"),
                fg_color=color,
                hover_color=hover,
                height=45,
                corner_radius=10,
                command=command,
            ).pack(pady=8, padx=20, fill="x")

    def _update_info_display(self) -> None:
        """Update VM info display."""
        if self._selected_vm:
            info_text = (
                f"Name: {self._selected_vm.name}\n"
                f"State: {self._selected_vm.state.value}\n"
                f"Memory: {self._selected_vm.memory} MB\n"
                f"vCPUs: {self._selected_vm.vcpus}"
            )
            self._vm_info_label.configure(text=info_text, text_color="#111827")
        else:
            self._vm_info_label.configure(text="No VM selected", text_color="#6b7280")

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
