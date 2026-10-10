"""Apply audio207-only changes to the independently reconstructed patch0016 tree."""
import pathlib, subprocess, sys
src=pathlib.Path(sys.argv[1]).resolve()
assert src.name=='reactos001' and 'device-workstreams207/audio/work' in str(src)
d=src/'drivers/wdm/audio/drivers/ac97'
def edit(name,old,new):
    p=d/name;s=p.read_text();assert s.count(old)==1,(name,s.count(old));p.write_text(s.replace(old,new))

# Quiesce the engine and detach the ISR's stream pointer before derived teardown.
# A broken engine retains its DMA allocation and miniport reference and blocks
# future streams: do not turn a hardware timeout into use-after-free.
edit('miniport.h','    PDMACHANNEL         DmaChannel;','    BOOLEAN             Audio207Fault; // zero-initialized by PortCls pool new\n    PDMACHANNEL         DmaChannel;')
edit('stream.h','    void ResetDMA (void);','    void ResetDMA (void);\n#ifdef XBOX_NT5_AC97_MMIO\n    BOOLEAN Audio207Touched;\n    static NTSTATUS NTAPI Quiesce207(PINTERRUPTSYNC Sync, PVOID Context);\n    BOOLEAN Quiesce207();\n#endif')
edit('wavecyclicstream.cpp','    // Release the scatter/gather table.\n    BDList_Free();',
'''#ifdef XBOX_NT5_AC97_MMIO
    if (!Quiesce207())
    {
        // Keep the miniport/DMA channel and descriptor allocation alive after
        // a hardware fault. ISR was detached; new streams are rejected.
        Miniport = NULL;
        return;
    }
#endif
    // Release only after hardware halt and synchronized ISR detachment.
    BDList_Free();''')
edit('stream2.cpp','                             PAGE_SIZE,','                             MAX_BDL_ENTRIES * sizeof(tBDEntry),')
edit('wavecyclicminiport.cpp','    if (Capture)\n','    if (Capture || Audio207Fault)\n')
edit('stream.cpp','    ResetDMA ();\n\n    //\n    // Now set',
'''#ifdef XBOX_NT5_AC97_MMIO
    Audio207Touched = TRUE;
#endif
    ResetDMA ();
#ifdef XBOX_NT5_AC97_MMIO
    if (Miniport->Audio207Fault)
        return STATUS_IO_DEVICE_ERROR;
#endif

    //
    // Now set''')
edit('stream.cpp','        DOUT (DBG_ERROR, ("ResetDMA TIMEOUT!!"));','''        DOUT (DBG_ERROR, ("ResetDMA TIMEOUT!!"));
#ifdef XBOX_NT5_AC97_MMIO
        Miniport->Audio207Fault = TRUE;
        WriteReg8(X_CR, 0);
        return;
#endif''')
edit('stream.cpp','        if (Miniport->AdapterCommon)\n','''        if (Miniport->AdapterCommon
#ifdef XBOX_NT5_AC97_MMIO
            && Audio207Touched
#endif
            )
''')
edit('stream2.cpp','    switch (State)\n','''#ifdef XBOX_NT5_AC97_MMIO
    if (Miniport->Audio207Fault)
        return STATUS_IO_DEVICE_ERROR;
#endif
    switch (State)
''')
edit('stream2.cpp','            ResetDMA ();\n            break;','''            ResetDMA ();
#ifdef XBOX_NT5_AC97_MMIO
            if (Miniport->Audio207Fault)
                return STATUS_IO_DEVICE_ERROR;
#endif
            break;''')
edit('stream.cpp','''    do
    {
        nCurrentIndex = ReadReg8(X_CIV);

        RegisterX_PICB = ReadReg16 (X_PICB);
    } while (nCurrentIndex != (int)ReadReg8(X_CIV));

    *buffPos = (BDList[nCurrentIndex].wLength - RegisterX_PICB) * 2;''','''#ifdef XBOX_NT5_AC97_MMIO
    for (ULONG attempt = 0; attempt < 8; ++attempt)
    {
        nCurrentIndex = ReadReg8(X_CIV);
        RegisterX_PICB = ReadReg16(X_PICB);
        if (nCurrentIndex != (int)ReadReg8(X_CIV))
            continue;
        if (!BDList || nCurrentIndex >= MAX_BDL_ENTRIES ||
            RegisterX_PICB > BDList[nCurrentIndex].wLength)
            break;
        *buffPos = (BDList[nCurrentIndex].wLength - RegisterX_PICB) * 2;
        return nCurrentIndex;
    }
    *buffPos = 0;
    return -1; // unstable or invalid device data is not a fabricated position
#else
    do
    {
        nCurrentIndex = ReadReg8(X_CIV);
        RegisterX_PICB = ReadReg16 (X_PICB);
    } while (nCurrentIndex != (int)ReadReg8(X_CIV));
    *buffPos = (BDList[nCurrentIndex].wLength - RegisterX_PICB) * 2;
#endif''')
edit('wavecyclicstream.cpp','    UCHAR   nCurrentIndex ;','    int     nCurrentIndex;')
edit('wavecyclicstream.cpp','    nCurrentIndex = GetBuffPos((DWORD*)Position);','''    nCurrentIndex = GetBuffPos((DWORD*)Position);
    if (nCurrentIndex < 0)
        return STATUS_IO_DEVICE_ERROR;''')
# Nonpageable synchronized callback: at most 100 microsecond stall, no pool free.
p=d/'stream.cpp';p.write_text(p.read_text()+'''
#ifdef XBOX_NT5_AC97_MMIO
NTSTATUS NTAPI CMiniportStream::Quiesce207(PINTERRUPTSYNC Sync, PVOID Context)
{
    UNREFERENCED_PARAMETER(Sync);
    CMiniportStream *stream = (CMiniportStream *)Context;
    CMiniport *miniport = stream->Miniport;
    stream->WriteReg8(X_CR, 0);
    stream->DMAEngineState = DMA_ENGINE_OFF;
    if (miniport->Streams[stream->Pin / 2] == stream)
        miniport->Streams[stream->Pin / 2] = NULL;
    for (ULONG attempt = 0; attempt < 100; ++attempt)
    {
        if (stream->ReadReg16(X_SR) & 1) // DCH: DMA controller halted
        {
            stream->WriteReg16(X_SR, 0x1c); // acknowledge only W1C status
            stream->WriteReg32(0, 0);
            return STATUS_SUCCESS;
        }
        KeStallExecutionProcessor(1);
    }
    miniport->Audio207Fault = TRUE;
    return STATUS_IO_DEVICE_ERROR;
}

BOOLEAN CMiniportStream::Quiesce207()
{
    if (!Audio207Touched || !Miniport || !Miniport->AdapterCommon)
        return TRUE;
    return NT_SUCCESS(Miniport->InterruptSync->CallSynchronizedRoutine(
        CMiniportStream::Quiesce207, this));
}
#endif
''')
# Never expose unchecked high DMA addresses or wrap the 32-bit descriptor field.
edit('wavecyclicstream.cpp','    DWORD addr = DmaChannel->PhysicalAddress().LowPart;', '''    PHYSICAL_ADDRESS physical = DmaChannel->PhysicalAddress();
    DWORD addr = physical.LowPart;
#ifdef XBOX_NT5_AC97_MMIO
    if (physical.HighPart || addr > 0xffffffffUL - totalSize ||
        bufferSize == 0 || bufferSize / 2 > 0xffff || (addr & 3))
        return STATUS_DEVICE_CONFIGURATION_ERROR;
#endif''')
edit('stream2.cpp','    return BDList;','''#ifdef XBOX_NT5_AC97_MMIO
    if (BDList && (BDList_PhysAddr.HighPart || (BDList_PhysAddr.LowPart & 7) ||
        BDList_PhysAddr.LowPart > 0xffffffffUL - MAX_BDL_ENTRIES * sizeof(tBDEntry)))
    {
        BDList_Free();
        return NULL;
    }
#endif
    return BDList;''')
# Capture an incremental patch relative to the staged, verified patch0016 tree.
patch=subprocess.check_output(['git','-C',str(src),'diff','--','drivers/wdm/audio/drivers/ac97'])
(pathlib.Path(__file__).parent/'0207-aci-lifecycle.patch').write_bytes(patch)
subprocess.run(['git','-C',str(src),'diff','--check'],check=True)
