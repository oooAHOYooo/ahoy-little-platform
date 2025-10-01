from app import app

def test_bookmarks_and_playlists(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    c = app.test_client()

    # Register & login
    assert c.post("/api/auth/register", json={"username":"alex","password":"secret"}).status_code == 200
    assert c.post("/api/auth/login", json={"username":"alex","password":"secret"}).status_code == 200

    # Bookmark toggle
    r = c.post("/api/activity/bookmark", json={"id":"demo-track-1","kind":"track"})
    assert r.status_code == 200
    assert r.get_json()["status"] in ("bookmarked", "removed")

    # Create playlist & add item
    r = c.post("/api/playlists", json={"name":"My List","description":""})
    assert r.status_code == 200
    pid = r.get_json()["playlist"]["id"]

    r = c.post(f"/api/playlists/{pid}/items", json={"id":"demo-track-1","type":"track"})
    assert r.status_code == 200

    # Confirm activity payload shape (no likes)
    r = c.get("/api/activity/me")
    assert r.status_code == 200
    me = r.get_json()
    assert "bookmarks" in me and isinstance(me["bookmarks"], list)
    assert "history" in me and isinstance(me["history"], list)
    assert "likes" not in me  # likes removed
