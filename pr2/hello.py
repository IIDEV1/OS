import sys

if len(sys.argv) != 2:
    print("Использование: python3 hello.py <файл>", file=sys.stderr)
    sys.exit(1)

filename = sys.argv[1]

try:
    with open(filename, "rb") as f:
        data = f.read()

    print(len(data))

except OSError as e:
    print(f"Ошибка: {e}", file=sys.stderr)
    sys.exit(1)