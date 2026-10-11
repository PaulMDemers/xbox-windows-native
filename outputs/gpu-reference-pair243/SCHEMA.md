# Compiled242 paired inventory, used unchanged by243

Header version242/state/published and explicit cpu_callbacks_observed0,
gl_bindings_observed0,retired0,native_grant0. State follows sole preservation
owner; only worker terminal3/4/6 publishes slots. Timeout5 hides mutable slots.
Each slot has valid,PG when,FIFO when,surface count,texture count. Valid slots
contain FIFO14/context20 as in238 SCHEMA, surface12 as in238 SCHEMA, stats48,
texture rows10 and four current bindings4. No reset/new242 request exists.
Before FIFO sample precedes PG before; PG after precedes FIFO after. No claim
that all actors are simultaneously sampled. Record actual admission at each.

| Stats indices | Values |
| --- | --- |
|0..3| atomic FIFO halt, PG waits, PG pending interrupts, PG enabled interrupts |
|4..6| downloads pending, dirty downloads pending, shader writeback pending |
|7..12| framebuffer ID, display buffer ID,width,height,render/display contexts present |
|13..20| used/free counts for texture,shader,shader-module,element LRUs |
|21..25| current shader binding present/initialized program ID,inline-array buffer,memory buffer,vertex array |
|26..30| display framebuffer,VAO,VBO,program,overlay texture |
|31..34| surface-to-texture framebuffer,VAO,VBO,program |
|35..36| zpass query count,nonzero inline-buffer count |
|37| texture LRU walked nodes (max512) |
|38..42| active shader nodes,initialized shaders,program-buffer pointers present,save handles present,walked nodes (max51200) |
|43..44| active shader modules,walked nodes (max51200) |
|45..47| active elements,initialized elements,walked nodes (max51200) |

Texture row10: texture offset/length,palette offset/length,binding present,
modeled GL texture ID,refcount,possibly_dirty,GL target,node hash. Current
binding4: present,GL texture ID,refcount,GL target. Hash/IDs describe modeled
objects; they aren't independently queried GL identities or CPU work completion.
Only in-use nodes have their initialized payload inspected; free payloads are
not read. Traversal bounded by pinned cache capacities, active counts compared
with actual LRU num_used. Shader data sampled under TRY cache lock; no wait/join.

243 gates wait/pending/work indices1,2,4,5,6 at zero. Enabled index3 must match
actual pre-PG row field5, even whenFFFFFFFF.242 originally misclassified index3
as pending; that attempt remains failed. Updated host regression includes actual
nonzero enabled value and rejects changes. All strict event gates stay intact.
