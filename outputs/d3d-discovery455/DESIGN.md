# Next probe: installed Direct3D7 device discovery

This rung follows the qualified bounded lifecycle controls. The probe is now
implemented; build and runtime receipts record its validation state. It inventories the installed interface and
capabilities; it will not create a render device, replace a DLL, touch the primary
surface or claim GPU support from a capability bit.

Create a DirectDraw7 object separately for default and explicit HEL, using
DDSCL_NORMAL and an owned window. Query IID_IDirect3D7. Preserve the actual
HRESULT: E_NOINTERFACE means this interface is unavailable in that path, not a
successful rendering result. If available, call EnumDevices once and retain each
callback's complete D3DDEVICEDESC7, GUID, bounded name and description. Use a fixed
capacity and sticky error on overflow, invalid context, duplicate GUID or incomplete
strings. Never accept a partial inventory as complete. A successful empty inventory
means zero devices were returned; it must not become a fabricated software device.

Use explicit little-endian transport and a separate decoder. Confirm the actual
compiled structure layout rather than guessing offsets. Join decoded GUID/caps to
scalar records and reject changed bytes, duplicate/missing records, count/size
mismatches, unknown completion states and failed cleanup. Report rasterization and
transform/lighting flags as runtime declarations, separately from an actual draw.
Do not equate successful QueryInterface/EnumDevices with CreateDevice or rendering.

Pin the installed DirectDraw and imported NT5 DLLs and compiler/header closure.
Preserve source/binary/probe identities and compare fresh NT5 PC and physical
Xbox runs. Use the existing bounded controller, fresh output namespaces, normal
restart, cold readback, independent extraction and exact result mutations.
Keep the current720p baseline. If software RGB is available, the following rung
can attempt an owned offscreen target, clear and pretransformed triangle with
independent interior/background pixels. Hardware submission remains separate.

Primary references reviewed:

- [Microsoft DirectDraw API](https://learn.microsoft.com/en-us/windows/win32/api/_directdraw/)
  identifies DirectDrawCreateEx as the DirectX7 Direct3D entry path.
- [Microsoft SDK d3d.h](https://github.com/microsoft/win32metadata/blob/main/generation/WinSDK/RecompiledIdlHeaders/um/d3d.h)
  defines IDirect3D7 QueryInterface/EnumDevices/CreateDevice and callback types.
- [Microsoft legacy device capabilities](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/d3dhal/ns-d3dhal-_d3ddevicedesc_v1)
  describes the rasterization/transform flags and construction of application-level
  D3DDEVICEDESC7. These definitions are not evidence of this Xbox's capabilities.

The installed RosBE headers were also read. IID_IDirect3D7 is
f5049e77-4861-11d2-a407-00a0c90629a8; their D3DDEVICEDESC7 definition includes both
line and triangle caps, render/depth formats, texture/lighting limits, deviceGUID
and reserved fields. Freeze exact files in the eventual build receipt; this design
does not substitute for that pin or an actual runtime result.
