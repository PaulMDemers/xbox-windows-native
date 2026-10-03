import hashlib,json,pathlib,sys,xml.etree.ElementTree as ET
root=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
sys.path.insert(0,'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts')
import fatx_stage_boot as fatx
image=pathlib.Path('/home/paul/xbox-windows-native/fixtures/dashboard-inspection.raw')
assert image.resolve().parent==pathlib.Path('/home/paul/xbox-windows-native/fixtures') and not image.is_symlink()
fatx.PARTITIONS['C']=(0x465400*512,0xfa000*512)
with image.open('r+b') as fp:
    part=fatx.open_partition(fp,image,'C')
    config=ET.fromstring(fatx.read_path_file(fp,part,'Config.xml'))
    net=config.find('Settings/Network');net.set('Enable','Yes');net.set('Type','DHCP')
    ET.SubElement(net,'AutoDetect').text='No'
    ftp=config.find('Settings/FTP');ftp.set('Enable','Yes')
    ET.SubElement(ftp,'MaxUsers').text='1'
    ET.SubElement(ftp,'AllowAnon').text='No'
    data=ET.tostring(config,encoding='utf-8',xml_declaration=True)
    result=fatx.write_path_file(fp,part,'Config.xml',data)
(root/'outputs/native-windows-stage2/unleashx-ftp-fixture.json').write_text(json.dumps({'config':result.__dict__,'network':'QEMU restricted user network; only localhost FTP control forwarding allowed; no external connections.'},indent=2)+'\n')
(root/'outputs/native-windows-stage2/unleashx-ftp-Config.xml').write_bytes(data)
