import pytest


@pytest.mark.parametrize(
    "email, password, first_name, last_name, username, status_code",
    [
        ("test@api.com", "testpassword123", "name", "lastname", "username", 200),
        ("test@api.com", "testpassword123", "name", "lastname", "username", 409),
        ("test2@api.com", "testpassword123", "name", "lastname", "username", 200),
        ("test", "testpassword123", "name", "lastname", "username", 422),
        ("test2@api", "testpassword123", "name", "lastname", "username", 422),
    ],
)
async def test_auth_flow(
    email, password, first_name, last_name, username, status_code, ac
):
    # /register
    response_register = await ac.post(
        "auth/register",
        json={
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "username": username,
        },
    )
    assert response_register.status_code == status_code
    if status_code != 200:
        return

    # /login
    response_login = await ac.post(
        "/auth/login", json={"email": email, "password": password}
    )
    assert response_login.status_code == 200
    assert ac.cookies["access_token"]

    # /me
    response_me = await ac.get(
        "/auth/me",
    )
    user = response_me.json()
    assert response_me.status_code == 200
    assert user["email"] == email
    assert user["first_name"] == first_name
    assert user["last_name"] == last_name
    assert user["username"] == username
    assert "password" not in user
    assert "hashed_password" not in user
    assert ac.cookies["access_token"]

    # /logout
    response_logout = await ac.post("/auth/logout")
    assert response_logout.status_code == 200
    assert "access_token" not in ac.cookies
