// FltGetFileNameInformation() Usage Pattern from NoMoreStealer
// Reference for getting file paths in kernel callbacks

#include <fltKernel.h>

FLT_PREOP_CALLBACK_STATUS GetFilePathExample(
    PFLT_CALLBACK_DATA Data,
    PCFLT_RELATED_OBJECTS FltObjects,
    PVOID* CompletionContext
) {
    UNREFERENCED_PARAMETER(FltObjects);
    UNREFERENCED_PARAMETER(CompletionContext);
    
    PFLT_FILE_NAME_INFORMATION nameInfo = nullptr;
    
    // Get normalized file name
    NTSTATUS status = FltGetFileNameInformation(
        Data,
        FLT_FILE_NAME_NORMALIZED | FLT_FILE_NAME_QUERY_DEFAULT,
        &nameInfo
    );
    
    if (!NT_SUCCESS(status) || !nameInfo) {
        if (nameInfo) FltReleaseFileNameInformation(nameInfo);
        return FLT_PREOP_SUCCESS_NO_CALLBACK;
    }
    
    // Parse the file name information
    status = FltParseFileNameInformation(nameInfo);
    if (!NT_SUCCESS(status)) {
        FltReleaseFileNameInformation(nameInfo);
        return FLT_PREOP_SUCCESS_NO_CALLBACK;
    }
    
    // Now you can access:
    // nameInfo->Name - Full path (e.g., \Device\HarddiskVolume2\Users\...)
    // nameInfo->Volume - Volume portion
    // nameInfo->Share - Share portion (for network paths)
    // nameInfo->ParentDir - Parent directory
    // nameInfo->FinalComponent - File name only
    
    DbgPrint("Full path: %wZ\n", &nameInfo->Name);
    DbgPrint("File name: %wZ\n", &nameInfo->FinalComponent);
    
    // Check if path contains protected directory
    UNICODE_STRING protectedPath;
    RtlInitUnicodeString(&protectedPath, L"\\Users\\");
    
    if (RtlPrefixUnicodeString(&protectedPath, &nameInfo->Name, TRUE)) {
        DbgPrint("Protected path accessed!\n");
    }
    
    // Always release when done
    FltReleaseFileNameInformation(nameInfo);
    
    return FLT_PREOP_SUCCESS_NO_CALLBACK;
}

// Path matching helper
BOOLEAN IsPathProtected(PUNICODE_STRING filePath, PUNICODE_STRING protectedPath) {
    if (!filePath || !protectedPath) return FALSE;
    
    // Case-insensitive prefix match
    return RtlPrefixUnicodeString(protectedPath, filePath, TRUE);
}

// Substring search in path
BOOLEAN PathContains(PUNICODE_STRING filePath, const WCHAR* substring) {
    if (!filePath || !substring) return FALSE;
    
    UNICODE_STRING searchString;
    RtlInitUnicodeString(&searchString, substring);
    
    // Convert both to uppercase for comparison
    UNICODE_STRING upperFile = {0};
    UNICODE_STRING upperSearch = {0};
    
    if (!NT_SUCCESS(RtlUpcaseUnicodeString(&upperFile, filePath, TRUE))) {
        return FALSE;
    }
    
    if (!NT_SUCCESS(RtlUpcaseUnicodeString(&upperSearch, &searchString, TRUE))) {
        RtlFreeUnicodeString(&upperFile);
        return FALSE;
    }
    
    BOOLEAN found = FALSE;
    ULONG fileLen = upperFile.Length / sizeof(WCHAR);
    ULONG searchLen = upperSearch.Length / sizeof(WCHAR);
    
    if (searchLen <= fileLen) {
        for (ULONG i = 0; i <= fileLen - searchLen; i++) {
            if (RtlCompareMemory(&upperFile.Buffer[i], upperSearch.Buffer, 
                upperSearch.Length) == upperSearch.Length) {
                found = TRUE;
                break;
            }
        }
    }
    
    RtlFreeUnicodeString(&upperFile);
    RtlFreeUnicodeString(&upperSearch);
    
    return found;
}
