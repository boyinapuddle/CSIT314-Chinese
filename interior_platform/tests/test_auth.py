def test_customer_login_success(client):
    response = client.post(
        "/login",
        data={"username": "customer", "password": "pass"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Dashboard" in response.data


def test_customer_login_rejects_bad_password(client):
    response = client.post(
        "/login",
        data={"username": "customer", "password": "wrong"},
        follow_redirects=True,
    )
    assert b"Login failed" in response.data


def test_login_page_does_not_ask_for_account_type(client):
    response = client.get("/login")
    assert b"Account type" not in response.data
    assert b'name="role"' not in response.data
