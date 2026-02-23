// Shared Memory Communication Pattern from NoMoreStealer
// Kernel-to-User-Mode communication for event notifications

#include <fltKernel.h>

#define SECTION_NAME L"\\BaseNamedObjects\\AntiRansomwareNotify"
#define SHARED_MEMORY_SIZE PAGE_SIZE  // 4096 bytes

// Shared memory structure
typedef struct _NOTIFICATION_DATA {
    ULONG ProcessId;
    ULONG PathLength;
    CHAR ProcessName[64];
    ULONG Ready;  // Flag: 0 = no data, 1 = data ready
    WCHAR FilePath[512];
} NOTIFICATION_DATA, *PNOTIFICATION_DATA;

// Global variables
static HANDLE gSectionHandle = nullptr;
static PVOID gSharedMemory = nullptr;
static KSPIN_LOCK gNotifyLock;

// Initialize shared memory section
NTSTATUS InitializeSharedMemory() {
    NTSTATUS status;
    UNICODE_STRING sectionName;
    OBJECT_ATTRIBUTES objAttr;
    LARGE_INTEGER maxSize;
    
    RtlInitUnicodeString(&sectionName, SECTION_NAME);
    maxSize.QuadPart = SHARED_MEMORY_SIZE;
    
    InitializeObjectAttributes(
        &objAttr,
        &sectionName,
        OBJ_KERNEL_HANDLE,
        nullptr,
        nullptr
    );
    
    // Create section
    status = ZwCreateSection(
        &gSectionHandle,
        SECTION_ALL_ACCESS,
        &objAttr,
        &maxSize,
        PAGE_READWRITE,
        SEC_COMMIT,
        nullptr
    );
    
    if (!NT_SUCCESS(status)) {
        return status;
    }
    
    // Map section into kernel space
    SIZE_T viewSize = SHARED_MEMORY_SIZE;
    status = ZwMapViewOfSection(
        gSectionHandle,
        ZwCurrentProcess(),
        &gSharedMemory,
        0,
        SHARED_MEMORY_SIZE,
        nullptr,
        &viewSize,
        ViewUnmap,
        0,
        PAGE_READWRITE
    );
    
    if (!NT_SUCCESS(status)) {
        ZwClose(gSectionHandle);
        gSectionHandle = nullptr;
        return status;
    }
    
    // Initialize memory
    RtlZeroMemory(gSharedMemory, SHARED_MEMORY_SIZE);
    
    // Initialize spinlock
    KeInitializeSpinLock(&gNotifyLock);
    
    return STATUS_SUCCESS;
}

// Cleanup shared memory
void CleanupSharedMemory() {
    if (gSharedMemory) {
        ZwUnmapViewOfSection(ZwCurrentProcess(), gSharedMemory);
        gSharedMemory = nullptr;
    }
    
    if (gSectionHandle) {
        ZwClose(gSectionHandle);
        gSectionHandle = nullptr;
    }
}

// Notify user-mode about blocked operation
void NotifyUserMode(PUNICODE_STRING filePath, const CHAR* processName, ULONG pid) {
    if (!gSharedMemory) return;
    
    KIRQL oldIrql;
    KeAcquireSpinLock(&gNotifyLock, &oldIrql);
    
    PNOTIFICATION_DATA data = (PNOTIFICATION_DATA)gSharedMemory;
    
    // Wait if previous notification not consumed
    if (data->Ready == 1) {
        KeReleaseSpinLock(&gNotifyLock, oldIrql);
        return;
    }
    
    // Fill notification data
    data->ProcessId = pid;
    
    if (processName) {
        RtlStringCbCopyA(data->ProcessName, sizeof(data->ProcessName), processName);
    }
    
    if (filePath && filePath->Buffer && filePath->Length > 0) {
        ULONG copyLen = min(filePath->Length / sizeof(WCHAR), 511);
        RtlCopyMemory(data->FilePath, filePath->Buffer, copyLen * sizeof(WCHAR));
        data->FilePath[copyLen] = L'\0';
        data->PathLength = copyLen;
    }
    
    // Set ready flag (user-mode polls this)
    data->Ready = 1;
    
    KeReleaseSpinLock(&gNotifyLock, oldIrql);
}

// Usage in driver
FLT_PREOP_CALLBACK_STATUS PreOperationWithNotification(
    PFLT_CALLBACK_DATA Data,
    PCFLT_RELATED_OBJECTS FltObjects,
    PVOID* CompletionContext
) {
    UNREFERENCED_PARAMETER(FltObjects);
    UNREFERENCED_PARAMETER(CompletionContext);
    
    PFLT_FILE_NAME_INFORMATION nameInfo = nullptr;
    NTSTATUS status = FltGetFileNameInformation(
        Data,
        FLT_FILE_NAME_NORMALIZED | FLT_FILE_NAME_QUERY_DEFAULT,
        &nameInfo
    );
    
    if (!NT_SUCCESS(status)) {
        return FLT_PREOP_SUCCESS_NO_CALLBACK;
    }
    
    PEPROCESS process = PsGetCurrentProcess();
    ULONG pid = HandleToULong(PsGetCurrentProcessId());
    
    CHAR procName[256] = {0};
    GetProcessName(process, procName, sizeof(procName));
    
    // Notify user-mode
    NotifyUserMode(&nameInfo->Name, procName, pid);
    
    FltReleaseFileNameInformation(nameInfo);
    
    // Block operation
    Data->IoStatus.Status = STATUS_ACCESS_DENIED;
    Data->IoStatus.Information = 0;
    return FLT_PREOP_COMPLETE;
}

/*
 * USER-MODE SIDE (Python/Go example):
 * 
 * 1. Open section:
 *    handle = OpenFileMapping(FILE_MAP_READ, False, "AntiRansomwareNotify")
 * 
 * 2. Map view:
 *    ptr = MapViewOfFile(handle, FILE_MAP_READ, 0, 0, 4096)
 * 
 * 3. Poll for events:
 *    while True:
 *        ready = read_uint32(ptr + offset_ready)
 *        if ready == 1:
 *            pid = read_uint32(ptr + 0)
 *            path_len = read_uint32(ptr + 4)
 *            proc_name = read_string(ptr + 8, 64)
 *            file_path = read_wstring(ptr + 76, path_len)
 *            
 *            # Process event
 *            print(f"Blocked: {proc_name} (PID {pid}) -> {file_path}")
 *            
 *            # Reset ready flag
 *            write_uint32(ptr + offset_ready, 0)
 *        
 *        time.sleep(0.1)
 */
