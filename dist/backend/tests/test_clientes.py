def test_create_cliente(client, headers, sample_cliente_data):
    response = client.post("/api/v1/clientes", json=sample_cliente_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["nome"] == sample_cliente_data["nome"]
    assert data["documento"] == sample_cliente_data["documento"]
    assert "id" in data


def test_duplicate_cnpj(client, headers, sample_cliente_data):
    client.post("/api/v1/clientes", json=sample_cliente_data, headers=headers)
    response = client.post("/api/v1/clientes", json=sample_cliente_data, headers=headers)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_list_clientes(client, headers, sample_cliente_data):
    client.post("/api/v1/clientes", json=sample_cliente_data, headers=headers)
    response = client.get("/api/v1/clientes", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_get_cliente(client, headers, created_cliente):
    response = client.get(f"/api/v1/clientes/{created_cliente['id']}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == created_cliente["id"]


def test_get_cliente_not_found(client, headers):
    response = client.get("/api/v1/clientes/nonexistent-id", headers=headers)
    assert response.status_code == 404


def test_update_cliente(client, headers, created_cliente):
    update_data = {"nome": "Nome Atualizado"}
    response = client.put(
        f"/api/v1/clientes/{created_cliente['id']}", json=update_data, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["nome"] == "Nome Atualizado"


def test_delete_cliente(client, headers, created_cliente):
    response = client.delete(f"/api/v1/clientes/{created_cliente['id']}", headers=headers)
    assert response.status_code == 200
    response = client.get(f"/api/v1/clientes/{created_cliente['id']}", headers=headers)
    assert response.status_code == 404


def test_missing_api_key(client, sample_cliente_data):
    response = client.post("/api/v1/clientes", json=sample_cliente_data)
    assert response.status_code == 422


def test_invalid_api_key(client, sample_cliente_data):
    response = client.post(
        "/api/v1/clientes", json=sample_cliente_data, headers={"X-API-Key": "wrong"}
    )
    assert response.status_code == 401
