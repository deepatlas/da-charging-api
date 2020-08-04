import os
from typing import Dict
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Float,
    String,
    ARRAY,
    Boolean,
    Binary,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, query_expression
from geoalchemy2 import Geometry
from ._mixins import DbMixin
from ..helpers._logger import get_logger

log = get_logger(os.path.basename(__file__))
Base = declarative_base()


class DbAddress(Base, DbMixin):
    __tablename__ = "address"
    __table_args__ = {"extend_existing": True}

    station_id = Column(
        Binary,
        ForeignKey("station.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        index=True,
    )
    street = Column(String(500))
    town = Column(String(500))
    postcode = Column(String(500))
    district = Column(String(500))
    state = Column(String(500))
    country = Column(String(500))

    station = relationship("DbStation", uselist=False, back_populates="address")


class DbCharging(Base, DbMixin):
    __tablename__ = "charging"
    __table_args__ = {"extend_existing": True}

    station_id = Column(
        Binary,
        ForeignKey("station.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        index=True,
    )

    capacity = Column(Integer)
    kw_list = Column(ARRAY(Float))
    ampere_list = Column(ARRAY(Float))
    volt_list = Column(ARRAY(Float))
    socket_type_list = Column(ARRAY(String))
    dc_support = Column(Boolean)
    total_kw = Column(Float)
    max_kw = Column(Float)

    station = relationship("DbStation", uselist=False, back_populates="charging")


class DbStation(Base, DbMixin):
    __tablename__ = "station"
    __table_args__ = {"extend_existing": True}

    id = Column(Binary, primary_key=True, index=True)
    data_source = Column(String(500))
    operator = Column(String(500))
    payment = Column(String(500))
    authentication = Column(String(500))
    coordinates = Column(Geometry("POINT"))
    raw_data = Column(String)
    distance = query_expression()

    address = relationship(
        "DbAddress",
        uselist=False,
        back_populates="station",
        cascade="all, delete-orphan",
    )
    charging = relationship(
        "DbCharging",
        uselist=False,
        back_populates="station",
        cascade="all, delete-orphan",
    )

    def __init__(self, **kwargs):
        attrs = self.get_attributes()
        for k, v in kwargs.items():
            if isinstance(v, Dict):
                if "address" == k:
                    v = DbAddress(**v)
                if "charging" == k:
                    v = DbCharging(**v)
            if k in attrs:
                setattr(self, k, v)
        if self.address is None:
            self.address = DbAddress()
        if self.charging is None:
            self.charging = DbCharging()


if __name__ == "__main__":
    # from ..server import Config
    # from sqlalchemy import create_engine
    #
    # engine = create_engine(Config.engine_string, connect_args=Config.connect_args)
    # engine.connect()
    # Base.metadata.create_all(engine, Base.metadata.tables.values(), checkfirst=True)
    print("done")
