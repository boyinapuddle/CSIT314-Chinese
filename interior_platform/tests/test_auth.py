def test_customer_login_success(client):
    r=client.post('/login',data={'username':'customer','password':'pass'},follow_redirects=True)
    assert r.status_code==200
    assert b'Dashboard' in r.data

def test_customer_login_rejects_bad_password(client):
    r=client.post('/login',data={'username':'customer','password':'wrong'},follow_redirects=True)
    assert b'Login failed' in r.data
