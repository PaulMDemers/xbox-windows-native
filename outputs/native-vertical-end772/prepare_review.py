"""Create772 freeze review from source-only770; does not run it."""
from pathlib import Path
K=Path(__file__).resolve().parent
s=(K.parent/'native-crtc-stridelow770/review_prepare.py').read_text().replace('770','772').replace('payload001.json','payload002.json')
s=s.replace("'secondCR17']","'secondCR17','secondCR19']").replace("'result_bytes':928","'result_bytes':1024").replace('0x54a0','0x5500').replace("'padded_payload_extent':9916","'padded_payload_extent':12800").replace("'integration_cases':268","'integration_cases':299")
s=s.replace('Five masks omitted raw; final success requires all13','Six masks omitted raw; final success requires all14').replace('CR13 diagnostic only; no later mode operations','NVVDISPEND diagnostic only; no NVVTOTAL or later mode operations')
s=s.replace("['prepare.py','extend_integration.py']", "['prepare.py','extend_integration.py','extend_bounds.py','prepare_review.py']")
p=K/'review_prepare.py';assert not p.exists();p.write_text(s,newline='\n')
print('Created772 freeze review')
