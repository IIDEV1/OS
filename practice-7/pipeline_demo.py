#!/usr/bin/env python3
import subprocess


def main():
    listing = subprocess.Popen(['ls'], stdout=subprocess.PIPE)
    try:
        filtering = subprocess.Popen(['grep', 'py'], stdin=listing.stdout, stdout=subprocess.PIPE, text=True)
        listing.stdout.close()  # Parent must not keep an unused pipe descriptor.
        output, _ = filtering.communicate(timeout=10)
        print(output, end='')
        assert filtering.returncode in (0, 1)
    finally:
        listing.wait(timeout=10)


if __name__ == '__main__':
    main()
