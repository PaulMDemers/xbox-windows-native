"""Exercise compiled mode reporting and the exact Paint divide that crashed."""
import pathlib, sys, json, hashlib
k = pathlib.Path(__file__).resolve().parent
sys.argv = [__file__, '--miniport', str(k/'artifacts/xboxvnt5-dimensions.sys')]
text = (k/'test-video-trace.py').read_text()
exec(text[:text.index('\nresults=[]')])
cases = []
for width, height, pitch in [(640,480,2560), (1024,576,4096), (1280,720,5120), (1920,200,7680)]:
    m = TraceMachine()
    m.put(MMIO+0x680838,width-1); m.put(MMIO+0x680818,height-1)
    m.crtc[0x13]=(pitch//8)&255; m.crtc[0x19]=((pitch//8)>>3)&0xe0
    assert m.init_adapter() == 1
    assert m.ioctl(0x230400) == (0,80)
    mode = struct.unpack('<20I', m.u.mem_read(OUTPUT,80))
    assert mode[8:10] == ((width*254+480)//960,(height*254+480)//960)
    assert mode[8] > 0 and mode[9] > 0
    assert m.ioctl(0x230408) == (0,80)
    assert struct.unpack('<20I',m.u.mem_read(OUTPUT,80)) == mode
    cases.append({'pixels':[width,height], 'fallback_millimeters':list(mode[8:10])})
# The physical DrWatson record identifies mspaint!0101e7d0 (idiv ecx),
# with ecx=0 and eax=1024*1000. Execute the owned binary's actual sequence.
paint_path=k/'package/F/winnt/system32/mspaint.exe'
paint=pefile.PE(str(paint_path)); code=paint.get_data(0x1e7bb,0x17)
assert code.hex() == '8b861002000069c0e80300008b8e180200006a0a99f7f9'
def conversion(mm):
    u=Uc(UC_ARCH_X86,UC_MODE_32)
    u.mem_map(0x100000,0x1000);u.mem_map(0x200000,0x2000)
    u.mem_write(0x100000,code)
    u.mem_write(0x200210,struct.pack('<I',1024))
    u.mem_write(0x200218,struct.pack('<I',mm))
    u.reg_write(UC_X86_REG_ESI,0x200000);u.reg_write(UC_X86_REG_ESP,0x201000)
    try: u.emu_start(0x100000,0x100000+len(code),count=20)
    except UcError as e:
        assert mm == 0 and e.errno == UC_ERR_EXCEPTION
        return {'divide_exception':True}
    assert mm > 0
    return {'divide_exception':False,'result':u.reg_read(UC_X86_REG_EAX)}
old=conversion(0);new=conversion(271)
assert old['divide_exception'] and not new['divide_exception'] and new['result']==1024000//271
r={'scope':'Compiled mode reporting and exact Paint faulting instruction sequence','miniport_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
   'paint_sha256':hashlib.sha256(paint_path.read_bytes()).hexdigest(),
   'modes':cases,'paint_original':old,'paint_candidate':new,
   'limitation':'Compiled modeled execution; no full Paint or physical validation yet.'}
(k/'video-dimensions-tests.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
