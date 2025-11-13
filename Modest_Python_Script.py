#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
KVM VM Manager - RHEL 7.2
Contributors: Kherroubi Mohamed El Amine, Bousdjira Nadine
"""

import libvirt, os, sys, logging, re

LOG_FILE = "vm_manager.log"
DISK_IMAGE_DIR = "/var/lib/libvirt/images"
DEFAULT_BRIDGE = "kvmbr0"
QEMU_EMULATOR = "/usr/libexec/qemu-kvm"

logging.basicConfig(
    filename=LOG_FILE, level=logging.INFO, format="%(asctime)s - %(message)s"
)

VM_STATES = {
    libvirt.VIR_DOMAIN_RUNNING: "Running",
    libvirt.VIR_DOMAIN_PAUSED: "Paused",
    libvirt.VIR_DOMAIN_SHUTDOWN: "Shutting down",
    libvirt.VIR_DOMAIN_SHUTOFF: "Stopped",
    libvirt.VIR_DOMAIN_CRASHED: "Crashed",
}


def safe_input(prompt):
    try:
        return raw_input(prompt).strip()
    except:
        print("\nCancelled.")
        return ""


class VMManager(object):
    def __init__(self):
        self.conn = None

    def connect(self):
        os.system("clear")
        print("\n=== KVM Manager ===\n")
        try:
            self.conn = libvirt.open("qemu:///system")
            if not self.conn:
                sys.exit(1)
            print("Connected: " + self.conn.getHostname())
            logging.info("Connected: %s", self.conn.getHostname())
        except Exception as e:
            print("Error: " + str(e))
            sys.exit(1)
        safe_input("\nPress Enter...")

    def close(self):
        if self.conn:
            self.conn.close()

    def show_menu(self):
        os.system("clear")
        print("\n=== KVM Manager ===\n")
        print("[0] Hypervisor info")
        print("[1] List VMs")
        print("[2] Get VM IP")
        print("[3] Create VM")
        print("[4] Start VM")
        print("[5] Stop VM")
        print("[6] Suspend VM")
        print("[7] Resume VM")
        print("[8] Delete VM")
        print("[9] VM console")
        print("[q] Quit\n")

    def show_hypervisor_info(self):
        os.system("clear")
        print("\n=== Hypervisor Info ===\n")
        try:
            info = self.conn.getInfo()
            print("Hostname:     " + self.conn.getHostname())
            print("Architecture: " + info[0])
            print("Memory:       %d MB" % info[1])
            print("CPUs:         %d" % info[2])
            print("Frequency:    %d MHz" % info[3])
            domains = self.conn.listAllDomains()
            print("VMs running:  %d" % sum(1 for d in domains if d.isActive()))
            print("VMs total:    %d" % len(domains))
        except Exception as e:
            print("Error: " + str(e))
        safe_input("\nPress Enter...")

    def list_vms(self):
        try:
            domains = self.conn.listAllDomains()
        except:
            print("Error listing VMs")
            return []
        if not domains:
            print("\nNo VMs found.")
            return []
        print(
            "\n%-5s %-20s %-6s %-8s %-10s" % ("ID", "Name", "vCPUs", "RAM(MB)", "State")
        )
        print("-" * 55)
        for dom in domains:
            vm_id = dom.ID() if dom.ID() != -1 else "-"
            state = VM_STATES.get(dom.state()[0], "Unknown")
            try:
                info = dom.info()
                print(
                    "%-5s %-20s %-6d %-8d %-10s"
                    % (vm_id, dom.name(), info[3], info[1] / 1024, state)
                )
            except:
                print(
                    "%-5s %-20s %-6s %-8s %-10s" % (vm_id, dom.name(), "-", "-", state)
                )
        print("-" * 55)
        return domains

    def create_vm(self):
        os.system("clear")
        print("\n=== Create VM ===\n")
        vm_name = safe_input("VM name: ")
        if not vm_name:
            return
        try:
            self.conn.lookupByName(vm_name)
            print("VM already exists!")
            safe_input("\nPress Enter...")
            return
        except:
            pass
        try:
            memory = int(safe_input("Memory MB [1024]: ") or "1024")
            vcpus = int(safe_input("vCPUs [1]: ") or "1")
            disk_size = int(safe_input("Disk GB [10]: ") or "10")
            iso_path = safe_input("ISO path: ")
            if not os.path.exists(iso_path):
                print("ISO not found")
                safe_input("\nPress Enter...")
                return
        except:
            print("Invalid input")
            safe_input("\nPress Enter...")
            return
        disk_path = "%s/%s.qcow2" % (DISK_IMAGE_DIR, vm_name)
        if os.system("qemu-img create -f qcow2 %s %dG" % (disk_path, disk_size)) != 0:
            print("Disk creation failed")
            safe_input("\nPress Enter...")
            return
        xml = """<domain type='kvm'>
  <name>%s</name>
  <memory unit='MiB'>%d</memory>
  <vcpu>%d</vcpu>
  <os><type arch='x86_64'>hvm</type><boot dev='cdrom'/><boot dev='hd'/></os>
  <features><acpi/><apic/></features>
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
  </devices>
</domain>""" % (
            vm_name,
            memory,
            vcpus,
            QEMU_EMULATOR,
            disk_path,
            iso_path,
            DEFAULT_BRIDGE,
        )
        try:
            dom = self.conn.defineXML(xml)
            print("VM created successfully!")
            logging.info("VM created: %s", vm_name)
            if safe_input("\nStart now? (y/N): ").lower() == "y":
                dom.create()
                print("VM started!")
                logging.info("VM started: %s", vm_name)
        except Exception as e:
            print("Error: " + str(e))
        safe_input("\nPress Enter...")

    def start_vm(self):
        os.system("clear")
        print("\n=== Start VM ===\n")
        self.list_vms()
        vm_name = safe_input("\nVM name: ")
        if not vm_name:
            return
        try:
            dom = self.conn.lookupByName(vm_name)
            state = dom.state()[0]
            if state == libvirt.VIR_DOMAIN_SHUTOFF:
                dom.create()
                print("VM started!")
                logging.info("VM started: %s", vm_name)
            elif state == libvirt.VIR_DOMAIN_RUNNING:
                print("VM already running.")
            elif state == libvirt.VIR_DOMAIN_PAUSED:
                print("VM is paused. Use Resume.")
            else:
                print("VM state: " + VM_STATES.get(state, "Unknown"))
        except Exception as e:
            print("Error: " + str(e))
        safe_input("\nPress Enter...")

    def stop_vm(self):
        os.system("clear")
        print("\n=== Stop VM ===\n")
        self.list_vms()
        vm_name = safe_input("\nVM name: ")
        if not vm_name:
            return
        try:
            dom = self.conn.lookupByName(vm_name)
            if dom.state()[0] != libvirt.VIR_DOMAIN_RUNNING:
                print("VM not running.")
                safe_input("\nPress Enter...")
                return
            print("\n[1] Graceful shutdown")
            print("[2] Force stop")
            choice = safe_input("\nChoice [1]: ") or "1"
            if choice == "2":
                dom.destroy()
                print("VM force stopped!")
                logging.info("VM force stopped: %s", vm_name)
            else:
                dom.shutdown()
                print("VM shutting down...")
                logging.info("VM shutdown: %s", vm_name)
        except Exception as e:
            print("Error: " + str(e))
        safe_input("\nPress Enter...")

    def suspend_vm(self):
        os.system("clear")
        print("\n=== Suspend VM ===\n")
        self.list_vms()
        vm_name = safe_input("\nVM name: ")
        if not vm_name:
            return
        try:
            dom = self.conn.lookupByName(vm_name)
            state = dom.state()[0]
            if state == libvirt.VIR_DOMAIN_RUNNING:
                dom.suspend()
                print("VM suspended!")
                logging.info("VM suspended: %s", vm_name)
            elif state == libvirt.VIR_DOMAIN_PAUSED:
                print("VM already suspended.")
            else:
                print("VM not running.")
        except Exception as e:
            print("Error: " + str(e))
        safe_input("\nPress Enter...")

    def resume_vm(self):
        os.system("clear")
        print("\n=== Resume VM ===\n")
        self.list_vms()
        vm_name = safe_input("\nVM name: ")
        if not vm_name:
            return
        try:
            dom = self.conn.lookupByName(vm_name)
            state = dom.state()[0]
            if state == libvirt.VIR_DOMAIN_PAUSED:
                dom.resume()
                print("VM resumed!")
                logging.info("VM resumed: %s", vm_name)
            elif state == libvirt.VIR_DOMAIN_RUNNING:
                print("VM already running.")
            else:
                print("VM not paused.")
        except Exception as e:
            print("Error: " + str(e))
        safe_input("\nPress Enter...")

    def delete_vm(self):
        os.system("clear")
        print("\n=== Delete VM ===\n")
        self.list_vms()
        vm_name = safe_input("\nVM name: ")
        if not vm_name:
            return
        try:
            dom = self.conn.lookupByName(vm_name)
            if dom.isActive():
                print("VM is running!")
                if safe_input("Stop first? (y/N): ").lower() == "y":
                    try:
                        dom.destroy()
                        print("VM stopped")
                    except Exception as e:
                        print("Error: " + str(e))
                        safe_input("\nPress Enter...")
                        return
                else:
                    print("Cannot delete running VM")
                    safe_input("\nPress Enter...")
                    return
            disk_paths = []
            try:
                xml_desc = dom.XMLDesc(0)
                disk_paths = re.findall(r"<source file='([^']*\.qcow2)'/>", xml_desc)
            except:
                pass
            print("\nWARNING: Permanent deletion!")
            if disk_paths:
                print("\nDisks:")
                for disk in disk_paths:
                    print("  " + disk)
            if safe_input("\nType VM name to confirm: ") != vm_name:
                print("Cancelled")
                safe_input("\nPress Enter...")
                return
            try:
                dom.undefine()
                print("VM deleted!")
                logging.info("VM deleted: %s", vm_name)
            except Exception as e:
                print("Error: " + str(e))
                safe_input("\nPress Enter...")
                return
            if disk_paths and safe_input("\nDelete disks? (y/N): ").lower() == "y":
                for disk_path in disk_paths:
                    if os.path.exists(disk_path):
                        try:
                            os.remove(disk_path)
                            print("Deleted: " + disk_path)
                            logging.info("Deleted disk: %s", disk_path)
                        except OSError as e:
                            print("Error: " + str(e))
                    else:
                        print("Not found: " + disk_path)
        except Exception as e:
            print("Error: " + str(e))
        safe_input("\nPress Enter...")

    def view_vm_console(self):
        os.system("clear")
        print("\n=== VM Console ===\n")
        self.list_vms()
        vm_name = safe_input("\nVM name: ")
        if not vm_name:
            return
        if os.system("which virt-viewer >/dev/null 2>&1") != 0:
            print("virt-viewer not installed!")
            print("Install: yum install virt-viewer")
            safe_input("\nPress Enter...")
            return
        try:
            dom = self.conn.lookupByName(vm_name)
            print("Launching console...")
            os.system("virt-viewer %s &" % vm_name)
            print("Console launched")
        except Exception as e:
            print("Error: " + str(e))
        safe_input("\nPress Enter...")

    def get_vm_ip(self):
        os.system("clear")
        print("\n=== Get VM IP ===\n")
        self.list_vms()
        vm_name = safe_input("\nVM name: ")
        if not vm_name:
            return
        try:
            dom = self.conn.lookupByName(vm_name)
            if not dom.isActive():
                print("VM must be running!")
                safe_input("\nPress Enter...")
                return
            print("Querying guest agent...")
            try:
                ifaces = dom.interfaceAddresses(
                    libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT, 0
                )
                found = False
                print("\nInterfaces:")
                for iface_name, iface_data in ifaces.iteritems():
                    if iface_name == "lo":
                        continue
                    if iface_data["addrs"]:
                        print("\n  " + iface_name)
                        for addr in iface_data["addrs"]:
                            if addr["type"] == libvirt.VIR_IP_ADDR_TYPE_IPV4:
                                print("    IPv4: " + addr["addr"])
                                found = True
                            elif addr["type"] == libvirt.VIR_IP_ADDR_TYPE_IPV6:
                                print("    IPv6: " + addr["addr"])
                if not found:
                    print("No IPs found")
            except:
                print("Cannot retrieve IP")
                print("Install qemu-guest-agent in VM")
        except Exception as e:
            print("Error: " + str(e))
        safe_input("\nPress Enter...")


def main():
    os.system("clear")
    print("\n=== KVM Manager ===")
    print("RHEL 7.2 - Python 2.7\n")
    safe_input("Press Enter...")

    manager = VMManager()
    manager.connect()

    while True:
        try:
            manager.show_menu()
            choice = safe_input("Choice: ")
            if choice == "0":
                manager.show_hypervisor_info()
            elif choice == "1":
                os.system("clear")
                print("\n=== All VMs ===\n")
                manager.list_vms()
                safe_input("\nPress Enter...")
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
                os.system("clear")
                print("\nClosing connection...")
                manager.close()
                print("Goodbye!")
                sys.exit(0)
            else:
                print("Invalid choice!")
                safe_input("\nPress Enter...")
        except KeyboardInterrupt:
            print("\n\nInterrupted")
            manager.close()
            sys.exit(0)
        except Exception as e:
            print("Error: " + str(e))
            logging.error("Error: %s", str(e))
            safe_input("\nPress Enter...")


if __name__ == "__main__":
    main()
