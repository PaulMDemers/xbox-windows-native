"""Explicit module loading for shared 846 helpers without preflight name collisions."""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE846 = ROOT / 'outputs/bundle-deploy846/source'
if str(SOURCE846) not in sys.path:
    sys.path.insert(0, str(SOURCE846))


def load_module(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f'Cannot load required helper {path}')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def preflight846():
    return load_module('xbox_bundle_preflight846', SOURCE846 / 'preflight.py')


def preflight847():
    return load_module('xbox_profile_preflight847', Path(__file__).resolve().with_name('preflight.py'))
