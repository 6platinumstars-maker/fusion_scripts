#!/bin/bash

BASE_SRC="$HOME/fusion_scripts"
BASE_DST="/mnt/c/Users/6plat/AppData/Roaming/Autodesk/Autodesk Fusion 360/API/Scripts"

for file in "$BASE_SRC"/*.py; do
    [ -e "$file" ] || continue

    name=$(basename "$file" .py)

    mkdir -p "$BASE_DST/$name"
    cp "$file" "$BASE_DST/$name/$name.py"

    echo "Synced: $name"
done

echo "All scripts synced!"