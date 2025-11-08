from collections.abc import Callable
import libvirt
from src.models import VMInfo, VMState


class LibvirtAdapter:
    """Adapter for libvirt operations."""

    __slots__ = ("_uri", "_conn")

    def __init__(self, uri: str = "qemu:///system") -> None:
        self._uri: str = uri
        self._conn: libvirt.virConnect | None = None

    def connect(self) -> bool:
        """Establish connection to libvirt."""
        try:
            self._conn = libvirt.open(self._uri)
            return self._conn is not None
        except libvirt.libvirtError:
            return False

    def disconnect(self) -> None:
        """Close libvirt connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def list_all_domains(self) -> list[VMInfo]:
        """Retrieve all virtual machines."""
        if not self._conn:
            return []

        vms: list[VMInfo] = []
        try:
            for domain in self._conn.listAllDomains():
                vm_info = self._extract_vm_info(domain)
                vms.append(vm_info)
        except libvirt.libvirtError:
            pass

        return vms

    def start_domain(self, name: str) -> bool:
        """Start virtual machine."""
        return self._execute_domain_action(name, lambda d: d.create())

    def shutdown_domain(self, name: str) -> bool:
        """Shutdown virtual machine gracefully."""
        return self._execute_domain_action(name, lambda d: d.shutdown())

    def destroy_domain(self, name: str) -> bool:
        """Force stop virtual machine."""
        return self._execute_domain_action(name, lambda d: d.destroy())

    def undefine_domain(self, name: str) -> bool:
        """Delete virtual machine definition."""
        return self._execute_domain_action(name, lambda d: d.undefine())

    def define_domain(self, xml: str) -> bool:
        """Define new virtual machine from XML."""
        if not self._conn:
            return False
        try:
            self._conn.defineXML(xml)
            return True
        except libvirt.libvirtError:
            return False

    def _execute_domain_action(self, name: str, action: Callable) -> bool:
        """Execute action on domain by name."""
        if not self._conn:
            return False
        try:
            domain = self._conn.lookupByName(name)
            action(domain)
            return True
        except libvirt.libvirtError:
            return False

    def _extract_vm_info(self, domain: libvirt.virDomain) -> VMInfo:
        """Extract VM information from domain."""
        state_code: int = domain.state()[0]
        state: VMState = self._map_state(state_code)
        info: tuple = domain.info()

        return VMInfo(
            name=domain.name(),
            state=state,
            uuid=domain.UUIDString(),
            memory=info[2] // 1024,
            vcpus=info[3],
        )

    @staticmethod
    def _map_state(state_code: int) -> VMState:
        """Map libvirt state code to VMState."""
        state_map: dict[int, VMState] = {
            1: VMState.RUNNING,
            5: VMState.SHUTOFF,
            3: VMState.PAUSED,
        }
        return state_map.get(state_code, VMState.UNKNOWN)
