import logging
import os
import json
from charging_api.models._rest_models import RestStation
from charging_api.models._db_models import DbStation

log = logging.getLogger(os.path.basename(__file__))


def _compare_attributes(restStation, dbStation, field=None):
    if field is not None:
        restStation = getattr(restStation, field)
        dbStation = getattr(dbStation, field)
    for field_name, _ in restStation.__fields__.items():
        rest_field_value = restStation.__dict__.get(field_name)
        db_field_value = getattr(dbStation, field_name)
        if field_name in ["address", "charging"]:
            _compare_attributes(
                restStation=restStation, dbStation=dbStation, field=field_name
            )
            continue
        assert rest_field_value == db_field_value


class TestConversion:
    test_data_file_path: str = os.path.realpath(
        os.path.join(os.path.dirname(__file__), "../data/test_restStation.json")
    )
    with open(test_data_file_path, "r") as f:
        restStation_dict = json.load(f)
    id: bytes = restStation_dict["id"].encode("utf8")
    restStation_dict["id"] = id
    restStation_dict["address"]["station_id"] = id
    restStation_dict["charging"]["station_id"] = id
    restStation: RestStation = RestStation(**restStation_dict)
    test_data_file_path: str = os.path.realpath(
        os.path.join(os.path.dirname(__file__), "../data/test_dbStation.json")
    )
    with open(test_data_file_path, "r") as f:
        dbStation_dict = json.load(f)
    id: bytes = dbStation_dict["id"].encode("utf8")
    dbStation_dict["id"] = id
    dbStation_dict["address"]["station_id"] = id
    dbStation_dict["charging"]["station_id"] = id
    dbStation: DbStation = DbStation(**dbStation_dict)

    def test_from_rest(self):
        dbStation: DbStation = DbStation().from_model(self.restStation)
        _compare_attributes(restStation=self.restStation, dbStation=dbStation)

    def test_from_db(self):

        restStation: RestStation = RestStation()
        restStation.from_model(self.dbStation)
        _compare_attributes(restStation=restStation, dbStation=self.dbStation)

    def test_to_dict(self):
        assert self.dbStation_dict == self.dbStation.to_dict()
        assert self.restStation_dict == self.restStation.to_dict()
