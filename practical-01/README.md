# Practical Work 1 — Linux Users, Groups and Permissions

## Goal

Learn how Linux identifies users and groups and how access permissions are applied to files and directories.

## Implemented tasks

- record the operating system, kernel, architecture, current user and working directory;
- inspect the current groups and available shells;
- prepare commands for creating `student2` and the `developers` group;
- configure the shared directory `/srv/shared`;
- set ownership, group ownership and access permissions;
- verify access for a group member and deny access to unrelated users.

## Result

`environment.png` contains the recorded environment information. The work demonstrates the `rwx` permission model for the owner, group and other users. The setgid bit makes new files inherit the directory group, which is useful for a shared team folder.

## Run

```bash
python3 solution.py
```

Run `setup_commands.sh` in Ubuntu/WSL2 for the extended Variant B setup.
