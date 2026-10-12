"""Independent little-endian generation decoder; does not prove runtime hooks."""
import struct
SIZE=5440
def decode(data,expected_keys,expected_identities,expected_names):
 assert len(data)==SIZE and len(expected_keys)==len(expected_identities)==len(expected_names)==4
 h=struct.unpack_from('<12Q',data);assert h[:3]==(0x3438324e5758,284,SIZE)
 mode,owner,errors,calls,seq,sealed,count,nextgen,reserved=h[3:]
 assert mode in (0,1) and owner and errors==reserved==0 and sealed==1 and count==4
 assert calls==seq==(16 if mode else 8) and nextgen==(9 if mode else 5)
 units=[];events=[]
 for u in range(4):
  at=96+1336*u;v=struct.unpack_from('<11Q',data,at)
  n,oldid,oldname,oldgen,oldrefs,freed,newid,newname,newgen,newrefs,bound=v
  assert 0<n<=1024 and oldid==expected_identities[u] and oldname==expected_names[u] and oldgen==u+1
  assert oldid and 0<oldname<=0xffffffff and bound==1
  key=data[at+88:at+88+1024];assert key[:n]==expected_keys[u] and not any(key[n:])
  if mode:assert oldrefs==0 and freed==1 and newid and 0<newname<=0xffffffff and 5<=newgen<=8 and newrefs==2
  else:assert oldrefs==2 and freed==newid==newname==newgen==newrefs==0
  es=[struct.unpack_from('<7Q',data,at+88+1024+j*56) for j in range(4)]
  for j,e in enumerate(es):
   if not mode and j in (1,2):assert e==(0,)*7;continue
   sequence,kind,generation,identity,name,refs,unit=e
   assert 1<=sequence<=seq and kind==j+1 and unit==u
   new=bool(mode and j>=2)
   assert (generation,identity,name)==((newgen,newid,newname) if new else (oldgen,oldid,oldname))
   assert refs==(2 if j in (0,3) else 1);events.append(e)
  assert es[0][0]<es[3][0]
  if mode:assert es[0][0]<es[1][0]<es[2][0]<es[3][0]
  units.append(dict(unit=u,old_generation=oldgen,old_identity=oldid,old_name=oldname,
   new_generation=newgen,new_identity=newid,new_name=newname,events=es))
 assert sorted(e[0] for e in events)==list(range(1,seq+1))
 assert len({u['old_identity'] for u in units})==len({u['old_name'] for u in units})==4
 if mode:
  assert len({u['new_identity'] for u in units})==len({u['new_name'] for u in units})==4
  births=sorted((e for e in events if e[1]==3),key=lambda e:e[0])
  assert [e[2] for e in births]==[5,6,7,8]
  assert max(e[0] for e in events if e[1]==2)<min(e[0] for e in births)
 return dict(core_accounting_complete=True,mode=mode,owner=owner,events=seq,units=units,
  actual_runtime_qualified=False,requires='Actual creation/free/bind adapter, owner/context proof, deleted names, snapshots and guest pixels')
