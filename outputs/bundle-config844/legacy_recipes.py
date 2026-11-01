"""Write fresh 1.0 E-profile recipes from pinned build artifacts, no packaging."""
import json
from pathlib import Path

k = Path(__file__).resolve().parent
base = json.loads((k / 'xbox10-720.json').read_text())
base['history'] = ('The launcher, FreeLoader, HAL, boot video and FATX driver match selected '
                   '1.0 physical-run component pins; the Windows registry comes from the older '
                   'immutable stock-E installation and its full equivalence to that later run is '
                   'not established. This assembled package is not boot-tested.')
base['source_records'] += [
    {'description': 'Independent matched FreeLoader build', 'source': 'outputs/stock-boot334/build001.json',
     'sha256': '6d5dda35b9a5096b851d3e2508dd5abe28ad9068cde9dbc5b0eb6f21c25aaed3'},
    {'description': 'Independent FATX390 build', 'source': 'outputs/fatx-enumeration390/build-report.json',
     'sha256': '2786704a0ac5e869ce33c888dc7254740dd64d765f3e66ccf580d609a5bc4f68'},
    {'description': '642 physical pre-test component pins', 'source': 'outputs/windows480p642/stage001.json',
     'sha256': 'abbe3c386a514dc816a3b20199f09268c1f37d6d309939d15ed02cf35634af39'}]
base['overlays'] += [
    {'target': 'E/Applications/XWNEBoot/freeldr.sys', 'source': 'E:/xwn334/build001/freeldr.sys',
     'sha256': '8723fc175cc490f0c3cd1650e9c91ab97e9ed04108734ad6202e6f0653804697'},
    {'target': 'E/Applications/XWNEBoot/rosload.exe', 'source': 'E:/xwn334/build001/rosload.exe',
     'sha256': '62f3620183cb2c7b1aa575d9908df3e54e043cd5bf62c1c8a291954e9876f4b1'},
    {'target': 'E/winnt/system32/drivers/xwnfatx.sys', 'source': 'D:/xwn844/fatx390.xwn',
     'sha256': '41040f9eaeaae3382a6fadf11a315253ff9017e908dc15a876818c5969039126'}]
for profile, title, filename in [('e-720p', 'Xbox 1.0 fixed 720p - private test', 'xbox10-720-matched.json'),
                                 ('e-720x480', 'Xbox 1.0 fixed 720x480 progressive - private test', 'xbox10-480p-matched.json')]:
    c = json.loads(json.dumps(base))
    c['profile'], c['title'] = profile, title
    if profile == 'e-720x480':
        c['overlays'][0] = {'target': 'E/Applications/XWNEBoot/default.xbe',
                            'source': 'C:/xwn633/build001/default.xbe',
                            'sha256': 'a53a09427f80411efee73ef53da0ec9829f8af0d27d404f5a3ff818e96b4bde4'}
        c['source_records'].append({'description': '720x480 candidate build and scoped physical evidence',
                                    'source': 'outputs/native480p633/REPORT.md',
                                    'sha256': 'd1fa3ffa21fd1838d14854a95418c04a58e06c991c94a588adbbfe1f572c93f1'})
    with (k / filename).open('x', encoding='utf-8') as f:
        json.dump(c, f, indent=2)
        f.write('\n')
