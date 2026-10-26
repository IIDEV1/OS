#!/usr/bin/env python3

import os
import time


pid = os.fork()

if pid == 0:
    print(f"Ребёнок PID={os.getpid()} завершается", flush=True)
    os._exit(0)

print(f"Родитель PID={os.getpid()}")
print(f"Ребёнок PID={pid}")
print()
print("В течение 30 секунд ребёнок будет zombie.")
print("Открой второе окно Ubuntu и выполни команду:")
print()
print(f"ps -o pid,ppid,stat,cmd -p {os.getpid()},{pid}")
print()

time.sleep(30)

os.waitpid(pid, 0)

print("Родитель вызвал waitpid(). Zombie очищен.")
