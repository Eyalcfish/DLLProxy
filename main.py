import pefile
import syntax

dll_name = "tiny.dll"


pe = pefile.PE("tiny.dll")

functionNames = []

if hasattr(pe, "DIRECTORY_ENTRY_EXPORT"):
    for x in pe.DIRECTORY_ENTRY_EXPORT.symbols:
        functionNames += [x.name.decode("utf-8")]

c_name = dll_name[0:dll_name.find('.')]
c_name += ".c"

print(syntax.createPrefix(functionNames))
for name in functionNames:
    print(syntax.createPreFunction(name))
    print(syntax.createPostFunction(name))
for name in functionNames:
    print(syntax.createProxyFunction(name))
print(syntax.createDLLMAIN(functionNames))

# with open(c_name, "w", encoding="utf-8") as file:
#     for name in functionNames:
#         file.write(name)
