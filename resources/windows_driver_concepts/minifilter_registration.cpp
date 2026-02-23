// Minifilter Registration Pattern from NoMoreStealer
// Reference for Month 4: Windows Driver Development

#include <fltKernel.h>

// Altitude: Determines filter position in driver stack
// Range 371000-379999: FSFilter Activity Monitor
// Higher altitude = runs earlier in the stack
#define FILTER_ALTITUDE L"371000"

// Operations to intercept
FLT_OPERATION_REGISTRATION CallbacksArray[] = {
    { IRP_MJ_CREATE, 0, PreCreateCallback, nullptr },
    { IRP_MJ_WRITE, 0, PreWriteCallback, nullptr },
    { IRP_MJ_SET_INFORMATION, 0, PreSetInfoCallback, nullptr },
    { IRP_MJ_OPERATION_END }
};

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

PFLT_FILTER gFilterHandle = nullptr;

// Driver entry point
NTSTATUS DriverEntry(PDRIVER_OBJECT DriverObject, PUNICODE_STRING RegistryPath) {
    NTSTATUS status;
    
    // Register minifilter
    status = FltRegisterFilter(DriverObject, &FilterRegistration, &gFilterHandle);
    if (!NT_SUCCESS(status)) {
        return status;
    }
    
    // Start filtering
    status = FltStartFiltering(gFilterHandle);
    if (!NT_SUCCESS(status)) {
        FltUnregisterFilter(gFilterHandle);
        return status;
    }
    
    return STATUS_SUCCESS;
}

// Unload callback
NTSTATUS FilterUnload(FLT_FILTER_UNLOAD_FLAGS Flags) {
    UNREFERENCED_PARAMETER(Flags);
    FltUnregisterFilter(gFilterHandle);
    return STATUS_SUCCESS;
}

// Instance setup - called when filter attaches to volume
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

// Pre-operation callbacks
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
    
    // Your logic here
    
    return FLT_PREOP_SUCCESS_NO_CALLBACK;
}

FLT_PREOP_CALLBACK_STATUS PreWriteCallback(
    PFLT_CALLBACK_DATA Data,
    PCFLT_RELATED_OBJECTS FltObjects,
    PVOID* CompletionContext
) {
    UNREFERENCED_PARAMETER(Data);
    UNREFERENCED_PARAMETER(FltObjects);
    UNREFERENCED_PARAMETER(CompletionContext);
    
    // Your write protection logic here
    
    return FLT_PREOP_SUCCESS_NO_CALLBACK;
}

FLT_PREOP_CALLBACK_STATUS PreSetInfoCallback(
    PFLT_CALLBACK_DATA Data,
    PCFLT_RELATED_OBJECTS FltObjects,
    PVOID* CompletionContext
) {
    UNREFERENCED_PARAMETER(Data);
    UNREFERENCED_PARAMETER(FltObjects);
    UNREFERENCED_PARAMETER(CompletionContext);
    
    // Your set information logic here (rename, delete)
    
    return FLT_PREOP_SUCCESS_NO_CALLBACK;
}
