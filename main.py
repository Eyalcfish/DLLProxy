import pefile
import syntax

dll_name = "tiny.dll"


pe = pefile.PE(dll_name)

functionNames = []

if hasattr(pe, "DIRECTORY_ENTRY_EXPORT"):
    for x in pe.DIRECTORY_ENTRY_EXPORT.symbols:
        functionNames += [x.name.decode("utf-8")]

c_name = dll_name[0:dll_name.find('.')]
c_name += ".c"

total = ""

total += syntax.createPrefix(functionNames)
for name in functionNames:
    total += syntax.createPreFunction(name)
    total += syntax.createPostFunction(name)
for name in functionNames:
    total += syntax.createProxyFunction(name)
total += syntax.createDLLMAIN(functionNames)

with open(c_name, "w", encoding="utf-8") as file:
    file.write(total)
