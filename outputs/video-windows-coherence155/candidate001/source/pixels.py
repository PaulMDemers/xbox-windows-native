"""Independent cold image gates; observed alpha is explicitly outside RGB scope."""
from protocol import expected_bytes,W,H
def reference(data,index):
    return data is not None and len(data)==W*H*4 and data==expected_bytes(index)
def observed(data,index):
    if data is None or len(data)!=W*H*4:return False
    expected=expected_bytes(index)
    return all(data[channel::4]==expected[channel::4] for channel in range(3))
