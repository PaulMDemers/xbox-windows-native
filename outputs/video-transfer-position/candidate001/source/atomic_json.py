"""Bounded Windows sharing-violation recovery without exposing partial JSON."""
import json,time
def write_json(path,value,timeout=3.0):
    temporary=path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value,indent=2)+'\n')
    deadline=time.monotonic()+timeout
    while True:
        try:
            temporary.replace(path)
            return
        except PermissionError:
            if time.monotonic()>=deadline:raise
            time.sleep(.025)
