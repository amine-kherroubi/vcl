#!/bin/bash
# RHEL KVM setup and VM deployment script

# Contributors:
# - Mohamed El Amine Kherroubi
# - Nadine Bousdjira	

# Register system and update packages
subscription-manager register --auto-attach
yum -y update
reboot

# Install KVM and management tools
yum -y install qemu-kvm libvirt virt-install virt-viewer virt-manager bridge-utils

# Load KVM kernel module and enable libvirt service
modprobe kvm
systemctl start libvirtd
systemctl enable libvirtd

# Verify KVM and virtualization status
lsmod | grep kvm
lscpu | grep Virtualization
systemctl status libvirtd

# Configure network bridge for VMs
nmcli c add type bridge autoconnect yes con-name kvmbr0 ifname kvmbr0
nmcli c delete eno16777736
nmcli c add type bridge-slave autoconnect yes con-name eno16777736 ifname eno16777736 master kvmbr0
systemctl restart NetworkManager

# Prepare ISO storage directory
mkdir -p /ISO

# Mount VMware shared folder
sudo mount -t fuse.vmhgfs-fuse .host:/ /mnt/hgfs -o allow_other

# Move RHEL ISO into local ISO directory
mv /mnt/hgfs/shared/rhel-server-7.2-x86_64-dvd.iso /ISO/

# Create first virtual machine
virt-install \
  --virt-type kvm \
  --name VM1 \
  --os-type linux \
  --os-variant rhel7.2 \
  --cdrom /ISO/rhel-server-7.2-x86_64-dvd.iso \
  --disk path=/var/lib/libvirt/images/VM1.qcow2,format=qcow2,size=10 \
  --memory 1024 \
  --vcpus 2 \
  --network bridge=kvmbr0

# Create second virtual machine
virt-install \
  --virt-type kvm \
  --name VM2 \
  --os-type linux \
  --os-variant rhel7.2 \
  --cdrom /ISO/rhel-server-7.2-x86_64-dvd.iso \
  --disk path=/var/lib/libvirt/images/VM2.qcow2,format=qcow2,size=10 \
  --memory 1024 \
  --vcpus 2 \
  --network bridge=kvmbr0

# List running VMs and open viewers
virsh list
virt-viewer VM1
virt-viewer VM2

