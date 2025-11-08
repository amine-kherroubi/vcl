from __future__ import annotations
import libvirt
from dataclasses import dataclass
from enum import Enum


class VMState(Enum):
    """Virtual machine state enumeration."""

    RUNNING = "running"
    SHUTOFF = "shutoff"
    PAUSED = "paused"
    UNKNOWN = "unknown"


@dataclass
class VMInfo:
    """Virtual machine information container."""

    name: str
    state: VMState
    uuid: str
    memory: int  # In MB
    vcpus: int


class LibvirtManager:
    """Manages libvirt connection and VM operations."""

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

    def list_vms(self) -> list[VMInfo]:
        """Retrieve list of all virtual machines."""
        if not self._conn:
            return []

        vms: list[VMInfo] = []
        try:
            for domain in self._conn.listAllDomains():
                state_code: int = domain.state()[0]
                state: VMState = self._get_vm_state(state_code)

                info: tuple = domain.info()
                vm_info = VMInfo(
                    name=domain.name(),
                    state=state,
                    uuid=domain.UUIDString(),
                    memory=info[2] // 1024,
                    vcpus=info[3],
                )
                vms.append(vm_info)
        except libvirt.libvirtError:
            pass

        return vms

    def start_vm(self, name: str) -> bool:
        """Start virtual machine."""
        if not self._conn:
            return False
        try:
            domain: libvirt.virDomain = self._conn.lookupByName(name)
            domain.create()
            return True
        except libvirt.libvirtError:
            return False

    def shutdown_vm(self, name: str) -> bool:
        """Shutdown virtual machine."""
        if not self._conn:
            return False
        try:
            domain: libvirt.virDomain = self._conn.lookupByName(name)
            domain.shutdown()
            return True
        except libvirt.libvirtError:
            return False

    def force_stop_vm(self, name: str) -> bool:
        """Force stop virtual machine."""
        if not self._conn:
            return False
        try:
            domain: libvirt.virDomain = self._conn.lookupByName(name)
            domain.destroy()
            return True
        except libvirt.libvirtError:
            return False

    def delete_vm(self, name: str) -> bool:
        """Delete virtual machine."""
        if not self._conn:
            return False
        try:
            domain: libvirt.virDomain = self._conn.lookupByName(name)
            domain.undefine()
            return True
        except libvirt.libvirtError:
            return False

    def create_vm(
        self,
        name: str,
        memory: int,
        vcpus: int,
        disk_path: str,
        iso_path: str | None = None,
    ) -> bool:
        """Create new virtual machine."""
        if not self._conn:
            return False

        xml: str = self._generate_vm_xml(name, memory, vcpus, disk_path, iso_path)
        try:
            self._conn.defineXML(xml)
            return True
        except libvirt.libvirtError:
            return False

    @staticmethod
    def _get_vm_state(state_code: int) -> VMState:
        """Convert libvirt state code to VMState."""
        state_map: dict[int, VMState] = {
            1: VMState.RUNNING,
            5: VMState.SHUTOFF,
            3: VMState.PAUSED,
        }
        return state_map.get(state_code, VMState.UNKNOWN)

    @staticmethod
    def _generate_vm_xml(
        name: str, memory: int, vcpus: int, disk_path: str, iso_path: str | None
    ) -> str:
        """Generate VM XML configuration."""
        iso_section: str = ""
        if iso_path:
            iso_section = f"""
    <disk type='file' device='cdrom'>
      <driver name='qemu' type='raw'/>
      <source file='{iso_path}'/>
      <target dev='hdc' bus='ide'/>
      <readonly/>
    </disk>"""

        return f"""
<domain type='kvm'>
  <name>{name}</name>
  <memory unit='MiB'>{memory}</memory>
  <vcpu placement='static'>{vcpus}</vcpu>
  <os>
    <type arch='x86_64' machine='pc'>hvm</type>
    <boot dev='hd'/>
    <boot dev='cdrom'/>
  </os>
  <devices>
    <emulator>/usr/bin/qemu-system-x86_64</emulator>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2'/>
      <source file='{disk_path}'/>
      <target dev='vda' bus='virtio'/>
    </disk>{iso_section}
    <interface type='network'>
      <source network='default'/>
      <model type='virtio'/>
    </interface>
    <graphics type='vnc' port='-1' autoport='yes'/>
  </devices>
</domain>"""
