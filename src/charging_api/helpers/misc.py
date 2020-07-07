from typing import Dict


def _update_config(to_obj, from_dict):
    for k, v in from_dict.items():
        if isinstance(v, Dict):
            current_value = getattr(to_obj, k)
            if isinstance(current_value, Dict):
                current_value.update(v)
                v = current_value
        setattr(to_obj, k, v)