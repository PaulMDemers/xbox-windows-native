# SPDX-License-Identifier: MIT
"""Exact-rational proposed varying-W control; no guest/runtime attestation."""
from fractions import Fraction as F
from functools import lru_cache
import struct

BG = 0x102030
PALETTES = ((0x206040, 0x40c080, 0x608020, 0x80a060),
            (0x802060, 0xc04080, 0xa06020, 0xe08040))
NAMES = ('constant_w', 'increasing_w', 'decreasing_w', 'swapped_uv', 'scaled_w')
DEPTHS = ((F(5,4),)*3, (F(5,4), F(5,2), F(5)),
          (F(5), F(5,2), F(5,4)), (F(5,4), F(5,2), F(5)),
          (F(5,2), F(5), F(10)))
ALL = frozenset((BG, *PALETTES[0], *PALETTES[1]))


def geometry(stage):
    if type(stage) is not int or not 0 <= stage < 5:
        raise ValueError('stage')
    identity = tuple(tuple(F(i == j) for j in range(4)) for i in range(4))
    projection = [list(row) for row in identity]
    projection[2][2], projection[2][3] = F(16,15), F(1)
    projection[3][2], projection[3][3] = -F(16,15), F(0)
    triangles = []
    for left, right in ((-F(7,8), -F(1,8)), (F(1,8), F(7,8))):
        directions = ((left,F(3,4)), (right,F(3,4)), (left,-F(3,4)))
        triangles.append(tuple((x*z,y*z,z) for (x,y),z in zip(directions,DEPTHS[stage])))
    return dict(triangles=tuple(triangles), matrices=(identity,identity,projection),
                viewport=(0,0,64,64,0,1), uv=((0,0),(0,1),(1,0)) if stage==3 else ((0,0),(1,0),(0,1)),
                order=(0,1), z_enabled=True, clear_z=1)


def project(vertices, matrices):
    result = []
    for xyz in vertices:
        q = [F(v) for v in xyz] + [F(1)]
        for matrix in matrices:
            q = [sum(q[i]*matrix[i][j] for i in range(4)) for j in range(4)]
        x,y,z,w = q
        if w <= 0 or not -w < x < w or not -w < y < w or not 0 < z < w:
            raise ValueError('clip volume')
        result.append((32*(x/w+1),32*(1-y/w),z/w,w))
    return tuple(result)


def edge(a,b,p):
    return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])


def coverage(points,p):
    area = edge(*points)
    if not area:
        raise ValueError('degenerate')
    sign = 1 if area > 0 else -1
    bands = [(sign*edge(points[j],points[(j+1)%3],p),
              2*(abs(points[(j+1)%3][0]-points[j][0])+abs(points[(j+1)%3][1]-points[j][1])))
             for j in range(3)]
    if any(d < -margin for d,margin in bands):
        return 'out'
    return 'in' if all(d > margin for d,margin in bands) else 'edge'


def interpolate(points,uv,p,affine=False):
    area = edge(*points)
    weights = [edge(points[(i+1)%3],points[(i+2)%3],p)/area for i in range(3)]
    if not affine:
        weights = [weight/point[3] for weight,point in zip(weights,points)]
    divisor = sum(weights)
    if divisor <= 0:
        raise ValueError('interpolation denominator')
    return tuple(sum(weights[i]*uv[i][axis] for i in range(3))/divisor for axis in range(2))


def texel_choices(points,uv,p,layer,affine=False):
    # On the entire two-pixel square the denominator is positive. A ratio of
    # affine forms has its extrema at vertices, so these four corners bound UV.
    corners = [interpolate(points,uv,(p[0]+dx,p[1]+dy),affine)
               for dx in (-2,2) for dy in (-2,2)]
    choices=[]
    for axis in range(2):
        low,high = min(c[axis] for c in corners),max(c[axis] for c in corners)
        choices.append((0,) if high < F(1,2) else (1,) if low > F(1,2) else (0,1))
    return frozenset(PALETTES[layer][v*2+u] for v in choices[1] for u in choices[0])


@lru_cache(maxsize=10)
def pixels_for_stage(stage,affine=False):
    g=geometry(stage);points=[project(t,g['matrices']) for t in g['triangles']]
    rows=[]
    for y in range(64):
        for x in range(64):
            allowed,tag=frozenset((BG,)),'background'
            for layer,triangle in enumerate(points):
                kind=coverage(triangle,(x,y))
                if kind=='edge':
                    allowed,tag=frozenset((BG,*PALETTES[layer])),'geometry_band';break
                if kind=='in':
                    allowed=texel_choices(triangle,g['uv'],(x,y),layer,affine)
                    tag='interior' if len(allowed)==1 else 'texture_band';break
            rows.append((allowed,tag))
    return tuple(rows)


def sources(alpha):
    if type(alpha) is not bool:
        raise ValueError('alpha')
    return b''.join(struct.pack('<I',PALETTES[layer][(y//4)*2+x//4] | (0xff000000 if alpha else 0))
                    for layer in range(2) for y in range(8) for x in range(8))


def validate(clear,draw,before,after,alpha):
    if len(clear)!=81920 or len(draw)!=81920:
        raise ValueError('capture extent')
    if before!=sources(alpha) or after!=before:
        raise ValueError('texture content/lifetime')
    for stage in range(5):
        for i,(a,b) in enumerate(zip(struct.unpack_from('<4096I',clear,stage*16384),
                                     struct.unpack_from('<4096I',draw,stage*16384))):
            if a & 0xffffff != BG:
                raise ValueError('clear RGB')
            if b & 0xffffff not in pixels_for_stage(stage)[i][0]:
                raise ValueError(f'perspective RGB stage={stage} x={i%64} y={i//64}')
    return dict(host_oracle_accepted=True,guest_qualification=False,
                captured_pixel_bytes=len(clear)+len(draw),source_bytes=len(before)+len(after),
                excluded='X byte and pitch padding; fixed two-pixel geometry/texel bands')
