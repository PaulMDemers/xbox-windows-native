/* SPDX-License-Identifier: MIT: compile-only assertions against pinned headers. */
#define DIRECTDRAW_VERSION 0x0700
#define DIRECT3D_VERSION 0x0700
#include <windows.h>
#include <d3d.h>
#include <stddef.h>
#define CHECK(name,expr) typedef char name[(expr)?1:-1]
CHECK(size,sizeof(D3DDEVICEDESC7)==236);
CHECK(caps,offsetof(D3DDEVICEDESC7,dwDevCaps)==0);
CHECK(render,offsetof(D3DDEVICEDESC7,dwDeviceRenderBitDepth)==116);
CHECK(depth,offsetof(D3DDEVICEDESC7,dwDeviceZBufferBitDepth)==120);
CHECK(width,offsetof(D3DDEVICEDESC7,dwMaxTextureWidth)==132);
CHECK(height,offsetof(D3DDEVICEDESC7,dwMaxTextureHeight)==136);
CHECK(ops,offsetof(D3DDEVICEDESC7,dwTextureOpCaps)==180);
CHECK(stages,offsetof(D3DDEVICEDESC7,wMaxTextureBlendStages)==184);
CHECK(textures,offsetof(D3DDEVICEDESC7,wMaxSimultaneousTextures)==186);
CHECK(guid,offsetof(D3DDEVICEDESC7,deviceGUID)==196);
CHECK(rasterflag,D3DDEVCAPS_HWRASTERIZATION==0x80000);
CHECK(tnlflag,D3DDEVCAPS_HWTRANSFORMANDLIGHT==0x10000);
