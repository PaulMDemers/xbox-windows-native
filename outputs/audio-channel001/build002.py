"""Build the NT5 helper and test the exact waveform plus independent capture rejection."""
import array,hashlib,importlib.util,json,pathlib,subprocess,sys,wave
k=pathlib.Path(__file__).resolve().parent;out=k/'artifacts/build002';out.mkdir(parents=True,exist_ok=False)
gcc='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc'
flags=['-Os','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-nostdlib','-fno-stack-protector','-fno-builtin','-Wl,--entry,_mainCRTStartup@0','-Wl,--subsystem,console:5.0']
subprocess.run([gcc,*flags,'-o',str(out/'probe.exe'),str(k/'probe.c'),'-lkernel32','-luser32','-lwinmm'],check=True)
subprocess.run(['gcc','-std=c99','-O2','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-o',str(out/'test-waveform'),str(k/'test-waveform.c')],check=True)
raw=subprocess.check_output([str(out/'test-waveform')]);assert len(raw)==6*144000*4
spec=importlib.util.spec_from_file_location('capture',k/'analyze-capture.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def check(name,data,expected):
 p=out/(name+'.wav')
 with wave.open(str(p),'wb') as w:w.setparams((2,2,48000,0,'NONE','not compressed'));w.writeframes(data)
 r=m.analyze(p);assert r['passed']==expected,(name,r);return {'name':name,'expected':expected,'result':r}
results=[check('correct',raw,True)]
s=array.array('h',raw)
swapped=array.array('h',s)
swapped[0::2]=s[1::2];swapped[1::2]=s[0::2]
results.append(check('swapped',swapped.tobytes(),False))
both=array.array('h',s);both[1::2]=s[0::2]
results.append(check('duplicated-left',both.tobytes(),False))
results.append(check('silent',bytes(len(raw)),False))
results.append(check('missing-phase',raw[:144000*4*5],False))
results.append(check('missing-gaps',b''.join(raw[i*144000*4:(i*144000+96000)*4] for i in range(6)),False))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record={'passed':True,'compiler':gcc,'compiler_version':subprocess.check_output([gcc,'--version'],text=True).splitlines()[0],'flags':flags,'driver_changed':False,'probe_sha256':sha(out/'probe.exe'),'source_sha256':{p.name:sha(p) for p in [k/'probe.c',k/'waveform.h',k/'test-waveform.c',k/'analyze-capture.py',k/'build.py']},'sanitizers':'ASan and UBSan','waveform_sample_values_checked':6*144000*2,'capture_cases':results}
(k/'build002.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({'passed':True,'probe_sha256':record['probe_sha256'],'capture_tests':len(results)}))
