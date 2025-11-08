"""Libvirt adapter for VM operations."""

from __future__ import annotations
from collections.abc import Callable
from typing import Any
import logging
import libvirt
from src.models import VMInfo, VMState


class LibvirtAdapter:
    """Adapter for libvirt operations."""

    __slots__ = ("_uri", "_conn", "_logger")

    def __init__(self, uri: str = "qemu:///system") -> None:
        self._uri: str = uri
        self._conn: libvirt.virConnect | None = None
        self._logger: logging.Logger = logging.getLogger("libvirt_manager.adapter")

    def connect(self) -> bool:
        """Establish connection to libvirt."""
        try:
            self._logger.info("Connecting to libvirt: %s", self._uri)
            self._conn = libvirt.open(self._uri)
            success = self._conn is not None
            if success:
                self._logger.info("Successfully connected to libvirt")
            return success
        except libvirt.libvirtError as e:
            self._logger.error("Failed to connect to libvirt: %s", e)
            return False

    def disconnect(self) -> None:
        """Close libvirt connection."""
        if self._conn:
            self._logger.info("Disconnecting from libvirt")
            try:
                self._conn.close()
            except libvirt.libvirtError as e:
                self._logger.error("Error disconnecting: %s", e)
            finally:
                self._conn = None

    def list_all_domains(self) -> list[VMInfo]:
        """Retrieve all virtual machines."""
        if not self._conn:
            self._logger.warning("Attempted to list domains without connection")
            return []

        vms: list[VMInfo] = []
        try:
            domains = self._conn.listAllDomains()
            self._logger.debug("Found %d domains", len(domains))
            for domain in domains:
                vm_info = self._extract_vm_info(domain)
                vms.append(vm_info)
        except libvirt.libvirtError as e:
            self._logger.error("Error listing domains: %s", e)

        return vms

    def start_domain(self, name: str) -> bool:
        """Start virtual machine."""
        self._logger.info("Starting VM: %s", name)
        result = self._execute_domain_action(name, lambda d: d.create())
        if result:
            self._logger.info("Successfully started VM: %s", name)
        else:
            self._logger.error("Failed to start VM: %s", name)
        return result

    def shutdown_domain(self, name: str) -> bool:
        """Shutdown virtual machine gracefully."""
        self._logger.info("Shutting down VM: %s", name)
        result = self._execute_domain_action(name, lambda d: d.shutdown())
        if result:
            self._logger.info("Successfully initiated shutdown for VM: %s", name)
        else:
            self._logger.error("Failed to shutdown VM: %s", name)
        return result

    def destroy_domain(self, name: str) -> bool:
        """Force stop virtual machine."""
        self._logger.warning("Force stopping VM: %s", name)
        result = self._execute_domain_action(name, lambda d: d.destroy())
        if result:
            self._logger.info("Successfully force stopped VM: %s", name)
        else:
            self._logger.error("Failed to force stop VM: %s", name)
        return result

    def undefine_domain(self, name: str) -> bool:
        """Delete virtual machine definition."""
        self._logger.warning("Deleting VM: %s", name)
        result = self._execute_domain_action(name, lambda d: d.undefine())
        if result:
            self._logger.info("Successfully deleted VM: %s", name)
        else:
            self._logger.error("Failed to delete VM: %s", name)
        return result

    def define_domain(self, xml: str) -> bool:
        """Define new virtual machine from XML."""
        if not self._conn:
            self._logger.warning("Attempted to define domain without connection")
            return False
        try:
            self._logger.info("Defining new VM from XML")
            self._conn.defineXML(xml)
            self._logger.info("Successfully defined new VM")
            return True
        except libvirt.libvirtError as e:
            self._logger.error("Failed to define VM: %s", e)
            return False

    def _execute_domain_action(self, name: str, action: Callable[[Any], None]) -> bool:
        """Execute action on domain by name."""
        if not self._conn:
            return False
        try:
            domain = self._conn.lookupByName(name)
            action(domain)
            return True
        except libvirt.libvirtError as e:
            self._logger.error("Domain action failed for %s: %s", name, e)
            return False

    def _extract_vm_info(self, domain: Any) -> VMInfo:
        """Extract VM information from domain."""
        state_code: int = domain.state()[0]
        state: VMState = self._map_state(state_code)
        info: tuple[int, int, int, int, int] = domain.info()

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
