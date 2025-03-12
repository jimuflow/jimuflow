#!/bin/bash

# 获取语言代码
if [ -n "$READTHEDOCS_LANGUAGE" ]; then
  lang_code=$(echo "$READTHEDOCS_LANGUAGE"|cut -d'-' -f1)
  site_dir=$READTHEDOCS_OUTPUT/html
elif [ -n "$lang_code" ]; then
  site_dir=$(pwd)/site/$lang_code
else
  lang_code='zh'
  site_dir=$(pwd)/site/$lang_code
fi

# 打印配置文件
cat config/$lang_code/mkdocs.yml

# 遍历examples目录下的子目录，压缩并保存为zip文件
examples_source_dir="$(pwd)/examples/$lang_code"
examples_dest_dir="$(pwd)/docs/$lang_code/examples"
# 创建目标目录（如果不存在）
mkdir -p "$examples_dest_dir"
# 遍历源目录中的子目录
find "$examples_source_dir" -mindepth 1 -maxdepth 1 -type d -print0 | while IFS= read -r -d '' dir; do
    # 获取目录名称
    dir_name=$(basename "$dir")
    # 设置输出路径
    zip_path="$examples_dest_dir/${dir_name}.zip"
    # 显示压缩进度
    echo "正在压缩: $dir -> $zip_path"
    # 执行压缩（保留目录结构但排除父级路径）
    (cd "$(dirname "$dir")" && zip -rq "$zip_path" "$(basename "$dir")")
done
echo "所有目录已压缩完成！保存至：$examples_dest_dir"

# 构建文档
python -m mkdocs build --clean --site-dir $site_dir --config-file config/$lang_code/mkdocs.yml
