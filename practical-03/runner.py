#!/usr/bin/env python3

import os
import sys
import time


def main():
    if len(sys.argv) < 3:
        print(
            f"Использование: {sys.argv[0]} N команда [аргументы...]",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        n = int(sys.argv[1])

        if n <= 0:
            raise ValueError
    except ValueError:
        print("Ошибка: N должно быть положительным числом", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[2:]

    children = {}
    results = []

    for i in range(n):
        start = time.monotonic()

        pid = os.fork()

        if pid == 0:
            try:
                os.execvp(command[0], command)
            except OSError as e:
                print(f"exec error: {e}", file=sys.stderr)
                os._exit(127)

        children[pid] = start
        print(f"Создан дочерний процесс PID={pid}")

    while children:
        pid, status = os.waitpid(-1, 0)

        end = time.monotonic()
        elapsed = end - children.pop(pid)

        if os.WIFEXITED(status):
            code = os.WEXITSTATUS(status)
        elif os.WIFSIGNALED(status):
            code = 128 + os.WTERMSIG(status)
        else:
            code = -1

        results.append((pid, code, elapsed))

    print()
    print("Результаты:")

    for pid, code, elapsed in sorted(results):
        print(
            f"PID={pid} "
            f"код возврата={code} "
            f"время={elapsed:.4f} сек"
        )


if __name__ == "__main__":
    main()
