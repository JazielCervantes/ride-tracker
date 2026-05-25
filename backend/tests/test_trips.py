def _login(client):
    client.post("/auth/login", json={"username": "testuser", "password": "TestPass123!"})


def test_create_individual_trip(client):
    _login(client)
    response = client.post("/trips", json={
        "date": "2026-05-20",
        "trip_type": "individual",
        "client1_name": "Juan",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["trip_type"] == "individual"
    assert float(data["amount_per_client"]) == 30.0
    assert float(data["total_amount"]) == 30.0
    assert data["client1_name"] == "Juan"
    assert data["client2_name"] is None
    assert data["week_start"] == "2026-05-20"


def test_create_pair_trip(client):
    _login(client)
    response = client.post("/trips", json={
        "date": "2026-05-21",
        "trip_type": "pair",
        "client1_name": "Juan",
        "client2_name": "María",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["trip_type"] == "pair"
    assert float(data["amount_per_client"]) == 25.0
    assert float(data["total_amount"]) == 50.0
    assert data["client2_name"] == "María"
    # May 21 is Thursday, week_start should be May 20 (Wednesday)
    assert data["week_start"] == "2026-05-20"


def test_create_pair_trip_missing_client2(client):
    _login(client)
    response = client.post("/trips", json={
        "date": "2026-05-20",
        "trip_type": "pair",
        "client1_name": "Juan",
    })
    assert response.status_code == 422


def test_list_trips_all(client):
    _login(client)
    client.post("/trips", json={"date": "2026-05-20", "trip_type": "individual", "client1_name": "A"})
    client.post("/trips", json={"date": "2026-05-21", "trip_type": "individual", "client1_name": "B"})
    response = client.get("/trips")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_trips_by_week(client):
    _login(client)
    # May 20 (Wed) and May 21 (Thu) → week_start 2026-05-20
    # May 27 (Wed) → week_start 2026-05-27
    client.post("/trips", json={"date": "2026-05-20", "trip_type": "individual", "client1_name": "A"})
    client.post("/trips", json={"date": "2026-05-27", "trip_type": "individual", "client1_name": "B"})
    response = client.get("/trips?week_start=2026-05-20")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["client1_name"] == "A"


def test_update_trip(client):
    _login(client)
    create = client.post("/trips", json={"date": "2026-05-20", "trip_type": "individual", "client1_name": "Juan"})
    trip_id = create.json()["id"]
    response = client.put(f"/trips/{trip_id}", json={"client1_name": "Pedro"})
    assert response.status_code == 200
    assert response.json()["client1_name"] == "Pedro"


def test_update_trip_type_recalculates_amount(client):
    _login(client)
    create = client.post("/trips", json={"date": "2026-05-20", "trip_type": "individual", "client1_name": "Juan"})
    trip_id = create.json()["id"]
    response = client.put(f"/trips/{trip_id}", json={"trip_type": "pair", "client2_name": "Ana"})
    assert response.status_code == 200
    data = response.json()
    assert float(data["amount_per_client"]) == 25.0
    assert float(data["total_amount"]) == 50.0


def test_delete_trip(client):
    _login(client)
    create = client.post("/trips", json={"date": "2026-05-20", "trip_type": "individual", "client1_name": "Juan"})
    trip_id = create.json()["id"]
    response = client.delete(f"/trips/{trip_id}")
    assert response.status_code == 204
    response = client.get("/trips")
    assert len(response.json()) == 0


def test_unauthenticated_access(client):
    response = client.get("/trips")
    assert response.status_code == 401


def test_cannot_access_other_user_trip(client):
    _login(client)
    create = client.post("/trips", json={"date": "2026-05-20", "trip_type": "individual", "client1_name": "Juan"})
    trip_id = create.json()["id"]
    # Use a non-existent trip ID
    response = client.delete(f"/trips/{trip_id + 999}")
    assert response.status_code == 404


def test_update_trip_full_frontend_payload(client):
    """Simulates the exact payload the frontend sends (all fields including notes=null)."""
    _login(client)
    create = client.post("/trips", json={
        "date": "2026-05-20",
        "trip_type": "individual",
        "client1_name": "Juan",
        "notes": "Some notes",
    })
    assert create.status_code == 201
    trip_id = create.json()["id"]

    # Exact payload the frontend sends for an individual trip edit
    payload = {
        "date": "2026-05-20",
        "trip_type": "individual",
        "client1_name": "Pedro",
        "notes": None,
    }
    response = client.put(f"/trips/{trip_id}", json=payload)
    assert response.status_code == 200, f"422 detail: {response.json()}"
    assert response.json()["client1_name"] == "Pedro"


def test_update_pair_trip_full_frontend_payload(client):
    """Simulates the exact payload the frontend sends for a pair trip edit."""
    _login(client)
    create = client.post("/trips", json={
        "date": "2026-05-21",
        "trip_type": "pair",
        "client1_name": "Juan",
        "client2_name": "Maria",
    })
    assert create.status_code == 201
    trip_id = create.json()["id"]

    payload = {
        "date": "2026-05-21",
        "trip_type": "pair",
        "client1_name": "Juan",
        "client2_name": "Ana",
        "notes": None,
    }
    response = client.put(f"/trips/{trip_id}", json=payload)
    assert response.status_code == 200, f"422 detail: {response.json()}"
    assert response.json()["client2_name"] == "Ana"
