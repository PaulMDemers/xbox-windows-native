"""Pinned native PFN backing, reservations, and delayed color-page accounting."""
import struct

def verify_pfn_backing(read, kernel, frame, mapped=False,committed=False):
    u32=lambda va:struct.unpack('<I',read(va,4))[0]
    for off,value in {0x81ab0:0xffb85000,0x72ee0:0xffb85000,0x8121c:5340,
        0x8239c:0x7e6a8000,0x8130c:91,0x811b8:0xffbdf000,0x811bc:0xffbdf100}.items():
        assert u32(kernel+off)==value,(hex(off),hex(u32(kernel+off)),hex(value))
    for off,value in {-8:0x3cf,-12:0x1d91,-16:0xc03fef7c,-32:0 if mapped else 0x3ce,-56:0xc0300c00 if mapped else 0x1d92,-60:91,-64:0,-84:0x160,-104:0x2000}.items():
        assert u32(frame+off)==value,(off,hex(u32(frame+off)),hex(value))
    descriptor=u32(frame-52)
    assert struct.unpack('<3I',read(descriptor+8,12))==((5,0x3cf,0x1d91) if committed else (5,0x3ce,0x1d92))
    for i in range(91):
        assert u32(0xc03fee14+i*4)==((0x374+i)<<12)|0x163
        if not mapped:assert read(0xffb85000+i*4096,4096)==bytes(4096)
    assert u32(0xc03fee10)==0 # Separately reserved PTE remains unmapped.
    return {'pfn_database_va':'0xffb85000','pfn_pages':90,'color_pages':1,
        'all_backing_pages_zero':not mapped,'pte_reservations':[91,1],
        'expansion_ptes_remaining':5340,'next_candidate_pfn':975,'candidate_pages_remaining':7569,
        'committed_descriptor_base':975 if committed else 974,'committed_descriptor_pages':7569 if committed else 7570,
        'color_page_descriptor_commit_pending':not committed,'population_not_reached':not mapped}
