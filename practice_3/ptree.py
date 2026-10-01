#!/usr/bin/env python3

import os
from collections import defaultdict


def read_process(pid):
    path = f"/proc/{pid}/status"

    try:
        with open(path, "r") as f:
            lines = f.readlines()
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        return None

    info = {}

    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            info[key] = value.strip()

    try:
        uid = int(info["Uid"].split()[0])
        ppid = int(info["PPid"])
    except (KeyError, ValueError):
        return None

    return {
        "pid": pid,
        "ppid": ppid,
        "uid": uid,
        "name": info.get("Name", "?"),
        "state": info.get("State", "?"),
        "rss": info.get("VmRSS", "0 kB"),
    }


def main():
    current_uid = os.getuid()
    processes = {}

    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue

        pid = int(entry)
        process = read_process(pid)

        if process is None:
            continue

        if process["uid"] == current_uid:
            processes[pid] = process

    children = defaultdict(list)

    for pid, process in processes.items():
        children[process["ppid"]].append(pid)

    for pids in children.values():
        pids.sort()

    roots = []

    for pid, process in processes.items():
        if process["ppid"] not in processes:
            roots.append(pid)

    roots.sort()

    def print_tree(pid, level=0):
        process = processes[pid]
        indent = "    " * level

        print(
            f"{indent}"
            f"PID={process['pid']} "
            f"NAME={process['name']} "
            f"STATE={process['state']} "
            f"RSS={process['rss']}"
        )

        for child_pid in children.get(pid, []):
            print_tree(child_pid, level + 1)

    print(f"Дерево процессов текущего пользователя UID={current_uid}")
    print()

    for root in roots:
        print_tree(root)


if __name__ == "__main__":
    main()
