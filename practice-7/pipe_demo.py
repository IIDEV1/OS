#!/usr/bin/env python3
import os


def main():
    reader, writer = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(reader)
        with os.fdopen(writer, 'wb') as stream:
            stream.write('Сообщение от дочернего процесса\n'.encode())
        os._exit(0)
    os.close(writer)
    with os.fdopen(reader, 'rb') as stream:
        print(stream.read().decode(), end='')
    _, status = os.waitpid(pid, 0)
    assert os.waitstatus_to_exitcode(status) == 0


if __name__ == '__main__':
    main()
