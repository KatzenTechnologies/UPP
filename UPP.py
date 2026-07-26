import pyc
import marshal
import os
import argparse
import bz2, gzip, zlib, lzma
import time

os.system("")

def is_file_exists(path):
    return os.path.exists(path) + os.path.isfile(path)

# Аргументы
parser = argparse.ArgumentParser(
                    prog='Ultimate Packer for Python',
                    description='Compress .PYC files')

parser.add_argument('filename')
parser.add_argument('-bz2', '--bz2',
                    action='store_true', help="Use bz2")
parser.add_argument('-gzip', '--gzip',
                    action='store_true', help="Use gzip")
parser.add_argument('-lzma', '--lzma',
                    action='store_true', help="Use lzma")
parser.add_argument('-zlib', '--zlib',
                    action='store_true', help="Use zlib (default)")
parser.add_argument('-cl', '--compression-level', help="Choose compression level")

parser.add_argument('-b', '--brute',
                    action='store_true', help="Making benchmarks so chooses the best compression method")
parser.add_argument('-be', '--brute-extreme',
                    action='store_true', help="Making benchmarks more extreme so testes even compression levels (requires -b)")
parser.add_argument('-e', '--exclude', help="Exclude compression methods")

parser.add_argument('-d', '--decompress',
                    action='store_true', help="Decompress packed file")


args = parser.parse_args()

# Графика (скудная)

def abort(text):
    print((f"\033[38;2;{255};{0};{0}m{text}\033[0m"))
    exit()

print("UPP - Ultimate Packer for Python")
print("v1.1")
print("-"*32)

if not is_file_exists(args.filename):
    abort(f"ERROR: COULDN'T FIND FILE {args.filename}!")

print(f"Loading up {args.filename}...")
content = open(args.filename, "rb").read()

print("Analyzing...")
try:
    header = pyc.PycHeader()
    header.analyze_header(content[:16])
except Exception:
    abort(f"Corrupted header!")

print(f"\nVersion: {".".join(map(str, header.get_magic()))}")
print("\nLoading code object...")

try:
    code_object = pyc.get_code_info(content, header)
except:
    abort(f"Corrupted code object!")

if args.decompress:
    flag = False
    for i in code_object.co_consts:
        if isinstance(i, str):
            if i.startswith("UPP!"):
                print(f"File packed with UPP v{i[4:]}!")
                flag = True
                break
    if flag:
        print("Decompressing...")
        print("Searching up for compressed code object...")
        code_obj = None
        for i in code_object.co_consts:
            if isinstance(i, bytes):
                if len(i) > 50:
                    print("Code found!")
                    code_obj = i
        if code_obj is None:
            abort("Code object not found!")
        print("Searching up for compression library...")
        lib = None
        for i in code_object.co_consts:
            if i in ["zlib", "bz2", "gzip", "lzma"]:
                lib = i
        if lib is None:
            abort("Library not found!")
        print("Decompressing code object...")
        try:
            code_obj = globals()[lib].decompress(code_obj)
        except:
            abort("Corrupted compressed bytes!")

        print("Constructing new PYC...")
        new_pyc = header.get_header()
        new_pyc += code_obj

        if not is_file_exists(args.filename[:-4] + "_decompressed.pyc"):
            print(f"Saved as {args.filename[:-4] + "_decompressed.pyc"}!")
            open(args.filename[:-4] + "_decompressed.pyc", "wb").write(new_pyc)
        else:
            print(f"Cannot override {args.filename[:-4] + "_decompressed.pyc"}!, how you want to save?")
            open(input(), "wb").write(new_pyc)
    else:
        print("Not compressed with UPP, or hacked/modified!")
    exit()

# Проверки
if not [args.bz2, args.zlib, args.lzma, args.gzip].count(True) in [0, 1]:
    abort(f"Too many compression parameters!")

if any([args.bz2, args.zlib, args.lzma, args.gzip]) and args.brute:
    abort(f"Combination of compression parameter and brute!")

if args.brute_extreme and not args.brute:
    abort(f"Extreme brute enabled but not brute!")

if any([args.bz2, args.lzma]) and args.compression_level is not None:
    abort("BZ2/LZMA not supports compression level")

# Стаб

def stub():
    exec(__import__("marshal").loads(__import__("<lib>").decompress(b"<PLACEHOLDER>")))

# Сама обработка

def strip_code(code_obj):
    try:
        code_obj.co_filename = ""
        code_obj.co_name = ""
        code_obj.co_qualname = ""
        code_obj.co_linetable = b""
        code_obj.co_lnotab = 0
        return code_obj
    except AttributeError:
        return code_obj.replace(co_filename="",
                         co_name="",
                         co_qualname="",
                         co_linetable=b"",
                         co_firstlineno=0)

print("Stripping stub metadata...")
stub_code = stub.__code__
stub_code = strip_code(stub_code)

print("Marshalling main code object...")
code = marshal.dumps(code_object)

print("Choosing compress library...")
if args.exclude is None:
    args.exclude = ""


if args.brute:
    best = ""
    best_compression = None
    best_size = float("inf")
    speed = float("inf")
    for i in [i for i in ["bz2", "gzip", "zlib", "lzma"] if not i in args.exclude.split(",")]:
        if args.brute_extreme:
            if i == "zlib":
                for j in range(1, 10):
                    timer = time.time()
                    compressed = globals()[i].compress(code, level=j)
                    timer = time.time() - timer
                    if len(compressed) <= best_size:
                        best = i
                        best_size = len(compressed)
                        best_compression = j
                    elif len(compressed) == best_size:
                        if speed > timer:
                            best = i
                            best_compression = j
            elif i == "gzip":
                for j in range(1, 10):
                    timer = time.time()
                    compressed = globals()[i].compress(code, compresslevel=j)
                    timer = time.time() - timer
                    if len(compressed) <= best_size:
                        best = i
                        best_size = len(compressed)
                        best_compression = j
                    elif len(compressed) == best_size:
                        if speed > timer:
                            best = i
                            best_compression = j
        else:
            if i in ["gzip", "zlib"]:
                timer = time.time()
                compressed = globals()[i].compress(code)
                timer = time.time() - timer
                if len(compressed) <= best_size:
                    best = i
                    best_size = len(compressed)
                elif len(compressed) == best_size:
                    if speed > timer:
                        best = i

        if i in ["bz2", "lzma"]:
            timer = time.time()
            compressed = globals()[i].compress(code)
            timer = time.time() - timer
            if len(compressed) <= best_size:
                best = i
                best_size = len(compressed)
            elif len(compressed) == best_size:
                if speed > timer:
                    best = i
    lib = best
    compression = best_compression
else:
    if args.bz2:
        lib = "bz2"
    elif args.gzip:
        lib = "gzip"
    elif args.zlib:
        lib = "zlib"
    elif args.lzma:
        lib = "lzma"
    else:
        lib = "zlib"
    compression = args.compression_level

if compression is None:
    compression = -1

print(f"Chosen: {lib}({compression})")

print("Compressing code...")
compressed = b""
if lib == "zlib":
    compressed = globals()[lib].compress(code, level=compression)
if lib == "gzip":
    compressed = globals()[lib].compress(code, compresslevel=compression)
else:
    compressed = globals()[lib].compress(code)

new_co_consts = []
print("Patching consts (stub)...")
for i in stub_code.co_consts:
    if i == b"<PLACEHOLDER>":
        new_co_consts.append(compressed)
    elif i == "<lib>":
        new_co_consts.append(lib)
    else:
        new_co_consts.append(i)
new_co_consts.append("UPP!1.10")
stub_code = stub_code.replace(co_consts=tuple(new_co_consts))

print("Constructing new PYC...")
new_pyc = header.get_header()
new_pyc += marshal.dumps(stub_code)

if not is_file_exists(args.filename[:-4]+"_compressed.pyc"):
    print(f"Saved as {args.filename[:-4]+"_compressed.pyc"}!")
    open(args.filename[:-4]+"_compressed.pyc", "wb").write(new_pyc)
else:
    print(f"Cannot override {args.filename[:-4]+"_compressed.pyc"}!, how you want to save?")
    open(input(),"wb").write(new_pyc)
