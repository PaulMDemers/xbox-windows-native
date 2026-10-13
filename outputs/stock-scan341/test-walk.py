"""Compile the actual directory walker against owned disk reads and counted record output."""
import hashlib,json,subprocess
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('/mnt/e/xwn341/host001');assert not P.exists();P.mkdir()
source=(K/'main.c').read_text();start=source.index('static int directories(void)');end=source.index('static int snapshot(void)',start);body=source[start:end]
header=r'''
#define _FILE_OFFSET_BITS 64
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef uint32_t ULONG;
typedef uint8_t BYTE;
static unsigned long long data_offset;
static ULONG count,dir_count,entry_count;
static ULONG *fat,*queue;
static BYTE *seen,*buf;
static FILE *raw,*out;
static int read_at(unsigned long long at,ULONG bytes,void *p){
 if(at>10000048ULL*512 || bytes>10000048ULL*512-at || (at&511) || (bytes&511))return 0;
 return !fseeko(raw,5633024ULL*512+at,SEEK_SET)&&fread(p,1,bytes,raw)==bytes;
}
static int record(ULONG type,ULONG head,ULONG cluster,ULONG aux,const BYTE *entry){
 BYTE row[80]={0};memcpy(row,&type,4);memcpy(row+4,&head,4);memcpy(row+8,&cluster,4);memcpy(row+12,&aux,4);if(entry)memcpy(row+16,entry,64);
 return fwrite(row,1,80,out)==80;
}
'''
main=r'''
int main(int argc,char **argv){
 if(argc!=3)return 1;
 raw=fopen(argv[1],"rb");out=fopen(argv[2],"wb");if(!raw||!out)return 2;
 count=(10000048ULL*512)/16384;data_offset=4096+(((unsigned long long)count*4+4095)&~4095ULL);
 count=(10000048ULL*512-data_offset)/16384+1;
 fat=malloc(data_offset-4096);seen=calloc((count+7)/8,1);queue=malloc(65536*4);buf=malloc(65536);
 if(!fat||!seen||!queue||!buf||!read_at(4096,data_offset-4096,fat))return 3;
 int ok=directories();fclose(raw);fclose(out);free(fat);free(seen);free(queue);free(buf);
 printf("Actual walker directories=%u entries=%u success=%d\n",dir_count,entry_count,ok);return ok?0:4;
}
'''
(P/'test.c').write_text(header+body+main)
command=['gcc','-std=c11','-D_POSIX_C_SOURCE=200809L','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-g',str(P/'test.c'),'-o',str(P/'test')]
subprocess.run(command,check=True,capture_output=True)
raw=Path('/mnt/e/xwn335/seed003/stock10gb.raw');result=P/'directories.bin'
run=subprocess.run([str(P/'test'),str(raw),str(result)],capture_output=True,check=True,timeout=90);(P/'console.txt').write_bytes(run.stdout+run.stderr)
expected=K.parent/'stock-runtime335/seed003/review002/artifacts/directories.bin'
assert result.read_bytes()==expected.read_bytes(),'Actual C directory records differ from independent cold reader'
meta=K.parent/'stock-runtime335/seed003/review002/artifacts/fat-metadata.bin'
with raw.open('rb') as f:f.seek(5633024*512);assert f.read(meta.stat().st_size)==meta.read_bytes()
r=dict(passed=True,actual_directory_function_sha256=hashlib.sha256(body.encode()).hexdigest(),records_sha256=hashlib.sha256(result.read_bytes()).hexdigest(),metadata_sha256=hashlib.sha256(meta.read_bytes()).hexdigest(),records_bytes=result.stat().st_size,console=run.stdout.decode(),interfaces='Actual C directory walker with modeled native I/O/record adapter; real owned disk bytes and independent cold QCOW-derived records. Not Xbox runtime qualification.',private=str(P))
(K/'host001.json').write_text(json.dumps(r,indent=2)+'\n');print(run.stdout.decode())
