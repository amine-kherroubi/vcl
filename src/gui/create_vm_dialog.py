from __future__ import annotations
from typing import TYPE_CHECKING
import customtkinter as ctk
from collections.abc import Callable
from tkinter import filedialog

if TYPE_CHECKING:
    from src.vm_service import VMService


class CreateVMDialog(ctk.CTkToplevel):
    __slots__ = (
        "_service",
        "_on_create",
        "_name_entry",
        "_memory_entry",
        "_vcpu_entry",
        "_disk_entry",
        "_disk_size_entry",
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
        self.geometry("540x720")
        self.resizable(False, False)
        self.configure(fg_color="#FFFFFF")

        self._name_entry: ctk.CTkEntry
        self._memory_entry: ctk.CTkEntry
        self._vcpu_entry: ctk.CTkEntry
        self._disk_entry: ctk.CTkEntry
        self._disk_size_entry: ctk.CTkEntry
        self._iso_entry: ctk.CTkEntry

        self._build_ui()

    def _build_ui(self) -> None:
        ctk.CTkLabel(
            self,
            text="Create New VM",
            font=("Inter", 24, "bold"),
            text_color="#0F0F0F",
        ).pack(pady=(30, 20))

        self._create_text_field("VM Name", "")
        self._create_text_field("Memory (MB)", "2048")
        self._create_text_field("vCPUs", "2")
        self._create_file_field(
            "Disk Path", "/var/lib/libvirt/images/vm.qcow2", self._browse_disk
        )
        self._create_text_field("Disk Size (GB)", "20")
        self._create_file_field("ISO Path (optional)", "", self._browse_iso)

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=20, padx=40, fill="x")

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            font=("Inter", 14),
            fg_color="#E5E5E5",
            hover_color="#D4D4D4",
            text_color="#0F0F0F",
            height=48,
            corner_radius=8,
            command=self.destroy,
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            button_frame,
            text="Create VM",
            font=("Inter", 14, "bold"),
            fg_color="#0F0F0F",
            hover_color="#262626",
            height=48,
            corner_radius=8,
            command=self._handle_create,
        ).pack(side="right", fill="x", expand=True, padx=(8, 0))

    def _create_text_field(self, label: str, default: str) -> None:
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(pady=10, padx=40, fill="x")

        ctk.CTkLabel(
            frame,
            text=label,
            font=("Inter", 13),
            text_color="#525252",
            anchor="w",
        ).pack(anchor="w", pady=(0, 5))

        entry = ctk.CTkEntry(
            frame,
            height=38,
            font=("Inter", 13),
            corner_radius=6,
            border_width=1,
            border_color="#E5E5E5",
        )
        if default:
            entry.insert(0, default)
        entry.pack(fill="x")

        if not hasattr(self, "_name_entry"):
            self._name_entry = entry
        elif not hasattr(self, "_memory_entry"):
            self._memory_entry = entry
        elif not hasattr(self, "_vcpu_entry"):
            self._vcpu_entry = entry
        elif not hasattr(self, "_disk_size_entry"):
            self._disk_size_entry = entry

    def _create_file_field(
        self, label: str, default: str, browse_cmd: Callable
    ) -> None:
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(pady=10, padx=40, fill="x")

        ctk.CTkLabel(
            frame,
            text=label,
            font=("Inter", 13),
            text_color="#525252",
            anchor="w",
        ).pack(anchor="w", pady=(0, 5))

        input_frame = ctk.CTkFrame(frame, fg_color="transparent")
        input_frame.pack(fill="x")

        entry = ctk.CTkEntry(
            input_frame,
            height=38,
            font=("Inter", 13),
            corner_radius=6,
            border_width=1,
            border_color="#E5E5E5",
        )
        if default:
            entry.insert(0, default)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            input_frame,
            text="Browse",
            font=("Inter", 12),
            fg_color="#E5E5E5",
            hover_color="#D4D4D4",
            text_color="#0F0F0F",
            width=80,
            height=38,
            corner_radius=6,
            command=lambda: browse_cmd(entry),
        ).pack(side="right")

        if "Disk" in label:
            self._disk_entry = entry
        else:
            self._iso_entry = entry

    def _browse_disk(self, entry: ctk.CTkEntry) -> None:
        filename = filedialog.asksaveasfilename(
            title="Select Disk Location",
            defaultextension=".qcow2",
            filetypes=[("QCOW2 Images", "*.qcow2"), ("All Files", "*.*")],
            initialdir="/var/lib/libvirt/images",
        )
        if filename:
            entry.delete(0, "end")
            entry.insert(0, filename)

    def _browse_iso(self, entry: ctk.CTkEntry) -> None:
        filename = filedialog.askopenfilename(
            title="Select ISO File",
            filetypes=[("ISO Images", "*.iso"), ("All Files", "*.*")],
            initialdir="/var/lib/libvirt/images",
        )
        if filename:
            entry.delete(0, "end")
            entry.insert(0, filename)

    def _handle_create(self) -> None:
        try:
            name = self._name_entry.get().strip()
            if not name:
                self._show_error("VM name is required")
                return

            memory = int(self._memory_entry.get())
            vcpus = int(self._vcpu_entry.get())
            disk = self._disk_entry.get().strip()
            disk_size = int(self._disk_size_entry.get())

            if not disk:
                self._show_error("Disk path is required")
                return

            iso = self._iso_entry.get().strip() or None

            self._create_button_loading()

            if self._service.create_vm(name, memory, vcpus, disk, disk_size, iso):
                self._on_create()
                self.destroy()
            else:
                self._show_error("Failed to create VM")
        except ValueError:
            self._show_error("Invalid numeric value")

    def _show_error(self, message: str) -> None:
        error_window = ctk.CTkToplevel(self)
        error_window.title("Error")
        error_window.geometry("350x150")
        error_window.resizable(False, False)
        error_window.configure(fg_color="#FFFFFF")
        error_window.transient(self)
        error_window.grab_set()

        ctk.CTkLabel(
            error_window,
            text="Error",
            font=("Inter", 18, "bold"),
            text_color="#EF4444",
        ).pack(pady=(20, 10))

        ctk.CTkLabel(
            error_window,
            text=message,
            font=("Inter", 13),
            text_color="#525252",
        ).pack(pady=10)

        ctk.CTkButton(
            error_window,
            text="OK",
            font=("Inter", 13, "bold"),
            fg_color="#0F0F0F",
            hover_color="#262626",
            height=36,
            corner_radius=6,
            command=error_window.destroy,
        ).pack(pady=15)

    def _create_button_loading(self) -> None:
        self.title("Creating VM...")
