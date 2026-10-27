# Full Report — Practical Work 1

## Purpose
This practical studies Linux users, groups and file permissions. The work records the execution environment and prepares a shared directory for members of the `developers` group.

## Implementation
The solution records the kernel, architecture, current user, groups and working directory. The setup script contains commands for creating `student2`, creating `developers`, assigning the user to the group and configuring `/srv/shared`.

The shared directory uses owner `root`, group `developers` and mode `2775`. The leading `2` enables setgid, so new files inherit the directory group.

## Verification and result
The environment graph and saved output document the system used for testing. The permission model was checked for the owner, group members and other users. The result demonstrates how Linux controls access to shared resources.
