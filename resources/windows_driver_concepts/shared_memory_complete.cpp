// Complete Shared Memory Communication Implementation from NoMoreStealer
// Full production-ready code for kernel-to-user-mode communication

#include <fltKernel.h>

#define NMS_SECTION_NAME L"\\BaseNamedObjects\\AntiRansomwareNotify"
#define POOL_TAG_COMM 'mmoC'

#pragma pack(push, 1)
struct NotifyData {
    ULONG pid;
    ULONG pathLen;
    CHAR procName[64];
    ULONG ready;  // Flag: 0 = no data, 1 = data ready
    // WCHAR path[] follows dynamically
};
#pragma pack(pop)

typedef struct _NOTIFY_WORK_ITEM {
    PIO_WORKITEM WorkItem;
    ULONG Pid;
    CHAR ProcName[64];
    UNICODE_STRING Path;
} NOTIFY_WORK_ITEM, *PNOTIFY_WORK_ITEM;

// Global variables
static HANDLE g_sectionHandle = nullptr;
static PVOID g_sectionBase = nullptr;
static NotifyData* g_notifyData = nullptr;
static KSPIN_LOCK g_commLock;
static volatile LONG g_activeWorkItems = 0;
static volatile BOOLEAN g_shutdownRequested = FALSE;
static PDEVICE_OBJECT g_workItemDeviceObject = nullptr;

// Work item routine - runs at PASSIVE_LEVEL
VOID NotifyWorkRoutine(_In_ PDEVICE_OBJECT DeviceObject, _In_opt_ PVOID Context) {
    UNREFERENCED_PARAMETER(DeviceObject);
    
    PNOTIFY_WORK_ITEM workItem = (PNOTIFY_WORK_ITEM)Context;
    if (!workItem) return;
    
    KIRQL oldIrql;
    KeAcquireSpinLock(&g_commLock, &oldIrql);
    
    if (g_notifyData && !g_shutdownRequested) {
        g_notifyData->pid = workItem->Pid;
        
        // Calculate available space for path
        ULONG maxPathBytes = PAGE_SIZE - sizeof(NotifyData);
        ULONG pathBytes = workItem->Path.Length;
        if (pathBytes > maxPathBytes) {
            pathBytes = maxPathBytes;
            pathBytes = (pathBytes / sizeof(WCHAR)) * sizeof(WCHAR);
        }
        
        // Copy path data
        PWCHAR pathDst = (PWCHAR)((PUCHAR)g_notifyData + sizeof(NotifyData));
        RtlZeroMemory(pathDst, maxPathBytes);
        if (pathBytes > 0 && workItem->Path.Buffer) {
            RtlCopyMemory(pathDst, workItem->Path.Buffer, pathBytes);
        }
        
        g_notifyData->pathLen = pathBytes;
        
        // Copy process name
        RtlZeroMemory(g_notifyData->procName, sizeof(g_notifyData->procName));
        SIZE_T procNameLen = sizeof(workItem->ProcName) < (sizeof(g_notifyData->procName) - 1) 
            ? sizeof(workItem->ProcName) 
            : (sizeof(g_notifyData->procName) - 1);
        
        if (procNameLen > 0) {
            ULONG copyLen = 0;
            while (copyLen < procNameLen - 1 && workItem->ProcName[copyLen] != '\0') {
                g_notifyData->procName[copyLen] = workItem->ProcName[copyLen];
                copyLen++;
            }
            g_notifyData->procName[copyLen] = '\0';
        }
        
        // Memory barrier before setting ready flag
        KeMemoryBarrier();
        *(volatile ULONG*)&g_notifyData->ready = 1;
    }
    
    KeReleaseSpinLock(&g_commLock, oldIrql);
    
    // Cleanup
    InterlockedDecrement(&g_activeWorkItems);
    if (workItem->Path.Buffer) {
        ExFreePoolWithTag(workItem->Path.Buffer, POOL_TAG_COMM);
    }
    if (workItem->WorkItem) {
        IoFreeWorkItem(workItem->WorkItem);
    }
    ExFreePoolWithTag(workItem, POOL_TAG_COMM);
}

// Initialize shared memory communication
NTSTATUS InitSharedMemory(_In_ PDRIVER_OBJECT DriverObject) {
    if (!DriverObject) {
        return STATUS_INVALID_PARAMETER;
    }
    
    KeInitializeSpinLock(&g_commLock);
    g_activeWorkItems = 0;
    g_shutdownRequested = FALSE;
    
    // Create security descriptor (allow SYSTEM and Administrators)
    UCHAR systemSidBuffer[SECURITY_MAX_SID_SIZE];
    UCHAR adminSidBuffer[SECURITY_MAX_SID_SIZE];
    PSID systemSid = (PSID)systemSidBuffer;
    PSID adminSid = (PSID)adminSidBuffer;
    
    // Initialize SYSTEM SID (S-1-5-18)
    SID_IDENTIFIER_AUTHORITY ntAuthority = SECURITY_NT_AUTHORITY;
    RtlInitializeSid(systemSid, &ntAuthority, 1);
    *(RtlSubAuthoritySid(systemSid, 0)) = SECURITY_LOCAL_SYSTEM_RID;
    
    // Initialize Administrators SID (S-1-5-32-544)
    RtlInitializeSid(adminSid, &ntAuthority, 2);
    *(RtlSubAuthoritySid(adminSid, 0)) = SECURITY_BUILTIN_DOMAIN_RID;
    *(RtlSubAuthoritySid(adminSid, 1)) = DOMAIN_ALIAS_RID_ADMINS;
    
    // Calculate DACL size
    ULONG systemSidLen = RtlLengthSid(systemSid);
    ULONG adminSidLen = RtlLengthSid(adminSid);
    ULONG daclSize = sizeof(ACL) +
        (sizeof(ACE_HEADER) + sizeof(ACCESS_MASK) + systemSidLen) +
        (sizeof(ACE_HEADER) + sizeof(ACCESS_MASK) + adminSidLen);
    
    PACL dacl = (PACL)ExAllocatePool2(POOL_FLAG_NON_PAGED, daclSize, POOL_TAG_COMM);
    if (!dacl) {
        return STATUS_INSUFFICIENT_RESOURCES;
    }
    
    NTSTATUS status = RtlCreateAcl(dacl, daclSize, ACL_REVISION);
    if (!NT_SUCCESS(status)) {
        ExFreePoolWithTag(dacl, POOL_TAG_COMM);
        return status;
    }
    
    // Add SYSTEM access
    status = RtlAddAccessAllowedAce(dacl, ACL_REVISION,
        SECTION_MAP_READ | SECTION_MAP_WRITE | SECTION_QUERY, systemSid);
    if (!NT_SUCCESS(status)) {
        ExFreePoolWithTag(dacl, POOL_TAG_COMM);
        return status;
    }
    
    // Add Administrators access
    status = RtlAddAccessAllowedAce(dacl, ACL_REVISION,
        SECTION_MAP_READ | SECTION_MAP_WRITE | SECTION_QUERY, adminSid);
    if (!NT_SUCCESS(status)) {
        ExFreePoolWithTag(dacl, POOL_TAG_COMM);
        return status;
    }
    
    // Create security descriptor
    SECURITY_DESCRIPTOR* sd = (SECURITY_DESCRIPTOR*)ExAllocatePool2(
        POOL_FLAG_NON_PAGED, SECURITY_DESCRIPTOR_MIN_LENGTH, POOL_TAG_COMM);
    if (!sd) {
        ExFreePoolWithTag(dacl, POOL_TAG_COMM);
        return STATUS_INSUFFICIENT_RESOURCES;
    }
    
    status = RtlCreateSecurityDescriptor(sd, SECURITY_DESCRIPTOR_REVISION);
    if (!NT_SUCCESS(status)) {
        ExFreePoolWithTag(sd, POOL_TAG_COMM);
        ExFreePoolWithTag(dacl, POOL_TAG_COMM);
        return status;
    }
    
    status = RtlSetDaclSecurityDescriptor(sd, TRUE, dacl, FALSE);
    if (!NT_SUCCESS(status)) {
        ExFreePoolWithTag(sd, POOL_TAG_COMM);
        ExFreePoolWithTag(dacl, POOL_TAG_COMM);
        return status;
    }
    
    // Create section
    UNICODE_STRING sectionName;
    RtlInitUnicodeString(&sectionName, NMS_SECTION_NAME);
    
    OBJECT_ATTRIBUTES oa;
    InitializeObjectAttributes(&oa, &sectionName, OBJ_CASE_INSENSITIVE, nullptr, sd);
    
    LARGE_INTEGER maxSize;
    maxSize.QuadPart = PAGE_SIZE;
    
    status = ZwCreateSection(
        &g_sectionHandle,
        SECTION_MAP_READ | SECTION_MAP_WRITE | SECTION_QUERY,
        &oa,
        &maxSize,
        PAGE_READWRITE,
        SEC_COMMIT,
        nullptr
    );
    
    ExFreePoolWithTag(sd, POOL_TAG_COMM);
    ExFreePoolWithTag(dacl, POOL_TAG_COMM);
    
    if (!NT_SUCCESS(status)) {
        DbgPrint("[AntiRansomware] Failed to create section: 0x%08X\n", status);
        return status;
    }
    
    // Map section into kernel space
    SIZE_T viewSize = PAGE_SIZE;
    status = ZwMapViewOfSection(
        g_sectionHandle,
        ZwCurrentProcess(),
        &g_sectionBase,
        0,
        0,
        nullptr,
        &viewSize,
        ViewUnmap,
        0,
        PAGE_READWRITE
    );
    
    if (!NT_SUCCESS(status)) {
        ZwClose(g_sectionHandle);
        g_sectionHandle = nullptr;
        DbgPrint("[AntiRansomware] Failed to map section: 0x%08X\n", status);
        return status;
    }
    
    g_notifyData = (NotifyData*)g_sectionBase;
    RtlZeroMemory(g_notifyData, sizeof(NotifyData));
    
    // Create device for work items
    UNICODE_STRING deviceName;
    RtlInitUnicodeString(&deviceName, L"\\Device\\AntiRansomwareWorkItem");
    
    status = IoCreateDevice(
        DriverObject,
        0,
        &deviceName,
        FILE_DEVICE_UNKNOWN,
        FILE_DEVICE_SECURE_OPEN,
        FALSE,
        &g_workItemDeviceObject
    );
    
    if (!NT_SUCCESS(status)) {
        DbgPrint("[AntiRansomware] Failed to create work item device: 0x%08X\n", status);
        g_workItemDeviceObject = nullptr;
    } else {
        g_workItemDeviceObject->Flags |= DO_DIRECT_IO;
        g_workItemDeviceObject->Flags &= ~DO_DEVICE_INITIALIZING;
    }
    
    DbgPrint("[AntiRansomware] Shared memory initialized at %p\n", g_sectionBase);
    return STATUS_SUCCESS;
}

// Cleanup shared memory
VOID CleanupSharedMemory() {
    KIRQL oldIrql;
    LARGE_INTEGER interval;
    
    g_shutdownRequested = TRUE;
    
    // Wait for active work items (max 10 seconds)
    interval.QuadPart = -10000000LL;  // 1 second
    ULONG maxWaitIterations = 10;
    ULONG waitIteration = 0;
    
    while (g_activeWorkItems > 0 && waitIteration < maxWaitIterations) {
        KeDelayExecutionThread(KernelMode, FALSE, &interval);
        waitIteration++;
    }
    
    KeAcquireSpinLock(&g_commLock, &oldIrql);
    
    if (g_sectionBase) {
        ZwUnmapViewOfSection(ZwCurrentProcess(), g_sectionBase);
        g_sectionBase = nullptr;
        g_notifyData = nullptr;
    }
    
    KeReleaseSpinLock(&g_commLock, oldIrql);
    
    if (g_sectionHandle) {
        ZwClose(g_sectionHandle);
        g_sectionHandle = nullptr;
    }
    
    if (g_workItemDeviceObject) {
        IoDeleteDevice(g_workItemDeviceObject);
        g_workItemDeviceObject = nullptr;
    }
}

// Notify user-mode about blocked operation
VOID NotifyUserMode(_In_ PUNICODE_STRING path, _In_opt_ const CHAR* procName, _In_ ULONG pid) {
    if (!path || !path->Buffer || path->Length == 0) return;
    if (g_shutdownRequested) return;
    
    // Allocate work item
    PNOTIFY_WORK_ITEM workItem = (PNOTIFY_WORK_ITEM)ExAllocatePool2(
        POOL_FLAG_NON_PAGED, sizeof(NOTIFY_WORK_ITEM), POOL_TAG_COMM);
    if (!workItem) return;
    
    RtlZeroMemory(workItem, sizeof(NOTIFY_WORK_ITEM));
    workItem->Pid = pid;
    
    // Copy process name
    if (procName) {
        ULONG copyLen = 0;
        while (copyLen < (sizeof(workItem->ProcName) - 1) && procName[copyLen] != '\0') {
            workItem->ProcName[copyLen] = procName[copyLen];
            copyLen++;
        }
        workItem->ProcName[copyLen] = '\0';
    }
    
    // Copy path
    workItem->Path.Length = path->Length;
    workItem->Path.MaximumLength = path->Length;
    workItem->Path.Buffer = (PWCHAR)ExAllocatePool2(
        POOL_FLAG_NON_PAGED, path->Length, POOL_TAG_COMM);
    
    if (!workItem->Path.Buffer) {
        ExFreePoolWithTag(workItem, POOL_TAG_COMM);
        return;
    }
    
    RtlCopyMemory(workItem->Path.Buffer, path->Buffer, path->Length);
    
    if (!g_workItemDeviceObject) {
        ExFreePoolWithTag(workItem->Path.Buffer, POOL_TAG_COMM);
        ExFreePoolWithTag(workItem, POOL_TAG_COMM);
        return;
    }
    
    // Allocate work item
    workItem->WorkItem = IoAllocateWorkItem(g_workItemDeviceObject);
    if (!workItem->WorkItem) {
        ExFreePoolWithTag(workItem->Path.Buffer, POOL_TAG_COMM);
        ExFreePoolWithTag(workItem, POOL_TAG_COMM);
        return;
    }
    
    InterlockedIncrement(&g_activeWorkItems);
    
    // Queue work item
    IoQueueWorkItem(
        workItem->WorkItem,
        NotifyWorkRoutine,
        DelayedWorkQueue,
        workItem
    );
}
