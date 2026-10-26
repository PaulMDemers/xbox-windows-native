"""Fresh sequences of retained legacy and new compiled code with a W1C bus model.
Not a physical boot, controller handoff, or permission to clear inherited state.
"""
import hashlib,json,struct,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('C:/xwn687/handoff001')
assert not P.exists() and not (K/'handoff001.json').exists();P.mkdir()
sys.path.insert(0,str(W/'work/python-packages'))
import unicorn as u
from unicorn import x86_const as x
root='/home/paul/xbox-windows-native/launcher677-validation002/default720'
sha=lambda b:hashlib.sha256(b).hexdigest()
r={'passed':False,'physical_access':False,'scope':'compiled legacy/new sequences, explicit modeled write-one-to-clear status','cases':[]}
pack=lambda *v:struct.pack('<'+'I'*len(v),*v)
try:
    r['parent_tree']=subprocess.check_output(['wsl','-d','Ubuntu','--','git','-C',root+'/source','write-tree'],text=True,timeout=15).strip()
    assert r['parent_tree']=='70c0a6c5aff82537f489e7d18410d5980fa797a7'
    assert not subprocess.check_output(['wsl','-d','Ubuntu','--','git','-C',root+'/source','diff','--name-only'],timeout=15)
    subprocess.run(['wsl','-d','Ubuntu','--','objcopy','-O','binary',root+'/source/obj/image-crom.elf','/mnt/c/xwn687/handoff001/legacy.bin'],check=True,timeout=20)
    old=(P/'legacy.bin').read_bytes();new=Path('C:/xwn687/build001/native.bin').read_bytes()
    syms=subprocess.check_output(['wsl','-d','Ubuntu','--','cat',root+'/symbols.txt'],text=True,timeout=15)
    oldsym={a[2]:int(a[0],16) for l in syms.splitlines() if len(a:=l.split())==3}
    newsym={a[2]:int(a[0],16) for l in Path('C:/xwn687/build001/symbols.stdout').read_text().splitlines() if len(a:=l.split())==3}
    r['legacy_image_sha256']=sha(old);r['new_image_sha256']=sha(new)
    for name,sequence in [('legacy_then_checked',[('legacy',0x54,0x96),('config',0x54,0x96)]),
                          ('checked_twice_then_block',[('config',0x54,0x96),('config',0x10,4),('block',0x70,0)])]:
        uc=u.Uc(u.UC_ARCH_X86,u.UC_MODE_32)
        uc.mem_map(0x02600000,0x200000);uc.mem_write(0x02600000,old)
        uc.mem_map(0x100000,0x10000);uc.mem_write(0x100000,new)
        uc.mem_map(0x200000,0x10000);state={'status':0,'data_index':0};trace=[];calls=[]
        def pin(uc,p,w,_):
            if p==0xc000:v=state['status'];assert w in [1,2]
            elif p==0xc006:v=4 if w==2 else 8
            elif (p,w)==(0xc009,1):v=[0x12,0x34,0x56,0x78][state['data_index']];state['data_index']+=1
            else:raise AssertionError(('read',p,w))
            trace.append(['in',p,w,v]);return v
        def pout(uc,p,w,v,_):
            trace.append(['out',p,w,v])
            if p==0xc000:assert w==2;state['status']&=~v
            elif p==0xc002:assert w==1 and v in [0x0a,0x0d];state['status']=0x10;state['data_index']=0
            else:assert p in [0xc004,0xc008] and w==1
        uc.hook_add(u.UC_HOOK_INSN,pin,None,1,0,x.UC_X86_INS_IN)
        uc.hook_add(u.UC_HOOK_INSN,pout,None,1,0,x.UC_X86_INS_OUT)
        for which,address,reg in sequence:
            pointer=0x204000;uc.mem_write(pointer,pack(0xdeadbeef));end=0x10ff00;sp=0x208000
            if which=='legacy':entry=oldsym['ReadfromSMBus'];args=[address,reg,1,pointer]
            elif which=='config':entry=newsym['native_config_read'];args=[address,reg,pointer]
            else:entry=newsym['native_read'];args=[reg,pointer]
            before=len(trace);uc.reg_write(x.UC_X86_REG_EFLAGS,2);uc.reg_write(x.UC_X86_REG_ESP,sp);uc.mem_write(sp,pack(end,*args))
            uc.emu_start(entry,end,timeout=1000000,count=100000)
            assert uc.reg_read(x.UC_X86_REG_EIP)==end
            calls.append({'function':which,'return':uc.reg_read(x.UC_X86_REG_EAX),'status_after':state['status'],
                          'value':struct.unpack('<I',uc.mem_read(pointer,4))[0],'io':trace[before:]})
        if name=='legacy_then_checked':
            assert [c['return'] for c in calls]==[0,3] and calls[0]['status_after']==0x10
            assert calls[1]['io']==[['in',0xc000,2,0x10]] and calls[1]['value']==0xdeadbeef
        else:
            assert all(c['return']==0 and c['status_after']==0 for c in calls)
            assert calls[-1]['value']==0x78563412
        r['cases'].append({'name':name,'calls':calls})
    r['passed']=True
except BaseException as e:r['failure']=repr(e);raise
finally:(K/'handoff001.json').write_text(json.dumps(r,indent=2)+'\n')
print('PASS two actual compiled-code sequences under explicit W1C model')
