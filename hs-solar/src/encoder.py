# This module serializes and deserializes pipeline stages results into JSON.

# Please interact with this code with extreme care.
# This application is only a prototype and the code doesn't follow best practices.

from dataclasses import asdict, is_dataclass
import json
from datetime import datetime

from typing import Any, TypeVar, Type

T = TypeVar('T')

class DataclassJSONEncoder(json.JSONEncoder):
    def default(self, o: Any):
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)

def dump_stage_result(stage_name: str, file_path: str, result: list) -> None:
    data = {
        "stage_metadata": {
            "name": stage_name,
            "timestamp": datetime.now().isoformat(),
        },
        "result": result,
    }

    with open(file_path, "w") as f:
        json.dump(data, f, cls=DataclassJSONEncoder, indent=2)
   

def from_dict(cls: Type[T], data: dict) -> T:
    fieldtypes = {f.name: f.type for f in cls.__dataclass_fields__.values()}
    kwargs = {}
    for k, v in data.items():
        if is_dataclass(fieldtypes[k]):
            kwargs[k] = from_dict(fieldtypes[k], v)
        elif isinstance(v, list) and hasattr(fieldtypes[k], '__args__'):  # List of dataclasses
            subtype = fieldtypes[k].__args__[0]
            if is_dataclass(subtype):
                kwargs[k] = [from_dict(subtype, i) for i in v]
            else:
                kwargs[k] = v
        else:
            kwargs[k] = v
    return cls(**kwargs)

def load_stage_result(path: str, result_type: Type[T]) -> dict:
    with open(path, "r") as f:
        raw = json.load(f)

    return raw["stage_metadata"], [from_dict(result_type, r) for r in raw["result"]]

        