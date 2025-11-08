import customtkinter as ctk
from collections.abc import Callable
from src.vm_service import VMService


class CreateVMDialog(ctk.CTkToplevel):
    """Dialog for creating new virtual machines."""

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
        master: ctk.CTkBaseClass,
        service: VMService,
        on_create: Callable[[], None],
    ) -> None:
        super().__init__(master)
        self._service: VMService = service
        self._on_create: Callable[[], None] = on_create

        self.title("Create Virtual Machine")
        self.geometry("400x450")
        self._build_ui()

    def _build_ui(self) -> None:
        """Build dialog UI."""
        fields = [
            ("VM Name:", ""),
            ("Memory (MB):", "2048"),
            ("vCPUs:", "2"),
            ("Disk Path:", ""),
            ("ISO Path (optional):", ""),
        ]

        entries = []
        for label, default in fields:
            ctk.CTkLabel(self, text=label).pack(pady=5)
            entry = ctk.CTkEntry(self, width=300)
            if default:
                entry.insert(0, default)
            entry.pack(pady=5)
            entries.append(entry)

        (
            self._name_entry,
            self._memory_entry,
            self._vcpu_entry,
            self._disk_entry,
            self._iso_entry,
        ) = entries

        ctk.CTkButton(self, text="Create", command=self._handle_create).pack(pady=20)

    def _handle_create(self) -> None:
        """Handle VM creation."""
        try:
            name = self._name_entry.get()
            memory = int(self._memory_entry.get())
            vcpus = int(self._vcpu_entry.get())
            disk = self._disk_entry.get()
            iso = self._iso_entry.get() or None

            if self._service.create_vm(name, memory, vcpus, disk, iso):
                self._on_create()
                self.destroy()
        except ValueError:
            pass
