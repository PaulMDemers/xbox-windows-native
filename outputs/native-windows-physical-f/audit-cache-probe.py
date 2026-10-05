"""Read-only cold verification of an owned, stopped cache-regression overlay."""
import argparse,pathlib,sys,subprocess,json,hashlib,importlib.util,struct
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/native-windows-physical-f'
p=argparse.ArgumentParser();p.add_argument('--run',required=True);a=p.parse_args()
assert a.run.startswith(('nt5-physical-f-cache-','nt5-physical-f-hives-','nt5-physical-f-high-allocation-')) and a.run.replace('-','').isalnum()
run=ws/'work/runs'/a.run;assert (run/'cleanup.json').exists()
raw=pathlib.Path('/home/paul/xbox-windows-native/fixtures')/(a.run+'-audit.raw');assert not raw.exists()
sys.path[:0]=[str(ws/'outputs/native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer
r={'scope':__doc__,'run':a.run,'files':[],'whole_filesystem_audit':False}
try:
    subprocess.run(['qemu-img','convert','-O','raw',str(run/'hdd.qcow2'),str(raw)],check=True)
    with raw.open('rb') as f:
        fatx.PARTITIONS['F']=(15633072*512,472764096*512);w=Writer(f,fatx.open_partition(f,raw,'F'))
        report=w.read('xwn-report-v2.txt');r['report']=report.decode('ascii').rstrip();r['probe_passed']='XWN-CACHE-PASS' in r['report']
        # Optional unchanged regression staged only into the explicit rename fixtures.
        if 'xwnrename.exe' in w.directory(1)['entries']:
            assert hashlib.sha256(w.read('xwnrename.exe')).hexdigest()=='6b379374ec52a8118fb6edbc824d64af2d2ffcc55ee471d8cbf7e4b650482d65'
            try:
                log=w.read('xwn-fs.log').decode('ascii')
                required=['Case-only rename of 42-byte name','42-byte case change persisted in directory',
                          'Same-directory rename to 42-byte name','42-byte rename persisted in directory',
                          'Reopen 42-byte renamed file','42-byte renamed data comparison',
                          'Delete 42-byte renamed file','Remove child directory','Remove test directory']
                r['rename_regression']={'log':log,'required_checks':required,
                    'passed':'Failures: 0\r\n' in log and 'FAIL:' not in log and all('PASS: '+s+'\r\n' in log for s in required),
                    'test_directory_removed':'xwnfstest' not in w.directory(1)['entries'],
                    'caveat':'API and cold checks do not negate delayed-write popups; inspect the screen and event log separately.'}
            except (KeyError,AssertionError) as e:r['rename_regression']={'passed':False,'error':repr(e)}
        for name in ['xwn-report-v2.txt','winnt/system32/config/sysevent.evt','xwn-cache-append.tmp','xwn-cache-map.tmp','xwn-cache-pressure.tmp']:
            try:data=w.read(name)
            except (KeyError,FileNotFoundError):r['files'].append({'path':name,'present':False});continue
            row={'path':name,'present':True,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
            if name.endswith('append.tmp'):
                row['pattern_match']=data==bytes((i*37+(i>>8)+0x65)&255 for i in range(131073))
            if name.endswith('pressure.tmp'):
                block=bytes((i*37+(i>>8)+0x77)&255 for i in range(65536))
                row['pattern_match']=len(data)==32*1024*1024 and all(data[i:i+65536]==block for i in range(0,len(data),65536))
            if name.endswith('map.tmp'):row['truncated_to_zero']=len(data)==0
            if name.endswith('.evt') or name.endswith('.txt'):
                target=k/'artifacts'/(a.run+'-'+pathlib.Path(name).name)
                if target.exists():assert target.read_bytes()==data
                else:target.write_bytes(data)
            r['files'].append(row)
        if a.run.startswith('nt5-physical-f-high-allocation-'):
            r['high_allocation_files']=[]
            for name in ['winnt/system32/drivers/xwnfatx.sys','winnt/system32/wbem/repository/cim.rep',
                         'winnt/system32/wbem/repository/$winmgmt.cfg','xwn-cache-append.tmp','xwn-cache-pressure.tmp']:
                parent=1;parts=w.parts(name)
                for part in parts[:-1]:parent=struct.unpack_from('<I',w.directory(parent)['entries'][part][2],44)[0]
                if parts[-1] not in w.directory(parent)['entries']:
                    r['high_allocation_files'].append({'path':name,'present':False});continue
                _,_,entry=w.directory(parent)['entries'][parts[-1]]
                start,size=struct.unpack_from('<II',entry,44)
                chain=[];error=None
                try:
                    if start:
                        for cluster in w.chain(start):chain.append(cluster)
                except AssertionError as e:error=repr(e)
                r['high_allocation_files'].append({'path':name,'size':size,'clusters':len(chain),
                    'first_cluster':start,'last_cluster':chain[-1] if chain else None,
                    'chain_capacity_sufficient':len(chain)*w.p.cluster_size>=size,'chain_error':error})
            for name in ['wbemcore.log','mofcomp.log','winmgmt.log']:
                try:data=w.read('winnt/system32/wbem/logs/'+name)
                except (KeyError,AssertionError) as e:
                    r.setdefault('wmi_log_errors',[]).append({'path':name,'error':repr(e)});continue
                assert len(data)<=1024*1024
                target=k/'artifacts'/(a.run+'-'+name)
                if target.exists():assert target.read_bytes()==data
                else:target.write_bytes(data)
finally:raw.unlink(missing_ok=True)
(k/(a.run+'-audit.json')).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
