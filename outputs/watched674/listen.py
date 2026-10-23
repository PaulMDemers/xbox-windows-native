"""Owned bounded receiver: validate manifest before socket/readiness."""
import json
from contract import config,receiver,P
cfg,build=config()
result=receiver.receive(cfg,build['attempt'],build['build_id'],build['artifacts']['default.xbe']['sha256'],P/'receiver-ready001.json',P/'capture001',seconds=180)
print(result['status'])
raise SystemExit(0 if result['status']=='one-distinct-valid-record' else 2)
