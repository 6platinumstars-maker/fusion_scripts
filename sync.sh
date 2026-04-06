#!/bin/bash

BASE_SRC="$HOME/fusion_scripts"
BASE_DST="/mnt/c/Users/6plat/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/Scripts"
CORE_SRC="$BASE_SRC/core"

for file in "$BASE_SRC"/*.py; do
    [ -e "$file" ] || continue

    name=$(basename "$file" .py)

    mkdir -p "$BASE_DST/$name"
    cp "$file" "$BASE_DST/$name/$name.py"

    if [ -d "$CORE_SRC" ]; then
        mkdir -p "$BASE_DST/$name/core"
        cp "$CORE_SRC"/*.py "$BASE_DST/$name/core/"
    fi

    echo "Synced: $name"
done

echo "All scripts synced!"
