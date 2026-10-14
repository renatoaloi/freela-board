def test_create_apontamento(client, headers, sample_apontamento_data):
    response = client.post(
        "/api/v1/apontamentos", json=sample_apontamento_data, headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["hora_ini"] == sample_apontamento_data["hora_ini"]
    assert data["hora_fim"] == sample_apontamento_data["hora_fim"]
    assert data["total_horas"] == 4.0


def test_apontamento_invalid_time_range(client, headers, created_tarefa):
    data = {
        "tarefa_id": created_tarefa["id"],
        "hora_ini": "14:00",
        "hora_fim": "13:00",
    }
    response = client.post("/api/v1/apontamentos", json=data, headers=headers)
    assert response.status_code == 422


def test_apontamento_total_horas(client, headers, created_tarefa):
    data = {
        "tarefa_id": created_tarefa["id"],
        "hora_ini": "09:30",
        "hora_fim": "12:45",
    }
    response = client.post("/api/v1/apontamentos", json=data, headers=headers)
    assert response.status_code == 201
    assert response.json()["total_horas"] == 3.25


def test_list_apontamentos_by_tarefa(client, headers, created_tarefa, sample_apontamento_data):
    client.post("/api/v1/apontamentos", json=sample_apontamento_data, headers=headers)
    response = client.get(
        f"/api/v1/apontamentos?tarefa_id={created_tarefa['id']}", headers=headers
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_update_apontamento(client, headers, created_apontamento):
    update_data = {"hora_ini": "10:00", "hora_fim": "14:00"}
    response = client.put(
        f"/api/v1/apontamentos/{created_apontamento['id']}",
        json=update_data,
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["total_horas"] == 4.0


def test_delete_apontamento(client, headers, created_apontamento):
    response = client.delete(
        f"/api/v1/apontamentos/{created_apontamento['id']}", headers=headers
    )
    assert response.status_code == 200
