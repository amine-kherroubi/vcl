"""Dialog for creating new virtual machines."""

from __future__ import annotations
from typing import TYPE_CHECKING
import customtkinter as ctk
from collections.abc import Callable

if TYPE_CHECKING:
    from src.vm_service import VMService


class CreateVMDialog(ctk.CTkToplevel):
    """Modern dialog for creating new virtual machines."""

    __slots__ = (
        "_service",
        "_on_create",
        "_name_entry",
        "_memory_entry",
        "_vcpu_entry",
        "_disk_entry",
        "_iso_entry",
    )

    def __init__(
        self,
        master: ctk.CTk | ctk.CTkToplevel,
        service: VMService,
        on_create: Callable[[], None],
    ) -> None:
        super().__init__(master)
        self._service: VMService = service
        self._on_create: Callable[[], None] = on_create

        self.title("Create Virtual Machine")
        self.geometry("500x550")
        self.configure(fg_color="#ffffff")

        # Initialize entry widgets
        self._name_entry: ctk.CTkEntry
        self._memory_entry: ctk.CTkEntry
        self._vcpu_entry: ctk.CTkEntry
        self._disk_entry: ctk.CTkEntry
        self._iso_entry: ctk.CTkEntry

        self._build_ui()

    def _build_ui(self) -> None:
        """Build modern dialog UI."""
        # Title
        ctk.CTkLabel(
            self,
            text="Create New VM",
            font=("SF Pro Display", 24, "bold"),
            text_color="#111827",
        ).pack(pady=(30, 20))

        # Form fields
        fields: list[tuple[str, str]] = [
            ("VM Name", ""),
            ("Memory (MB)", "2048"),
            ("vCPUs", "2"),
            ("Disk Path", "/var/lib/libvirt/images/vm.qcow2"),
            ("ISO Path (optional)", ""),
        ]

        entries: list[ctk.CTkEntry] = []
        for label, default in fields:
            frame = ctk.CTkFrame(self, fg_color="transparent")
            frame.pack(pady=10, padx=40, fill="x")

            ctk.CTkLabel(
                frame,
                text=label,
                font=("SF Pro Display", 13),
                text_color="#374151",
                anchor="w",
            ).pack(anchor="w", pady=(0, 5))

            entry = ctk.CTkEntry(
                frame,
                height=40,
                font=("SF Pro Display", 13),
                corner_radius=8,
                border_width=1,
                border_color="#e5e7eb",
            )
            if default:
                entry.insert(0, default)
            entry.pack(fill="x")
            entries.append(entry)

        (
            self._name_entry,
            self._memory_entry,
            self._vcpu_entry,
            self._disk_entry,
            self._iso_entry,
        ) = entries

        # Create button
        ctk.CTkButton(
            self,
            text="Create Virtual Machine",
            font=("SF Pro Display", 14, "bold"),
            fg_color="#3b82f6",
            hover_color="#2563eb",
            height=50,
            corner_radius=10,
            command=self._handle_create,
        ).pack(pady=30, padx=40, fill="x")

    def _handle_create(self) -> None:
        """Handle VM creation."""
        try:
            name = self._name_entry.get().strip()
            if not name:
                return

            memory = int(self._memory_entry.get())
            vcpus = int(self._vcpu_entry.get())
            disk = self._disk_entry.get().strip()

            if not disk:
                return

            iso = self._iso_entry.get().strip() or None

            if self._service.create_vm(name, memory, vcpus, disk, iso):
                self._on_create()
                self.destroy()
        except ValueError:
            pass
