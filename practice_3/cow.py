#!/usr/bin/env python3

import os
import time


PAGE_SIZE = 4096
BLOCKS = 20000


def memory_info():
    result = {
        "VmRSS": 0,
        "Pss": 0,
        "Private_Dirty": 0,
    }

    with open(f"/proc/{os.getpid()}/status") as f:
        for line in f:
            if line.startswith("VmRSS:"):
                result["VmRSS"] = int(line.split()[1])

    try:
        with open(f"/proc/{os.getpid()}/smaps_rollup") as f:
            for line in f:
                key = line.split(":", 1)[0]

                if key in result:
                    result[key] = int(line.split()[1])
    except FileNotFoundError:
        pass

    return result


def show_memory(title):
    mem = memory_info()

    print(title)
    print(f"  RSS:           {mem['VmRSS']} kB")
    print(f"  PSS:           {mem['Pss']} kB")
    print(f"  Private_Dirty: {mem['Private_Dirty']} kB")
    print()


print("Родитель создаёт большой список...")

data = [
    bytearray(PAGE_SIZE)
    for _ in range(BLOCKS)
]

print(
    f"Размер данных примерно: "
    f"{BLOCKS * PAGE_SIZE / 1024 / 1024:.1f} MiB"
)

pid = os.fork()

if pid == 0:
    print(f"\nРебёнок PID={os.getpid()}")

    show_memory("До изменения унаследованного списка:")

    for block in data:
        block[0] = 1

    show_memory("После изменения унаследованного списка:")

    time.sleep(2)
    os._exit(0)

os.waitpid(pid, 0)

print("Родитель завершил ожидание ребёнка.")
