"""Expose the actual fixed render path in one WaveCyclic filter, without a node-less topology filter."""
import hashlib,json,pathlib,subprocess,sys
k=pathlib.Path(__file__).resolve().parent;src=pathlib.Path(sys.argv[1]);d=src/'drivers/wdm/audio/drivers/ac97'
pins=json.loads((k/'source-build003.json').read_text())['sources']
assert all(hashlib.sha256((d/n).read_bytes()).hexdigest()==h for n,h in pins.items())
old=k/'artifacts/source003-before004';old.mkdir(exist_ok=False)
for n in ['adapter.cpp','miniport.cpp','mintopo.cpp']:(old/n).write_bytes((d/n).read_bytes())
# The PC target keeps its original topology implementation. NT5 fixed-render
# never instantiates this redundant filter or registers inter-filter bridges.
(d/'mintopo.cpp').write_bytes(subprocess.check_output(['git','-C',str(src),'show',':drivers/wdm/audio/drivers/ac97/mintopo.cpp']))
p=d/'adapter.cpp';s=p.read_text()
a=s.index('    //\n    // Start the topology miniport.')
b=s.index('    //\n    // Start the wave miniport.',a)
s=s[:a]+'#ifndef XBOX_NT5_AC97_MMIO\n'+s[a:b]+'#endif\n\n'+s[b:]
a=s.index('    //\n    // Establish physical connections between filters as shown.')
b=s.index('    //\n    // Release the adapter common object.',a)
s=s[:a]+'#ifndef XBOX_NT5_AC97_MMIO\n'+s[a:b]+'#endif\n\n'+s[b:]
# Keep the unused pointer out of this target (other cleanup pointers stay NULL).
s=s.replace('    PMINIPORT               miniTopology            = NULL;', '#ifndef XBOX_NT5_AC97_MMIO\n    PMINIPORT               miniTopology            = NULL;\n#endif')
p.write_text(s)
p=d/'miniport.cpp';s=p.read_text()
anchor='static PCFILTER_DESCRIPTOR MiniportFilterDescriptor ='
assert s.count(anchor)==1
s=s.replace(anchor,'#ifdef XBOX_NT5_AC97_MMIO\nstatic GUID Audio207Categories[2];\n#endif\n\n'+anchor)
anchor='''            MiniportFilterDescriptor.PinCount = 2;
            MiniportFilterDescriptor.NodeCount = 1;
            MiniportFilterDescriptor.ConnectionCount = 2;'''
assert s.count(anchor)==1
s=s.replace(anchor,anchor+'''
            // PCM -> actual DAC -> external analog output. There are no
            // hardware mixer controls requiring a separate topology filter.
            MiniportPins[PIN_WAVEOUT_BRIDGE].KsPinDescriptor.Category = &KSNODETYPE_SPEAKER;
            Audio207Categories[0] = KSCATEGORY_AUDIO;
            Audio207Categories[1] = KSCATEGORY_RENDER;
            MiniportFilterDescriptor.CategoryCount = 2;
            MiniportFilterDescriptor.Categories = Audio207Categories;''')
p.write_text(s)
subprocess.run(['git','-C',str(src),'diff','--check','--','drivers/wdm/audio/drivers/ac97'],check=True)
p=k/'0210-waveonly-cumulative.patch';assert not p.exists()
p.write_bytes(subprocess.check_output(['git','-C',str(src),'diff','--','drivers/wdm/audio/drivers/ac97']))
print('Authored cumulative0210; prior source preserved. Runtime validation pending.')
