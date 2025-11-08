from src.libvirt_adapter import LibvirtAdapter
from src.xml_generator import VMXMLGenerator
from src.models import VMInfo


class VMService:
    """Application service for VM operations."""

    __slots__ = ("_adapter", "_xml_generator")

    def __init__(self, adapter: LibvirtAdapter) -> None:
        self._adapter: LibvirtAdapter = adapter
        self._xml_generator: VMXMLGenerator = VMXMLGenerator()

    def list_vms(self) -> list[VMInfo]:
        """List all virtual machines."""
        return self._adapter.list_all_domains()

    def start_vm(self, name: str) -> bool:
        """Start virtual machine."""
        return self._adapter.start_domain(name)

    def shutdown_vm(self, name: str) -> bool:
        """Shutdown virtual machine."""
        return self._adapter.shutdown_domain(name)

    def force_stop_vm(self, name: str) -> bool:
        """Force stop virtual machine."""
        return self._adapter.destroy_domain(name)

    def delete_vm(self, name: str) -> bool:
        """Delete virtual machine."""
        return self._adapter.undefine_domain(name)

    def create_vm(
        self,
        name: str,
        memory: int,
        vcpus: int,
        disk_path: str,
        iso_path: str | None = None,
    ) -> bool:
        """Create new virtual machine."""
        xml = self._xml_generator.generate_vm_xml(
            name, memory, vcpus, disk_path, iso_path
        )
        return self._adapter.define_domain(xml)
