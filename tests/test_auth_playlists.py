from app import app

def test_register_login_and_playlist(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    c = app.test_client()

    assert c.post("/api/auth/register", json={"username":"alex","password":"secret"}).status_code == 200
    assert c.post("/api/auth/login", json={"username":"alex","password":"secret"}).status_code == 200

    r = c.post("/api/playlists", json={"name":"X","description":""})
    assert r.status_code == 200
    pid = r.get_json()["id"]

    assert c.post(f"/api/playlists/{pid}/items", json={"id":"demo","kind":"track"}).status_code == 200
    assert c.get("/api/playlists").status_code == 200
