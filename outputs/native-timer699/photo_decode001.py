"""Decode ten optical MSB-left rows, without expected register values.
Cell geometry is calibrated separately for each row. White cells on the white
reference quadrant merge with the background, so sample predicted cell centers.
This is optical evidence, not a native register dump. Keep the photo private.
"""
import datetime, hashlib, json, statistics, sys
from pathlib import Path
K = Path(__file__).resolve().parent
sys.path.insert(0, str(K.parents[1] / 'work/python-packages'))
from PIL import Image

def fit(points, axis):
    # Least-squares quadratic geometry; no bit values enter the fit.
    terms = [[1, c / 31, (c / 31) ** 2] for c, p in points]
    a = [[sum(t[i] * t[j] for t in terms) for j in range(3)] +
         [sum(t[i] * p[axis] for t, (c, p) in zip(terms, points))]
         for i in range(3)]
    for i in range(3):
        pivot = max(range(i, 3), key=lambda j: abs(a[j][i]))
        a[i], a[pivot] = a[pivot], a[i]
        d = a[i][i]
        assert abs(d) > 1e-10
        a[i] = [v / d for v in a[i]]
        for j in range(3):
            if j != i:
                d = a[j][i]
                a[j] = [v - d * w for v, w in zip(a[j], a[i])]
    return [a[i][3] for i in range(3)]

def predict(coeff, col):
    t = col / 31
    return coeff[0] + coeff[1] * t + coeff[2] * t * t

def components(im):
    mask = {}
    for y in range(265, 760):
        for x in range(100, 1140):
            rgb = im.getpixel((x, y))
            if max(rgb) < 95:
                mask[x, y] = 0
            elif min(rgb) > 160:
                mask[x, y] = 1
    found = []
    while mask:
        start, bit = mask.popitem()
        stack, pts = [start], [start]
        while stack:
            x, y = stack.pop()
            for q in [(x-1,y), (x+1,y), (x,y-1), (x,y+1)]:
                if mask.get(q, -1) == bit:
                    del mask[q]
                    stack.append(q)
                    pts.append(q)
        if len(pts) < 220:
            continue
        xs, ys = zip(*pts)
        w, h = max(xs)-min(xs)+1, max(ys)-min(ys)+1
        if 17 <= w <= 40 and 20 <= h <= 40:
            found.append({'center': [sum(xs)/len(xs), sum(ys)/len(ys)],
                          'bit': bit, 'box': [min(xs),min(ys),w,h]})
    return found

def main():
    assert len(sys.argv) == 2
    out = K / 'photo001.json'
    assert not out.exists()
    raw = Path(sys.argv[1]).read_bytes()
    im = Image.open(sys.argv[1]).convert('RGB')
    receipt = {'passed': False, 'scope': __doc__,
               'photo_sha256': hashlib.sha256(raw).hexdigest(),
               'size': list(im.size), 'rows': []}
    try:
        comps = components(im)
        left = [286,331,377,422,467,512,558,604,650,697]
        right = [311,357,403,451,499,546,593,641,690,739]
        for row in range(10):
            cells = sorted([v for v in comps if abs(v['center'][1] -
                (left[row]+(right[row]-left[row])*(v['center'][0]-140)/965)) < 14],
                key=lambda v: v['center'][0])
            # All first16 cells are isolated on the red/blue reference panels.
            assert len(cells) >= 16, (row, len(cells))
            seed = cells[:16]
            assert seed[0]['center'][0] < 160 and seed[-1]['center'][0] < 690
            assert all(27 < b['center'][0]-a['center'][0] < 43
                       for a,b in zip(seed,seed[1:]))
            points = [(c, v['center']) for c,v in enumerate(seed)]
            assigned = list(range(16))
            spacings = [seed[i]['center'][0]-seed[i-1]['center'][0] for i in range(1,16)]
            previous = seed[-1]['center'][0]
            for v in cells[16:]:
                gap = v['center'][0]-previous
                pitch = statistics.median(spacings[-3:])
                steps = round(gap/pitch)
                assert 1 <= steps <= 8 and abs(gap/steps-pitch) < 3
                col = assigned[-1]+steps
                assert col < 32
                assigned.append(col)
                points.append((col,v['center']))
                spacings.append(gap/steps)
                previous = v['center'][0]
            assert max(assigned) >= 24
            fx, fy = fit(points,0), fit(points,1)
            residual = max(max(abs(predict(fx,c)-p[0]),abs(predict(fy,c)-p[1])) for c,p in points)
            assert residual < 4, (row,residual)
            samples = []
            for col in range(32):
                x,y = round(predict(fx,col)),round(predict(fy,col))
                variants = []
                for dx,dy in [(0,0),(-3,0),(3,0),(0,-3),(0,3)]:
                    pixels = [im.getpixel((x+dx+u,y+dy+v)) for u in range(-2,3) for v in range(-2,3)]
                    rgb = [statistics.median(p[k] for p in pixels) for k in range(3)]
                    bits = [0 if max(rgb)<b else 1 if min(rgb)>w else None
                            for b,w in [(95,160),(105,150),(115,140)]]
                    assert bits[0] is not None and len(set(bits)) == 1, (row,col,rgb)
                    variants.append({'offset':[dx,dy],'median_rgb':rgb,'bit':bits[0]})
                assert len(set(v['bit'] for v in variants)) == 1
                bit = variants[0]['bit']
                if col in assigned:
                    assert bit == cells[assigned.index(col)]['bit']
                samples.append({'column':col,'center':[x,y],'bit':bit,'variants':variants})
            bits = ''.join(str(v['bit']) for v in samples)
            receipt['rows'].append({'row':row,'bits_msb_left':bits,'value_hex':f'0x{int(bits,2):08x}',
                'calibration_columns':assigned,'components':cells,'fit_x':fx,'fit_y':fy,
                'max_residual_px':residual,'samples':samples})
        receipt['bar_samples'] = [{'pixel':[1000,y],'rgb':list(im.getpixel((1000,y)))} for y in [135,215]]
        for sample in receipt['bar_samples']:
            r,g,b = sample['rgb']
            assert g > 160 and r < 100 and b < 100
        receipt['decoded_rows'] = [v['value_hex'] for v in receipt['rows']]
        receipt['passed'] = True
    except BaseException as exc:
        receipt['failure'] = repr(exc)
        raise
    finally:
        receipt['utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        out.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ['passed','decoded_rows','bar_samples']}))

if __name__ == '__main__':
    main()
