"""Independent model of the pinned 64 MiB, no-pool-override startup profile."""
import struct

GLOBALS = {
    'pages':0x823d8, 'highest':0x81bb4, 'possible_highest':0x82498,
    'initial_pool':0x82390, 'maximum_pool':0x82320, 'colors':0x81b68,
    'expanded_pool':0x81178, 'pool_start':0x811c0, 'aligned_pool':0x82278,
    'system_start':0x82330, 'system_ptes':0x81bfc,
    'minimum_pool':0x727e0, 'minimum_growth':0x727e4,
    'default_maximum':0x727e8, 'maximum_growth':0x727ec, 'pool_end':0x72ee0,
    'pool_percent':0x81bb0, 'virtual_bias':0x823e0, 'dynamic_pfn':0x73d30,
    'verifier':0x73d40, 'protect_freed':0x824a8,
}

def verify_sizing(read, kernel, frame, ebx, after=False,pool=False,initialized=False,pfn=False,mapped=False):
    u32=lambda va:struct.unpack('<I',read(va,4))[0]
    g={name:u32(kernel+rva) for name,rva in GLOBALS.items()}
    f=lambda off:u32(frame+off)
    assert g['pages']==g['highest']==g['possible_highest']==0x3bff
    for name in ['expanded_pool','pool_percent','virtual_bias','dynamic_pfn','verifier','protect_freed']:
        assert g[name]==0,(name,g[name])
    expected={'minimum_pool':0x40000,'minimum_growth':0x8000,'default_maximum':0x100000,
              'maximum_growth':0x64000,'pool_end':0xffb85000 if pfn else 0xffbe0000,'system_ptes':0x55f0}
    assert all(g[n]==v for n,v in expected.items())
    colors=g['colors'];assert 2<=colors<=1024 and colors&(colors-1)==0
    pfn_bytes=(g['highest']+1)*24
    groups=(g['pages']-1024)//256
    initial=(g['minimum_pool']+groups*g['minimum_growth'])&~4095
    maximum=(pfn_bytes&~4095)+g['default_maximum']+groups*g['maximum_growth']
    maximum=min(0x8000000,max(maximum,(pfn_bytes&~4095)+initial+0x10000))
    pfn_pages=(pfn_bytes+16*colors)//4096+1
    maximum+=pfn_pages*4096
    pool_start=(0xffbe0000-maximum)&~4095
    system_start=(pool_start-(g['system_ptes']+1)*4096)&0xffc00000
    first=0xc0300000+4*(system_start>>22)
    last=0xc0300000+4*((0xffbe0000-1)>>22)
    planned=(last-first)//4+1
    assert (g['initial_pool'],g['maximum_pool'],g['pool_start'],g['aligned_pool'],g['system_start'])==(initial,maximum,pool_start,pool_start,system_start)
    assert system_start>=0xeb000000 and first<=last
    assert (f(-60),f(-16),f(-68))==(pfn_pages,0xc03fef7c if pfn else last+4 if after else first,initial if pool else last)
    candidate=f(-52);typ,base,pages=struct.unpack('<3I',read(candidate+8,12))
    if pfn:
        assert (typ,base,pages)==(5,0x3ce,0x1d92)
        base,pages=0x160,0x2000 # Original descriptor before native commit.
    assert typ in (2,4,5,8) and ebx==0 # This fixture uses the same largest and low candidate.
    assert (f(-8),f(-12),f(-84),f(-104))==(base+planned+(595 if pfn else 504 if pool else 0) if after else base,pages-planned-(595 if pfn else 504 if pool else 0) if after else pages,base,pages)
    assert all(f(o)==0 for o in ([-28,-32,-40,-44] if mapped else [-28,-40,-44,-48] if pfn else [-28,-32,-40,-44,-48]))
    if mapped:assert f(-48)==0xc0301000
    assert base>2 and planned<pages and base+planned<=0x1000
    if after:
        for i,pde in enumerate(range(first,last+1,4)):
            mask=0
            if mapped:
                from mapped_pfn_model import permission_mask
                mask=permission_mask(read,kernel,(pde<<10)&0xffffffff)|permission_mask(read,kernel,pde)
            assert u32(pde)==(((base+i)*4096)|0x163|mask)
            data=read((pde<<10)&0xffffffff,4096)
            for j,value in enumerate(struct.unpack('<1024I',data)):
                va=(((pde-0xc0300000)//4)<<22)|(j<<12)
                expected=((base+planned+(va-pool_start)//4096)*4096)|0x163 if pool and pool_start<=va<pool_start+initial else 0
                if initialized and va==0xfe6a8000:expected=0xfffff000
                if initialized and va==0xfe6a9000:expected=(5340 if pfn else 5432)<<12
                if pfn and 0xffb85000<=va<0xffbe0000:expected=((0x374+(va-0xffb85000)//4096)<<12)|0x163
                if mapped and expected&1:expected|=permission_mask(read,kernel,0xc0000000+((pde-0xc0300000)//4)*4096+j*4)
                assert value==expected,(hex(va),hex(value),hex(expected))
    else:
        assert all(u32(pde)&1==0 for pde in range(first,last+1,4))
    return {'globals':g,'pfn_color_pages':pfn_pages,'page_table_pages_planned':planned,
            'first_pde':hex(first),'last_pde':hex(last),'candidate':{'pointer':hex(candidate),'type':typ,'base_page':base,'pages':pages},
            'native_results_match_model':True,'target_pdes_all_absent':not after,'first_tables_created_and_zeroed':after and not pool,'pool_backing_mappings_verified':pool,'allocation_not_reached':not after}
