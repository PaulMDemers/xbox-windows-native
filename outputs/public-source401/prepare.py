"""Private source-export preparation. Reads preserved Git objects; never builds or deploys."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

K = Path(__file__).resolve().parent
W = K.parents[1]
OUT = Path('/mnt/c/xwn401/source001')
WORK = Path('/mnt/c/xwn401/object-work001')
BASE = 'afc0127e8f937ab68503d715d948844973756aa1'
CBASE = '9fc54d0c7cbed7bc3c70373642d833684853011f'
CACHE = Path('/home/paul/xbox-windows-native/sources/reactos-extended')
CCACHE = Path('/home/paul/xbox-windows-native/sources/cromwell')
BUILD = Path('/home/paul/xbox-windows-native/build')
sha = lambda b: hashlib.sha256(b).hexdigest()
read = lambda p: json.loads(p.read_text())


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


def main():
    if sys.platform != 'linux' or OUT.exists() or WORK.exists():
        raise RuntimeError('Linux and fresh source001/object-work001 required')
    OUT.mkdir(parents=True)
    WORK.mkdir()
    provenance = {}
    def record(rel):
        p = W / rel
        provenance[rel] = sha(p.read_bytes())
        return read(p)
    fat = record('outputs/fatx-enumeration390/inputs.json')
    hd = record('outputs/hd-reservation300/build001.json')
    hdsrc = record('outputs/hd-reservation300/source-review002.json')
    boot = record('outputs/stock-boot334/build001.json')
    bootsrc = record('outputs/stock-boot334/source-review001.json')
    video = record('outputs/hd-surface303/build003.json')
    launch = record('outputs/resolution-e374/build001.json')
    audio = record('outputs/audio207/source-build004.json')
    audio_base = record('outputs/native-windows-nt5-kernel/patch-check-0016.json')
    specs = [
        ('fatx390', BUILD/'fatx-enumeration390-001/source', fat['result_tree'], BASE, fat['profiles']['fatx']),
        ('hd300', BUILD/'hd-reservation300-build001/source', hdsrc['trees']['reactos'], BASE,
         {'definitions': hd['cases']['candidate001']['definitions'], 'targets': ['xboxvnt5', 'xboxbvid']}),
        ('boot-e334', BUILD/'stock-boot334-build001/reactos', bootsrc['trees']['reactos'], BASE,
         {'definitions': boot['definitions'], 'targets': ['freeldr', 'rosload']}),
        ('display303', BUILD/'hd-surface303-build001/source', video['source_tree'], BASE,
         {'definitions': video['cases']['candidate001']['definitions'], 'targets': ['xwnown']}),
        ('launcher-e720p374', BUILD/'resolution-e374-build001/source', launch['tree'], CBASE,
         {'make_target': 'all', 'flags': launch['flags'], 'compiler_sha256': launch['gcc12_sha256']}),
        ('audio004', CACHE, None, BASE, {'definitions': {
            'ARCH':'i386', 'SARCH':'xbox', 'OARCH':'pentium', 'CMAKE_BUILD_TYPE':'Release',
            'PCH':'OFF', 'ENABLE_CCACHE':'OFF', 'XBOX_NT5_HAL':'ON',
            'XBOX_NATIVE_PREFLIGHT':'OFF', 'XBOX_NATIVE_IO_PREFLIGHT':'OFF'},
            'targets':['ac97xnt5', 'ac97']}),
    ]
    components = []
    reviews = []
    for name, repo, tree, base, build in specs:
        local = WORK/name
        subprocess.run(['git','init','-q',str(local)], check=True)
        cache = CCACHE if base == CBASE else CACHE
        # Read-only alternates exist ONLY in this private verification process.
        # No alternate, .git, object database, or local path enters the export.
        env = dict(os.environ, GIT_ALTERNATE_OBJECT_DIRECTORIES=os.pathsep.join(
            str(p/'.git/objects') for p in dict.fromkeys([repo,cache])))
        def git(*args):
            return subprocess.check_output(['git','-C',str(local),*args], env=env)
        git('read-tree', base)
        if name == 'audio004':
            for rel in audio_base['patches']:
                p=W/rel; provenance[rel]=sha(p.read_bytes())
                git('apply','--cached',str(p))
            if git('write-tree').decode().strip() != audio_base['result_tree']:
                raise RuntimeError('Audio base replay mismatch')
            p=W/'outputs/audio207/0210-waveonly-cumulative.patch'
            if sha(p.read_bytes()) != audio['patch_sha256']:
                raise RuntimeError('Audio cumulative patch mismatch')
            provenance[str(p.relative_to(W))]=sha(p.read_bytes())
            git('apply','--cached',str(p))
            tree=git('write-tree').decode().strip()
            for rel, expected in audio['sources'].items():
                data=git('show',tree+':drivers/wdm/audio/drivers/ac97/'+rel)
                if sha(data)!=expected: raise RuntimeError('Audio compiled-source mismatch: '+rel)
        git('cat-file','-e',tree+'^{tree}')
        data=git('diff','--no-ext-diff','--no-textconv','--full-index',base,tree,'--')
        if not data or b'GIT binary patch' in data or re.search(rb'^Binary files ', data, re.M):
            raise RuntimeError('Missing or binary patch: '+name)
        patch='patches/'+name+'.patch'
        (OUT/'patches').mkdir(exist_ok=True)
        (OUT/patch).write_bytes(data)
        git('read-tree',base)
        git('apply','--cached',str(OUT/patch))
        if git('write-tree').decode().strip()!=tree:
            raise RuntimeError('Export replay tree mismatch: '+name)
        changed=git('diff','--name-only',base,tree).decode().splitlines()
        notices=[]
        for path in changed:
            exists=subprocess.run(['git','-C',str(local),'cat-file','-e',tree+':'+path],env=env,capture_output=True)
            if exists.returncode: continue
            contents=git('show',tree+':'+path)
            if b'\0' in contents: raise RuntimeError('Binary changed source: '+path)
            top=contents.decode('utf-8',errors='replace').splitlines()[:80]
            lines=[line.strip() for line in top if re.search(r'copyright|SPDX|licen[sc]e|GNU General|public domain',line,re.I)]
            notices.append({'path':path,'sha256':sha(contents),'header_notice_lines':lines,
                            'manual_license_review_required':True})
        # Original upstream license texts, not a replacement blanket license.
        license_names=git('ls-tree','--name-only',base).decode().splitlines()
        for license_name in license_names:
            if re.fullmatch(r'COPYING(?:[.A-Z0-9_-]*)?|LICENSE(?:[.a-zA-Z0-9_-]*)?',license_name):
                try: license_data=git('show',base+':'+license_name)
                except subprocess.CalledProcessError: continue
                dest=OUT/'licenses'/('cromwell' if base==CBASE else 'reactos')/license_name
                dest.parent.mkdir(parents=True,exist_ok=True)
                if dest.exists() and dest.read_bytes()!=license_data: raise RuntimeError('License mismatch')
                dest.write_bytes(license_data)
        if name=='audio004':
            dest=OUT/'licenses/audio-ac97.txt';dest.write_bytes(git('show',tree+':drivers/wdm/audio/drivers/ac97/license.txt'))
        save(OUT/('notices/'+name+'.json'),notices)
        # Strip local build output paths from the source-only portable recipe.
        build={k:v for k,v in build.items() if k in ('definitions','targets','make_target','flags','compiler_sha256')}
        entry=dict(name=name,base_commit=base,result_tree=tree,patch=patch,patch_sha256=sha(data),
                   build=build,source_replay_verified=True,compiled_in_this_export=False,
                   provenance='Independent cumulative diff from preserved exact source tree; source-only replay')
        components.append(entry)
        reviews.append(dict(name=name,tree=tree,changed_files=len(changed),patch_bytes=len(data),
                            compiled_audio_files_verified=len(audio['sources']) if name=='audio004' else None))
        print(name, 'source replay verified',len(changed),'files',flush=True)
    for rel,dest in [('tools/configure-e-display.py','tools/configure-e-display.py'),
                     ('tools/e-display-policy.json','tools/e-display-policy.json'),
                     ('outputs/demo-settings376/settings.c','tools/display-settings.c')]:
        p=W/rel;provenance[rel]=sha(p.read_bytes());q=OUT/dest;q.parent.mkdir(exist_ok=True);q.write_bytes(p.read_bytes())
    for p in (K/'public').rglob('*'):
        if p.is_file():
            q=OUT/p.relative_to(K/'public');q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
            provenance[str(p.relative_to(W))]=sha(p.read_bytes())
    save(OUT/'components.json',{'schema':1,'status':'PRIVATE REVIEW DRAFT',
         'public_release_ready':False,'components':components,'rosbe_tool_pins':fat['tool_sha256'],
         'upstream_locations_as_recorded':{'reactos':'https://github.com/DistroHopper39B/reactos.git',
                                         'cromwell':'https://github.com/PaulMDemers/cromwell.git'},
         'location_availability_checked':False})
    save(K/'source001.json',{'source_package':str(OUT),'reviews':reviews,'input_sha256':provenance,
         'scope':'Six exact source replays; no compiler, deployment, guest, license clearance or public publication',
         'all_source_replays_passed':True})


if __name__ == '__main__': main()
