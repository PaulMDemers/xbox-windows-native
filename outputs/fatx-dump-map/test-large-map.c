/* Additional discriminator: this fixture's pagefile starts beyond 128 GiB. */
#define main prior_test_main
#include "test-map.c"
#undef main
int main(void){
 EXT e={{65536,512,128,10000,270000000,271280000},1};FCB f={0};f.Flags=FCB_IS_PAGE_FILE;f.RFCB.FileSize=large(3*65536);f.entry=20;
 ChainCount=3;Chain[0]=20;Chain[1]=21;Chain[2]=40;
 assert(VfatBuildPagingMap(&e,&f)==0);
 mapping(f.PagingMap,&e.FatInfo,65536);mapping(f.PagingMap,&e.FatInfo,2*65536+512);mapping(f.PagingMap,&e.FatInfo,3*65536);
 PLARGE_INTEGER p=NULL;assert(VfatMakeDumpMapping(f.PagingMap,&e.FatInfo,large(65536),&p)==0);
 assert(p[1].QuadPart==138241179648LL && p[1].QuadPart>0x2000000000LL);ExFreePool(p);++Checks;
 FATINFO bad={MAXULONG,MAXULONG,1,3,0,MAXULONG};expected_error(f.PagingMap,&bad,MAXULONG,STATUS_INVALID_PARAMETER);
 clean(&f);printf("large_offset_checks=%u leaks=%d\n",Checks,Live);return 0;
}
