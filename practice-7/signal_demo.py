#!/usr/bin/env python3
import os
import signal


def main():
    def handle(signum, frame):
        print('SIGINT получен: процесс продолжает работу', flush=True)
    signal.signal(signal.SIGINT, handle)
    signal.signal(signal.SIGTERM, lambda *_: exit(0))
    print(f'READY PID={os.getpid()}; Ctrl+C / kill -INT; завершение: kill -TERM', flush=True)
    while True:
        signal.pause()


if __name__ == '__main__':
    main()
