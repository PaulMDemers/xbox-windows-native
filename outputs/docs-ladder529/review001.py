#!/usr/bin/env python3
"""Read-only documentation/source/evidence joins; no runtime re-execution."""
import ast
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
KIT = Path(__file__).resolve().parent
DOCS = ('docs/graphics-samples.md', 'docs/graphics-roadmap.md',
        'src/samples/graphics-ladder/README.md')
EVIDENCE = (
    'outputs/context-adapter490/PHYSICAL.md',
    'outputs/context-adapter490/runtime-review002.json',
    'outputs/context-adapter490/physical-final001.json',
    'outputs/d3d-present492/REPORT.md',
    'outputs/d3d-transform494/REPORT.md',
    'outputs/d3d-scene496/REPORT.md',
    'outputs/d3d-scene496/runtime-review002.json',
    'outputs/d3d-scene496/final-review.json',
    'outputs/d3d-scene497/REPORT.md',
    'outputs/blend-context526/REPORT.md',
    'outputs/visible-dispatch528/NEXT.md',
    'outputs/visible-dispatch528/final-review.json',
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8'))


def main():
    output = KIT / 'review001.json'
    if output.exists():
        raise RuntimeError('Closed review output exists; choose a new review ID')
    record = dict(scope='Documentation links, builder mappings and historical record joins only',
                  source_sha256=sha(Path(__file__)), runtime_executed=False,
                  physical_access=False, passed=False)
    try:
        links = []
        for name in DOCS:
            path = ROOT / name
            for target in re.findall(r'\[[^\]\n]*\]\(([^)\s]+)\)', path.read_text(encoding='utf-8')):
                parts = urlsplit(target)
                if parts.scheme or parts.netloc:
                    continue
                dest = (path.parent / unquote(parts.path)).resolve() if parts.path else path
                assert dest.is_relative_to(ROOT) and dest.is_file(), (name, target)
                if parts.fragment:
                    headings = re.findall(r'^#{1,6}\s+(.+?)\s*$', dest.read_text(encoding='utf-8'), re.M)
                    slugs = {re.sub(r'[^\w\- ]', '', h.lower()).replace(' ', '-') for h in headings}
                    assert unquote(parts.fragment) in slugs, (name, target)
                links.append(dict(document=name, target=target))
        record['local_links_checked'] = len(links)
        record['links'] = links
        builder = ROOT / 'tools/build-graphics-samples.py'
        tree = ast.parse(builder.read_text(encoding='utf-8'))
        choices = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value == '--sample':
                choices = list(ast.literal_eval(next(x.value for x in node.keywords if x.arg == 'choices')))
        assert len(choices) == 13 and len(set(choices)) == 13
        readme = (ROOT / DOCS[2]).read_text(encoding='utf-8')
        mappings = []
        for sample in choices:
            runner = 'run' if sample == 'ladder' else sample
            checker = 'sample' if sample == 'ladder' else sample
            names = [f'src/samples/graphics-ladder/{sample}.c',
                     f'src/samples/graphics-ladder/{runner}.cmd',
                     f'tools/graphics_{checker}.py']
            assert f'| `{sample}`' in readme
            for name in names:
                assert (ROOT/name).is_file(), name
                assert Path(name).name in readme, name
            mappings.append(dict(sample=sample, files={n:sha(ROOT/n) for n in names}))
        record['builder_sha256'] = sha(builder)
        record['sample_mappings'] = mappings
        alpha = read_json(EVIDENCE[1])
        alpha_final = read_json(EVIDENCE[2])
        scene = read_json('outputs/d3d-scene496/runtime-review002.json')
        scene_final = read_json('outputs/d3d-scene496/final-review.json')
        for actual in (alpha, scene):
            assert actual['all_allowed_cases_passed'] is True
            assert actual['runner']['completed_cases'] == '2'
            assert actual['runner']['case0_exit'] == actual['runner']['case1_exit'] == '0'
        assert alpha_final['closed'] and alpha_final['arithmetic_characterization_passed']
        assert not alpha_final['exact_ideal_alpha_qualified']
        assert not alpha_final['repeat_boot_stability_qualified']
        assert not alpha_final['gpu_qualified'] and not alpha_final['game_compatibility_qualified']
        assert scene_final['scoped_d3d_scene_passed'] and scene_final['normal_restart']
        assert scene_final['physical_access'] is False and scene_final['owned_processes_open'] == []
        record['historical_claims'] = dict(alpha490_selected_inputs_passed=True,
            alpha490_ideal_endpoints_passed=False, alpha490_boot_stability_qualified=False,
            scene496_pc_passed=True, scene496_physical_access=False,
            scope='Existing records inspected; no captures regenerated or runtime rerun')
        record['document_hashes'] = {n:sha(ROOT/n) for n in DOCS}
        record['evidence_hashes'] = {n:sha(ROOT/n) for n in EVIDENCE}
        record['passed'] = True
    except Exception as exc:
        record['error'] = repr(exc)
        raise
    finally:
        with output.open('x', encoding='utf-8', newline='\n') as f:
            json.dump(record, f, indent=2)
            f.write('\n')
    print(json.dumps({k:record[k] for k in ('passed','local_links_checked','historical_claims')}))


if __name__ == '__main__':
    main()
