from datetime import date

import pytest


try:
    import weasyprint  # noqa: F401
    HAS_WEASYPRINT = True
except (ImportError, OSError):
    HAS_WEASYPRINT = False


MES = 5
ANO = 2025


def fechar_mes(client, headers, cliente_id, tarefa_ids):
    return client.post(
        "/api/v1/fechamentos",
        json={
            "cliente_id": cliente_id,
            "mes": MES,
            "ano": ANO,
            "tarefa_ids": tarefa_ids,
        },
        headers=headers,
    )


def lista_relatorios(client, headers):
    return client.get("/api/v1/relatorios", headers=headers)


def obtem_relatorio(client, headers, relatorio_id):
    return client.get(f"/api/v1/relatorios/{relatorio_id}", headers=headers)


def test_lista_relatorios_vazia(client, headers, created_cliente):
    response = lista_relatorios(client, headers)
    assert response.status_code == 200
    assert response.json() == []


def test_lista_relatorios(
    client, headers, created_cliente, created_projeto, created_tarefa_pronta, created_apontamento_passado
):
    fechado = fechar_mes(
        client, headers, created_cliente["id"], [created_tarefa_pronta["id"]]
    ).json()

    response = lista_relatorios(client, headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == fechado["id"]
    assert data[0]["cliente_id"] == created_cliente["id"]
    assert data[0]["cliente_nome"] == created_cliente["nome"]
    assert data[0]["mes"] == MES
    assert data[0]["ano"] == ANO
    assert data[0]["total_horas"] == 4.0
    assert data[0]["total_valor"] == 4.0 * created_projeto["valor_por_hora"]
    assert data[0]["data_fechamento"]


def test_relatorio_por_id(
    client, headers, created_cliente, created_projeto, created_tarefa_pronta, created_apontamento_passado
):
    fechado = fechar_mes(
        client, headers, created_cliente["id"], [created_tarefa_pronta["id"]]
    ).json()

    response = obtem_relatorio(client, headers, fechado["id"])
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == fechado["id"]
    assert data["cliente"]["id"] == created_cliente["id"]
    assert data["cliente"]["nome"] == created_cliente["nome"]
    assert data["cliente"]["razao_social"] == created_cliente["razao_social"]
    assert data["cliente"]["documento"] == created_cliente["documento"]
    assert data["cliente"]["email"] == created_cliente["email"]
    assert data["mes_referencia"] == f"{MES:02d}/{ANO}"
    assert data["totais"]["total_horas"] == 4.0
    assert data["totais"]["total_valor"] == 4.0 * created_projeto["valor_por_hora"]
    assert len(data["projetos"]) == 1
    assert data["projetos"][0]["titulo"] == created_projeto["titulo"]
    assert data["projetos"][0]["valor_por_hora"] == created_projeto["valor_por_hora"]
    assert len(data["projetos"][0]["tarefas"]) == 1
    assert data["projetos"][0]["tarefas"][0]["titulo"] == created_tarefa_pronta["titulo"]
    assert data["projetos"][0]["tarefas"][0]["total_horas"] == 4.0


def test_relatorio_detalhe_id_inexistente(client, headers):
    response = obtem_relatorio(client, headers, "nao-existe")
    assert response.status_code == 404


def test_relatorio_detalhe_sem_autenticacao(
    client, created_cliente, created_tarefa_pronta, created_apontamento_passado
):
    fechado = fechar_mes(
        client, {"X-API-Key": "freela-secret-key-2024"},
        created_cliente["id"],
        [created_tarefa_pronta["id"]],
    ).json()

    assert obtem_relatorio(client, {}, fechado["id"]).status_code == 422
    assert (
        obtem_relatorio(client, {"X-API-Key": "errada"}, fechado["id"]).status_code
        == 401
    )


def test_relatorio_snapshot_inclui_dados_bancarios(
    client, headers, created_cliente, created_tarefa_pronta, created_apontamento_passado
):
    client.put(
        "/api/v1/dados-bancarios",
        json={"banco_nome": "Nubank", "chave_pix": "123.456.789-00", "tipo_chave_pix": "cpf"},
        headers=headers,
    )
    fechado = fechar_mes(
        client, headers, created_cliente["id"], [created_tarefa_pronta["id"]]
    ).json()
    assert fechado["dados_bancarios"]["banco_nome"] == "Nubank"

    client.put(
        "/api/v1/dados-bancarios",
        json={"banco_nome": "Itau", "chave_pix": "123.456.789-00", "tipo_chave_pix": "cpf"},
        headers=headers,
    )

    response = obtem_relatorio(client, headers, fechado["id"])
    assert response.status_code == 200
    assert response.json()["dados_bancarios"]["banco_nome"] == "Nubank"


def test_relatorio_dados_bancarios_sem_preenchimento(
    client, headers, created_cliente, created_tarefa_pronta, created_apontamento_passado
):
    fechado = fechar_mes(
        client, headers, created_cliente["id"], [created_tarefa_pronta["id"]]
    ).json()
    assert fechado["dados_bancarios"] is None


def test_dashboard(client, headers, created_cliente, created_projeto, created_tarefa, created_apontamento_passado):
    response = client.get("/api/v1/dashboard", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "tarefas_por_status" in data
    assert "horas_por_cliente_mes" in data
    assert "melhores_clientes" in data
    assert "melhores_projetos" in data
    assert "ultimos_projetos" in data


def test_tarefas_filtradas_por_competencia(
    client,
    headers,
    created_cliente,
    created_projeto,
    created_tarefa_pronta,
    created_apontamento_passado,
):
    sem_apontamento = client.post(
        "/api/v1/tarefas",
        json={"projeto_id": created_projeto["id"], "titulo": "Sem horas no periodo"},
        headers=headers,
    ).json()

    response = client.get(
        f"/api/v1/tarefas?projeto_id={created_projeto['id']}&mes={MES}&ano={ANO}",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == created_tarefa_pronta["id"]
    assert sem_apontamento["id"] not in [t["id"] for t in data]

    response = client.get(
        f"/api/v1/tarefas?projeto_id={created_projeto['id']}", headers=headers
    )
    assert len(response.json()) == 2


@pytest.mark.skipif(not HAS_WEASYPRINT, reason="WeasyPrint not available")
def test_relatorio_pdf_por_id(
    client, headers, created_cliente, created_tarefa_pronta, created_apontamento_passado
):
    fechado = fechar_mes(
        client, headers, created_cliente["id"], [created_tarefa_pronta["id"]]
    ).json()

    response = client.get(f"/api/v1/relatorios/{fechado['id']}/pdf", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/pdf"
    assert response.content.startswith(b"%PDF-")


@pytest.mark.skipif(not HAS_WEASYPRINT, reason="WeasyPrint not available")
def test_relatorio_pdf_id_inexistente(client, headers):
    response = client.get("/api/v1/relatorios/nao-existe/pdf", headers=headers)
    assert response.status_code == 404


@pytest.mark.skipif(not HAS_WEASYPRINT, reason="WeasyPrint not available")
def test_relatorio_pdf_sem_autenticacao(
    client, created_cliente, created_tarefa_pronta, created_apontamento_passado
):
    fechado = fechar_mes(
        client,
        {"X-API-Key": "freela-secret-key-2024"},
        created_cliente["id"],
        [created_tarefa_pronta["id"]],
    ).json()

    response = client.get(
        f"/api/v1/relatorios/{fechado['id']}/pdf",
        headers={"X-API-Key": "errada"},
    )
    assert response.status_code == 401
