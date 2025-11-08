class VMXMLGenerator:
    __slots__ = ()

    @staticmethod
    def generate_vm_xml(
        name: str, memory: int, vcpus: int, disk_path: str, iso_path: str | None = None
    ) -> str:
        cdrom_device = VMXMLGenerator._generate_cdrom(iso_path) if iso_path else ""

        return f"""<domain type='kvm'>
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
    </disk>{cdrom_device}
    <interface type='network'>
      <source network='default'/>
      <model type='virtio'/>
    </interface>
    <graphics type='vnc' port='-1' autoport='yes'/>
  </devices>
</domain>"""

    @staticmethod
    def _generate_cdrom(iso_path: str) -> str:
        return f"""
    <disk type='file' device='cdrom'>
      <driver name='qemu' type='raw'/>
      <source file='{iso_path}'/>
      <target dev='hdc' bus='ide'/>
      <readonly/>
    </disk>"""
