import os
import secrets
import uvicorn
from typing import Optional, List, Dict
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm.scoping import ScopedSession, scoped_session
from starlette.middleware.cors import CORSMiddleware
from starlette.status import HTTP_401_UNAUTHORIZED
from sqlalchemy.orm import Session, sessionmaker
from charging_stations.connectors import _config as Connector_Config
from ..helpers._misc import _update_config
from ..models._rest_models import RestStation
from ..helpers import get_logger
from . import _config as Db_Config, _crud as Crud

engine: Engine = create_engine(
    Db_Config.engine_string, connect_args=Db_Config.connect_args
)
SessionFactory: sessionmaker = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

log = get_logger(os.path.basename(__file__))
app = FastAPI()
security = HTTPBasic()
origins = [
    "http//:localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_session():
    Session: Optional[ScopedSession] = scoped_session(SessionFactory)
    session: Session = Session()
    yield session
    session.close()


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    incorrect_username: bool = not secrets.compare_digest(
        credentials.username, Db_Config.SECURITY_CREDENTIALS["user"]
    )
    incorrect_password: bool = not secrets.compare_digest(
        credentials.password, Db_Config.SECURITY_CREDENTIALS["password"]
    )
    if incorrect_username | incorrect_password:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect Credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True


@app.get("/health", status_code=200)
async def health():
    return {"status": "up"}


@app.post("/api/stations", status_code=200)
def create_station(
    station: RestStation,
    session: Session = Depends(get_session),
    authenticated: bool = Depends(verify_credentials),
):
    Crud.create(session=session, station=station)


@app.get("/api/stations", response_model=List[RestStation], status_code=200)
def read_stations(
    session: Session = Depends(get_session),
    authenticated: bool = Depends(verify_credentials),
):
    return Crud.read_all(session=session)


@app.get("/api/stations/{id}", response_model=RestStation, status_code=200)
def read_station(
    id: str,
    session: Session = Depends(get_session),
    authenticated: bool = Depends(verify_credentials),
):
    return Crud.read(session=session, id=id.encode("utf8"))


@app.delete("/api/stations/{id}", status_code=200)
def delete_station(
    id: str,
    session: Session = Depends(get_session),
    authenticated: bool = Depends(verify_credentials),
):
    return Crud.delete(session=session, id=id.encode("utf8"))


@app.put("/api/stations", status_code=200)
def update_station(
    station: RestStation,
    session: Session = Depends(get_session),
    authenticated: bool = Depends(verify_credentials),
):
    return Crud.update(session=session, station=station)


@app.get("/api/init-stations", status_code=202)
def init_stations(
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session),
    authenticated: bool = Depends(verify_credentials),
):
    return background_tasks.add_task(Crud._init_stations, session)


def start_api(
    fastapi_instance: Optional[FastAPI] = None,
    db_config: Optional[Dict] = None,
    connector_config: Optional[Dict] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
):
    if db_config is not None:
        _update_config(Db_Config, db_config)
        Db_Config.schema = Db_Config.DB_CONFIG.get("schema")
        Db_Config.engine_string = f"postgresql://{Db_Config.DB_CONFIG['user']}:{Db_Config.DB_CONFIG['password']}@{Db_Config.DB_CONFIG['host']}:{Db_Config.DB_CONFIG['port']}/{Db_Config.DB_CONFIG['database']}"
        Db_Config.connect_args = (
            {"options": f"-c search_path={Db_Config.schema}"}
            if Db_Config.schema is not None
            else None
        )
    if connector_config is not None:
        _update_config(Connector_Config, connector_config)
    engine: Engine = create_engine(
        Db_Config.engine_string, connect_args=Db_Config.connect_args
    )
    engine.connect()
    if fastapi_instance is None:
        fastapi_instance = app
    uvicorn.run(
        fastapi_instance,
        host=host if host is not None else "0.0.0.0",
        port=port if port is not None else 8080,
    )
