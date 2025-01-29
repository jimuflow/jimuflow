#!/bin/bash
scripts_dir=$(dirname "$0")
base_dir=$(dirname "$scripts_dir")
export PYTHONPATH=$base_dir
pybabel extract -F $base_dir/jimuflow/locales/babel_mapping.ini -o $base_dir/jimuflow/locales/messages.pot --add-location=never --input-dirs=$base_dir --project=jimuflow --version=1.0.0
