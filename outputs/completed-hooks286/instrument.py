"""Exact281 hook proposal; inverse transformation must recover original bytes."""
import re
def function(text,name):
 m=re.search(r'(?m)^(?:static )?(?:void|bool) '+name+r'\([^)]*\)\s*\{',text);assert m,name
 end=m.end();depth=1
 while depth:depth+=(text[end]=='{')-(text[end]=='}');end+=1
 return text[m.start():end]
def instrument(text):
 original=text;changes=[]
 def change(old,new,count=1):
  nonlocal text
  assert text.count(old)==count,(old,text.count(old));text=text.replace(old,new);changes.append((old,new,count))
 body=function(text,'texture_binding_destroy')
 changed=body.replace('    x269_destroying(binding);','    X286Saved completed286 = x286_before_destroy(binding);\n    x269_destroying(binding);')
 assert changed.endswith('\n}');changed=changed[:-2]+'\n    x286_after_destroy(completed286);\n}'
 change(body,changed)
 old='key_out->binding = generate_texture(state, texture_data, palette_data);'
 change(old,old+'\n            x286_created(i, key_out);')
 matches=re.findall(r'(?m)^([ \t]*)(x269_bound\(d,\s*i,\s*[^;]+;)',text);assert len(matches)==2,matches
 for indent,call in matches:
  args=call[len('x269_bound('):-2].split(',');binding=args[2].strip()
  change(indent+call,indent+call+'\n'+indent+'x286_bound(i, '+binding+');')
 # The private full-source proposal needs the adapter declarations at this site.
 anchor='static void texture_binding_destroy(gpointer data);'
 change(anchor,'#include "adapter.h"\n'+anchor)
 restored=text
 for old,new,count in reversed(changes):
  assert restored.count(new)==count;restored=restored.replace(new,old)
 assert restored==original
 return text,changes
