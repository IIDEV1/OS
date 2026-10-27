#!/usr/bin/env python3
"""Sequential FIFO service or fork-per-client Unix socket service."""
import argparse
import json
import os
from pathlib import Path
import signal
import socket
from calculator import response


def interrupted(signum, frame):
    raise SystemExit(128 + signum)


def read_request(stream):
    raw = stream.readline(4097)
    if not raw or len(raw) > 4096 or not raw.endswith(b'\n'):
        raise ValueError('A newline-terminated request of at most 4096 bytes is required')
    return json.loads(raw)


def encoded(value):
    return (json.dumps(value, ensure_ascii=False) + '\n').encode()


def serve_request(stream):
    try:
        return response(read_request(stream))
    except (ValueError, UnicodeError) as error:
        return {'ok': False, 'error': str(error)}


def fifo_server(directory, count):
    directory.mkdir(parents=True, exist_ok=True)
    created = []
    try:
        for name in ('request.fifo', 'response.fifo'):
            path = directory / name
            os.mkfifo(path, 0o600)  # Refuse to overwrite an existing endpoint.
            created.append(path)
        print('READY FIFO', flush=True)
        for _ in range(count):
            with (directory/'request.fifo').open('rb', buffering=0) as stream:
                answer = serve_request(stream)
            with (directory/'response.fifo').open('wb', buffering=0) as stream:
                stream.write(encoded(answer))
    finally:
        for path in created:
            path.unlink(missing_ok=True)


def fifo_client(directory, expression):
    with (directory/'request.fifo').open('wb', buffering=0) as stream:
        stream.write(encoded(expression))
    with (directory/'response.fifo').open('rb', buffering=0) as stream:
        return read_request(stream)


def unix_server(path, count):
    children = set()
    bound = False
    listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        listener.bind(str(path))
        bound = True
        os.chmod(path, 0o600)
        listener.listen(16)
        print('READY UNIX', flush=True)
        for _ in range(count):
            conn, _ = listener.accept()
            try:
                pid = os.fork()
            except BaseException:
                conn.close()
                raise
            if pid == 0:
                listener.close()
                try:
                    signal.signal(signal.SIGTERM, signal.SIG_DFL)
                    signal.signal(signal.SIGINT, signal.SIG_DFL)
                    conn.settimeout(5)
                    with conn, conn.makefile('rb') as stream:
                        conn.sendall(encoded(serve_request(stream)))
                    os._exit(0)
                except BaseException:
                    os._exit(1)
            conn.close()
            children.add(pid)
            for old_pid in list(children):
                done, status = os.waitpid(old_pid, os.WNOHANG)
                if done:
                    children.remove(old_pid)
                    if status:
                        raise RuntimeError('Client handler failed')
        while children:
            pid = next(iter(children))
            _, status = os.waitpid(pid, 0)
            children.remove(pid)
            if status:
                raise RuntimeError('Client handler failed')
    finally:
        listener.close()
        for pid in children:
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        for pid in children:
            os.waitpid(pid, 0)
        if bound:
            path.unlink(missing_ok=True)


def unix_client(path, expression):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as conn:
        conn.settimeout(10)
        conn.connect(str(path))
        conn.sendall(encoded(expression))
        with conn.makefile('rb') as stream:
            return read_request(stream)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('transport', choices=['fifo', 'unix'])
    parser.add_argument('role', choices=['server', 'client'])
    parser.add_argument('path', type=Path)
    parser.add_argument('expression', nargs='?')
    parser.add_argument('--count', type=int, default=3)
    args = parser.parse_args()
    if args.count < 1:
        parser.error('--count must be positive')
    if args.role == 'server':
        signal.signal(signal.SIGTERM, interrupted)
        signal.signal(signal.SIGINT, interrupted)
        (fifo_server if args.transport == 'fifo' else unix_server)(args.path, args.count)
    else:
        if args.expression is None:
            parser.error('Expression required')
        answer = (fifo_client if args.transport == 'fifo' else unix_client)(args.path, args.expression)
        print(json.dumps(answer, ensure_ascii=False))


if __name__ == '__main__':
    main()
