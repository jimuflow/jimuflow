import importlib
import json
import os.path
import pkgutil
from pathlib import Path

base_path = os.path.dirname(os.path.dirname(__file__))
packages_path = Path(os.path.join(base_path, 'jimuflow', 'packages'))
modules = set()


def get_type_module(type_name: str):
    return type_name.rsplit('.', 1)[0]


for package_path in packages_path.iterdir():
    if package_path.is_dir():
        package_json_file = package_path / 'jimuflow.json'
        if package_json_file.exists():
            for file in package_path.rglob('*.comp.json'):
                with open(file, 'r', encoding='utf-8') as f:
                    comp_json = json.load(f)
                    comp_type = comp_json['type']
                    modules.add(get_type_module(comp_type))
                    if 'variables' in comp_json:
                        for variable in comp_json['variables']:
                            if 'uiConfig' in variable:
                                if 'inputEditorType' in variable['uiConfig']:
                                    modules.add(get_type_module(variable['uiConfig']['inputEditorType']))
            for file in package_path.rglob('*.type.json'):
                with open(file, 'r', encoding='utf-8') as f:
                    type_json = json.load(f)
                    if 'registrar' in type_json:
                        modules.add(get_type_module(type_json['registrar']))

packages = ['mysql.connector.locales', 'mysql.connector.plugins']
for package_name in packages:
    package = importlib.import_module(package_name)
    for _, name, _ in pkgutil.walk_packages(package.__path__, package_name + '.'):
        modules.add(name)
print(' '.join(f'--hidden-import={name}' for name in modules))
