# Publishing to PyPI

## Building the Project

Run the following command to package the project:
```shell
python -m build
rm -rf jimuflow.egg-info # Remove unnecessary package information
```
This will generate .tar.gz and .whl files in the dist/ directory.

## Testing in a Virtual Environment

If you want to test the .whl in a clean environment, you can create a new virtual environment:
```shell
python -m venv test_venv
source test_venv/bin/activate # macOS/Linux
# Or for Windows:
test_venv\Scripts\activate
```

Then install the .whl:
```shell
pip install --force-reinstall dist/jimuflow-1.0.0-py3-none-any.whl
```

After testing, exit the virtual environment:
```shell
deactivate
```

## Testing in Python Interactive Mode

In Python interactive mode, try importing your package:
```shell
python
```

Then:
```python
import jimuflow
print(jimuflow.__version__)  # If your package defines __version__
```

## Uninstalling the Test Package

If you want to uninstall the installed .whl:
```shell
pip uninstall jimuflow
```
If you need to reinstall, simply use pip install --force-reinstall.

## Uploading to PyPI

Use twine to upload:
```shell
twine upload dist/* -u __token__ -p YOUR_PYPI_API_TOKEN
```