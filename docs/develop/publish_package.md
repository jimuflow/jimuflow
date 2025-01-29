# 发布到PyPI

## 构建项目

运行以下命令打包：
```shell
python -m build
rm -rf jimuflow.egg-info # 删除无用的包信息
```
这将在 dist/ 目录下生成 .tar.gz 和 .whl 文件。

## 在虚拟环境中测试

如果你想在一个干净的环境中测试 .whl，可以创建一个新的虚拟环境：
```shell
python -m venv test_venv
source test_venv/bin/activate # macOS/Linux
# 或者 Windows:
test_venv\Scripts\activate
```

然后安装 .whl：
```shell
pip install --force-reinstall dist/jimuflow-1.0.0-py3-none-any.whl
```

测试完毕后，退出虚拟环境：
```shell
deactivate
```

## 进入 Python 交互模式测试

在 Python 交互模式中，尝试导入你的包：
```shell
python
```

然后：
```python
import jimuflow
print(jimuflow.__version__)  # 如果你的包定义了 __version__
```

## 卸载测试包
如果你想卸载已安装的 .whl：
```shell
pip uninstall jimuflow
```
如果你需要重新安装，直接使用 pip install --force-reinstall。

## 上传到 PyPI

使用 twine 进行上传：
```shell
twine upload dist/* -u __token__ -p YOUR_PYPI_API_TOKEN
```
