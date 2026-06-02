from datetime import date


def test_relatorio_generation(client, headers, created_cliente, created_projeto, created_tarefa):
    today = date.today()
    mes, ano = today.month, today.year

    apontamento_data = {
        "tarefa_id": created_tarefa["id"],
        "data": today.isoformat(),
        "hora_ini": "08:00",
        "hora_fim": "12:00",
    }
    client.post("/api/v1/apontamentos", json=apontamento_data, headers=headers)

    response = client.get(
        f"/api/v1/relatorios?cliente_id={created_cliente['id']}&mes={mes}&ano={ano}",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["cliente_id"] == created_cliente["id"]
    assert data["mes_referencia"] == f"{mes:02d}/{ano}"
    assert len(data["projetos"]) >= 1
    assert data["total_geral_horas"] == 4.0
    valor_esperado = 4.0 * created_projeto["valor_por_hora"]
    assert data["total_geral_valor"] == valor_esperado


def test_relatorio_cliente_not_found(client, headers):
    today = date.today()
    response = client.get(
        f"/api/v1/relatorios?cliente_id=nonexistent&mes={today.month}&ano={today.year}",
        headers=headers,
    )
    assert response.status_code == 404


def test_dashboard(client, headers, created_cliente, created_projeto, created_tarefa):
    today = date.today()
    apontamento_data = {
        "tarefa_id": created_tarefa["id"],
        "data": today.isoformat(),
        "hora_ini": "08:00",
        "hora_fim": "10:00",
    }
    client.post("/api/v1/apontamentos", json=apontamento_data, headers=headers)

    response = client.get("/api/v1/dashboard", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "tarefas_por_status" in data
    assert "horas_por_cliente_mes" in data
    assert "melhores_clientes" in data
    assert "melhores_projetos" in data
    assert "ultimos_projetos" in data
