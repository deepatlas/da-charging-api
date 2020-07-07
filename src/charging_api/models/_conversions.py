from typing import Dict, Set
from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape
from shapely.geometry import Point


def from_model(to_instance: object, from_instance: object):
    if not all(["get_attributes" in dir(obj) for obj in [to_instance, from_instance]]):
        raise RuntimeError(
            "Missing method get_attributes! to_instance and from_instance objects need to implement get_attributes() method!"
        )
    to_instance_fields: Set = set(to_instance.get_attributes())
    from_instance_fields: Set = set(from_instance.get_attributes())
    fields_to_update: Set = to_instance_fields.intersection(from_instance_fields)
    for field_name in fields_to_update:
        new_field_value = getattr(from_instance, field_name)
        if (isinstance(new_field_value, WKBElement)) & (hasattr(to_instance, "Config")):
            geom: Point = to_shape(new_field_value)
            new_field_value = f"POINT({geom.x} {geom.y})"
        if field_name == "address":
            to_instance.address.from_model(new_field_value)
            continue
        if field_name == "charging":
            to_instance.charging.from_model(new_field_value)
            continue
        setattr(to_instance, field_name, new_field_value)


def to_dict(table_dict: Dict[str, any], ignore_objs: Set[object] = set()):
    return_dict = {}
    for k, v in table_dict.items():
        if any([isinstance(v, io) for io in ignore_objs]):
            continue
        if (not isinstance(v, (str, int, float, complex, list, bytes, WKBElement))) & (
            v is not None
        ):
            v = to_dict(table_dict=v.__dict__, ignore_objs=ignore_objs)
        if isinstance(v, WKBElement):
            geom = to_shape(v)
            v = f"POINT({geom.x} {geom.y})"
        return_dict[k] = v
    return return_dict
