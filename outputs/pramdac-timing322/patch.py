"""Three ordinary PRAMDAC timing latches; no guest-specific returned constants."""
def once(s,a,b):
    assert s.count(a)==1,a
    return s.replace(a,b)

REGS=[('FP_VTOTAL','fp_vtotal',0x804),('FP_VSYNC_START','fp_vsync_start',0x80c),('FP_HTOTAL','fp_htotal',0x824)]

def apply(files):
    f=dict(files)
    c='hw/xbox/nv2a/pramdac.c';h='hw/xbox/nv2a/nv2a_int.h';r='hw/xbox/nv2a/nv2a_regs.h';v='hw/xbox/nv2a/nv2a.c'
    for reg,field,offset in REGS:
        f[r]=once(f[r],'#define NV_PRAMDAC_FP_VDISPLAY_END',f'#define NV_PRAMDAC_{reg} 0x{offset:08X}\n#define NV_PRAMDAC_FP_VDISPLAY_END')
        f[h]=once(f[h],'        uint32_t fp_vdisplay_end;',f'        uint32_t {field};\n        uint32_t fp_vdisplay_end;')
        f[c]=once(f[c],'    case NV_PRAMDAC_FP_VDISPLAY_END:\n        r =',f'    case NV_PRAMDAC_{reg}:\n        r = d->pramdac.{field};\n        break;\n    case NV_PRAMDAC_FP_VDISPLAY_END:\n        r =')
        f[c]=once(f[c],'    case NV_PRAMDAC_FP_VDISPLAY_END:\n        d->',f'    case NV_PRAMDAC_{reg}:\n        d->pramdac.{field} = val;\n        break;\n    case NV_PRAMDAC_FP_VDISPLAY_END:\n        d->')
    zero=''.join(f'    d->pramdac.{field} = 0;\n' for _,field,_ in REGS)
    f[v]=once(f[v],'    d->pcrtc.start = 0;','    d->pcrtc.start = 0;\n'+zero.rstrip())
    f[v]=once(f[v],'static int nv2a_pre_load(void *opaque)\n{\n    NV2AState *d = opaque;\n    nv2a_lock_fifo(d);',
        'static int nv2a_pre_load(void *opaque)\n{\n    NV2AState *d = opaque;\n    nv2a_lock_fifo(d);\n    /* Versions before 4 did not retain these timing registers. */\n'+zero.rstrip())
    f[v]=once(f[v],'.name = "nv2a",\n    .version_id = 3,','.name = "nv2a",\n    .version_id = 4,')
    f[v]=once(f[v],'        VMSTATE_BOOL(pgraph.waiting_for_context_switch, NV2AState),\n        VMSTATE_END_OF_LIST()',
        '        VMSTATE_BOOL(pgraph.waiting_for_context_switch, NV2AState),\n'+''.join(f'        VMSTATE_UINT32_V(pramdac.{field}, NV2AState, 4),\n' for _,field,_ in REGS)+'        VMSTATE_END_OF_LIST()')
    return f
