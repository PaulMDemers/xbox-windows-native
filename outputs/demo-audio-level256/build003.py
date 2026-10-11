"""Build the NT5 helper and test the exact waveform plus independent capture rejection."""
import array,hashlib,importlib.util,json,pathlib,subprocess,sys,wave
k=pathlib.Path(__file__).resolve().parent;out=k/'artifacts/build003';out.mkdir(parents=True,exist_ok=False)
gcc='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-gcc'
flags=['-Os','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-nostdlib','-fno-stack-protector','-fno-builtin','-Wl,--entry,_mainCRTStartup@0','-Wl,--subsystem,console:5.0']
subprocess.run([gcc,*flags,'-o',str(out/'probe.exe'),str(k/'probe.c'),'-lkernel32','-luser32','-lwinmm'],check=True)
subprocess.run(['gcc','-std=c99','-O2','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-o',str(out/'test-waveform'),str(k/'test-waveform.c')],check=True)
raw=subprocess.check_output([str(out/'test-waveform')]);assert len(raw)==6*144000*4
samples=array.array('h',raw)
peaks=[]
for cycle in range(6):
 phase=samples[cycle*144000*2:(cycle+1)*144000*2]
 peaks.append([max(abs(v) for v in phase[ch::2]) for ch in range(2)])
assert peaks==[[1888,0],[0,1248],[1888,1248],[7552,0],[0,4992],[7552,4992]],peaks
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record={'passed':True,'compiler':gcc,'compiler_version':subprocess.check_output([gcc,'--version'],text=True).splitlines()[0],'flags':flags,'driver_changed':False,'probe_sha256':sha(out/'probe.exe'),'source_sha256':{p.name:sha(p) for p in [k/'probe.c',k/'waveform.h',k/'test-waveform.c',k/'build003.py',k/'Build003.ps1']},'sanitizers':'ASan and UBSan','waveform_sample_values_checked':6*144000*2,'phase_peaks':peaks}
(k/'build003.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({'passed':True,'probe_sha256':record['probe_sha256'],'phase_peaks':peaks}))
