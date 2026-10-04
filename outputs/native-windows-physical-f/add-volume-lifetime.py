from pathlib import Path
s=Path('/home/paul/xbox-windows-native/sources/reactos-extended/boot/freeldr/freeldr')
p=s/'lib/fs/fs.c';t=p.read_text();needle='''            if (pDevice->FileFuncTable)
                break;''';assert t.count(needle)==2
t=t.replace(needle,'''            if (pDevice->FileFuncTable)
            {
#ifdef XBOX_NATIVE_FATX_F_BOOT
                /* Filesystems keep mounted state indexed by DeviceId, while
                 * DEVICE caches FileFuncTable across file opens. Keep the
                 * backing slot alive for that mount's lifetime: reusing it
                 * for another FATX volume otherwise replaces FatVolumes[id]
                 * beneath the first device's cached dispatch table.
                 * There is no filesystem-unmount API during this loader run. */
                ++pDevice->ReferenceCount;
                ++FileData[DeviceId].ReferenceCount;
#endif
                break;
            }''');p.write_text(t)
p=s/'pcat.cmake';t=p.read_text();needle='    target_compile_definitions(freeldr_pe PRIVATE XBOX_NATIVE_FATX_F_BOOT=1)';assert t.count(needle)==1;t=t.replace(needle,needle+'\n    target_compile_definitions(freeldr_common PRIVATE XBOX_NATIVE_FATX_F_BOOT=1)');p.write_text(t)
