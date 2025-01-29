#!/bin/bash
scripts_dir=$(dirname "$0")
base_dir=$(dirname "$scripts_dir")
msgattrib --untranslated $base_dir/jimuflow/locales/zh_CN/LC_MESSAGES/messages.po
