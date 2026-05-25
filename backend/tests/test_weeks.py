from datetime import date
from app.services.week_service import get_week_start, get_week_end, get_payment_date


# --- Tests de funciones puras (sin BD) ---

def test_week_start_wednesday():
    # 20 mayo 2026 es miércoles
    assert get_week_start(date(2026, 5, 20)) == date(2026, 5, 20)


def test_week_start_thursday():
    # 21 mayo (jue) → semana desde 20 mayo (mié)
    assert get_week_start(date(2026, 5, 21)) == date(2026, 5, 20)


def test_week_start_friday():
    # 22 mayo (vie) → semana desde 20 mayo (mié)
    assert get_week_start(date(2026, 5, 22)) == date(2026, 5, 20)


def test_week_start_monday():
    # 25 mayo (lun) → semana desde 20 mayo (mié)
    assert get_week_start(date(2026, 5, 25)) == date(2026, 5, 20)


def test_week_start_tuesday():
    # 26 mayo (mar) → semana desde 20 mayo (mié)
    assert get_week_start(date(2026, 5, 26)) == date(2026, 5, 20)


def test_week_start_next_wednesday():
    # 27 mayo (mié) → nueva semana, desde 27 mayo
    assert get_week_start(date(2026, 5, 27)) == date(2026, 5, 27)


def test_week_end():
    # semana mié 20 mayo → cierra mar 26 mayo
    assert get_week_end(date(2026, 5, 20)) == date(2026, 5, 26)


def test_payment_date():
    # semana mié 20 mayo → cobro vie 29 mayo (20 + 9 días)
    assert get_payment_date(date(2026, 5, 20)) == date(2026, 5, 29)


def test_payment_date_is_friday():
    ws = date(2026, 5, 20)
    pd = get_payment_date(ws)
    assert pd.weekday() == 4  # viernes


# --- Tests de endpoints (requieren BD) ---

def test_weeks_endpoint_requires_auth(client):
    response = client.get("/weeks")
    assert response.status_code == 401


def test_current_week(client):
    client.post("/auth/login", json={"username": "testuser", "password": "TestPass123!"})
    response = client.get("/weeks/current")
    assert response.status_code == 200
    data = response.json()
    assert "week_start" in data
    assert "week_end" in data
    assert "payment_date" in data
    assert "total_trips" in data
    assert "total_income" in data
    assert data["total_trips"] == 0


def test_weeks_list_empty(client):
    client.post("/auth/login", json={"username": "testuser", "password": "TestPass123!"})
    response = client.get("/weeks")
    assert response.status_code == 200
    assert response.json() == []


def test_weeks_list_after_trips(client):
    client.post("/auth/login", json={"username": "testuser", "password": "TestPass123!"})
    client.post("/trips", json={"date": "2026-05-20", "trip_type": "individual", "client1_name": "A"})
    client.post("/trips", json={"date": "2026-05-21", "trip_type": "pair", "client1_name": "B", "client2_name": "C"})
    client.post("/trips", json={"date": "2026-05-27", "trip_type": "individual", "client1_name": "D"})

    response = client.get("/weeks")
    assert response.status_code == 200
    weeks = response.json()
    assert len(weeks) == 2

    # Semana más reciente primero
    week1 = weeks[0]
    assert week1["week_start"] == "2026-05-27"
    assert week1["total_trips"] == 1
    assert float(week1["total_income"]) == 30.0

    week2 = weeks[1]
    assert week2["week_start"] == "2026-05-20"
    assert week2["total_trips"] == 2
    assert float(week2["total_income"]) == 80.0  # 30 + 50


def test_week_detail(client):
    client.post("/auth/login", json={"username": "testuser", "password": "TestPass123!"})
    client.post("/trips", json={"date": "2026-05-20", "trip_type": "individual", "client1_name": "Juan"})
    response = client.get("/weeks/2026-05-20")
    assert response.status_code == 200
    data = response.json()
    assert data["total_trips"] == 1
    assert data["trips"] is not None
    assert len(data["trips"]) == 1
    assert data["trips"][0]["client1_name"] == "Juan"
    assert data["payment_date"] == "2026-05-29"
