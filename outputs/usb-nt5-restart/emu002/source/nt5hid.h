/* SPDX-License-Identifier: MIT
 * Narrow documented WDM HID minidriver ABI. See DESIGN.md for header defect.
 */
#ifndef XWN_NT5_HID_H
#define XWN_NT5_HID_H
#include <ntifs.h>
typedef struct {
    ULONG Revision;
    PDRIVER_OBJECT DriverObject;
    PUNICODE_STRING RegistryPath;
    ULONG DeviceExtensionSize;
    BOOLEAN DevicesArePolled;
    UCHAR Reserved[3];
} XWN_HID_REGISTRATION;
typedef struct {
    PDEVICE_OBJECT PhysicalDeviceObject, NextDeviceObject;
    PVOID MiniDeviceExtension;
} XWN_HID_EXTENSION;
typedef struct {
    ULONG Size;
    USHORT VendorID, ProductID, VersionNumber, Reserved[11];
} XWN_HID_ATTRIBUTES;
NTSTATUS NTAPI HidRegisterMinidriver(XWN_HID_REGISTRATION *registration);
#define XWN_HID_CTL(n) CTL_CODE(FILE_DEVICE_KEYBOARD,(n),METHOD_NEITHER,FILE_ANY_ACCESS)
#define XWN_HID_DESCRIPTOR XWN_HID_CTL(0)
#define XWN_HID_REPORT_DESCRIPTOR XWN_HID_CTL(1)
#define XWN_HID_READ XWN_HID_CTL(2)
#define XWN_HID_ATTRIBUTES_CTL XWN_HID_CTL(9)
typedef char xwn_hid_registration_size[(sizeof(XWN_HID_REGISTRATION)==20)?1:-1];
typedef char xwn_hid_extension_size[(sizeof(XWN_HID_EXTENSION)==12)?1:-1];
typedef char xwn_hid_attributes_size[(sizeof(XWN_HID_ATTRIBUTES)==32)?1:-1];
#endif
