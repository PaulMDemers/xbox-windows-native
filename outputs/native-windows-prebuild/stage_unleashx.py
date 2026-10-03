"""Stage the supplied dashboard and our Xromwell into one private FATX fixture."""
import hashlib,json,pathlib,sys,zipfile,xml.etree.ElementTree as ET
root=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
sys.path.insert(0,'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts')
import fatx_stage_boot as fatx
image=pathlib.Path('/home/paul/xbox-windows-native/fixtures/dashboard-inspection.raw')
assert image.resolve().parent==pathlib.Path('/home/paul/xbox-windows-native/fixtures') and not image.is_symlink()
manifest=root/'outputs/native-windows-stage2/unleashx-fixture.json'
if manifest.exists():raise SystemExit('Fixture already staged; inspect before rebuilding')
zip_path=root/'UnleashX.zip'
with zipfile.ZipFile(zip_path) as z:
    xbe=z.read('default.xbe')
    assert xbe[:4]==b'XBEH'
    config=ET.fromstring(z.read('Config.xml'))
    for child in list(config):
        if child.tag!='Settings':config.remove(child)
    settings=config.find('Settings')
    for child in list(settings):
        if child.tag!='Preference':settings.remove(child)
    ET.SubElement(settings,'Network',{'Enable':'No'})
    ET.SubElement(settings,'FTP',{'Enable':'No'})
    pref=settings.find('Preference')
    for child in list(pref):
        if child.tag in ('SNTP','AutoSetTime','Skin'):pref.remove(child)
    ET.SubElement(pref,'AutoSetTime').text='No'
    ET.SubElement(pref,'EnableSoundTrack').text='Off'
    ET.SubElement(pref,'Data',{'AutoLaunch':'No'})
    menu=ET.SubElement(config,'Menu')
    ET.SubElement(menu,'Item',{'Action':r'E:\Apps\XWN\default.xbe'}).text='XWN: launch native loader diagnostic'
    config_data=ET.tostring(config,encoding='utf-8',xml_declaration=True)
fatx.PARTITIONS['C']=(0x465400*512,0xfa000*512)
records=[]
with image.open('r+b') as fp:
    for partition,files in {
        'C':{'evoxdash.xbe':xbe,'xboxdash.xbe':xbe,'Config.xml':config_data},
        'E':{'Apps/XWN/default.xbe':(root/'outputs/native-windows-build/artifacts/xromwell.xbe').read_bytes()},
    }.items():
        part=fatx.open_partition(fp,image,partition)
        for name,data in files.items():
            result=fatx.write_path_file(fp,part,name,data)
            records.append({'partition':partition,**result.__dict__})
manifest.write_text(json.dumps({'supplied_zip_sha256':hashlib.sha256(zip_path.read_bytes()).hexdigest(),'unleashx_xbe_sha256':hashlib.sha256(xbe).hexdigest(),'fatx_writer_sha256':hashlib.sha256(pathlib.Path(fatx.__file__).read_bytes()).hexdigest(),'files':records,'scope':'Private emulator fixture; dashboard launch through Complex BIOS, not physical softmod exploit validation.'},indent=2)+'\n')
(root/'outputs/native-windows-stage2/unleashx-Config.xml').write_bytes(config_data)
print('Private dashboard fixture staged; all files read back and hash-verified.')
