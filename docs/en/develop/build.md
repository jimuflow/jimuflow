# Building and Running JimuFlow

This guide provides instructions on how to build and run JimuFlow. Developers can set up a local development environment based on this guide.

## Installing Python

Python version requirement: >=3.9, <3.14

## Creating a Python Virtual Environment

```shell
python3 -m venv venv
```

## Activating the Virtual Environment

On Linux or MacOS, activate the virtual environment:
```shell
source venv/bin/activate
```
On Windows, activate the virtual environment:
```shell
venv\Scripts\activate.bat
```

## Installing Dependencies

```shell
pip install -r requirements.txt
playwright install chromium
```

## Installing Development Dependencies
```shell
pip install -r requirements-dev.txt
```

## Starting the Application
```shell
python -m jimuflow.gui.main_window
```

## Running Test Cases
```shell
pytest
```

## Packaging the Application

On MacOS, execute the shell script [package_on_macos.sh](../../../scripts/package_on_macos.sh):
```shell
./scripts/package_on_macos.sh
```
After execution, JimuFlow.ap will be generated in the dist directory at the project root.

On Windows, execute the batch script [package_on_windows.bat](../../../scripts/windows/package_on_windows.bat):
```shell
.\scripts\windows\package_on_windows.bat
```
After execution, a JimuFlow folder will be generated in the dist directory at the project root. This folder contains the executable files for JimuFlow.

On Linux, execute the shell script [package_on_linux.sh](../../../scripts/package_on_linux.sh):
```shell
./scripts/package_on_linux.sh
```
After execution, a JimuFlow folder will be generated in the dist directory at the project root. This folder contains the executable files for JimuFlow.