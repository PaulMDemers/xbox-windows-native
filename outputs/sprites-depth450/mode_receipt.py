"""Independent receipt contract for the temporary24-bit desktop transaction."""
def validate_mode(fields):
    expected={}
    for prefix,bits in [('mode_original',16),('mode_requested',24),('mode_active',24),('mode_after_restore',16)]:
        expected.update({prefix+'_'+k:str(v) for k,v in [('bits',bits),('width',640),('height',480),('hz',60),('flags',0)]})
    expected.update({k:str(v) for k,v in [('mode_inventory_complete',1),('mode_selected',1),('mode_test_status',0),('mode_apply_status',0),('mode_changed',1),('mode_restore_status',0),('mode_restored',1)]})
    for k,v in expected.items():
        if fields.get(k)!=v:raise ValueError('Mode receipt mismatch: '+k)
    def integer(k,lo,hi):
        v=fields.get(k,'')
        if type(v) is not str or not v.isascii() or not v.isdecimal() or str(int(v))!=v or not lo<=int(v)<=hi:raise ValueError('Mode integer: '+k)
        return int(v)
    count=integer('mode_inventory_count',1,4095);index=integer('mode_selected_index',0,count-1)
    expected.update(mode_inventory_count=str(count),mode_selected_index=str(index))
    if {k for k in fields if k.startswith('mode_')}!=set(expected):raise ValueError('Unknown mode receipt')
    return dict(passed=True,original_bits=16,active_bits=24,restored_bits=16,width=640,height=480,hz=60,flags=0,inventory_count=count,selected_index=index)
