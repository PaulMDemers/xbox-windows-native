from pathlib import Path
import difflib, hashlib
K=Path(__file__).resolve().parent
p=K/'main.c'; old=p.read_text(); start=old.index('    HANDLE file = INVALID_HANDLE_VALUE;',old.index('static int save_report')); end=old.index('    DWORD written = 0;',start)
new=old[:start]+'''    snprintf(path, size, "E:\\\\Applications\\\\XWNEBoot\\\\boot-report.json");
    HANDLE file = CreateFileA(path, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (file == INVALID_HANDLE_VALUE) return 1;
'''+old[end:]
new=new.replace('        append("  \\\"start_record\\\":\\\"%s\\\",\\n", path + 3); /* E-root basename, no JSON escapes. */','        append("  \\\"status_record\\\":\\\"boot-report.json\\\",\\n");')
assert new!=old and 'path + 3' not in new
p.write_text(new)
(K/'wrapper.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),'a/main.c','b/main.c')))
print(hashlib.sha256(p.read_bytes()).hexdigest())
