# 构建和运行JimuFlow

本指南介绍了如何构建和运行JimuFlow，开发人员可以基于本指南搭建本地开发环境。

## 安装python

python版本要求>=3.9,<3.14

## 创建python虚拟环境

```shell
python3 -m venv venv
```

## 激活虚拟环境

在Linux或MacOS上，激活虚拟环境
```shell
source venv/bin/activate
```
在Windows上，激活虚拟环境
```shell
venv\Scripts\activate.bat
```

## 安装依赖

```shell
pip install -r requirements.txt
playwright install chromium
```

## 安装开发依赖
```shell
pip install -r requirements-dev.txt
```

## 启动应用
```shell
python -m jimuflow.gui.main_window
```

## 运行测试用例
```shell
pytest
```

## 打包应用

在MacOS上，执行shell脚本[package_on_macos.sh](../../../scripts/package_on_macos.sh)
```shell
./scripts/package_on_macos.sh
```
执行之后，将会在项目根目录的dist目录下生成JimuFlow.ap。

在Windows上，执行批处理脚本[package_on_windows.bat](../../../scripts/windows/package_on_windows.bat)
```shell
.\scripts\windows\package_on_windows.bat
```
执行之后，将会在项目根目录的dist目录下生成一个JimuFlow文件夹，该文件夹下包含了JimuFlow的可执行文件。

在Linux上，执行shell脚本[package_on_linux.sh](../../../scripts/package_on_linux.sh)
```shell
./scripts/package_on_linux.sh
```
执行之后，将会在项目根目录的dist目录下生成一个JimuFlow文件夹，该文件夹下包含了JimuFlow的可执行文件。
