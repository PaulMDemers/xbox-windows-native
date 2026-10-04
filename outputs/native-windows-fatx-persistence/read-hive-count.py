"""Read only the persistence probe's known DWORD; never modify the hive."""
import sys,json
sys.path.insert(0,'/home/paul/xbox-windows-native/toolchains/offline-disk/root/usr/lib/python3/dist-packages')
import hivex
h=hivex.Hivex(sys.argv[1]);node=h.root()
for name in ['XWN','PersistenceProbe']:
 node=h.node_get_child(node,name);assert node
value=h.node_get_value(node,'Count');assert value
typ,data=h.value_value(value);assert typ==4 and len(data)==4
print(json.dumps({'count':h.value_dword(value)}))
