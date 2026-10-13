from pathlib import Path
import json
K=Path(__file__).resolve().parent
t=(K/'test-walk.py').read_text().replace('host001','host002')
t=t.replace("body=source[start:end]", "body=source[start:end]\noriginal_body=body\nbody=body.replace('if(tail>=65536)return 0;queue[tail++]=first;', 'if(tail>=65536)return 0;\\n     queue[tail++]=first;')\nassert ''.join(body.split())==''.join(original_body.split())")
t=t.replace("records_bytes=result.stat().st_size", "host_statement_wrapping_only=True,original_function_sha256=hashlib.sha256(original_body.encode()).hexdigest(),records_bytes=result.stat().st_size")
(K/'test-walk002.py').write_text(t,newline='\n')
(K/'host001-failure.json').write_text(json.dumps(dict(stage='host_compile',error='GCC misleading-indentation on inherited two-statement line; native Clang build passed',private='E:/xwn341/host001',runtime=False,correction='Fresh host002 inserts newline only, asserts identical non-whitespace source, retains all compiler warnings as errors',unused_alternative='WSL clang unavailable; shell inline generator also failed before file creation; no host002 consumed'),indent=2)+'\n')
