def test_create_tarefa(client, headers, sample_tarefa_data):
    response = client.post("/api/v1/tarefas", json=sample_tarefa_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["titulo"] == sample_tarefa_data["titulo"]
    assert data["status"] == "nova"


def test_list_tarefas(client, headers, sample_tarefa_data):
    client.post("/api/v1/tarefas", json=sample_tarefa_data, headers=headers)
    response = client.get("/api/v1/tarefas", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_list_tarefas_by_projeto(client, headers, created_projeto, sample_tarefa_data):
    client.post("/api/v1/tarefas", json=sample_tarefa_data, headers=headers)
    response = client.get(
        f"/api/v1/tarefas?projeto_id={created_projeto['id']}", headers=headers
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_tarefa(client, headers, created_tarefa):
    response = client.get(f"/api/v1/tarefas/{created_tarefa['id']}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == created_tarefa["id"]


def test_update_tarefa_status(client, headers, created_tarefa):
    update_data = {"status": "em_andamento"}
    response = client.put(
        f"/api/v1/tarefas/{created_tarefa['id']}", json=update_data, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "em_andamento"


def test_update_tarefa_invalid_status(client, headers, created_tarefa):
    update_data = {"status": "invalido"}
    response = client.put(
        f"/api/v1/tarefas/{created_tarefa['id']}", json=update_data, headers=headers
    )
    assert response.status_code == 422


def test_delete_tarefa(client, headers, created_tarefa):
    response = client.delete(f"/api/v1/tarefas/{created_tarefa['id']}", headers=headers)
    assert response.status_code == 200
    response = client.get(f"/api/v1/tarefas/{created_tarefa['id']}", headers=headers)
    assert response.status_code == 404
