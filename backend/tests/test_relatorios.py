from datetime import date

import pytest


try:
    import weasyprint  # noqa: F401
    HAS_WEASYPRINT = True
except (ImportError, OSError):
    HAS_WEASYPRINT = False


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
    assert data["cliente"]["id"] == created_cliente["id"]
    assert data["cliente"]["documento"] == created_cliente["documento"]
    assert data["mes_referencia"] == f"{mes:02d}/{ano}"
    assert len(data["projetos"]) >= 1
    assert data["projetos"][0]["titulo"] == created_projeto["titulo"]
    assert data["totais"]["total_horas"] == 4.0
    valor_esperado = 4.0 * created_projeto["valor_por_hora"]
    assert data["totais"]["total_valor"] == valor_esperado
    assert len(data["projetos"][0]["tarefas"]) == 1
    assert data["projetos"][0]["tarefas"][0]["total_horas"] == 4.0


def test_relatorio_inclui_dados_bancarios(
    client, headers, created_cliente, created_projeto, created_tarefa
):
    today = date.today()
    mes, ano = today.month, today.year

    apontamento_data = {
        "tarefa_id": created_tarefa["id"],
        "data": today.isoformat(),
        "hora_ini": "08:00",
        "hora_fim": "12:00",
    }
    client.post("/api/v1/apontamentos", json=apontamento_data, headers=headers)

    client.put(
        "/api/v1/dados-bancarios",
        json={"banco_nome": "Nubank", "chave_pix": "123.456.789-00", "tipo_chave_pix": "cpf"},
        headers=headers,
    )

    response = client.get(
        f"/api/v1/relatorios?cliente_id={created_cliente['id']}&mes={mes}&ano={ano}",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["dados_bancarios"] is not None
    assert data["dados_bancarios"]["banco_nome"] == "Nubank"
    assert data["dados_bancarios"]["chave_pix"] == "123.456.789-00"
    assert data["dados_bancarios"]["tipo_chave_pix"] == "cpf"


def test_relatorio_dados_bancarios_sem_preenchimento(
    client, headers, created_cliente, created_projeto, created_tarefa
):
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
    assert data["dados_bancarios"] is None


def test_relatorio_cliente_not_found(client, headers):
    today = date.today()
    response = client.get(
        f"/api/v1/relatorios?cliente_id=nonexistent&mes={today.month}&ano={today.year}",
        headers=headers,
    )
    assert response.status_code == 404


def test_relatorio_mes_passado(client, headers, created_cliente, created_projeto, created_tarefa):
    data_passada = date(2025, 5, 15)
    apontamento_data = {
        "tarefa_id": created_tarefa["id"],
        "data": data_passada.isoformat(),
        "hora_ini": "08:00",
        "hora_fim": "12:00",
    }
    client.post("/api/v1/apontamentos", json=apontamento_data, headers=headers)

    response = client.get(
        f"/api/v1/relatorios?cliente_id={created_cliente['id']}&mes=5&ano=2025",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["cliente"]["id"] == created_cliente["id"]
    assert data["totais"]["total_horas"] == 4.0
    assert len(data["projetos"]) == 1
    assert data["projetos"][0]["total_horas"] == 4.0
    assert len(data["projetos"][0]["tarefas"]) == 1
    assert data["projetos"][0]["tarefas"][0]["total_horas"] == 4.0


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


@pytest.mark.skipif(not HAS_WEASYPRINT, reason="WeasyPrint not available")
def test_relatorio_pdf_endpoint(client, headers, created_cliente, created_projeto, created_tarefa):
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
        f"/api/v1/relatorios/pdf?cliente_id={created_cliente['id']}&mes={mes}&ano={ano}",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/pdf"
    assert response.content.startswith(b"%PDF-")


@pytest.mark.skipif(not HAS_WEASYPRINT, reason="WeasyPrint not available")
def test_relatorio_pdf_cliente_not_found(client, headers):
    today = date.today()
    response = client.get(
        f"/api/v1/relatorios/pdf?cliente_id=nonexistent&mes={today.month}&ano={today.year}",
        headers=headers,
    )
    assert response.status_code == 404


@pytest.mark.skipif(not HAS_WEASYPRINT, reason="WeasyPrint not available")
def test_relatorio_pdf_sem_apontamentos(client, headers, created_cliente):
    today = date.today()
    response = client.get(
        f"/api/v1/relatorios/pdf?cliente_id={created_cliente['id']}&mes=1&ano=2000",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/pdf"
    assert response.content.startswith(b"%PDF-")
