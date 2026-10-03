#include <assert.h>
#include <stdio.h>
#include "pci-policy.h"
int main(void) {
 unsigned count=0;
 for(unsigned bus=0;bus<256;++bus) for(unsigned dev=0;dev<32;++dev) for(unsigned fn=0;fn<8;++fn) {
  int allowed=pci_target_allowed(bus,dev,fn);
  assert(!(allowed && bus==0 && dev==0 && (fn==1 || fn==2)));
  assert(!(allowed && bus==1 && (dev!=0 || fn!=0)));
  if(allowed) ++count;
 }
 assert(count==12);
 for(unsigned i=0;i<sizeof(pci_targets)/sizeof(pci_targets[0]);++i) {
  assert(pci_target_allowed(pci_targets[i].bus,pci_targets[i].dev,pci_targets[i].fn));
  for(unsigned j=i+1;j<sizeof(pci_targets)/sizeof(pci_targets[0]);++j)
   assert(pci_targets[i].bus!=pci_targets[j].bus || pci_targets[i].dev!=pci_targets[j].dev || pci_targets[i].fn!=pci_targets[j].fn);
 }
 puts("{\"tested_bdf_combinations\":65536,\"allowed\":12,\"dangerous_host_functions_rejected\":true,\"gpu_aliases_rejected\":true,\"unique_targets\":true}");
 return 0;
}
