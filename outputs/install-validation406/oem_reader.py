"""Read-only CP437 view; unchanged FATX structure/chain validation from owned writer."""
import sys
from pathlib import Path
W=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(W/'outputs/video-text-oracle206'));from common import m
sys.path.insert(0,str(W/'tools'));from fatx_names import check_path

class OemReader(m.Writer):
    def parts(self,path):
        check_path(path,437)
        return path.replace('\\','/').split('/')
    def directory(self,start):
        if start in self.dirs:return self.dirs[start]
        entries={};slots=[];chain=list(self.chain(start));ended=False
        for c in chain:
            b=self.read_cluster(c)
            for off in range(0,len(b),64):
                marker=b[off]
                if marker in (0,255):ended=True
                if ended or marker==229:slots.append((c,off));continue
                assert 1<=marker<=42
                e=bytes(b[off:off+64]);name=e[2:2+marker].decode('cp437').lower()
                assert name not in entries;entries[name]=(c,off,e)
        result=dict(entries=entries,slots=slots,chain=chain);self.dirs[start]=result;return result
    def write(self,*args):raise RuntimeError('Read-only OEM reader')
    def write_cluster(self,*args):raise RuntimeError('Read-only OEM reader')
    def flush(self):raise RuntimeError('Read-only OEM reader')
