#!/bin/bash
cd "$(dirname "$0")"
./Osiranking.py
git add README.md
git commit -m "Auto update"
git push origin master