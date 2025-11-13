#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
KVM Virtual Machine Manager
---------------------------
A terminal-based VM management tool using libvirt
Made for RHEL 7.2 using Python 2.7

Contributors:
- Kherroubi Mohamed El Amine
- Bousdjira Nadine
"""

import libvirt
import os
import sys
import logging
from datetime import datetime

# =============================================================================
# CONFIGURATION
# =============================================================================

LOG_FILE = 'vm_manager.log'
DISK_IMAGE_DIR = '/var/lib/libvirt/images'
DEFAULT_BRIDGE = 'kvmbr0'
QEMU_EMULATOR = '/usr/libexec/qemu-kvm'

# =============================================================================
# LOGGING SETUP
# =============================================================================

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# =============================================================================
# CONSTANTS
# =============================================================================

# VM state mapping for human-readable output
VM_STATES = {
    libvirt.VIR_DOMAIN_RUNNING: "Running",
    libvirt.VIR_DOMAIN_PAUSED: "Paused",
    libvirt.VIR_DOMAIN_SHUTDOWN: "Shutting down",
    libvirt.VIR_DOMAIN_SHUTOFF: "Stopped",
    libvirt.VIR_DOMAIN_CRASHED: "Crashed",
}

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def clear_screen():
    """Clear the terminal screen"""
    os.system("clear")


def print_header(text, color=Colors.BLUE):
    """Print a formatted header with color"""
    print("\n" + color + Colors.BOLD + "=" * 70 + Colors.ENDC)
    print(color + Colors.BOLD + " " + text.center(68) + Colors.ENDC)
    print(color + Colors.BOLD + "=" * 70 + Colors.ENDC + "\n")


def print_success(text):
    """Print success message in green"""
    print(Colors.GREEN + "[SUCCESS] " + text + Colors.ENDC)


def print_error(text):
    """Print error message in red"""
    print(Colors.RED + "[ERROR] " + text + Colors.ENDC)


def print_warning(text):
    """Print warning message in yellow"""
    print(Colors.YELLOW + "[WARNING] " + text + Colors.ENDC)


def print_info(text):
    """Print info message in blue"""
    print(Colors.BLUE + "[INFO] " + text + Colors.ENDC)


def safe_input(prompt):
    """
    Safe input wrapper that handles keyboard interrupts
    
    Args:
        prompt: The prompt text to display
        
    Returns:
        Stripped user input string
    """
    try:
        return raw_input(prompt).strip()
    except (KeyboardInterrupt, EOFError):
        print("\n" + Colors.YELLOW + "Operation cancelled by user." + Colors.ENDC)
        return ""


def pause():
    """Pause execution until user presses Enter"""
    safe_input("\n" + Colors.BOLD + "Press Enter to continue..." + Colors.ENDC)


# =============================================================================
# VM MANAGER CLASS
# =============================================================================

class VMManager(object):
    """
    KVM Virtual Machine Manager
    
    Manages libvirt connection and provides VM lifecycle operations
    """
    
    def __init__(self):
        """Initialize the VM manager"""
        self.conn = None
        self.connected = False
    
    # -------------------------------------------------------------------------
    # CONNECTION MANAGEMENT
    # -------------------------------------------------------------------------
    
    def connect(self):
        """Establish connection to the KVM hypervisor"""
        clear_screen()
        print_header("KVM Hypervisor Connection", Colors.BLUE)
        
        print_info("Attempting to connect to qemu:///system...")
        
        try:
            self.conn = libvirt.open("qemu:///system")
            if not self.conn:
                print_error("Failed to establish connection!")
                sys.exit(1)
            
            self.connected = True
            print_success("Successfully connected to KVM hypervisor")
            print_info("Hostname: %s" % self.conn.getHostname())
            
            logging.info("Connected to hypervisor: %s", self.conn.getHostname())
            
        except libvirt.libvirtError as e:
            print_error("Connection failed: %s" % str(e))
            logging.error("Connection error: %s", str(e))
            sys.exit(1)
        
        pause()
    
    
    def close(self):
        """Close the hypervisor connection"""
        if self.conn and self.connected:
            self.conn.close()
            self.connected = False
            logging.info("Connection closed")
    
    # -------------------------------------------------------------------------
    # MENU SYSTEM
    # -------------------------------------------------------------------------
    
    def show_menu(self):
        """Display the main menu"""
        clear_screen()
        print_header("KVM Virtual Machine Manager", Colors.BLUE)
        
        print(Colors.BOLD + "  INFORMATION" + Colors.ENDC)
        print("  [0] View hypervisor information")
        print("  [1] List all virtual machines")
        print("  [2] Get VM IP address")
        
        print("\n" + Colors.BOLD + "  VM LIFECYCLE" + Colors.ENDC)
        print("  [3] Create new VM")
        print("  [4] Start VM")
        print("  [5] Stop VM")
        print("  [6] Suspend VM")
        print("  [7] Resume VM")
        print("  [8] Delete VM")
        
        print("\n" + Colors.BOLD + "  CONSOLE" + Colors.ENDC)
        print("  [9] View VM console (requires virt-viewer)")
        
        print("\n" + Colors.BOLD + "  SYSTEM" + Colors.ENDC)
        print("  [q] Quit")
        
        print("\n" + Colors.BLUE + "=" * 70 + Colors.ENDC)
    
    # -------------------------------------------------------------------------
    # HYPERVISOR INFORMATION
    # -------------------------------------------------------------------------
    
    def show_hypervisor_info(self):
        """Display detailed hypervisor information"""
        clear_screen()
        print_header("Hypervisor Information", Colors.GREEN)
        
        try:
            # Basic info
            hostname = self.conn.getHostname()
            info = self.conn.getInfo()
            
            print(Colors.BOLD + "System Information:" + Colors.ENDC)
            print("  Hostname:        %s" % hostname)
            print("  Architecture:    %s" % info[0])
            print("  Total Memory:    %d MB" % info[1])
            print("  Physical CPUs:   %d" % info[2])
            print("  CPU Frequency:   %d MHz" % info[3])
            print("  NUMA Nodes:      %d" % info[4])
            print("  CPU Sockets:     %d" % info[5])
            print("  Cores per Socket:%d" % info[6])
            print("  Threads per Core:%d" % info[7])
            
            # Count VMs
            try:
                all_domains = self.conn.listAllDomains()
                running = sum(1 for d in all_domains if d.isActive())
                total = len(all_domains)
                print("\n" + Colors.BOLD + "Virtual Machines:" + Colors.ENDC)
                print("  Running:         %d" % running)
                print("  Total Defined:   %d" % total)
            except Exception:
                pass
            
            # Libvirt version
            try:
                lib_ver = self.conn.getLibVersion()
                print("\n" + Colors.BOLD + "Software:" + Colors.ENDC)
                print("  libvirt version: %d.%d.%d" % 
                      (lib_ver / 1000000, (lib_ver / 1000) % 1000, lib_ver % 1000))
            except Exception:
                pass
            
        except Exception as e:
            print_error("Failed to retrieve hypervisor info: %s" % str(e))
            logging.error("Hypervisor info error: %s", str(e))
        
        pause()
    
    # -------------------------------------------------------------------------
    # VM LISTING
    # -------------------------------------------------------------------------
    
    def list_vms(self):
        """
        List all virtual machines with formatted output
        
        Returns:
            List of domain objects
        """
        try:
            domains = self.conn.listAllDomains()
        except libvirt.libvirtError as e:
            print_error("Failed to list VMs: %s" % str(e))
            return []
        
        if not domains:
            print("\n" + Colors.YELLOW + "No virtual machines found." + Colors.ENDC)
            return []
        
        # Calculate column width for VM names
        max_name_len = max([len(dom.name()) for dom in domains] + [10])
        max_name_len = min(max(max_name_len, 15), 30)
        
        # Print table header
        print("\n" + Colors.BOLD + "Virtual Machines:" + Colors.ENDC)
        header_line = "=" * (10 + max_name_len + 35)
        print(header_line)
        print("%-8s %-*s %-12s %-8s %-10s" % 
              ("ID", max_name_len, "Name", "vCPUs", "RAM (MB)", "State"))
        print(header_line)
        
        # Print each VM
        for dom in domains:
            # Get VM ID
            vm_id = dom.ID() if dom.ID() != -1 else "-"
            
            # Get VM state
            state_code = dom.state()[0]
            state = self.get_vm_state(state_code)
            
            # Colorize state
            if state_code == libvirt.VIR_DOMAIN_RUNNING:
                state = Colors.GREEN + state + Colors.ENDC
            elif state_code == libvirt.VIR_DOMAIN_PAUSED:
                state = Colors.YELLOW + state + Colors.ENDC
            elif state_code == libvirt.VIR_DOMAIN_CRASHED:
                state = Colors.RED + state + Colors.ENDC
            
            # Get VM info
            try:
                info = dom.info()
                vcpus = info[3]
                memory_mb = info[1] / 1024
            except Exception:
                vcpus = 0
                memory_mb = 0
            
            print("%-8s %-*s %-12d %-8d %s" % 
                  (vm_id, max_name_len, dom.name(), vcpus, memory_mb, state))
        
        print(header_line)
        return domains
    
    
    def get_vm_state(self, code):
        """
        Convert VM state code to human-readable string
        
        Args:
            code: libvirt domain state code
            
        Returns:
            Human-readable state string
        """
        return VM_STATES.get(code, "Unknown")
    
    # -------------------------------------------------------------------------
    # VM CREATION
    # -------------------------------------------------------------------------
    
    def create_vm(self):
        """Create a new virtual machine interactively"""
        clear_screen()
        print_header("Create New Virtual Machine", Colors.GREEN)
        
        # Get VM name
        vm_name = safe_input(Colors.BOLD + "VM Name: " + Colors.ENDC)
        if not vm_name:
            print_error("VM name cannot be empty!")
            pause()
            return
        
        # Check if VM already exists
        try:
            self.conn.lookupByName(vm_name)
            print_error("VM '%s' already exists!" % vm_name)
            pause()
            return
        except libvirt.libvirtError:
            # VM doesn't exist, this is good
            pass
        
        # Get VM specifications
        try:
            memory = int(safe_input("Memory (MB) [1024]: ") or "1024")
            vcpus = int(safe_input("Virtual CPUs [1]: ") or "1")
            disk_size = int(safe_input("Disk Size (GB) [10]: ") or "10")
            
            iso_path = safe_input("Installation ISO path: ")
            if not iso_path or not os.path.exists(iso_path):
                print_error("ISO file not found: %s" % iso_path)
                pause()
                return
                
        except ValueError:
            print_error("Invalid numeric input!")
            pause()
            return
        
        # Create disk image
        print_info("Creating disk image...")
        disk_path = "%s/%s.qcow2" % (DISK_IMAGE_DIR, vm_name)
        
        cmd = "qemu-img create -f qcow2 %s %dG" % (disk_path, disk_size)
        if os.system(cmd) != 0:
            print_error("Failed to create disk image!")
            pause()
            return
        
        print_success("Disk image created: %s" % disk_path)
        
        # Generate VM XML definition
        xml = self._generate_vm_xml(vm_name, memory, vcpus, disk_path, iso_path)
        
        # Define and optionally start VM
        try:
            dom = self.conn.defineXML(xml)
            print_success("VM '%s' created successfully!" % vm_name)
            logging.info("VM created: %s (Memory: %dMB, vCPUs: %d)", 
                        vm_name, memory, vcpus)
            
            # Ask to start VM
            start_now = safe_input("\nStart VM now? (y/N): ").lower()
            if start_now == "y":
                dom.create()
                print_success("VM '%s' started!" % vm_name)
                logging.info("VM started: %s", vm_name)
            
        except libvirt.libvirtError as e:
            print_error("Failed to create VM: %s" % str(e))
            logging.error("VM creation failed: %s - %s", vm_name, str(e))
        
        pause()
    
    
    def _generate_vm_xml(self, name, memory, vcpus, disk_path, iso_path):
        """
        Generate XML definition for a new VM
        
        Args:
            name: VM name
            memory: Memory in MB
            vcpus: Number of virtual CPUs
            disk_path: Path to disk image
            iso_path: Path to installation ISO
            
        Returns:
            XML string for VM definition
        """
        xml = """<domain type='kvm'>
  <name>%s</name>
  <memory unit='MiB'>%d</memory>
  <vcpu>%d</vcpu>
  <os>
    <type arch='x86_64'>hvm</type>
    <boot dev='cdrom'/>
    <boot dev='hd'/>
  </os>
  <features>
    <acpi/>
    <apic/>
  </features>
  <clock offset='utc'/>
  <devices>
    <emulator>%s</emulator>
    <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2'/>
      <source file='%s'/>
      <target dev='vda' bus='virtio'/>
    </disk>
    <disk type='file' device='cdrom'>
      <driver name='qemu' type='raw'/>
      <source file='%s'/>
      <target dev='hdc' bus='ide'/>
      <readonly/>
    </disk>
    <interface type='bridge'>
      <source bridge='%s'/>
      <model type='virtio'/>
    </interface>
    <graphics type='vnc' port='-1' autoport='yes'/>
    <console type='pty'/>
    <input type='mouse' bus='ps2'/>
    <input type='keyboard' bus='ps2'/>
  </devices>
</domain>""" % (name, memory, vcpus, QEMU_EMULATOR, disk_path, 
               iso_path, DEFAULT_BRIDGE)
        
        return xml
    
    # -------------------------------------------------------------------------
    # VM LIFECYCLE OPERATIONS
    # -------------------------------------------------------------------------
    
    def start_vm(self):
        """Start a stopped virtual machine"""
        clear_screen()
        print_header("Start Virtual Machine", Colors.GREEN)
        
        domains = self.list_vms()
        if not domains:
            pause()
            return
        
        vm_name = safe_input("\n" + Colors.BOLD + "VM name to start: " + Colors.ENDC)
        if not vm_name:
            return
        
        try:
            dom = self.conn.lookupByName(vm_name)
            state = dom.state()[0]
            
            if state == libvirt.VIR_DOMAIN_SHUTOFF:
                dom.create()
                print_success("VM '%s' started successfully!" % vm_name)
                logging.info("VM started: %s", vm_name)
            elif state == libvirt.VIR_DOMAIN_RUNNING:
                print_warning("VM '%s' is already running." % vm_name)
            elif state == libvirt.VIR_DOMAIN_PAUSED:
                print_warning("VM '%s' is paused. Use 'Resume VM' option." % vm_name)
            else:
                print_warning("VM '%s' is in state: %s" % 
                            (vm_name, self.get_vm_state(state)))
                
        except libvirt.libvirtError as e:
            print_error("Failed to start VM: %s" % str(e))
            logging.error("VM start failed: %s - %s", vm_name, str(e))
        
        pause()
    
    
    def stop_vm(self):
        """Stop a running virtual machine"""
        clear_screen()
        print_header("Stop Virtual Machine", Colors.YELLOW)
        
        domains = self.list_vms()
        if not domains:
            pause()
            return
        
        vm_name = safe_input("\n" + Colors.BOLD + "VM name to stop: " + Colors.ENDC)
        if not vm_name:
            return
        
        try:
            dom = self.conn.lookupByName(vm_name)
            state = dom.state()[0]
            
            if state != libvirt.VIR_DOMAIN_RUNNING:
                print_warning("VM '%s' is not running." % vm_name)
                pause()
                return
            
            # Ask for shutdown method
            print("\n" + Colors.BOLD + "Shutdown Method:" + Colors.ENDC)
            print("  [1] Graceful shutdown (ACPI)")
            print("  [2] Force stop (destroy)")
            
            choice = safe_input("\nChoice [1]: ") or "1"
            
            if choice == "2":
                dom.destroy()
                print_success("VM '%s' forcefully stopped!" % vm_name)
                logging.info("VM force stopped: %s", vm_name)
            else:
                dom.shutdown()
                print_success("VM '%s' shutdown initiated..." % vm_name)
                print_info("VM will shutdown gracefully")
                logging.info("VM shutdown: %s", vm_name)
                
        except libvirt.libvirtError as e:
            print_error("Failed to stop VM: %s" % str(e))
            logging.error("VM stop failed: %s - %s", vm_name, str(e))
        
        pause()
    
    
    def suspend_vm(self):
        """Suspend (pause) a running virtual machine"""
        clear_screen()
        print_header("Suspend Virtual Machine", Colors.YELLOW)
        
        domains = self.list_vms()
        if not domains:
            pause()
            return
        
        vm_name = safe_input("\n" + Colors.BOLD + "VM name to suspend: " + Colors.ENDC)
        if not vm_name:
            return
        
        try:
            dom = self.conn.lookupByName(vm_name)
            state = dom.state()[0]
            
            if state == libvirt.VIR_DOMAIN_RUNNING:
                dom.suspend()
                print_success("VM '%s' suspended!" % vm_name)
                logging.info("VM suspended: %s", vm_name)
            elif state == libvirt.VIR_DOMAIN_PAUSED:
                print_warning("VM '%s' is already suspended." % vm_name)
            else:
                print_warning("VM '%s' is not running." % vm_name)
                
        except libvirt.libvirtError as e:
            print_error("Failed to suspend VM: %s" % str(e))
            logging.error("VM suspend failed: %s - %s", vm_name, str(e))
        
        pause()
    
    
    def resume_vm(self):
        """Resume a suspended virtual machine"""
        clear_screen()
        print_header("Resume Virtual Machine", Colors.GREEN)
        
        domains = self.list_vms()
        if not domains:
            pause()
            return
        
        vm_name = safe_input("\n" + Colors.BOLD + "VM name to resume: " + Colors.ENDC)
        if not vm_name:
            return
        
        try:
            dom = self.conn.lookupByName(vm_name)
            state = dom.state()[0]
            
            if state == libvirt.VIR_DOMAIN_PAUSED:
                dom.resume()
                print_success("VM '%s' resumed!" % vm_name)
                logging.info("VM resumed: %s", vm_name)
            elif state == libvirt.VIR_DOMAIN_RUNNING:
                print_warning("VM '%s' is already running." % vm_name)
            else:
                print_warning("VM '%s' is not paused." % vm_name)
                
        except libvirt.libvirtError as e:
            print_error("Failed to resume VM: %s" % str(e))
            logging.error("VM resume failed: %s - %s", vm_name, str(e))
        
        pause()
    
    
    def delete_vm(self):
        """Delete a virtual machine and optionally its disk"""
        clear_screen()
        print_header("Delete Virtual Machine", Colors.RED)
        
        domains = self.list_vms()
        if not domains:
            pause()
            return
        
        vm_name = safe_input("\n" + Colors.BOLD + "VM name to delete: " + Colors.ENDC)
        if not vm_name:
            return
        
        try:
            dom = self.conn.lookupByName(vm_name)
            
            # Check if VM is running
            if dom.isActive():
                print_warning("VM '%s' is currently running!" % vm_name)
                stop_first = safe_input("Stop VM before deletion? (y/N): ").lower()
                if stop_first == "y":
                    try:
                        dom.destroy()
                        print_info("VM stopped")
                    except libvirt.libvirtError as e:
                        print_error("Failed to stop VM: %s" % str(e))
                        pause()
                        return
                else:
                    print_error("Cannot delete a running VM")
                    pause()
                    return
            
            # Get disk paths before undefining
            disk_paths = []
            try:
                xml_desc = dom.XMLDesc(0)
                # Simple XML parsing to find disk paths
                import re
                disk_matches = re.findall(r"<source file='([^']*\.qcow2)'/>", xml_desc)
                disk_paths = disk_matches
            except Exception:
                pass
            
            # Confirm deletion
            print("\n" + Colors.YELLOW + Colors.BOLD + "WARNING: This will permanently delete the VM!" + Colors.ENDC)
            if disk_paths:
                print("\n" + Colors.BOLD + "Associated disk files:" + Colors.ENDC)
                for disk in disk_paths:
                    print("  - %s" % disk)
            
            confirm = safe_input("\nType VM name to confirm deletion: ")
            if confirm != vm_name:
                print_error("Deletion cancelled - name mismatch")
                pause()
                return
            
            # Undefine (delete) the VM
            try:
                dom.undefine()
                print_success("VM '%s' deleted from hypervisor!" % vm_name)
                logging.info("VM deleted: %s", vm_name)
            except libvirt.libvirtError as e:
                print_error("Failed to delete VM: %s" % str(e))
                logging.error("VM deletion failed: %s - %s", vm_name, str(e))
                pause()
                return
            
            # Ask about disk deletion
            if disk_paths:
                delete_disks = safe_input("\nDelete associated disk files? (y/N): ").lower()
                if delete_disks == "y":
                    for disk_path in disk_paths:
                        if os.path.exists(disk_path):
                            try:
                                os.remove(disk_path)
                                print_success("Deleted disk: %s" % disk_path)
                                logging.info("Deleted disk: %s", disk_path)
                            except OSError as e:
                                print_error("Failed to delete disk %s: %s" % (disk_path, str(e)))
                                logging.error("Disk deletion failed: %s - %s", disk_path, str(e))
                        else:
                            print_warning("Disk not found: %s" % disk_path)
                else:
                    print_info("Disk files preserved")
            
        except libvirt.libvirtError as e:
            print_error("VM not found: %s" % str(e))
        
        pause()
    
    # -------------------------------------------------------------------------
    # CONSOLE AND NETWORK
    # -------------------------------------------------------------------------
    
    def view_vm_console(self):
        """Open VM console using virt-viewer"""
        clear_screen()
        print_header("View VM Console", Colors.BLUE)
        
        domains = self.list_vms()
        if not domains:
            pause()
            return
        
        vm_name = safe_input("\n" + Colors.BOLD + "VM name to view: " + Colors.ENDC)
        if not vm_name:
            return
        
        # Check if virt-viewer is installed
        if os.system("which virt-viewer >/dev/null 2>&1") != 0:
            print_error("virt-viewer is not installed!")
            print_info("Install with: yum install virt-viewer")
            pause()
            return
        
        try:
            dom = self.conn.lookupByName(vm_name)
            
            print_info("Launching virt-viewer for '%s'..." % vm_name)
            os.system("virt-viewer %s &" % vm_name)
            print_success("Console viewer launched in background")
            
        except libvirt.libvirtError as e:
            print_error("Failed to open console: %s" % str(e))
        
        pause()
    
    
    def get_vm_ip(self):
        """Retrieve IP address of a running VM"""
        clear_screen()
        print_header("Get VM IP Address", Colors.BLUE)
        
        domains = self.list_vms()
        if not domains:
            pause()
            return
        
        vm_name = safe_input("\n" + Colors.BOLD + "VM name: " + Colors.ENDC)
        if not vm_name:
            return
        
        try:
            dom = self.conn.lookupByName(vm_name)
            
            if not dom.isActive():
                print_warning("VM '%s' must be running to retrieve IP!" % vm_name)
                pause()
                return
            
            print_info("Querying guest agent for network information...")
            
            try:
                # Query guest agent for interface addresses
                ifaces = dom.interfaceAddresses(
                    libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT, 0
                )
                
                found = False
                print("\n" + Colors.BOLD + "Network Interfaces:" + Colors.ENDC)
                
                for iface_name, iface_data in ifaces.iteritems():
                    if iface_name == "lo":
                        continue  # Skip loopback
                    
                    if iface_data["addrs"]:
                        print("\n  Interface: %s" % iface_name)
                        for addr in iface_data["addrs"]:
                            if addr["type"] == libvirt.VIR_IP_ADDR_TYPE_IPV4:
                                print("    IPv4: %s" % Colors.GREEN + 
                                      addr["addr"] + Colors.ENDC)
                                found = True
                            elif addr["type"] == libvirt.VIR_IP_ADDR_TYPE_IPV6:
                                print("    IPv6: %s" % addr["addr"])
                
                if not found:
                    print_warning("No IP addresses found")
                    
            except libvirt.libvirtError as e:
                print_error("Unable to retrieve IP address")
                print_info("Ensure qemu-guest-agent is installed and running in the VM")
                print_info("Install with: yum install qemu-guest-agent")
                
        except libvirt.libvirtError as e:
            print_error("VM not found: %s" % str(e))
        
        pause()


# =============================================================================
# MAIN PROGRAM
# =============================================================================

def main():
    """Main program entry point"""
    
    # Print banner
    clear_screen()
    print(Colors.BLUE + Colors.BOLD)
    print("")
    print("    KVM VIRTUAL MACHINE MANAGER")
    print("    RHEL 7.2 - Python 2.7")
    print("")
    print(Colors.ENDC)
    
    pause()
    
    # Initialize manager
    manager = VMManager()
    manager.connect()
    
    # Main menu loop
    while True:
        try:
            manager.show_menu()
            choice = safe_input("\n" + Colors.BOLD + "Enter choice: " + Colors.ENDC)
            
            if choice == "0":
                manager.show_hypervisor_info()
            elif choice == "1":
                clear_screen()
                print_header("All Virtual Machines", Colors.BLUE)
                manager.list_vms()
                pause()
            elif choice == "2":
                manager.get_vm_ip()
            elif choice == "3":
                manager.create_vm()
            elif choice == "4":
                manager.start_vm()
            elif choice == "5":
                manager.stop_vm()
            elif choice == "6":
                manager.suspend_vm()
            elif choice == "7":
                manager.resume_vm()
            elif choice == "8":
                manager.delete_vm()
            elif choice == "9":
                manager.view_vm_console()
            elif choice == "q" or choice == "Q":
                clear_screen()
                print_header("Shutting Down", Colors.YELLOW)
                print_info("Closing connection to hypervisor...")
                manager.close()
                print_success("Goodbye!")
                sys.exit(0)
            else:
                print_error("Invalid choice! Please select 0-9 or q.")
                pause()
                
        except KeyboardInterrupt:
            print("\n" + Colors.YELLOW + "Interrupted by user" + Colors.ENDC)
            manager.close()
            sys.exit(0)
        except Exception as e:
            print_error("Unexpected error: %s" % str(e))
            logging.error("Unexpected error: %s", str(e))
            pause()


if __name__ == "__main__":
    main()
