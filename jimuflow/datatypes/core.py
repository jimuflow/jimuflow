# This software is dual-licensed under the GNU General Public License (GPL) 
# and a commercial license.
#
# You may use this software under the terms of the GNU GPL v3 (or, at your option,
# any later version) as published by the Free Software Foundation. See 
# <https://www.gnu.org/licenses/> for details.
#
# If you require a proprietary/commercial license for this software, please 
# contact us at jimuflow@gmail.com for more information.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# Copyright (C) 2024-2025  Weng Jing

class DataTypeDef:
    def __init__(self, name, display_name, properties: list["DataTypeProperty"] = [], is_list=False, types=()):
        self.name = name
        self.display_name = display_name
        self.is_list = is_list
        self.properties = properties
        self.types = types

    def get_property_value(self, data_obj, property_name):
        """
        获取数据对象的属性值
        :param data_obj: 数据对象
        :param property_name: 属性名称
        """
        if isinstance(data_obj, dict):
            return data_obj.get(property_name)
        for prop in self.properties:
            if prop.name == property_name:
                if prop.accessor:
                    return prop.accessor(data_obj)
                else:
                    return getattr(data_obj, property_name)

    def get_property(self, name: str):
        return next((prop for prop in self.properties if prop.name == name), None)

    def __repr__(self):
        return f"DataTypeDef(name={self.name}, properties={self.properties}, is_list={self.is_list}, types={self.types})"


class DataTypeProperty:
    def __init__(self, name, data_type, description, accessor=None, element_type=None):
        self.name = name
        self.data_type = data_type
        self.description = description
        self.accessor = accessor
        self.element_type = element_type

    def __repr__(self):
        return (f"DataTypeProperty(name={self.name}, data_type={self.data_type}, description={self.description}, "
                f"accessor={self.accessor}, element_type={self.element_type})")


class DataTypeRegistry:
    def __init__(self):
        self._data_types = {}

    def copy_from_registry(self, registry: "DataTypeRegistry"):
        for data_type in registry.data_types:
            self.register(data_type)

    def register(self, data_type: DataTypeDef):
        if data_type.name in self._data_types:
            raise Exception(f"Data type {data_type.name} already registered")
        self._data_types[data_type.name] = data_type

    def get_data_type(self, name) -> DataTypeDef:
        return self._data_types.get(name)

    def get_obj_data_type(self, obj) -> DataTypeDef:
        candidates = []
        for data_type in self._data_types.values():
            if len(data_type.types) > 0 and isinstance(obj, data_type.types):
                if any(type(obj) is t for t in data_type.types):
                    return data_type
                else:
                    candidates.append(data_type)
        return self.get_data_type("any") if not candidates else candidates[0]

    @property
    def data_types(self) -> list[DataTypeDef]:
        return list(self._data_types.values())
