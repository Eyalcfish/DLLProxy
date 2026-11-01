registers_x64 = [
    ("rax", 8),
    ("rcx", 8),
    ("rdx", 8),
    ("rbx", 8),
    ("rsi", 8),
    ("rdi", 8),
    ("rbp", 8),
    ("rsp", 8),
    ("r8",  8),
    ("r9",  8),
    ("r10", 8),
    ("r11", 8),
    ("r12", 8),
    ("r13", 8),
    ("r14", 8),
    ("r15", 8),

    ("rflags", 8),
]

registers_sse = [
    (f"xmm{i}", 16) for i in range(16)
]

register_rip = [
    ("rip", 8)
]

total_size = 0
for reg in registers_x64+registers_sse+register_rip: # We do not support avx/avx2/avx512 yet
    total_size += reg[1]

def createPrefix(functionNames):
    final = ""
    includes = f"#include <windows.h>\n\n"
    variables = ""
    variables += f"char reg_vals[{total_size}];\n\n"
    for name in functionNames:
        variables += f"void* {name}_addr = (void*)0;\n\n"
    final += includes
    final += variables
    return final

def createProxyFunction(functionName):
    load_registers = ""
    save_registers = ""
    i = 0
    for reg in registers_x64+registers_sse:
        cmd = "mov"
        if "xmm" in reg[0]:
            cmd = "movups"
        if "rflags" in reg[0]:
            save_registers += '         "pushfq\\n\\t"\n'
            save_registers += f'         "pop qword ptr [reg_vals+{i}]\\n\\t"\n'
            load_registers += f'         "push qword ptr [reg_vals+{i}]\\n\\t"\n'
            load_registers += '         "popfq\\n\\t"\n'
        else:
            save_registers += f'        "{cmd} [reg_vals+{i}], {reg[0]}\\n\\t"\n'
            load_registers += f'        "{cmd} {reg[0]}, [reg_vals+{i}]\\n\\t"\n'
        i += reg[1]
    return f"""
void __attribute__((naked)) {functionName}() {{
    __asm__ volatile (
        ".intel_syntax noprefix\\n\\t"
{save_registers}
        "sub rsp, 8\\n\\t"
        "call {functionName}_Pre\\n\\t"
        "add rsp, 8\\n\\t"
        "mov rax, [rsp]\\n\\t" // load rax to our ret rip(the original caller)
        "mov [reg_vals+{i}], rax\\n\\t" // save said rip
        "lea rax, [rip+after_call_{functionName}]\\n\\t" // get our current location
        "mov [rsp], rax\\n\\t"
{load_registers}
        "jmp [{functionName}_addr]\\n\\t"
        "after_call_{functionName}:\\n\\t"
{save_registers}
        "sub rsp, 8\\n\\t"
        "call {functionName}_Post\\n\\t"
        "add rsp, 8\\n\\t"
{load_registers}
        "jmp [reg_vals+{i}]\\n\\t"
        ".att_syntax prefix\\n\\t"
    );
}}\n"""

def createPreFunction(functionName):
    return f"""void {functionName}_Pre() {{
    // Fill code in here!
}}\n"""

def createPostFunction(functionName):
    return f"""void {functionName}_Post() {{
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
        HMODULE ourDLL = LoadLibraryA("tiny.dll");
        {loads}
    }}
    return TRUE;
}}\n"""
