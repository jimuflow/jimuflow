# 修改PyInstaller spec文件的BUNDLE部分，添加version参数
import os.path


def modify_bundle_version(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 查找BUNDLE块起始位置
    start_line = None
    for i, line in enumerate(lines):
        if line.strip().startswith('app = BUNDLE('):
            start_line = i
            break

    if start_line is None:
        raise ValueError("未找到BUNDLE块")

    # 查找闭合括号位置
    brace_count = 1
    end_line = None
    for i in range(start_line + 1, len(lines)):
        brace_count += lines[i].count('(')
        brace_count -= lines[i].count(')')
        if brace_count == 0:
            end_line = i
            break

    if end_line is None:
        raise ValueError("未找到BUNDLE块的闭合括号")

    # 插入version参数（保持4空格缩进）
    version_line = '    version=\'1.0.1\',\n'
    lines.insert(end_line, version_line)

    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("文件修改完成")


# 使用示例（将路径替换为实际文件路径）
spec_file_path = os.path.join(os.path.dirname(__file__), '../JimuFlow.spec')
modify_bundle_version(spec_file_path)
