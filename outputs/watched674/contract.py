"""Pinned receiver contract and exact configured candidate identity."""
import hashlib,importlib.util,json
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn674')
helper=K.parent/'receiver673/readiness.py';decoder=K.parent/'udp655/receiver.py'
assert hashlib.sha256(helper.read_bytes()).hexdigest()=='8503110896e955fd3c288e7fe9f82e3760162aae2ae628f9757aa8d993a31d84'
assert hashlib.sha256(decoder.read_bytes()).hexdigest()=='f6650e7eab5f7e7999d59e734ae998b4fa3bdfa8a747b49d5fb4c97f5e5ce98d'
spec=importlib.util.spec_from_file_location('readiness673',helper)
receiver=importlib.util.module_from_spec(spec);spec.loader.exec_module(receiver)
def config():
 c=json.loads((P/'config.json').read_text());b=json.loads((K/'build001.json').read_text())
 receiver.preflight(c,b['attempt'],b['build_id'],b['artifacts']['default.xbe']['sha256'])
 return c,b
