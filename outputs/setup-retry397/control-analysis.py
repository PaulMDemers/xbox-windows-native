"""Separate control discriminator; never rewrites the complete audit's failed gates."""
import hashlib,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent;O=K/'control001';A=K/'artifacts/control001/E/xwndemo397control001'
read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest()
c=read(O/'collection.json');a=read(O/'audit.json');assert c['completed']
sys.path.insert(0,str(K.parent/'video-text-oracle206'))
from runner_analysis import helper
rows=lambda name:(A/name).read_text().splitlines() if (A/name).exists() else []
trace=rows('file-trace.log');api=rows('file-api.log');cmd=rows('cmd/file-trace.log')
r=dict(scope='Original0101 setup-first control; copy bytes and known enumeration defects separate',setup_before_files_passed=False,physical_release_qualified=False)
try:
 r['gate_helper']=helper((A/'gate/wizard201.log').read_bytes(),0)
 expected=['BEGIN','GATE_START','GATE_EXIT 0','FILE_API_START']
 r['setup_before_files_passed']=trace[:4]==expected and trace.count('GATE_EXIT 0')==1
except (OSError,AssertionError,ValueError) as e:r['gate_failure']=repr(e)
expected=read(K/'package.json')['helpers'][-1]
r['native_bytes_exact']=all((A/n).exists() and (A/n).stat().st_size==expected['bytes'] and sha((A/n).read_bytes())==expected['sha256'] for n in ['saved.bmp','reopened.bmp']) and all((A/n).exists() and (A/n).read_bytes()==b'XWN386 text persistence check\r\n' for n in ['note.txt','note-reopened.txt'])
r['native_operations_completed']=all(api.count(tag+' 1 0')==1 for tag in ['COPY_BMP','MOVE_BMP','REOPEN_BMP','MOVE_NOTE','REOPEN_NOTE'])
r['original_duplicate_enumeration_reproduced']=api.count('ENUM_EXACT 0 111')==2 and api[-1:]==['FILE_API_END 2']
r['api_terminal']=api[-1:] if api else []
r['file_child_exit']=[v for v in trace if v.startswith('FILE_API_EXIT ')]
r['cmd_results']=[v for v in cmd if v.startswith('RC ')]
r['cmd_failed']=cmd.count('FILE_FAILED')==1
r['native_intermediates_absent']=all(c['intermediate_files_absent'][n] for n in ['saved.tmp','note.tmp'])
r['native_copy_discriminator_passed']=all(r[n] for n in ['setup_before_files_passed','native_bytes_exact','native_operations_completed','native_intermediates_absent']) and r['file_child_exit'] in [['FILE_API_EXIT 0'],['FILE_API_EXIT 1']] and api[-1:] in [['FILE_API_END 0'],['FILE_API_END 2']]
r['independent_workload_and_integrity_passed']=all(a[n] for n in ['audio_probe_passed','audio_state_passed','audio_children_joined','setup_gate_passed','display_workload_passed','integrity_passed','mode720p_passed']) and a['normal_shutdown_count']==1
r['original_complete_scope_passed']=a['scoped_combined_passed'];r['strict_qualification_passed']=a['strict_qualification_passed']
r['warnings_errors']=a['warnings_errors'];r['normal_shutdown_count']=a['normal_shutdown_count']
r['limits']='No cause inferred merely from settling setup. This original-driver control is not a matched candidate result or a waiver of duplicate enumeration/CMD failure. Original audit is unchanged.'
p=O/'control-analysis.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
