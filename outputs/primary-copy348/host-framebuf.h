/* Host ABI/ownership models only. No kernel/GL/device authority. */
#include <stdint.h>
#include <string.h>
#include <stddef.h>
typedef uint32_t ULONG;typedef int32_t LONG;typedef uint64_t ULONGLONG;
typedef struct {LONG left,top,right,bottom;} RECTL;
typedef struct {LONG x,y;} POINTL;
typedef struct {LONG cx,cy;} SIZEL;
typedef struct {ULONG flXlate;} XLATEOBJ;
typedef struct {ULONG iDComplexity;RECTL rclBounds;} CLIPOBJ;
typedef struct {void *owner;ULONG iType,iBitmapFormat,fjBitmap,cjBits;void *pvBits,*pvScan0,*hsurf,*hdev;LONG lDelta;SIZEL sizlBitmap;} SURFOBJ;
typedef struct {int ShadowActive;ULONG BitsPerPixel,ScreenWidth,ScreenHeight,ScreenDelta;SURFOBJ *ShadowObject;void *ShadowBits,*ShadowSurface,*hDevEng;} PDEV,*PPDEV;
#define STYPE_BITMAP 0
#define BMF_32BPP 6
#define BMF_NOTSYSMEM 0x80
#define XO_TRIVIAL 1
#define DC_TRIVIAL 0
#define DC_RECT 1
#define DC_COMPLEX 3
static PPDEV XwnOwner(SURFOBJ *s){return s?s->owner:NULL;}
