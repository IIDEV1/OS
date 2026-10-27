#!/usr/bin/env python3

import os
import time


pid = os.fork()

if pid > 0:
    print(f"Родитель PID={os.getpid()}", flush=True)
    print(f"Ребёнок PID={pid}", flush=True)
    print("Родитель завершается.", flush=True)
    os._exit(0)

child_pid = os.getpid()
old_ppid = os.getppid()

print(f"Ребёнок PID={child_pid}", flush=True)
print(f"Первоначальный PPID={old_ppid}", flush=True)

time.sleep(3)

new_ppid = os.getppid()

print(f"После завершения родителя новый PPID={new_ppid}", flush=True)
print()
print("Проверь в другом окне командой:")
print(f"ps -o pid,ppid,stat,cmd -p {child_pid},{new_ppid}")
print()

time.sleep(30)
