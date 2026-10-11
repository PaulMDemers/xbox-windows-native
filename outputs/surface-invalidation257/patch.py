"""Add bounded scalar telemetry to exact compiled247; no disposal policy change."""
from pathlib import Path
def apply(s):
 p=s/'hw/xbox/nv2a/pgraph/gl/surface.c';t=p.read_text()
 def once(old,new):
  nonlocal t
  assert t.count(old)==1,old[:100];t=t.replace(old,new)
 helper=Path(__file__).with_name('observation.c').read_text()
 once('static bool check_surface_overlaps_range(',helper+'\nstatic bool check_surface_overlaps_range(')
 once('        hwaddr offset = addr - surface->vram_addr;', '        trace_surface257(d, surface, write ? 12 : 11);\n        hwaddr offset = addr - surface->vram_addr;')
 once('            pgraph_gl_surface_download_if_dirty(d, other_surface);','            trace_surface257(d, other_surface, 1);\n            pgraph_gl_surface_download_if_dirty(d, other_surface);')
 once('            pgraph_gl_surface_download_if_dirty(d, s);','            trace_surface257(d, s, 2);\n            pgraph_gl_surface_download_if_dirty(d, s);')
 once('            pgraph_gl_surface_download_if_dirty(d, surface);','            trace_surface257(d, surface, 3);\n            pgraph_gl_surface_download_if_dirty(d, surface);')
 once('    /*244 Scalar observation survives the existing disposal, not a new owner. */','    trace_surface257(d, surface, 6);\n    /*244 Scalar observation survives the existing disposal, not a new owner. */')
 once('        /*247 Observation only: actual latest flags BEFORE natural invalidation.','        trace_surface257(d, s, 5);\n        /*247 Observation only: actual latest flags BEFORE natural invalidation.')
 # Incompatible replacement must be found by its actual adjacent source.
 once('                pgraph_gl_surface_download_if_dirty(d, found);','                trace_surface257(d, found, 4);\n                pgraph_gl_surface_download_if_dirty(d, found);')
 p.write_text(t)
