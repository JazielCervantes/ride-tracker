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


def test_login_rate_limit_after_failed_attempts(client):
    from app.routes.auth import _failed_logins, _MAX_FAILED_ATTEMPTS

    _failed_logins.clear()
    try:
        for _ in range(_MAX_FAILED_ATTEMPTS):
            response = client.post("/auth/login", json={"username": "testuser", "password": "wrong"})
            assert response.status_code == 401

        # Con el límite alcanzado, incluso la contraseña correcta recibe 429
        response = client.post("/auth/login", json={"username": "testuser", "password": "TestPass123!"})
        assert response.status_code == 429
    finally:
        # Estado en memoria compartido: limpiarlo para no bloquear otros tests
        _failed_logins.clear()

    response = client.post("/auth/login", json={"username": "testuser", "password": "TestPass123!"})
    assert response.status_code == 200
