from pathlib import Path
import subprocess,json,re,hashlib,os
K=Path(__file__).resolve().parent; B=Path(os.environ['XWN_BUILD_DIR'])/'cromwell';O=Path(os.environ['XWN_TEST_OUTPUT']);assert not O.exists();O.mkdir();s=(B/'drivers/video/BootVgaInitialization.c').read_text();h=(B/'drivers/video/VideoInitialization.h').read_text();a=re.search(r'typedef enum enumAVTypes\s*\{.*?\}\s*xbox_av_type;',h,re.S)
if not a:
 a=re.search(r'typedef enum \w+\s*\{[^}]*AV_SCART_RGB[^}]*\}\s*xbox_av_type;',h,re.S)
assert a
av=re.search(r'if \(av_type != AV_COMPOSITE.*?\n\s*\}',s,re.S).group();av=av.replace('__asm__ __volatile__("cli"); for (;;) __asm__ __volatile__("hlt");','return -1;')
start=s.index('if(((u8 *)&eeprom)[0x96]&0x01');end=s.index('\n\n',start);mode=s[start:end].replace('__asm__ __volatile__("cli"); for (;;) __asm__ __volatile__("hlt");','return -1;')
b=(B/'boot/BootResetAction.c').read_text();assert b.index('if (xbox_ram != 64)')>b.index('BootDetectMemorySize();') and b.index('if (xbox_ram != 64)')<b.index('memset((void *)FB_START')
prefix='#include <assert.h>\n'+a.group()+'\ntypedef unsigned char u8;static u8 eeprom[256]; static int video_encoder;\n#define ENCODER_CONEXANT 0\n#define VIDEO_MODE_1024x576 9\nstruct mode {int m_nVideoModeIndex;};\nint choose(int av_type,struct mode *pvmode){\n'
suffix='''\nreturn pvmode->m_nVideoModeIndex;}\nint main(void){struct mode x;for(int flag=0;flag<256;flag++)for(int enc=0;enc<4;enc++)for(int av=-1;av<=7;av++){eeprom[0x96]=flag;video_encoder=enc;x.m_nVideoModeIndex=0;int want=((flag&1)&&enc==0&&(av==AV_COMPOSITE||av==AV_SVIDEO||av==AV_SCART_RGB))?9:-1;assert(choose(av,&x)==want);}return 0;}\n'''
(O/'test.c').write_text(prefix+av+'\n'+mode+suffix);subprocess.run(['gcc-12','-std=c11','-Wall','-Wextra','-Werror',str(O/'test.c'),'-o',str(O/'test')],check=True);subprocess.run([str(O/'test')],check=True)
exe=(Path(os.environ['XWN_OUTPUT_DIR'])/'default.xbe').read_bytes();assert b'/Applications/XWNEBoot/freeldr.sys' in exe
(O/'host-test-report.json').write_text(json.dumps({'passed':True,'mode_guard_cases':9216,'scope':'Actual source cable and mode guards compiled with privileged halts replaced by return; memory guard source ordering and binary path checked. No hardware/guest claim.','xbe_sha256':hashlib.sha256(exe).hexdigest()},indent=2)+'\n')
