"""Keep physical connections within the render-only filter's advertised pins."""
import hashlib,json,pathlib,subprocess,sys
k=pathlib.Path(__file__).resolve().parent;src=pathlib.Path(sys.argv[1]);d=src/'drivers/wdm/audio/drivers/ac97'
pins=json.loads((k/'source-build002.json').read_text())['sources']
assert all(hashlib.sha256((d/n).read_bytes()).hexdigest()==h for n,h in pins.items())
old=k/'artifacts/source002-before003';old.mkdir(exist_ok=False)
for name in ['adapter.cpp','mintopo.cpp']:(old/name).write_bytes((d/name).read_bytes())
p=d/'adapter.cpp';s=p.read_text();a='''        if (NT_SUCCESS (ntStatus))
        {
            // register mic capture connection''';assert s.count(a)==1
p.write_text(s.replace(a,'''        if (NT_SUCCESS (ntStatus) && ulMicIn != (ULONG)-1)
        {
            // register mic capture connection'''))
p=d/'mintopo.cpp';s=p.read_text();a='''    // this is optional
    if (AdapterCommon->GetPinConfig (PINC_MICIN_PRESENT))
        *MicInDest = TransPinDefToPinNr (PIN_MICIN_DEST);
    else
        *MicInDest = (ULONG)-1;''';assert s.count(a)==1
p.write_text(s.replace(a,'''#ifdef XBOX_NT5_AC97_MMIO
    *MicInDest = (ULONG)-1;
#else
'''+a+'''
#endif'''))
subprocess.run(['git','-C',str(src),'diff','--check','--','drivers/wdm/audio/drivers/ac97'],check=True)
dest=k/'0209-render-connections-cumulative.patch';assert not dest.exists()
dest.write_bytes(subprocess.check_output(['git','-C',str(src),'diff','--','drivers/wdm/audio/drivers/ac97']))
print('Authored cumulative0209; source002 snapshot retained; no runtime verdict')
