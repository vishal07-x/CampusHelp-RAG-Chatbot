def test_register_student(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newstudent@example.edu",
            "password": "ValidPassword123!",
            "full_name": "New Student",
            "role": "student"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "student"
    assert data["email"] == "newstudent@example.edu"


def test_register_duplicate_email(client):
    payload = {
        "email": "dup@example.edu",
        "password": "ValidPassword123!",
        "full_name": "Duplicate User",
        "role": "student"
    }
    r1 = client.post("/api/v1/auth/register", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/api/v1/auth/register", json=payload)
    assert r2.status_code == 400
    assert "already exists" in r2.json()["detail"]


def test_login_successful(client):
    # Register first
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "login_test@example.edu",
            "password": "Password1234!",
            "full_name": "Login Tester"
        }
    )
    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "login_test@example.edu",
            "password": "Password1234!"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_login_invalid_password(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "login_test@example.edu",
            "password": "WrongPassword!"
        }
    )
    assert response.status_code == 401


def test_get_current_user_profile(client, student_token):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "student"
