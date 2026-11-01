def createPrefix(functionNames):
    final = ""
    includes = f"#include <windows.h>\n\n"
    variables = ""
    for name in functionNames:
        variables += f"void* {name}_addr = (void*)0;\n"
    final += includes
    final += variables
    return final

def createFunction(functionName):
    return f"""void"""

def createProxyFunction(functionName):
    return f"""void {functionName}() {{
    saveRegisters();
    {functionName}_Pre();
    loadRegisters();
    {functionName}_addr();
    saveRegisters();
    {functionName}_Post();
    loadRegisters();

}}\n"""

def createPreFunction(functionName):
    return f"""void inline {functionName}_Pre() {{
    // Fill code in here!
}}\n"""

def createPostFunction(functionName):
    return f"""void inline {functionName}_Post() {{
    // Fill code in here!
}}\n"""

def createDLLMAIN(functionNames):
    loads = ""
    for name in functionNames:
        loads += f'{name}_addr = GetProcAddress(ourDLL, "{name}");\n'
    return f"""BOOL WINAPI DllMain(
    HINSTANCE hinstDLL,  // Handle to the DLL module
    DWORD     fdwReason, // Reason for calling function
    LPVOID    lpReserved // Reserved
) {{
    if (fdwReason == DLL_PROCESS_ATTACH) {{
        HMODULE ourDLL = LoadLibraryA("tiny.dll"):
        {loads}
    }}
    return TRUE;
}}\n"""
