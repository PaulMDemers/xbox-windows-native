"""MIT. Create a new control namespace; never modify the closed568 runtime."""
from pathlib import Path
K=Path(__file__).resolve().parent
old=K.parent/'rct568'
names=['runner.c','build001.py','media001.py','review_media001.py','prepare002.py','vm.py','cold002.py','login001.py','collect001.py','review001.py','edition.json','.gitattributes']
for name in names:
    dest=K/name
    assert not dest.exists(),name
    text=(old/name).read_text(encoding='utf-8').replace('568','569')
    if name=='build001.py':
        text=text.replace("shutil.copyfile(K/'runner.c',O/'runner.c')", "shutil.copyfile(K/'runner.c',O/'runner.c');shutil.copyfile(K/'input.h',O/'input.h')")
        text=text.replace("'-ladvapi32'", "'-ladvapi32','-lgdi32'")
    if name=='media001.py':text=text.replace('C:\\xwn569-kit\\RUN569.EXE\nexit', 'C:\\xwn569-kit\\RUN569.EXE /pc800\nexit')
    if name=='prepare002.py':text=text.replace("K/'runner.c',K/'edition.json'", "K/'runner.c',K/'input.h',K/'edition.json'")
    if name=='collect001.py':text=text.replace("for name in ['xwn569/runner.txt','xwn569/registry.bin']:", "for name in sorted(n for n in manifest if n.startswith('xwn569/')):")
    dest.write_bytes(text.encode('utf-8'))
