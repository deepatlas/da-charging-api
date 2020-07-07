from typing import Optional, Dict
from fastapi.testclient import TestClient
from requests import Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.orm.scoping import ScopedSession
from starlette.status import HTTP_200_OK, HTTP_202_ACCEPTED
from charging_api.server._config import engine_string, connect_args
from charging_api.server._rest import app, get_session

engine = create_engine(engine_string, connect_args=connect_args)
engine.connect()
SessionFactory: sessionmaker = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)
Session: ScopedSession = scoped_session(SessionFactory)


def override_get_db():
    session: Optional[Session] = None
    try:
        session: Session = Session()
        yield session
    finally:
        session.close()


app.dependency_overrides[get_session] = override_get_db
client = TestClient(app)


class TestRest:
    def test_health(self):
        response: Response = client.get("/health")
        payload: Optional[Dict] = response.json()
        assert (payload.get("status") == "up") & (response.status_code == HTTP_200_OK)

    def test_create_station(self):
        assert False

    def test_read_stations(self):
        assert False

    def test_read_station(self):
        assert False

    def test_delete_station(self):
        assert False

    def test_update_station(self):
        assert False

    def test_init_stations(self):
        response: Response = client.get("/api/init-stations")
        assert response.status_code == HTTP_202_ACCEPTED
