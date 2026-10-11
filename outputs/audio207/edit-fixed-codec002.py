"""Second source candidate: reviewed WM9709 path; frozen build001 stays intact."""
import hashlib,json,pathlib,subprocess,sys
src=pathlib.Path(sys.argv[1]).resolve();assert src.name=='reactos001' and 'device-workstreams207/audio/work' in str(src)
d=src/'drivers/wdm/audio/drivers/ac97';k=pathlib.Path(__file__).resolve().parent
pins=json.loads((k/'source-build001.json').read_text())['sources']
assert all(hashlib.sha256((d/n).read_bytes()).hexdigest()==h for n,h in pins.items()),'Source001 changed'
initial={n:(d/n).read_text() for n in pins};texts=dict(initial)
def edit(name,old,new):
    s=texts[name];assert s.count(old)==1,(name,s.count(old));texts[name]=s.replace(old,new)
def enter(name,signature,code):
    s=texts[name];at=s.index('{',s.index(signature))+1;texts[name]=s[:at]+code+s[at:]
edit('shared.h','DECLARE_INTERFACE_(IAC97AdapterCommon,IUnknown)\n{','''DECLARE_INTERFACE_(IAC97AdapterCommon,IUnknown)
{
#ifdef XBOX_NT5_AC97_MMIO
    STDMETHOD_(BOOL,IsFixedCodec207)(THIS) PURE;
    STDMETHOD_(BOOL,CodecReady207)(THIS) PURE;
#endif''')
edit('common.h','    PVOID          m_pAciMapping;','''    PVOID          m_pAciMapping;
    BOOL           m_FixedCodec207;
    BOOL           m_FixedReady207;''')
edit('common.h','CAC97AdapterCommon(PUNKNOWN outer) : CUnknown(outer), m_pAciMapping(NULL) { }','''CAC97AdapterCommon(PUNKNOWN outer) : CUnknown(outer), m_pAciMapping(NULL),
        m_FixedCodec207(FALSE), m_FixedReady207(FALSE) { }
    STDMETHODIMP_(BOOL) IsFixedCodec207() { return m_FixedCodec207; }
    STDMETHODIMP_(BOOL) CodecReady207() { return !m_FixedCodec207 || m_FixedReady207; }''')
edit('adapter.cpp','if ((countIO != 0) || (ResourceList->NumberOfMemories() != 1) ||','if ((countIO != 0 && countIO != 2) || (ResourceList->NumberOfMemories() != 1) ||')
# Ports are present on hardware, absent in xemu. They are never accessed.
anchor='    // validate resources\n'
edit('adapter.cpp',anchor,'''#ifdef XBOX_NT5_AC97_MMIO
    if (countIO == 2)
    {
        PCM_PARTIAL_RESOURCE_DESCRIPTOR codec = ResourceList->FindTranslatedPort(0);
        PCM_PARTIAL_RESOURCE_DESCRIPTOR bus = ResourceList->FindTranslatedPort(1);
        if (!codec || !bus || codec->u.Port.Start.HighPart || bus->u.Port.Start.HighPart ||
            codec->u.Port.Length < 0x100 || codec->u.Port.Length > 0x10000 ||
            bus->u.Port.Length < 0x80 || bus->u.Port.Length > 0x10000 ||
            codec->u.Port.Start.LowPart > 0x10000 - codec->u.Port.Length ||
            bus->u.Port.Start.LowPart > 0x10000 - bus->u.Port.Length ||
            !(codec->u.Port.Start.LowPart + codec->u.Port.Length <= bus->u.Port.Start.LowPart ||
              bus->u.Port.Start.LowPart + bus->u.Port.Length <= codec->u.Port.Start.LowPart))
            return STATUS_DEVICE_CONFIGURATION_ERROR;
    }
#endif
'''+anchor)
for name,old in [('adapter.cpp','ResourceList->FindTranslatedMemory(0)->u.Memory.Length < 0x180'),('common.cpp','memory->u.Memory.Length < 0x180')]:
    memory='ResourceList->FindTranslatedMemory(0)' if name=='adapter.cpp' else 'memory'
    edit(name,old,old+' ||\n        '+memory+'->u.Memory.Start.HighPart ||\n        ('+memory+'->u.Memory.Start.LowPart & 3) ||\n        '+memory+'->u.Memory.Start.LowPart > 0xffffffffUL - 0x17f')
edit('common.cpp','    m_bDirectRead = TRUE;\n','''    m_bDirectRead = TRUE;
#ifdef XBOX_NT5_AC97_MMIO
    // Identify before PC-only mixer/power probing. WM9709 has no such registers.
    ntStatus = PrimaryCodecReady();
    if (!NT_SUCCESS(ntStatus)) return ntStatus;
    WORD id1, id2;
    ntStatus = ReadCodecRegister(AC97REG_VENDOR_ID1, &id1);
    if (!NT_SUCCESS(ntStatus)) return ntStatus;
    ntStatus = ReadCodecRegister(AC97REG_VENDOR_ID2, &id2);
    if (!NT_SUCCESS(ntStatus)) return ntStatus;
    if (id1 == 0x574d && id2 == 0x4c09)
    {
        m_FixedCodec207 = TRUE;
        // Both output engines may retain dashboard DMA state. Stop/reset before
        // exposing any NT5 stream. Only analog PCM is offered by this candidate.
        for (ULONG engine = 0x10; engine <= 0x70; engine += 0x60)
        {
            WriteBMControlRegister(engine + X_CR, (UCHAR)0);
            WriteBMControlRegister(engine + X_CR, (UCHAR)CR_RR);
            ULONG attempt;
            for (attempt = 0; attempt < 1000; ++attempt)
            {
                UCHAR control = ReadBMControlRegister8(engine + X_CR);
                if (control != 0xff && !(control & CR_RR)) break;
                KeStallExecutionProcessor(1);
            }
            if (attempt == 1000) return STATUS_IO_DEVICE_ERROR;
            WriteBMControlRegister(engine + X_CR, (UCHAR)0);
            for (attempt = 0; attempt < 100; ++attempt)
            {
                USHORT status = ReadBMControlRegister16(engine + X_SR);
                if (status != 0xffff && (status & 1)) break;
                KeStallExecutionProcessor(1);
            }
            if (attempt == 100) return STATUS_IO_DEVICE_ERROR;
            WriteBMControlRegister(engine + X_SR, (USHORT)0x1c);
            WriteBMControlRegister(engine, (ULONG)0);
        }
        for (int n = 0; n < NODEC_TOP_ELEMENT; ++n) SetNodeConfig((TopoNodeConfig)n, FALSE);
        for (int n = 0; n < PINC_TOP_ELEMENT; ++n) SetPinConfig((TopoPinConfig)n, FALSE);
        m_bDirectRead = FALSE;
        m_PowerState = PowerDeviceD0;
        m_FixedReady207 = TRUE;
        return STATUS_SUCCESS;
    }
    // Preserve the documented xemu STAC9700 path; unknown codecs fail honestly.
    if (id1 != 0x8384 || id2 != 0x7600) return STATUS_NOT_SUPPORTED;
#endif
''')
enter('common.cpp','STDMETHODIMP_(NTSTATUS) CAC97AdapterCommon::WriteCodecRegister','''
#ifdef XBOX_NT5_AC97_MMIO
    if (m_FixedCodec207) return STATUS_NOT_SUPPORTED;
#endif
''')
enter('common.cpp','STDMETHODIMP_(NTSTATUS) CAC97AdapterCommon::ReadCodecRegister','''
#ifdef XBOX_NT5_AC97_MMIO
    if (m_FixedCodec207 && reg != AC97REG_VENDOR_ID1 && reg != AC97REG_VENDOR_ID2)
        return STATUS_NOT_SUPPORTED;
#endif
''')
enter('common.cpp','STDMETHODIMP_(NTSTATUS) CAC97AdapterCommon::ProgramSampleRate','''
#ifdef XBOX_NT5_AC97_MMIO
    if (Register != AC97REG_FRONT_SAMPLERATE || dwSampleRate != 48000)
        return STATUS_NOT_SUPPORTED;
    if (m_FixedCodec207)
        return m_FixedReady207 ? STATUS_SUCCESS : STATUS_DEVICE_NOT_READY;
#endif
''')
enter('common.cpp','STDMETHODIMP_(void) CAC97AdapterCommon::PowerChangeState','''
#ifdef XBOX_NT5_AC97_MMIO
    if (m_FixedCodec207)
    {
        if (NewState.DeviceState < PowerDeviceD0 || NewState.DeviceState > PowerDeviceD3) return;
        if (NewState.DeviceState == PowerDeviceD0)
            m_FixedReady207 = NT_SUCCESS(PrimaryCodecReady());
        else
        {
            WriteBMControlRegister(PO_CR, (UCHAR)0);
            WriteBMControlRegister(0x7b, (UCHAR)0);
            m_FixedReady207 = FALSE;
        }
        m_PowerState = NewState.DeviceState;
        return; // no nonexistent codec power/mixer registers
    }
#endif
''')
edit('common.cpp','''        if (READ_PORT_ULONG ((PULONG)(m_pBusMasterBase + GLOB_STA)) &
            GLOB_STA_PCR)''','''        DWORD status = READ_PORT_ULONG((PULONG)(m_pBusMasterBase + GLOB_STA));
        if (status != 0xffffffff && (status & GLOB_STA_PCR))''')
edit('common.cpp','    DWORD dwRegValue = ReadBMControlRegister32 (GLOB_CNT);','''    DWORD dwRegValue = ReadBMControlRegister32 (GLOB_CNT);
#ifdef XBOX_NT5_AC97_MMIO
    if (dwRegValue == 0xffffffff) return STATUS_IO_DEVICE_ERROR;
#endif''')
edit('wavecyclicminiport.cpp','if (Capture || Audio207Fault)','if (Capture || Audio207Fault || !AdapterCommon->CodecReady207())')
edit('stream2.cpp','if (Miniport->Audio207Fault)\n        return STATUS_IO_DEVICE_ERROR;','if (Miniport->Audio207Fault || !Miniport->AdapterCommon->CodecReady207())\n        return STATUS_IO_DEVICE_ERROR;')
edit('stream.cpp','''        if (stream->ReadReg16(X_SR) & 1) // DCH: DMA controller halted''','''        USHORT status = stream->ReadReg16(X_SR);
        if (status != 0xffff && (status & 1)) // DCH: DMA controller halted''')
edit('miniport.cpp','''        //
        // Process the resources.
        //''','''#ifdef XBOX_NT5_AC97_MMIO
        {
            MiniportFilterDescriptor.PinCount = 2;
            MiniportFilterDescriptor.NodeCount = 1;
            MiniportFilterDescriptor.ConnectionCount = 2;
        }
#endif
        //
        // Process the resources.
        //''')
edit('common.cpp','    *pwChannels = 2;\n','''    *pwChannels = 2;
#ifdef XBOX_NT5_AC97_MMIO
    return; // this target exposes only stereo PCM; no registry expansion to 4/6ch
#endif
''')
edit('miniport.cpp','''            // We can accept different channel configurations, depending''','''#ifdef XBOX_NT5_AC97_MMIO
            if (*(PLONG)PropertyRequest->Value != KSAUDIO_SPEAKER_STEREO)
                return STATUS_INVALID_PARAMETER;
#endif
            // We can accept different channel configurations, depending''')
edit('miniport.cpp','    // Check for the render sample rates.','''#ifdef XBOX_NT5_AC97_MMIO
    nChannels = 2;
#endif
    // Check for the render sample rates.''')
edit('miniport.cpp','''    //
    // We only support PCM, 16-bit.
    //''','''#ifdef XBOX_NT5_AC97_MMIO
    if (Pin != PIN_WAVEOUT || waveFormat->Format.nChannels != 2 ||
         waveFormat->Format.nSamplesPerSec != 48000 ||
         waveFormat->Format.nBlockAlign != 4 || waveFormat->Format.nAvgBytesPerSec != 192000)
        return STATUS_INVALID_PARAMETER;
#endif
    //
    // We only support PCM, 16-bit.
    //''')
edit('mintopo.cpp','''        RtlZeroMemory (FilterDescriptor, sizeof(PCFILTER_DESCRIPTOR));''','''        RtlZeroMemory (FilterDescriptor, sizeof(PCFILTER_DESCRIPTOR));
#ifdef XBOX_NT5_AC97_MMIO
        {
            PinDescriptors = (PPCPIN_DESCRIPTOR)ExAllocatePoolWithTag(PagedPool, 2 * sizeof(PCPIN_DESCRIPTOR), PoolTag);
            ConnectionDescriptors = (PPCCONNECTION_DESCRIPTOR)ExAllocatePoolWithTag(PagedPool, sizeof(PCCONNECTION_DESCRIPTOR), PoolTag);
            if (!PinDescriptors || !ConnectionDescriptors) return STATUS_INSUFFICIENT_RESOURCES;
            RtlZeroMemory(PinDescriptors, 2 * sizeof(PCPIN_DESCRIPTOR));
            for (int pin = 0; pin < 2; ++pin)
            {
                PinDescriptors[pin].KsPinDescriptor.DataRangesCount = SIZEOF_ARRAY(PinDataRangePointersAnalogBridge);
                PinDescriptors[pin].KsPinDescriptor.DataRanges = PinDataRangePointersAnalogBridge;
                PinDescriptors[pin].KsPinDescriptor.DataFlow = pin ? KSPIN_DATAFLOW_OUT : KSPIN_DATAFLOW_IN;
                PinDescriptors[pin].KsPinDescriptor.Communication = KSPIN_COMMUNICATION_NONE;
                PinDescriptors[pin].KsPinDescriptor.Category = pin ? &KSNODETYPE_SPEAKER : &KSCATEGORY_AUDIO;
            }
            SetPinTranslation(0, PIN_WAVEOUT_SOURCE);
            SetPinTranslation(1, PIN_MASTEROUT_DEST);
            PCCONNECTION_DESCRIPTOR connection = {PCFILTER_NODE, 0, PCFILTER_NODE, 1};
            *ConnectionDescriptors = connection;
            FilterDescriptor->PinSize = sizeof(PCPIN_DESCRIPTOR);
            FilterDescriptor->PinCount = 2;
            FilterDescriptor->Pins = PinDescriptors;
            FilterDescriptor->NodeSize = sizeof(PCNODE_DESCRIPTOR);
            FilterDescriptor->ConnectionCount = 1;
            FilterDescriptor->Connections = ConnectionDescriptors;
            return STATUS_SUCCESS; // no fictitious hardware mixer or capture nodes
        }
#endif''')
edit('mintopo.cpp','    *WaveInDest = TransPinDefToPinNr (PIN_WAVEIN_DEST);','''#ifdef XBOX_NT5_AC97_MMIO
    *WaveInDest = (ULONG)-1;
#else
    *WaveInDest = TransPinDefToPinNr (PIN_WAVEIN_DEST);
#endif''')
edit('adapter.cpp','''        if (NT_SUCCESS (ntStatus))
        {
            // register wave capture connection''','''        if (NT_SUCCESS (ntStatus) && ulWaveIn != (ULONG)-1)
        {
            // register wave capture connection''')
edit('mintopo.h','''            UpdateRecordMute ();''','''#ifdef XBOX_NT5_AC97_MMIO
            if (!AdapterCommon->IsFixedCodec207())
#endif
                UpdateRecordMute ();''')
if '--check' in sys.argv:
    print('Validated source pins and all edit anchors without writing');sys.exit(0)
assert not (k/'0208-fixed-codec-cumulative.patch').exists()
for name,s in texts.items():
    if s!=initial[name]:(d/name).write_text(s)
subprocess.run(['git','-C',str(src),'diff','--check','--','drivers/wdm/audio/drivers/ac97'],check=True)
(k/'0208-fixed-codec-cumulative.patch').write_bytes(subprocess.check_output(['git','-C',str(src),'diff','--','drivers/wdm/audio/drivers/ac97']))
print('Authored fixed-codec candidate; no runtime or physical qualification')
