import os
import geopandas as gpd
from typing import List, Dict
from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette.status import HTTP_404_NOT_FOUND
from tqdm import tqdm
from charging_stations.connectors import (
    Config as Connector_Config,
    BNAConnector,
    OCMConnector,
    OSMConnector,
    Merger,
)
from ..server import _config as Db_Config
from ..helpers import get_logger
from ..models._rest_models import RestStation, RestAddress, RestCharging
from ..models._db_models import DbStation

log = get_logger(os.path.basename(__file__))


def create(session: Session, station: RestStation):
    dbStation: DbStation = DbStation().from_model(station)
    session.add(dbStation)
    session.commit()


def delete(session: Session, id: bytes):
    result: DbStation = _read(session=session, id=id)
    session.delete(result)
    session.commit()


def _delete_all(session: Session):
    session.query(DbStation).delete()
    session.commit()


def update(session: Session, station: RestStation):
    result: DbStation = _read(session=session, id=station.id)
    result.from_model(station)
    session.commit()


def _read(session: Session, id: bytes) -> DbStation:
    result: List[DbStation] = session.query(DbStation).filter(DbStation.id == id).all()
    if len(result) != 1:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND, detail=f"Id: {id} not found!",
        )
    return result[0]


def read(session: Session, id: bytes) -> RestStation:
    return RestStation().from_model(_read(session=session, id=id))


def read_all(session: Session) -> List[RestStation]:
    result: List[DbStation] = session.query(DbStation).all()
    restStations: List[RestStation] = [RestStation().from_model(s) for s in result]
    return restStations


def _init_stations(session: Session):
    _delete_all(session=session)
    connectors: Dict = {
        c.__data_source__: c(
            base_path=os.path.realpath(os.path.join(os.getcwd(), "../data/")),
            **Connector_Config.CONNECTOR_CONFIGS[c.__data_source__],
        )
        for c in [BNAConnector, OCMConnector, OSMConnector]
    }
    stations_list: List = []
    # TODO: if bored >> joblib.Parallel :)
    for data_source, connector in connectors.items():
        connector.get_data(to_disk=True)
        connector.process(to_disk=True)
        log.debug(f"Got {len(connector.processed_data)} stations from {data_source}!")
        stations_list += connector.processed_data

    merger: Merger = Merger()
    merger.merge(stations_list=stations_list)
    stations: gpd.GeoDataFrame = merger.merged_stations_gdf
    log.debug("Stations after merging: {}".format(stations.shape[0]))
    stations["coordinates"] = stations.geometry.apply(
        lambda x: f"SRID={Db_Config.SRID};{x}"
    )

    for _, station in tqdm(stations.iterrows()):
        non_na_stations_dict: Dict = station.dropna().to_dict()
        restAddress: RestAddress = RestAddress(**non_na_stations_dict)
        restCharging: RestCharging = RestCharging(**non_na_stations_dict)
        restStation: RestStation = RestStation(
            address=restAddress, charging=restCharging, **non_na_stations_dict
        )
        create(session=session, station=restStation)

    log.debug("Finished stations-update!")
