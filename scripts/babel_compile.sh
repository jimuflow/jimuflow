#!/bin/bash
scripts_dir=$(dirname "$0")
base_dir=$(dirname "$scripts_dir")
export PYTHONPATH=$base_dir
pybabel compile -f -D messages -d $base_dir/jimuflow/locales
