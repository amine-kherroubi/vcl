from __future__ import annotations
import logging
from src.libvirt_adapter import LibvirtAdapter
from src.xml_generator import VMXMLGenerator
from src.models import VMInfo


class VMService:
    __slots__ = ("_adapter", "_xml_generator", "_logger")

    def __init__(self, adapter: LibvirtAdapter) -> None:
        self._adapter: LibvirtAdapter = adapter
        self._xml_generator: VMXMLGenerator = VMXMLGenerator()
        self._logger: logging.Logger = logging.getLogger("libvirt_manager.service")

    def list_vms(self) -> list[VMInfo]:
        self._logger.debug("Listing all VMs")
        return self._adapter.list_all_domains()

    def start_vm(self, name: str) -> bool:
        return self._adapter.start_domain(name)

    def shutdown_vm(self, name: str) -> bool:
        return self._adapter.shutdown_domain(name)

    def force_stop_vm(self, name: str) -> bool:
        return self._adapter.destroy_domain(name)

    def delete_vm(self, name: str) -> bool:
        return self._adapter.undefine_domain(name)

    def create_vm(
        self,
        name: str,
        memory: int,
        vcpus: int,
        disk_path: str,
        disk_size: int,
        iso_path: str | None = None,
    ) -> bool:
        self._logger.info(
            "Creating VM: %s (Memory: %dMB, vCPUs: %d, Disk: %dGB)",
            name,
            memory,
            vcpus,
            disk_size,
        )

        from pathlib import Path
        import subprocess

        disk_file = Path(disk_path)
        if not disk_file.exists():
            try:
                disk_file.parent.mkdir(parents=True, exist_ok=True)
                result = subprocess.run(
                    [
                        "qemu-img",
                        "create",
                        "-f",
                        "qcow2",
                        str(disk_file),
                        f"{disk_size}G",
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                self._logger.info("Created disk image: %s", disk_path)
            except subprocess.CalledProcessError as e:
                self._logger.error("Failed to create disk image: %s", e.stderr)
                return False
            except Exception as e:
                self._logger.error("Error creating disk: %s", e)
                return False

        xml = self._xml_generator.generate_vm_xml(
            name, memory, vcpus, disk_path, iso_path
        )
        return self._adapter.define_domain(xml)
