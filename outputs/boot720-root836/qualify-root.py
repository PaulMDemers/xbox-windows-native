"""Reproduce FATX root truncation using actual loader C and a fragmented fixture.

Source-only reuse of pinned835; no runtime parenting, hardware or disk writes.
"""
import datetime, difflib, hashlib, json, os, subprocess, sys
from pathlib import Path
K = Path(__file__).resolve().parent
W = K.parents[1]
B = Path('/home/paul/xbox-windows-native/boot720835-source001/reactos')
O = Path('/mnt/c/xwn836/root001')
assert os.environ.get('XWN_BUILD_LEASE') == 'held' and not O.exists()
sys.path.insert(0, str(W/'tools'))
from build_space import require_space
r = {'passed': False, 'physical_access': False, 'space': require_space(O.parent, 20.1), 'tests': {}}
O.mkdir(parents=True)
sha = lambda b: hashlib.sha256(b).hexdigest()
def save(): (K/'root001.json').write_text(json.dumps(r, indent=2)+'\n')
save()
try:
    source = B/'boot/freeldr/freeldr/lib/fs/fat.c'
    s = source.read_text()
    r['source_sha256'] = sha(source.read_bytes())
    tree = json.loads((W/'outputs/boot720-native835/source002.json').read_text())['trees']['reactos']
    assert subprocess.check_output(['git','-C',str(B),'write-tree'], text=True).strip() == tree
    assert not subprocess.check_output(['git','-C',str(B),'diff','--name-only'])
    r['parent_source_tree'] = tree
    old = '''    /*
     * For FAT32, the root directory is nothing special. We can treat it the same
     * as a subdirectory.
     */
    if (RootDirectory && Volume->FatType == FAT32)
    {
        DirectoryStartCluster = Volume->RootDirStartCluster;
        RootDirectory = FALSE;
    }'''
    new = '''    /* FAT32 and FATX roots are cluster chains, like subdirectories.
     * The existing FATX layout places cluster 1 at RootDirSectorStart;
     * reading only RootDirSectors hides entries beyond its first cluster. */
    if (RootDirectory && (Volume->FatType == FAT32 || ISFATX(Volume->FatType)))
    {
        DirectoryStartCluster = ISFATX(Volume->FatType) ? 1 : Volume->RootDirStartCluster;
        RootDirectory = FALSE;
    }'''
    assert s.count(old) == 1
    fixed = s.replace(old, new)
    anchor = '''    //
    // Attempt to allocate memory for directory buffer
    //'''
    assert fixed.count(anchor) == 1
    fixed = fixed.replace(anchor, '''    /* A failed chain read must not allocate a header-only buffer. */
    if (*DirectorySize == 0)
        return NULL;

'''+anchor)
    patch = ''.join(difflib.unified_diff(s.splitlines(True), fixed.splitlines(True),
        fromfile='a/boot/freeldr/freeldr/lib/fs/fat.c', tofile='b/boot/freeldr/freeldr/lib/fs/fat.c'))
    (K/'fatx-root.patch').write_text(patch)
    (O/'fat-before.c').write_text(s)
    (O/'fat-after.c').write_text(fixed)
    r['patched_source_sha256'] = sha(fixed.encode())
    def extract(text):
        return text[text.index('typedef struct _DIRECTORY_BUFFER'):text.index('static BOOLEAN FatSearchDirectoryBufferForFile')]
    prefix = r'''
#include <assert.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stddef.h>
typedef void *PVOID; typedef uint32_t ULONG; typedef unsigned char UCHAR;
typedef int BOOLEAN;
#define TRUE 1
#define FALSE 0
#define FAT16 16
#define FAT32 32
#define FATX16 116
#define FATX32 132
#define ISFATX(t) ((t)==FATX16 || (t)==FATX32)
#define TRACE(...) ((void)0)
#define TAG_FAT_BUFFER 0
typedef struct _LIST_ENTRY {struct _LIST_ENTRY *Flink,*Blink;} LIST_ENTRY,*PLIST_ENTRY;
#define CONTAINING_RECORD(p,t,f) ((t *)((char *)(p)-offsetof(t,f)))
static void InsertTailList(PLIST_ENTRY h,PLIST_ENTRY e){e->Flink=h;e->Blink=h->Blink;h->Blink->Flink=e;h->Blink=e;}
typedef struct {ULONG FatType,RootDirStartCluster,RootDirSectors,BytesPerSector,SectorsPerCluster,RootDirSectorStart;} FAT_VOLUME_INFO,*PFAT_VOLUME_INFO;
static unsigned char disk[80*16384]; static ULONG links[80];
static int fail_alloc,fail_count,fail_read; static unsigned reads,chain_reads;
static void *FrLdrTempAlloc(size_t n,int t){(void)t;return fail_alloc?NULL:malloc(n);}
static void FrLdrTempFree(void *p,int t){(void)t;free(p);}
static ULONG FatCountClustersInChain(PFAT_VOLUME_INFO v,ULONG n){(void)v;ULONG k=0;if(fail_count)return 0;while(n){assert(n<80 && k<80);k++;n=links[n];}return k;}
static int FatReadVolumeSectors(PFAT_VOLUME_INFO v,ULONG at,ULONG count,void *p){(void)v;reads++;if(fail_read)return 0;assert((at+count)*512<=sizeof(disk));memcpy(p,disk+at*512,count*512);return 1;}
static int FatReadClusterChain(PFAT_VOLUME_INFO v,ULONG n,ULONG count,void *p,void *last){(void)count;(void)last;chain_reads++;if(fail_read)return 0;unsigned k=0;while(n){assert(n<80 && k++<80);memcpy(p,disk+n*16384,16384);p=(char *)p+16384;n=links[n];}return 1;}
'''
    suffix = r'''
static void clear_cache(void){while(DirectoryBufferListHead.Flink!=&DirectoryBufferListHead){PLIST_ENTRY e=DirectoryBufferListHead.Flink;DirectoryBufferListHead.Flink=e->Flink;free(CONTAINING_RECORD(e,DIRECTORY_BUFFER,Link));}DirectoryBufferListHead.Blink=&DirectoryBufferListHead;}
static void init(void){clear_cache();memset(disk,0,sizeof(disk));memset(links,0,sizeof(links));fail_alloc=fail_count=fail_read=reads=chain_reads=0;}
int main(void){FAT_VOLUME_INFO v={FATX32,0,32,512,32,32};ULONG n;void *p;unsigned cases=0;
/* Fragmented five-cluster root: target at logical entry1070, beyond entry255. */
for(unsigned type=0;type<2;type++){
 init();v.FatType=type?FATX16:FATX32;links[1]=9;links[9]=4;links[4]=30;links[30]=2;
 memcpy(disk+2*16384+46*64,"WINNT",6);
 p=FatBufferDirectory(&v,0,&n,1);assert(p);
#ifdef EXPECT_OLD
 assert(n==16384);assert(reads==1 && chain_reads==0);
#else
 assert(n==5*16384);assert(memcmp((char *)p+1070*64,"WINNT",6)==0);assert(reads==0 && chain_reads==1);
 assert(FatBufferDirectory(&v,0,&n,1)==p && chain_reads==1);
#endif
 cases++;
}
#ifndef EXPECT_OLD
/* Existing FAT16 fixed root, FAT32 root chain, FATX subdirectory stay valid. */
init();v.FatType=FAT16;p=FatBufferDirectory(&v,0,&n,1);assert(p && n==16384 && reads==1);cases++;
init();v.FatType=FAT32;v.RootDirStartCluster=8;links[8]=11;p=FatBufferDirectory(&v,0,&n,1);assert(p && n==32768 && chain_reads==1);cases++;
init();v.FatType=FATX32;links[7]=12;p=FatBufferDirectory(&v,7,&n,0);assert(p && n==32768);cases++;
init();fail_count=1;assert(!FatBufferDirectory(&v,0,&n,1) && !chain_reads);cases++;
init();fail_alloc=1;assert(!FatBufferDirectory(&v,0,&n,1) && !chain_reads);cases++;
init();fail_read=1;assert(!FatBufferDirectory(&v,0,&n,1));assert(DirectoryBufferListHead.Flink==&DirectoryBufferListHead);cases++;
init();p=FatBufferDirectory(&v,0,&n,1);assert(p && n==16384 && chain_reads==1);cases++;
#endif
clear_cache();printf("PASS %u cases\n",cases);return 0;}
'''
    cc = Path('/usr/bin/gcc-12').resolve()
    assert sha(cc.read_bytes()) == 'e53063edf46fe26e22d8c79258856275784c07b199aac441e345aabd62092ad4'
    for name, body in [('before',s),('after',fixed)]:
        (O/(name+'.c')).write_text(prefix+extract(body)+suffix)
        args=[str(cc),'-O1','-Wall','-Wextra','-Wno-unused-parameter','-fsanitize=address,undefined']
        if name=='before':args+=['-DEXPECT_OLD']
        args += [str(O/(name+'.c')),'-o',str(O/name)]
        b=subprocess.run(args,capture_output=True,timeout=60)
        (O/(name+'-build.log')).write_bytes(b.stdout+b.stderr)
        assert b.returncode==0,b.stderr.decode()
        t=subprocess.run([str(O/name)],capture_output=True,timeout=20)
        (O/(name+'-run.log')).write_bytes(t.stdout+t.stderr)
        assert t.returncode==0,t.stderr.decode()
        r['tests'][name]=t.stdout.decode().strip()
    r['scope']='Actual FatBufferDirectory C with synthetic fragmented storage and substituted allocation/chain I/O; before reproduces truncation, after traverses root. Not a physical boot result.'
    r['passed']=True
except BaseException as e:
    r['error']=repr(e)
    raise
finally:
    r['utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    r['artifacts']={p.name:{'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in O.iterdir() if p.is_file()}
    save()
    print(json.dumps(r['tests']))
