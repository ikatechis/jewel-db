def test_create_item_roundtrip(client):
    body = {
        "name": "Silver Ring",
        "material": "silver",
        "price": 99.9,
        "tags": ["silver", "2025"],
    }
    # create
    r = client.post("/api/items", json=body)
    assert r.status_code == 201
    item = r.json()
    assert item["name"] == "Silver Ring"
    assert "id" in item

    # fetch list
    r2 = client.get("/api/items")
    assert r2.status_code == 200
    data = r2.json()
    assert any(it["id"] == item["id"] for it in data)
