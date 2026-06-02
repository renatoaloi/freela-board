def test_create_projeto(client, headers, sample_projeto_data):
    response = client.post("/api/v1/projetos", json=sample_projeto_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["titulo"] == sample_projeto_data["titulo"]
    assert data["valor_por_hora"] == sample_projeto_data["valor_por_hora"]


def test_create_projeto_invalid_cliente(client, headers, sample_projeto_data):
    data = {**sample_projeto_data, "cliente_id": "nonexistent"}
    response = client.post("/api/v1/projetos", json=data, headers=headers)
    assert response.status_code == 404


def test_list_projetos(client, headers, sample_projeto_data):
    client.post("/api/v1/projetos", json=sample_projeto_data, headers=headers)
    response = client.get("/api/v1/projetos", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_list_projetos_by_cliente(client, headers, created_cliente, sample_projeto_data):
    client.post("/api/v1/projetos", json=sample_projeto_data, headers=headers)
    response = client.get(
        f"/api/v1/projetos?cliente_id={created_cliente['id']}", headers=headers
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_projeto(client, headers, created_projeto):
    response = client.get(f"/api/v1/projetos/{created_projeto['id']}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == created_projeto["id"]


def test_update_projeto(client, headers, created_projeto):
    update_data = {"titulo": "Projeto Atualizado"}
    response = client.put(
        f"/api/v1/projetos/{created_projeto['id']}", json=update_data, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["titulo"] == "Projeto Atualizado"


def test_delete_projeto(client, headers, created_projeto):
    response = client.delete(f"/api/v1/projetos/{created_projeto['id']}", headers=headers)
    assert response.status_code == 200
    response = client.get(f"/api/v1/projetos/{created_projeto['id']}", headers=headers)
    assert response.status_code == 404
