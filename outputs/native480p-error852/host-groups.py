from pathlib import Path
import re,subprocess,tempfile,json
K=Path(__file__).resolve().parent;f=Path('/home/paul/xbox-windows-native/build/native480p-error852/source/drivers/video/xwn_hd_native.c').read_text();g=re.search(r'static void group852[^\n]+',f,re.S);assert g
# Compile the real group emitter and verify pulse patterns and exact counts.
h='''#include <assert.h>\nstruct xwn_hd_io{int unused;}; static unsigned writes,waits,last;\nstatic void led852(const struct xwn_hd_io *io,unsigned v){(void)io;assert(v==0 || v==0xff || v==0xf0 || v==0x0f);last=v;writes++;}\nstatic void sleep852(unsigned ms){assert(ms==500 || ms==2000);waits++;}\n'''+g.group()+'''\nint main(void){struct xwn_hd_io io={0};for(unsigned c=0;c<3;c++)for(unsigned n=1;n<=10;n++){writes=waits=0;group852(&io,c==0?0xff:c==1?0xf0:0x0f,n);assert(writes==2*n&&waits==2*n+1&&last==0);}return 0;}'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d)/'test.c';p.write_text(h);e=Path(d)/'test';r=subprocess.run(['gcc-12','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-pie','-no-pie',str(p),'-o',str(e)],capture_output=True);assert r.returncode==0,r.stderr.decode();subprocess.run([str(e)],check=True)
(K/'host-groups001.json').write_text(json.dumps({'passed':True,'cases':30,'scope':'Actual pulse group function with modeled LED/timer; physical signaling and full repeated cycle not modeled.'},indent=2)+'\n');print('30 pulse-group cases passed')

