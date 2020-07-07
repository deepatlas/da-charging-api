from typing import Optional, List, Dict
from pydantic import BaseModel, root_validator
from ._mixins import RestMixin


class RestAddress(BaseModel, RestMixin):
    station_id: Optional[bytes]
    street: Optional[str]
    town: Optional[str]
    postcode: Optional[str]
    district: Optional[str]
    state: Optional[str]
    country: Optional[str]

    class Config:
        orm_mode = True


class RestCharging(BaseModel, RestMixin):
    station_id: Optional[bytes]
    capacity: Optional[int]
    kw_list: Optional[List[float]]
    ampere_list: Optional[List[float]]
    volt_list: Optional[List[float]]
    socket_type_list: Optional[List[str]]
    dc_support: Optional[bool]
    total_kw: Optional[float]
    max_kw: Optional[float]

    class Config:
        orm_mode = True


class RestStation(BaseModel, RestMixin):
    id: Optional[bytes]
    data_source: Optional[str]
    operator: Optional[str]
    payment: Optional[str]
    authentication: Optional[str]
    coordinates: Optional[str]
    raw_data: Optional[str]
    address: Optional[RestAddress]
    charging: Optional[RestCharging]

    @root_validator(pre=True)
    def set_address_charging(cls, v):
        id: bytes = v.get("id")
        if isinstance(id, memoryview):
            id = id.tobytes()
        if isinstance(id, str):
            id = id.encode("utf8")
        if not isinstance(id, bytes):
            raise RuntimeError(f"id: {id} (type: {type(id)}) is not of type bytes! Could not convert to bytes!")
        address = v.get("address")
        if isinstance(address, Dict):
            v["address"] = RestAddress(**address)

        charging = v.get("charging")
        if isinstance(address, Dict):
            v["charging"] = RestCharging(**charging)

        if address is None:
            v["address"] = RestAddress(id=id)

        if charging is None:
            v["charging"] = RestCharging(id=id)

        return v

    class Config:
        orm_mode = True
