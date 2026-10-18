"""Finite return observer, control-only; receipt content is verified cold separately."""
import time
from probe import probe,ProbeFailure

def wait_control(port,credentials,path,record,*,seconds=45,attempt=probe,clock=time.monotonic,sleep=time.sleep):
 assert 0<seconds<=45
 end=clock()+seconds
 for index in range(90):
  if clock()>=end:break
  try:
   value=attempt(port,credentials,path,112,min(end,clock()+5))
  except ProbeFailure as error:
   record(dict(index=index,passed=False,stage=error.stage,error_type=error.error_type,events=error.events))
  else:
   assert value.get('passed') is True and value.get('authenticated_control') is True
   assert value.get('receipt_size')==112 and value.get('live_receipt_bytes_verified') is False
   assert clock()<=end
   record(dict(index=index,passed=True,result=value));return value
  if clock()<end:sleep(min(.5,end-clock()))
 raise TimeoutError('No complete dashboard control proof within return deadline')
