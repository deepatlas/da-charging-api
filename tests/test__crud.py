import json
import os
from typing import List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm.scoping import ScopedSession, scoped_session
from charging_api.models._db_models import DbStation
from charging_api.models._rest_models import RestStation
from charging_api.server._config import engine_string, connect_args
from charging_api.server._crud import (
    create,
    delete,
    update,
    read,
    _delete_all,
    _init_stations,
)


class TestCrud:
    engine = create_engine(engine_string, connect_args=connect_args)
    engine.connect()
    SessionFactory: sessionmaker = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    Session: ScopedSession = scoped_session(SessionFactory)

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

    def test_create_delete(self):
        session: Session = self.Session()
        create(session=session, station=self.restStation)
        result: List[DbStation] = (
            session.query(DbStation).filter(DbStation.id == self.restStation.id).all()
        )
        assert len(result) == 1
        delete(session=session, id=self.restStation.id)
        result = (
            session.query(DbStation).filter(DbStation.id == self.restStation.id).all()
        )
        assert len(result) == 0

    def test_update(self):
        session: Session = self.Session()
        create(session=session, station=self.restStation)
        self.restStation.payment = "UPDATED VALUE"
        update(session=session, station=self.restStation)
        result: List[DbStation] = (
            session.query(DbStation).filter(DbStation.id == self.restStation.id).all()
        )
        assert len(result) == 1
        assert result[0].payment == self.restStation.payment
        delete(session=session, id=self.restStation.id)

    def test_read(self):
        session: Session = self.Session()
        create(session=session, station=self.restStation)
        actual_station: RestStation = read(session=session, id=self.restStation.id)
        assert actual_station.to_dict() == self.restStation_dict
        delete(session=session, id=self.restStation.id)

    def test__delete_all(self):
        session: Session = self.Session()
        create(session=session, station=self.restStation)
        rows_before: int = session.query(DbStation).count()
        assert rows_before > 0
        _delete_all(session=session)
        rows_after: int = session.query(DbStation).count()
        assert rows_after == 0

    def test__init_stations(self):
        session: Session = self.Session()
        _init_stations(session=session)
        rows: int = session.query(DbStation).count()
        assert rows > 0
