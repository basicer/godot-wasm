import argparse
from pathlib import Path
import re
import shutil

opts = argparse.ArgumentParser("update")
opts.add_argument("-s", "--src")

args = opts.parse_args()

files = [
    "core/iwasm/interpreter/wasm_loader.c",
    "core/iwasm/interpreter/wasm_runtime.c",
    "core/iwasm/interpreter/wasm_interp_fast.c",

    "core/shared/utils/bh_assert.c",
    #"core/shared/utils/bh_log.c",
    "core/shared/utils/bh_vector.c",
    "core/shared/utils/bh_bitmap.c",
    "core/shared/utils/bh_queue.c",
    "core/shared/utils/bh_list.c",
    "core/shared/utils/bh_common.c",
    "core/shared/utils/bh_hashmap.c",
    "core/shared/utils/bh_leb128.c",
    #"core/shared/utils/runtime_timer.c",

    "core/shared/platform/cosmopolitan/platform_init.c",
    "core/shared/platform/common/posix/posix_thread.c",
    "core/shared/platform/common/posix/posix_malloc.c",
    "core/shared/platform/common/posix/posix_memmap.c",
    #"core/shared/platform/common/posix/posix_blocking_op.c",
    "core/shared/platform/common/memory/mremap.c",
    #"core/shared/platform/common/posix/posix_time.c",

    #"core/iwasm/common/arch/invokeNative_general.c",

    "core/iwasm/common/wasm_memory.c",
    "core/iwasm/common/wasm_runtime_common.c",
    "core/iwasm/common/wasm_exec_env.c",
    "core/iwasm/common/wasm_loader_common.c",
    
    #"core/iwasm/common/wasm_shared_memory.c",

    #"core/iwasm/common/wasm_native.c",

    "core/shared/mem-alloc/mem_alloc.c",
    "core/shared/mem-alloc/ems/ems_alloc.c",
    "core/shared/mem-alloc/ems/ems_kfc.c",

    "core/iwasm/common/wasm_c_api.c",
    #"samples/wasm-c-api/src/hello.c",
]



src = Path(args.src)
dest = Path(__file__).parent.resolve()

search = list(map(lambda o: src / o, [
    "core/shared/utils",
    "core/shared/platform/posix", 
    "core/shared/platform/include",
    "core/iwasm/common",
    "core/shared/mem-alloc",
    "core/iwasm/include",
    "core/iwasm/interpreter",
    "core/iwasm/libraries",
    "core/shared/platform/cosmopolitan",
    "core/shared/mem-alloc/ems",
    "core",
]))

r_include = re.compile("^#include ([\"<])([^\"<>]*)[>\"]", re.DOTALL | re.MULTILINE )
r_guard = re.compile(r"^#if\s*([^\n]*)\s*\n#include[^\n]*\n+#endif" , re.DOTALL | re.MULTILINE)

r_banned = re.compile(r"aot|uvwasi|jit|gc")

if not dest.exists():
    raise "Destination path doesnt exist"

if not src.exists():
    raise "Source path doesnt exist"

for p in dest.glob("src/*.c"):
    p.unlink()

if not (dest / "src").exists():
    (dest / "src").mkdir()

if not (dest / "include").exists():
    (dest / "include").mkdir()

shutil.copy(src / "LICENSE", dest / "LICENSE")

includes = set()


done = set()

def matcher(m):
    if m.group(1) == "<":
        return m.group(0)

    s = m.group(2).split("/")[-1]

    if r_banned.match(s):
        return ''

    includes.add(s)
    return f"#include \"{s}\" // {m.group(2)}"

def guarder(m):
    if m.group(1) in [
        "WASM_ENABLE_GC != 0",
        "WASM_ENABLE_AOT != 0",
        "WASM_ENABLE_SHARED_MEMORY != 0",
        "WASM_ENABLE_JIT != 0",
        "WASM_ENABLE_DEBUG_AOT != 0",
        "WASM_ENABLE_THREAD_MGR != 0",
        "WASM_ENABLE_WASM_CACHE != 0"
    ]:
        return ''

    return m.group(0)

def process(text):
    text = r_guard.sub(guarder, text)
    text = r_include.sub(matcher, text)
    return text


for file in files:
    p = src / Path(file)
    s = ""
    with p.open("r") as f:
        s = f.read()

    s = process(s)

    with (dest / "src" / p.name).open("w") as f:
        f.write(s)

while True:
    todo = includes - done
    if len(todo) < 1:
        break
    i = todo.pop()
    done.add(i)

    found = None
    for s in search:
        o = s / i
        if o.exists():
            found = o
            break

    if not found:
        print("Cant find", i)
    else:
        with found.open("r") as f:
            text = f.read()
            text = process(text)
            with (dest / "include" / found.name).open("w") as f2:
                f2.write(text)
            
