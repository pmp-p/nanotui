import sys

def stringify(blob):
    c = 0
    for b in blob:
        yield chr(int(b) + 248)
        c += 1
        if c > 78:
            yield "\n"
            c = 0

html = sys.stdout

html.write('''
def fs_decode(fsname, o248):
    import os
    print("fs:", fsname)
    path = fsname.rsplit('/')
    for i in range(len(path)):
        try:
            os.mkdir('/'.join( path[0:i] ))
        except:
            pass
    with open(fsname, "wb") as fs:
        for input in o248.split("\\n"):
            if not input:
                continue
            fs.write(bytes([ord(c) - 248 for c in input]))

''')
#raise SystemExit

main = "main.py"
for arg in sys.argv:
    if arg.endswith('/pygpacker.py'):
        continue

#    if arg.endswith("/main.py"):
#        main = arg
#        continue

    html.write(f"\nfs_decode('{arg}','''\n")
    for text in stringify(open(arg, "rb").read()):
        html.write(text)
    html.write("''')\n")

#html.write(f"\n# {arg}\n")
#html.write( open(main,"r").read() )
html.write('execfile("main.py")')

