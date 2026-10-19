"""MIT. Independent cold review of exact Welcome-close control; no runtime access."""
import datetime,hashlib,json,re,struct,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn580/pc001')
sys.path.insert(0,str(W/'work/python-packages'));from Registry import Registry
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
state=json.loads((K/'ntfs-phase1.json').read_text());cold=json.loads((K/'ntfs-cold1-002.json').read_text());collect=json.loads((K/'collection001.json').read_text())
assert state['closed'] and state['exit_code']==0 and not any(state.get(x) for x in ['deadline','host_quit','host_terminate','host_kill','space_stop'])
assert cold['complete'] and cold['audit_unchanged'] and cold['source_unchanged'] and cold['normal_shutdown_delta']==1
assert all(x['clean'] and x['header_valid'] and x['independent_raw_values_agree'] for x in cold['hives'])
assert sha(P/'disk.qcow2')==state['disk_sha256']==cold['disk_sha256']
logpath=P/'collection001/close.txt';log=logpath.read_text();numbers={n:int(v) for n,v in re.findall(r'^([a-z_]+)=(\d+)$',log,re.M)}
for n in ['close_mode','fake_created','candidate_count','process_open','close_posted','window_gone','fake_survived','close_qualified','restart_privilege','restart_requested']:assert numbers[n]==1,n
assert numbers['process_wait']==0
rows=re.findall(r'window hwnd=([0-9a-f]+) pid=(\d+).*?class=\[([^\]]+)\] title=\[([^\]]+)\] module=\[([^\]]+)\] candidate=(\d+)',log)
real=[r for r in rows if r[5]=='1'];fake=[r for r in rows if r[4].lower()=='c:\\xwn580-kit\\run580.exe']
assert len(real)==3 and len(set((r[0],r[1]) for r in real))==1
assert all(r[2]=='_BerksWin2kWelcomeApp_' and r[3]=='Getting Started with Windows 2000' and r[4].lower()=='c:\\winnt\\welcome.exe' for r in real)
assert len(fake)==1 and fake[0][2:4]==real[0][2:4] and fake[0][1]!=real[0][1] and fake[0][5]=='0'
assert 'child id=100 class=[Button] title=[&Show this screen at startup.] visible=1 check=1' in log
show=[];users=[]
for phase in [0,1]:
 p=P/f'cold{phase}-002/files/Documents and Settings/Win2K/NTUSER.DAT';data=p.read_bytes();seq=struct.unpack_from('<II',data,4);assert data[:4]==b'regf' and seq[0]==seq[1]
 value=Registry.Registry(str(p)).open('Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\tips').value('Show').value();show.append(value);users.append(dict(phase=phase,sha256=sha(p),sequences=seq,show=value))
assert show==[1,1]
a=json.loads((P/'cold0-002/manifest.json').read_text());b=json.loads((P/'cold1-002/manifest.json').read_text())
assert a['winnt/welcome.exe']['sha256']==b['winnt/welcome.exe']['sha256']=='80a904ead0bea82aab8b17fac12d30170d1e6e7f2166eec6dc01e05c0673c190'
assert b['xwn580-kit/run580.exe']['sha256']==json.loads((K/'runner-build001.json').read_text())['rows'][0]['sha256']
result=dict(passed=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),close_log_sha256=sha(logpath),candidate_count=1,normal_close_posted=True,process_exited=True,real_window_gone=True,wrong_process_lookalike_survived=True,startup_checkbox_checked=True,startup_show_before_after=show,user_hives=users,normal_shutdown_delta=1,new_system_events=cold['new_system_events'],protected_windows_binaries_unchanged=True,disk_sha256=sha(P/'disk.qcow2'),scope='Fresh PC standalone Welcome close only. No delayed arrival/game integration/Xbox input/performance qualification. Guest event timestamps are not calibrated UTC; generated times place shutdown after startup despite event record ordering.',physical_access=False)
out=K/'review001.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print('Exact Welcome close and wrong-process refusal qualified; startup Show unchanged')
