#ifndef XWN343_REPORT_PATH_H
#define XWN343_REPORT_PATH_H
#include <stddef.h>
#include <string.h>
/* Exact native launch namespace. Length-counted input; output untouched on refusal. */
static int xwn343_report_path(const char *image,size_t n,char *out,size_t cap) {
    const char prefix[]="\\Device\\Harddisk0\\Partition1\\Applications\\XWNEPci";
    const char suffix[]="\\default.xbe";
    const char report[]="\\pci.txt";
    size_t start=sizeof(prefix)-1,folder=start+8;
    if(!image||!out||n!=folder+sizeof(suffix)-1||cap<folder+sizeof(report))return 0;
    if(memcmp(image,prefix,start)||memcmp(image+folder,suffix,sizeof(suffix)-1))return 0;
    for(size_t i=start;i<folder;i++)if(!((image[i]>='0'&&image[i]<='9')||(image[i]>='a'&&image[i]<='f')))return 0;
    memcpy(out,image,folder);memcpy(out+folder,report,sizeof(report));return 1;
}
#endif
