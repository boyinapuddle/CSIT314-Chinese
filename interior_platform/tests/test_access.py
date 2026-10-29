def test_protected_route_redirects_anonymous(client):
    r=client.get('/favourites')
    assert r.status_code==302
    assert '/login' in r.location
