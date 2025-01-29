#!/bin/bash
scripts_dir=$(dirname "$0")
base_dir=$(dirname "$scripts_dir")
export PYTHONPATH=$base_dir
pybabel update -D messages -i $base_dir/jimuflow/locales/messages.pot -d $base_dir/jimuflow/locales -l zh_CN
