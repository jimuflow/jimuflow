#!/bin/bash
scripts_dir=$(dirname "$0")
base_dir=$(dirname "$scripts_dir")
pyside6-rcc $base_dir/jimuflow/icons.qrc -o $base_dir/jimuflow/rc_icons.py
