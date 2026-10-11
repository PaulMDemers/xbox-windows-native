"""Owned paused xemu qtest: actual C telemetry engine, never guest/PnP qualification."""
import argparse, hashlib, importlib, json, os, shutil, socket, subprocess, time, sys
from pathlib import Path

def sha(p):
    with Path(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--case', required=True)
    ap.add_argument('--encoder', choices=['conexant','xcalibur'], default='conexant')
    args = ap.parse_args()
    assert args.case.isalnum()
    assert os.environ.get('XBOX_XEMU_MODE') == 'exclusive'
    k = Path(__file__).resolve().parent
    canonical = Path('C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
    exe = canonical / 'outputs/xemu-cpu-surface-evict/build003/artifacts/xemu-candidate.exe'
    assert sha(exe) == '685f24e317322469cac8710286bf928f7b2accbde5062f3cf8c86a9b21e97890'
    core = k / 'artifacts/core002/smbus-model.exe'
    build = json.loads((k/'core002-build.json').read_text())
    sys.dont_write_bytecode=True
    compiled=importlib.import_module('model-pe')
    assert sha(core) == next(r['sha256'] for r in build['files'] if r['name'] == core.name)
    for row in build['sources']:
        assert sha(k / row['name']) == row['sha256']
    out = k / 'artifacts' / args.case
    assert not out.exists()
    # No guest disk or firmware executes: -S pauses from process start. The disk
    # is a fresh owned copy of the configured blank disk; never a canonical guest.
    for port in (4674, 4675):
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', port))
    out.mkdir()
    bios = Path('C:/Emulators/xemu/system/bios/Complex_4627.bin')
    mcpx = Path('C:/Emulators/xemu/system/mcpx/mcpx_1.0.bin')
    eeprom = canonical / 'work/runs/nt5-physical-f-high-allocation-r15/eeprom.bin'
    blank = Path('C:/Emulators/xemu/system/xbox_hdd.qcow2')
    shutil.copyfile(eeprom, out/'eeprom.bin')
    shutil.copyfile(blank, out/'hdd.qcow2')
    config = out/'config.toml'
    config.write_text("[general]\nshow_welcome = false\n[general.updates]\ncheck = false\n[sys.files]\n" +
                      '\n'.join(f"{n} = '{p.as_posix()}'" for n,p in
                      [('bootrom_path',mcpx),('flashrom_path',bios),('eeprom_path',out/'eeprom.bin'),('hdd_path',out/'hdd.qcow2')]) + '\n[net]\nenable = false\n')
    report = {'scope': __doc__, 'debugger_model_test': True, 'ordinary_guest_boot': False,
              'physical_access': False, 'passed': False, 'closed': False,
              'encoder':args.encoder, 'engine_execution':'Core002 x86 under Unicorn; I/O/CRT hooks only; not Windows loader validation',
              'inputs': {str(p):sha(p) for p in (exe, core, bios, mcpx, eeprom, blank, config, Path(__file__), k/'model-pe.py')}, 'transactions':[]}
    dest = k / (args.case + '.json')
    assert not dest.exists()
    trace = (out/'qtest-transcript.jsonl').open('x')
    stdout = (out/'stdout.log').open('xb'); stderr = (out/'stderr.log').open('xb')
    vm = None; q = None; stream = None
    def save():
        dest.write_text(json.dumps(report, indent=2)+'\n')
    def command(line):
        q.sendall((line+'\n').encode())
        while True:
            reply = stream.readline().decode().strip()
            if not reply: raise EOFError('qtest disconnected')
            trace.write(json.dumps({'command':line,'reply':reply})+'\n'); trace.flush()
            if reply.startswith('IRQ '): continue
            assert reply.startswith('OK'), reply
            return int(reply.split()[1], 0) if len(reply.split()) > 1 else 0
    def config_read(slot, function, reg):
        command(f'outl 0xcf8 {0x80000000 | slot << 11 | function << 8 | reg}')
        return command('inl 0xcfc')
    try:
        argv = [str(exe), '-config_path', str(config), '-S', '-display', 'none', '-m', '64',
                '-machine', 'xbox,kernel-irqchip=off,avpack=composite,video-encoder='+args.encoder,
                '-qtest', 'tcp:127.0.0.1:4674,server=on,wait=off',
                '-monitor', 'tcp:127.0.0.1:4675,server=on,wait=off']
        report['argv'] = argv
        vm = subprocess.Popen(argv, cwd=out, stdout=stdout, stderr=stderr, creationflags=subprocess.CREATE_NO_WINDOW,
                              env=dict(os.environ, TEMP=str(out), TMP=str(out), TMPDIR=str(out)))
        report['pid'] = vm.pid; save()
        deadline = time.monotonic()+25
        while True:
            assert vm.poll() is None, 'xemu exited; inspect retained stderr'
            try: q = socket.create_connection(('127.0.0.1',4674), timeout=2); break
            except OSError:
                if time.monotonic() > deadline: raise
                time.sleep(.1)
        stream = q.makefile('rb')
        report['smbus_pci_id'] = config_read(1,1,0)
        report['smbus_class_rev'] = config_read(1,1,8)
        report['modem_pci_id'] = config_read(6,1,0)
        assert report['smbus_pci_id'] == 0x01b410de
        assert report['smbus_class_rev'] >> 8 == 0x0c0500
        # Paused diagnostic intervention: configure only this model's BAR1 and
        # I/O decode. This deliberately is not proof of NT5 resource assignment.
        command(f'outl 0xcf8 {0x80000914}'); command('outl 0xcfc 0xc001')
        command(f'outl 0xcf8 {0x80000904}'); command('outw 0xcfc 1')
        assert config_read(1,1,0x14) == 0xc001
        for address, reg in [(0x10,4),(0x4c,0),(0x4c,1),(0x54,0),(0x10,0x11),(0x10,4)]:
            def transport(op,offset,value):
                if op=='DELAY': return 0 # Synchronous device model; no guest clock advanced.
                if op=='R8': return command(f'inb {0xc000+offset}')
                if op=='R16': return command(f'inw {0xc000+offset}')
                if op=='W8': return command(f'outb {0xc000+offset} {value}')
                raise AssertionError(op)
            result=compiled.run(core,address,reg,transport)
            report['transactions'].append(dict(address=address,command=reg,**result)); save()
            expected=0 if (address,reg) in ((0x10,4),(0x4c,0),(0x4c,1)) else 1
            if address==0x4c and args.encoder=='xcalibur': expected=3 # no ADM1032, real model NACK
            assert result['result'] == expected
            if result['result'] == 0:
                assert result['data'] == (6 if address == 0x10 else 50), 'Independent model value oracle'
                assert result['polls'] == 1 and result['attempts'] == 1
        report['passed'] = True
    except BaseException as e:
        report['failure'] = type(e).__name__ + ': ' + str(e)
        raise
    finally:
        if stream: stream.close()
        if q: q.close()
        if vm:
            if vm.poll() is None: vm.terminate()
            vm.wait(timeout=10)
            report['exit_code'] = vm.returncode
        stdout.close(); stderr.close(); trace.close()
        report['closed'] = True
        report['trace_sha256'] = sha(out/'qtest-transcript.jsonl')
        report['eeprom_unchanged'] = sha(out/'eeprom.bin') == sha(eeprom)
        save()
    print(json.dumps(report['transactions']))

if __name__ == '__main__': main()
