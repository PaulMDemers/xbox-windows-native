"""Search decoded owned image files and PE bitmap/icon resources; no guest execution."""
import hashlib,io,json,struct,sys,time
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];sys.path.insert(0,str(ws/'work/python-packages'))
from PIL import Image
import pefile
source=ws/'outputs/physical-gpu-setup/log-anomaly.json';b=bytes.fromhex(json.loads(source.read_text())['malformed_range_hex'])
needles={'full111':b,'first24':b[:24],'middle24':b[42:66],'last24':b[-24:]}
root=Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files');out=k/'image-search.json';assert not out.exists()
r=dict(scope=__doc__,physical_access=False,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),root=str(root),image_frames=0,pe_images=0,decoded_resources=0,matches=[],decode_errors=[],skipped_large=[],scanned_image_hashes=[])
def search(im,label,digest):
    if im.width*im.height>10000000:r['skipped_large'].append(dict(label=label,size=im.size));return
    rgb=im.convert('RGB');red,green,blue=rgb.split();bgr=Image.merge('RGB',(blue,green,red))
    r['image_frames']+=1;r['scanned_image_hashes'].append(dict(label=label,source_sha256=digest,size=im.size))
    for order,picture in [('RGB',rgb),('BGR',bgr)]:
        for orientation,data in [('top-down',picture.tobytes()),('bottom-up',picture.transpose(Image.Transpose.FLIP_TOP_BOTTOM).tobytes())]:
            for name,needle in needles.items():
                at=data.find(needle)
                if at>=0:r['matches'].append(dict(label=label,order=order,orientation=orientation,needle=name,byte_offset=at,size=im.size,decoded_sha256=hashlib.sha256(data).hexdigest()))
def resource_image(blob,kind):
    if blob.startswith(b'\x89PNG\r\n\x1a\n'):return Image.open(io.BytesIO(blob))
    header,width,height=struct.unpack_from('<Iii',blob);assert header>=40 and len(blob)>=header
    planes,bits,compression=struct.unpack_from('<HHI',blob,12)
    if kind==3:
        assert 0<width<=256 and 0<height//2<=256
        ico=struct.pack('<HHH',0,1,1)+struct.pack('<BBBBHHII',width%256,(height//2)%256,0,0,planes,bits,len(blob),22)+blob
        return Image.open(io.BytesIO(ico))
    used=struct.unpack_from('<I',blob,32)[0]
    colors=used if used else (1<<bits if bits<=8 else 0)
    offset=14+header+colors*4+(12 if header==40 and compression==3 else 0)
    return Image.open(io.BytesIO(b'BM'+struct.pack('<IHHI',14+len(blob),0,0,offset)+blob))
started=time.monotonic()
for path in sorted(root.rglob('*')):
    if not path.is_file():continue
    label=str(path.relative_to(root));suffix=path.suffix.lower()
    if suffix in ['.bmp','.dib','.png','.jpg','.jpeg','.gif','.ico','.cur']:
        try:
            data=path.read_bytes();digest=hashlib.sha256(data).hexdigest()
            with Image.open(io.BytesIO(data)) as im:
                for frame in range(getattr(im,'n_frames',1)):
                    im.seek(frame);search(im,label+'#frame'+str(frame),digest)
        except Exception as exc:r['decode_errors'].append(dict(label=label,error=repr(exc)))
    try:
        with path.open('rb') as f:magic=f.read(2)
        if magic!=b'MZ':continue
        pe=pefile.PE(str(path),fast_load=True)
        pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_RESOURCE']]);r['pe_images']+=1
        for typ in getattr(getattr(pe,'DIRECTORY_ENTRY_RESOURCE',None),'entries',[]):
            if typ.id not in [2,3]:continue
            for name in typ.directory.entries:
                for lang in name.directory.entries:
                    entry=lang.data.struct;blob=pe.get_data(entry.OffsetToData,entry.Size);sub=f'{label}#RT{typ.id}/{name.id}/{lang.id}'
                    try:
                        with resource_image(blob,typ.id) as im:search(im,sub,hashlib.sha256(blob).hexdigest())
                        r['decoded_resources']+=1
                    except Exception as exc:r['decode_errors'].append(dict(label=sub,error=repr(exc)))
        pe.close()
    except pefile.PEFormatError:pass # DOS/non-PE files are outside this resource search.
    except Exception as exc:r['decode_errors'].append(dict(label=label,error=repr(exc)))
r['elapsed_seconds']=time.monotonic()-started
r['limits']='Only these retained files, RGB/BGR24 top-down/bottom-up decoding, supported Pillow image formats, RT_BITMAP/RT_ICON resources. Not live surfaces, transformed/scaled images, missing files, original pre-write slack, or proof of a graphics cause.'
out.write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['image_frames','pe_images','decoded_resources','matches','skipped_large','elapsed_seconds']},indent=2));print('decode_errors',len(r['decode_errors']))
