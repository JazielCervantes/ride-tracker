def test_login_success(client):
    response = client.post("/auth/login", json={"username": "testuser", "password": "TestPass123!"})
    assert response.status_code == 200
    assert "access_token" in response.cookies


def test_login_wrong_password(client):
    response = client.post("/auth/login", json={"username": "testuser", "password": "wrong"})
    assert response.status_code == 401


def test_login_wrong_user(client):
    response = client.post("/auth/login", json={"username": "noexiste", "password": "TestPass123!"})
    assert response.status_code == 401


def test_me_authenticated(client):
    client.post("/auth/login", json={"username": "testuser", "password": "TestPass123!"})
    response = client.get("/auth/me")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_me_unauthenticated(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_logout(client):
    client.post("/auth/login", json={"username": "testuser", "password": "TestPass123!"})
    response = client.post("/auth/logout")
    assert response.status_code == 200
