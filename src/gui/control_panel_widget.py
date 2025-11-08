from __future__ import annotations
from typing import TYPE_CHECKING
import customtkinter as ctk
from collections.abc import Callable
from src.models import VMInfo

if TYPE_CHECKING:
    from src.vm_service import VMService


class ControlPanelWidget(ctk.CTkFrame):
    __slots__ = ("_service", "_on_action", "_selected_vm", "_vm_info_label")

    def __init__(
        self,
        master: ctk.CTkFrame | ctk.CTk,
        service: VMService,
        on_action: Callable[[], None],
    ) -> None:
        super().__init__(master, fg_color="#F5F5F5", corner_radius=12)
        self._service: VMService = service
        self._on_action: Callable[[], None] = on_action
        self._selected_vm: VMInfo | None = None
        self._vm_info_label: ctk.CTkLabel
        self._build_ui()

    def set_selected_vm(self, vm: VMInfo) -> None:
        self._selected_vm = vm
        self._update_info_display()

    def _build_ui(self) -> None:
        ctk.CTkLabel(
            self,
            text="VM Controls",
            font=("Inter", 18, "bold"),
            text_color="#0F0F0F",
        ).pack(pady=(20, 10), padx=20)

        self._vm_info_label = ctk.CTkLabel(
            self,
            text="No VM selected",
            font=("Inter", 12),
            text_color="#737373",
            wraplength=200,
        )
        self._vm_info_label.pack(pady=10, padx=20)

        ctk.CTkFrame(self, height=1, fg_color="#E5E5E5").pack(
            fill="x", padx=20, pady=15
        )

        buttons: list[tuple[str, Callable[[], None], str, str]] = [
            ("Start", self._start_vm, "#10B981", "#059669"),
            ("Shutdown", self._shutdown_vm, "#0F0F0F", "#262626"),
            ("Force Stop", self._force_stop_vm, "#F97316", "#EA580C"),
            ("Delete", self._delete_vm, "#EF4444", "#DC2626"),
        ]

        for text, command, color, hover in buttons:
            ctk.CTkButton(
                self,
                text=text,
                font=("Inter", 13, "bold"),
                fg_color=color,
                hover_color=hover,
                height=42,
                corner_radius=8,
                command=command,
            ).pack(pady=8, padx=20, fill="x")

    def _update_info_display(self) -> None:
        if self._selected_vm:
            info_text = (
                f"Name: {self._selected_vm.name}\n"
                f"State: {self._selected_vm.state.value}\n"
                f"Memory: {self._selected_vm.memory} MB\n"
                f"vCPUs: {self._selected_vm.vcpus}"
            )
            self._vm_info_label.configure(text=info_text, text_color="#0F0F0F")
        else:
            self._vm_info_label.configure(text="No VM selected", text_color="#737373")

    def _start_vm(self) -> None:
        if self._selected_vm:
            self._service.start_vm(self._selected_vm.name)
            self._on_action()

    def _shutdown_vm(self) -> None:
        if self._selected_vm:
            self._service.shutdown_vm(self._selected_vm.name)
            self._on_action()

    def _force_stop_vm(self) -> None:
        if self._selected_vm:
            self._service.force_stop_vm(self._selected_vm.name)
            self._on_action()

    def _delete_vm(self) -> None:
        if self._selected_vm:
            if self._confirm_delete():
                self._service.delete_vm(self._selected_vm.name)
                self._selected_vm = None
                self._on_action()

    def _confirm_delete(self) -> bool:
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Delete")
        dialog.geometry("400x180")
        dialog.resizable(False, False)
        dialog.configure(fg_color="#FFFFFF")
        dialog.grab_set()

        result = [False]

        ctk.CTkLabel(
            dialog,
            text="Delete Virtual Machine?",
            font=("Inter", 18, "bold"),
            text_color="#0F0F0F",
        ).pack(pady=(25, 10))

        ctk.CTkLabel(
            dialog,
            text=f"This will permanently delete:\n{self._selected_vm.name}",
            font=("Inter", 13),
            text_color="#737373",
        ).pack(pady=10)

        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=20, padx=30, fill="x")

        def on_cancel():
            result[0] = False
            dialog.destroy()

        def on_confirm():
            result[0] = True
            dialog.destroy()

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            font=("Inter", 13),
            fg_color="#E5E5E5",
            hover_color="#D4D4D4",
            text_color="#0F0F0F",
            height=40,
            corner_radius=6,
            command=on_cancel,
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            button_frame,
            text="Delete",
            font=("Inter", 13, "bold"),
            fg_color="#EF4444",
            hover_color="#DC2626",
            height=40,
            corner_radius=6,
            command=on_confirm,
        ).pack(side="right", fill="x", expand=True, padx=(8, 0))

        dialog.wait_window()
        return result[0]
