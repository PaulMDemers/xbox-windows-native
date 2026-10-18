# SPDX-License-Identifier: MIT
"""Host-only proposed scene oracle. No device/guest/transport attestation."""
from fractions import Fraction as F
from functools import lru_cache
import struct

BG = 0x102030
PALETTES = ((0x206040, 0x40c080, 0x608020, 0x80a060),
            (0x802060, 0xc04080, 0xa06020, 0xe08040))
NAMES = ('far_near', 'near_far', 'no_z', 'zero_z', 'camera_move')
ALL = frozenset((BG, *PALETTES[0], *PALETTES[1]))


def identity():
    return tuple(tuple(F(i == j) for j in range(4)) for i in range(4))


def geometry(stage):
    if type(stage) is not int or not 0 <= stage < 5:
        raise ValueError('stage')
    world = [list(r) for r in identity()]
    view = [list(r) for r in identity()]
    projection = [list(r) for r in identity()]
    world[3][0] = F(-1 if stage == 4 else 1, 8)
    view[3][1] = -F(1, 8)
    projection[2][2], projection[2][3] = F(2), F(1)
    projection[3][2], projection[3][3] = F(-2), F(0)
    # Literal model coordinates, not screen coordinates or captured pixels.
    triangles = (((-F(7,8),F(3,4),F(5,4)), (F(5,8),F(3,4),F(5,4)),
                  (-F(7,8),-F(3,4),F(5,4))),
                 ((-F(1,4),F(3,4),F(3,2)), (F(5,4),F(3,4),F(3,2)),
                  (-F(1,4),-F(3,4),F(3,2))))
    return dict(triangles=triangles, matrices=(world,view,projection),
                viewport=(0,0,64,64,0,1), uv=((0,0),(1,0),(0,1)),
                order=(1,0) if stage == 0 else (0,1),
                z_enabled=stage != 2, clear_z=0 if stage == 3 else 1)


def project(vertices, matrices):
    if len(vertices) != 3 or len(matrices) != 3:
        raise ValueError('geometry extent')
    result = []
    for vertex in vertices:
        if len(vertex) != 3:
            raise ValueError('vertex extent')
        q = [F(v) for v in vertex] + [F(1)]
        for matrix in matrices:
            if len(matrix) != 4 or any(len(row) != 4 for row in matrix):
                raise ValueError('matrix extent')
            q = [sum(q[i]*F(matrix[i][j]) for i in range(4)) for j in range(4)]
        x,y,z,w = q
        if w <= 0 or not -w <= x <= w or not -w <= y <= w or not 0 <= z <= w:
            raise ValueError('outside specified clip volume')
        result.append((32*(x/w+1),32*(1-y/w),z/w,w))
    if edge(result[0],result[1],result[2]) == 0:
        raise ValueError('degenerate')
    # This particular oracle has constant depth/W within each triangle.
    # It does not claim coverage of perspective-correct varying-W interpolation.
    if len({p[2:] for p in result}) != 1:
        raise ValueError('varying depth/W outside this control')
    return tuple(result)


def edge(a,b,p):
    return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])


def coverage(points, p):
    sign = 1 if edge(*points) > 0 else -1
    distances = [(sign*edge(points[j],points[(j+1)%3],p),
                  2*(abs(points[(j+1)%3][0]-points[j][0])+
                     abs(points[(j+1)%3][1]-points[j][1]))) for j in range(3)]
    if any(d < -margin for d,margin in distances):
        return 'out'
    return 'in' if all(d > margin for d,margin in distances) else 'edge'


def uv(points, p):
    area = edge(*points)
    return (edge(points[2],points[0],p)/area,
            edge(points[0],points[1],p)/area)


def texel_choices(points, p, layer):
    u,v = uv(points,p)
    origin = uv(points,(0,0))
    dx,dy = uv(points,(1,0)),uv(points,(0,1))
    bands = [2*(abs(dx[i]-origin[i])+abs(dy[i]-origin[i])) for i in range(2)]
    choices = []
    for coordinate,band in zip((u,v),bands):
        choices.append((0,) if coordinate < F(1,2)-band else
                       (1,) if coordinate > F(1,2)+band else (0,1))
    return frozenset(PALETTES[layer][y*2+x] for y in choices[1] for x in choices[0])


@lru_cache(maxsize=5)
def pixels_for_stage(stage):
    g = geometry(stage)
    projected = tuple(project(v,g['matrices']) for v in g['triangles'])
    if not 0 < projected[0][0][2] < projected[1][0][2] < 1:
        raise ValueError('depth separation')
    priority = (0,1) if g['z_enabled'] else tuple(reversed(g['order']))
    rows = []
    for y in range(64):
        for x in range(64):
            allowed,tag = frozenset((BG,)), 'background'
            if g['clear_z']:
                for layer in priority:
                    kind = coverage(projected[layer],(x,y))
                    if kind == 'edge':
                        allowed,tag = ALL,'geometry_band'
                        break
                    if kind == 'in':
                        allowed = texel_choices(projected[layer],(x,y),layer)
                        tag = ('near' if layer == 0 else 'far') if len(allowed)==1 else 'texture_band'
                        break
            rows.append((allowed,tag))
    counts = {tag:sum(t==tag for _,t in rows) for tag in
              ('near','far','background','geometry_band','texture_band')}
    if counts['background'] < 2000 or (stage != 3 and min(counts['near'],counts['far']) < 20):
        raise ValueError('insufficient independent region coverage')
    return tuple(rows)


def sources(alpha):
    if type(alpha) is not bool:
        raise ValueError('format alpha flag')
    return b''.join(struct.pack('<I',PALETTES[layer][(y//4)*2+x//4] |
                               (0xff000000 if alpha else 0))
                    for layer in range(2) for y in range(8) for x in range(8))


def validate_sources(before,after,alpha):
    if before != sources(alpha) or after != before:
        raise ValueError('source extent/content/lifetime')


def validate_pixel(stage,index,value):
    if type(index) is not int or not 0 <= index < 4096:
        raise ValueError('pixel index')
    if type(value) is not int or not 0 <= value <= 0xffffffff:
        raise ValueError('pixel word')
    if value & 0xffffff not in pixels_for_stage(stage)[index][0]:
        raise ValueError('scene RGB')


def validate(clear,draw,before,after,alpha):
    if len(clear) != 5*16384 or len(draw) != 5*16384:
        raise ValueError('capture extent')
    validate_sources(before,after,alpha)
    for stage in range(5):
        for j,(a,b) in enumerate(zip(struct.unpack_from('<4096I',clear,stage*16384),
                                     struct.unpack_from('<4096I',draw,stage*16384))):
            if a & 0xffffff != BG:
                raise ValueError('clear RGB')
            validate_pixel(stage,j,b)
    return dict(host_oracle_accepted=True,guest_qualification=False,
                captured_pixel_bytes=len(clear)+len(draw),source_bytes=len(before)+len(after),
                excluded='X byte, pitch padding; declared edge and texel bands are sets')
