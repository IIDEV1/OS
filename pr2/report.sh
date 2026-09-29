#!/usr/bin/env bash

usage() {
    echo "Использование: $0 <каталог> <ERROR|WARN> [--top N]" >&2
}

if [[ $# -ne 2 && $# -ne 4 ]]; then
    usage
    exit 1
fi

DIR="$1"
LEVEL="$2"

if [[ ! -d "$DIR" ]]; then
    echo "Ошибка: каталог '$DIR' не существует" >&2
    usage
    exit 1
fi

if [[ "$LEVEL" != "ERROR" && "$LEVEL" != "WARN" ]]; then
    echo "Ошибка: уровень должен быть ERROR или WARN" >&2
    usage
    exit 1
fi

TOP=""

if [[ $# -eq 4 ]]; then
    if [[ "$3" != "--top" || ! "$4" =~ ^[0-9]+$ ]]; then
        echo "Ошибка: N должно быть числом" >&2
        usage
        exit 1
    fi

    TOP="$4"
fi

RESULT=$(
    awk -v level="$LEVEL" '
        $3 == level {
            module = $4
            sub(/^module=/, "", module)
            count[module]++
        }

        END {
            for (module in count) {
                print module, count[module]
            }
        }
    ' "$DIR"/*.log | sort -k2,2nr
)

if [[ -n "$TOP" ]]; then
    printf "%s\n" "$RESULT" | head -n "$TOP"
else
    printf "%s\n" "$RESULT"
fi