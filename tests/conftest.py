import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.testclient import TestClient

import backend.database as db_module
import backend.main as main_module
from backend.database import Base, get_db
from backend.main import app
from backend.models import Flight


def _noop_seed() -> None:
    return None


@pytest.fixture(autouse=True)
def memory_db(monkeypatch):
    # StaticPool: :memory: SQLite is per-connection by default; one shared connection
    # so create_all + seed + TestClient requests see the same database.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    monkeypatch.setattr(db_module, "engine", engine)
    monkeypatch.setattr(db_module, "SessionLocal", TestSessionLocal)
    monkeypatch.setattr(main_module, "engine", engine)
    monkeypatch.setattr(main_module, "SessionLocal", TestSessionLocal)
    monkeypatch.setattr(main_module, "_seed_sample_flights_if_empty", _noop_seed)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    utc = timezone.utc
    with TestSessionLocal() as session:
        session.add_all(
            [
                Flight(
                    origin="TestOrigin",
                    destination="TestDest",
                    departure_datetime=datetime(2026, 7, 1, 12, 0, tzinfo=utc),
                    duration_minutes=120,
                    price_per_seat=199.0,
                    total_seats=10,
                    available_seats=1,
                ),
                Flight(
                    origin="OtherCity",
                    destination="FarAway",
                    departure_datetime=datetime(2026, 7, 2, 8, 0, tzinfo=utc),
                    duration_minutes=180,
                    price_per_seat=299.0,
                    total_seats=10,
                    available_seats=5,
                ),
            ]
        )
        session.commit()

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.clear()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
