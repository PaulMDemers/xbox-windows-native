"""Reject dangerous extent/count interpretations before producing a contract."""
from pathlib import Path
import importlib.util
import json

kit = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('inventory', kit/'analyze-inventory.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
text = (kit/'evidence/physical-storage.txt').read_text()
good = module.analyze(text)
assert good['excluded_out_of_disk_query_partitions'] == [2]
assert good['cluster_bytes'] == 65536
assert good['requires_addressing_beyond_lba28']
assert not good['native_windows_writes_ready']
cases = {
    'truncated': text.split('END partition=7')[0],
    'log_failure': text.replace('INVENTORY_COMPLETE log_ok=1', 'INVENTORY_COMPLETE log_ok=0'),
    'missing_f': text.replace('partition=6 start_bytes=', 'partition=9 start_bytes='),
    'out_of_bounds': text.replace('length_bytes=242055217152', 'length_bytes=250059350016'),
    'zero_length': text.replace('length_bytes=242055217152', 'length_bytes=0'),
    'unaligned': text.replace('start_bytes=8004132864', 'start_bytes=8004132865'),
    'overlap_e': text.replace('start_bytes=8004132864', 'start_bytes=2884108288'),
    'bad_cluster': text.replace('sectors_per_unit=128', 'sectors_per_unit=127'),
    'bad_sector': text.replace('bytes_per_sector=512', 'bytes_per_sector=4096'),
    'free_exceeds_total': text.replace('free_units=1550731', 'free_units=3693245'),
    'volume_exceeds_extent': text.replace('total_units=3693244', 'total_units=99999999'),
    'duplicate_extent': text+'\npartition=6 start_bytes=8004132864 length_bytes=242055217152\n',
}
passed = []
for name, changed in cases.items():
    try: module.analyze(changed)
    except ValueError: passed.append(name)
    else: raise AssertionError('Invalid inventory accepted: '+name)
(kit/'inventory-tests.json').write_text(json.dumps({
    'physical_inventory_accepted': True, 'out_of_disk_c_excluded': True,
    'invalid_inventories_rejected': passed}, indent=2)+'\n')
print('Physical inventory accepted; twelve invalid inventories rejected.')
