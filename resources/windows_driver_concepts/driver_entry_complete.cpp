// Complete Driver Entry Point - Anti-Ransomware Minifilter
// Integrates all components: registration, callbacks, process verification, shared memory

#include <fltKernel.h>

// Forward declarations
NTSTATUS InitSharedMemory(_In_ PDRIVER_OBJECT DriverObject);
VOID CleanupSharedMemory();
VOID NotifyUserMode(_In_ PUNICODE_STRING path, _In_opt_ const CHAR* procName, _In_ ULONG pid);
BOOLEAN IsProcessAllowed(PEPROCESS process);

// Altitude for FSFilter Activity Monitor
#define FILTER_ALTITUDE L"371000"

// Global filter handle
PFLT_FILTER gFilterHandle = nullptr;

// Pre-operation callback for CREATE
FLT_PREOP_CALLBACK_STATUS PreCreateCallback(
    PFLT_CALLBACK_DATA Data,
    PCFLT_RELATED_OBJECTS FltObjects,
    PVOID* CompletionContext
) {
    UNREFERENCED_PARAMETER(FltObjects);
    UNREFERENCED_PARAMETER(CompletionContext);
    
    // Skip paging I/O
    if (FlagOn(Data->Iopb->IrpFlags, IRP_PAGING_IO)) {
        return FLT_PREOP_SUCCESS_NO_CALLBACK;
    }
    
    // Get file name
    PFLT_FILE_NAME_INFORMATION nameInfo = nullptr;
    NTSTATUS status = FltGetFileNameInformation(
        Data,
        FLT_FILE_NAME_NORMALIZED | FLT_FILE_NAME_QUERY_DEFAULT,
        &nameInfo
    );
    
    if (!NT_SUCCESS(status) || !nameInfo) {
        if (nameInfo) FltReleaseFileNameInformation(nameInfo);
        return FLT_PREOP_SUCCESS_NO_CALLBACK;
    }
    
    status = FltParseFileNameInformation(nameInfo);
    if (!NT_SUCCESS(status)) {
        FltReleaseFileNameInformation(nameInfo);
        return FLT_PREOP_SUCCESS_NO_CALLBACK;
    }
    
    // Check if path is protected (implement your logic here)
    // For now, protect anything in C:\Protected\
    UNICODE_STRING protectedPath;
    RtlInitUnicodeString(&protectedPath, L"\\Device\\HarddiskVolume");
    
    // Get current process
    PEPROCESS currentProcess = PsGetCurrentProcess();
    ULONG pid = HandleToULong(PsGetCurrentProcessId());
    
    // Check if process is allowed
    if (!IsProcessAllowed(currentProcess)) {
        // Get process name
        CHAR procName[256] = {0};
        const CHAR* imageName = PsGetProcessImageFileName(currentProcess);
        if (imageName) {
            RtlStringCbCopyA(procName, sizeof(procName), imageName);
        }
        
        // Notify user-mode
        NotifyUserMode(&nameInfo->Name, procName, pid);
        
        // Block operation
        DbgPrint("[AntiRansomware] BLOCKED: %s (PID %lu) -> %wZ\n", 
            procName, pid, &nameInfo->Name);
        
        Data->IoStatus.Status = STATUS_ACCESS_DENIED;
        Data->IoStatus.Information = 0;
        FltReleaseFileNameInformation(nameInfo);
        return FLT_PREOP_COMPLETE;
    }
    
    FltReleaseFileNameInformation(nameInfo);
    return FLT_PREOP_SUCCESS_NO_CALLBACK;
}

// Pre-operation callback for WRITE
FLT_PREOP_CALLBACK_STATUS PreWriteCallback(
    PFLT_CALLBACK_DATA Data,
    PCFLT_RELATED_OBJECTS FltObjects,
    PVOID* CompletionContext
) {
    UNREFERENCED_PARAMETER(FltObjects);
    UNREFERENCED_PARAMETER(CompletionContext);
    
    // Skip paging I/O
    if (FlagOn(Data->Iopb->IrpFlags, IRP_PAGING_IO)) {
        return FLT_PREOP_SUCCESS_NO_CALLBACK;
    }
    
    // Get current process
    PEPROCESS currentProcess = PsGetCurrentProcess();
    
    // Check if process is allowed
    if (!IsProcessAllowed(currentProcess)) {
        // Block write operation
        Data->IoStatus.Status = STATUS_ACCESS_DENIED;
        Data->IoStatus.Information = 0;
        return FLT_PREOP_COMPLETE;
    }
    
    return FLT_PREOP_SUCCESS_NO_CALLBACK;
}

// Pre-operation callback for SET_INFORMATION
FLT_PREOP_CALLBACK_STATUS PreSetInfoCallback(
    PFLT_CALLBACK_DATA Data,
    PCFLT_RELATED_OBJECTS FltObjects,
    PVOID* CompletionContext
) {
    UNREFERENCED_PARAMETER(FltObjects);
    UNREFERENCED_PARAMETER(CompletionContext);
    
    FILE_INFORMATION_CLASS infoClass = Data->Iopb->Parameters.SetFileInformation.FileInformationClass;
    
    // Check for destructive operations
    if (infoClass == FileDispositionInformation ||
        infoClass == FileDispositionInformationEx ||
        infoClass == FileRenameInformation ||
        infoClass == FileRenameInformationEx) {
        
        PEPROCESS currentProcess = PsGetCurrentProcess();
        
        if (!IsProcessAllowed(currentProcess)) {
            // Block operation
            Data->IoStatus.Status = STATUS_ACCESS_DENIED;
            Data->IoStatus.Information = 0;
            return FLT_PREOP_COMPLETE;
        }
    }
    
    return FLT_PREOP_SUCCESS_NO_CALLBACK;
}

// Operation registration
FLT_OPERATION_REGISTRATION CallbacksArray[] = {
    { IRP_MJ_CREATE, 0, PreCreateCallback, nullptr },
    { IRP_MJ_WRITE, 0, PreWriteCallback, nullptr },
    { IRP_MJ_SET_INFORMATION, 0, PreSetInfoCallback, nullptr },
    { IRP_MJ_OPERATION_END }
};

// Instance setup callback
NTSTATUS InstanceSetup(
    PCFLT_RELATED_OBJECTS FltObjects,
    FLT_INSTANCE_SETUP_FLAGS Flags,
    DEVICE_TYPE VolumeDeviceType,
    FLT_FILESYSTEM_TYPE VolumeFilesystemType
) {
    UNREFERENCED_PARAMETER(FltObjects);
    UNREFERENCED_PARAMETER(Flags);
    UNREFERENCED_PARAMETER(VolumeDeviceType);
    
    // Only attach to NTFS volumes
    if (VolumeFilesystemType == FLT_FSTYPE_NTFS) {
        return STATUS_SUCCESS;
    }
    
    return STATUS_FLT_DO_NOT_ATTACH;
}

// Unload callback
NTSTATUS FilterUnload(FLT_FILTER_UNLOAD_FLAGS Flags) {
    UNREFERENCED_PARAMETER(Flags);
    
    CleanupSharedMemory();
    FltUnregisterFilter(gFilterHandle);
    
    DbgPrint("[AntiRansomware] Driver unloaded\n");
    return STATUS_SUCCESS;
}

// Filter registration structure
const FLT_REGISTRATION FilterRegistration = {
    sizeof(FLT_REGISTRATION),           // Size
    FLT_REGISTRATION_VERSION,           // Version
    0,                                  // Flags
    nullptr,                            // Context
    CallbacksArray,                     // Operation callbacks
    FilterUnload,                       // Unload callback
    InstanceSetup,                      // Instance setup
    nullptr,                            // Instance query callback
    nullptr,                            // Instance teardown start
    nullptr,                            // Instance teardown complete
    nullptr,                            // Generate file name
    nullptr,                            // Normalize name component
    nullptr                             // Normalize context cleanup
};

// Driver entry point
NTSTATUS DriverEntry(
    PDRIVER_OBJECT DriverObject,
    PUNICODE_STRING RegistryPath
) {
    UNREFERENCED_PARAMETER(RegistryPath);
    NTSTATUS status;
    
    DbgPrint("[AntiRansomware] Driver loading...\n");
    
    // Initialize shared memory communication
    status = InitSharedMemory(DriverObject);
    if (!NT_SUCCESS(status)) {
        DbgPrint("[AntiRansomware] Failed to initialize shared memory: 0x%08X\n", status);
        return status;
    }
    
    // Register minifilter
    status = FltRegisterFilter(DriverObject, &FilterRegistration, &gFilterHandle);
    if (!NT_SUCCESS(status)) {
        DbgPrint("[AntiRansomware] Failed to register filter: 0x%08X\n", status);
        CleanupSharedMemory();
        return status;
    }
    
    // Start filtering
    status = FltStartFiltering(gFilterHandle);
    if (!NT_SUCCESS(status)) {
        DbgPrint("[AntiRansomware] Failed to start filtering: 0x%08X\n", status);
        FltUnregisterFilter(gFilterHandle);
        CleanupSharedMemory();
        return status;
    }
    
    DbgPrint("[AntiRansomware] Driver loaded successfully\n");
    return STATUS_SUCCESS;
}
