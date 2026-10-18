"""Use actual allocated loader target and bounded async-stop reply handling."""
from pathlib import Path
K=Path(__file__).resolve().parent;assert not (K/'Run003.ps1').exists()
(K/'Run003.ps1').write_text((K/'Run002.ps1').read_text().replace('emu002','emu003'))
s=(K/'protocol.py').read_text();old='    def ask(self,text):self.send(text);return self.recv()'
new='''    def ask(self,text):
        self.send(text)
        for _ in range(4):
            reply=self.recv()
            if text!='?' and reply.startswith(('T','S')):
                self.async_stops=getattr(self,'async_stops',[])+[reply]
                continue
            return reply
        raise RuntimeError('Too many asynchronous stop replies')'''
assert s.count(old)==1;s=s.replace(old,new);(K/'protocol003.py').write_text(s)
s=(K/'trace002.py').read_text().replace('emu002','emu003').replace('trace002','trace003').replace('from protocol import','from protocol003 import')
s=s.replace("advance(0x1000000,'before_original_loader_cli')","advance(words[9],'before_original_loader_cli')")
s=s.replace("assert loader['EFL']&0xed5==words[28]&0xed5","assert loader['EFL']==words[28]")
s=s.replace("            g.s.close()","            r['asynchronous_stop_replies']=getattr(g,'async_stops',[])\n            g.s.close()")
(K/'trace003.py').write_text(s)
(K/'collect003.py').write_text((K/'collect002.py').read_text().replace('emu002','emu003').replace('cold002','cold003'))
(K/'preflight003.py').write_text((K/'preflight002.py').read_text().replace("K/'emu002'","K/'emu003'"))
(K/'emu003').mkdir()
