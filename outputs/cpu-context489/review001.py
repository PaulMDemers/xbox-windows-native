"""Independent expected CPU/register oracle for the synthetic two-epoch fixture."""
import struct
from decode import decode
def review(data,symbols):
 def need(ok,why):
  if not ok:raise ValueError(why)
 need(len(data)==397 and data[:4]==b'T489' and data[-1:]==b'P','transport')
 records=[]
 for i in range(2):
  r=decode(data[4+160*i:164+160*i]);records.append(r)
  expected=dict(epoch=i+1,eflags=0x682,cr0=0x80000011,cr2=[0x12345000,0x6789a000][i],cr3=[0x1000000,0x1002000][i],cr4=0x10,selectors=[8,16,16,16,16,16,0,0],gdtr=[23,symbols['fixture_gdt']],idtr=[0,0],entry_esp=0x17fffc,return_eip=symbols['expected_return'+str(i+1)])
  for k,v in expected.items():need(r[k]==v,k)
  frame=struct.unpack_from('<9I',data,324+36*i)
  need(frame==(0x120000+256*i,0x44444444,0x55555555,0x17fffc,0x22222222,0x33333333,160,0x11111111,0x682),'restored registers/flags')
 return dict(passed=True,records=records,two_contexts_observed=True,registers_flags_restored=True,guard_and_refusal_paths_reached=True,physical_cpu_qualification=False)
