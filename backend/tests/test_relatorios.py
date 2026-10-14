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


def test_relatorio_detalhe_traz_dias_apontamentos_e_anexos(
    client, headers, created_cliente, created_tarefa_pronta, created_apontamento_passado
):
    client.post(
        "/api/v1/apontamentos",
        json={
            "tarefa_id": created_tarefa_pronta["id"],
            "data": f"{ANO}-0{MES}-20",
            "hora_ini": "14:00",
            "hora_fim": "16:00",
        },
        headers=headers,
    )
    fechado = fechar_mes(
        client, headers, created_cliente["id"], [created_tarefa_pronta["id"]]
    ).json()

    response = obtem_relatorio(client, headers, fechado["id"])
    assert response.status_code == 200
    tarefa = response.json()["projetos"][0]["tarefas"][0]

    assert [d["data"] for d in tarefa["dias"]] == [f"{ANO}-0{MES}-15", f"{ANO}-0{MES}-20"]
    assert tarefa["dias"][0]["apontamentos"] == [
        {"hora_ini": "08:00", "hora_fim": "12:00", "total_horas": 4.0}
    ]
    assert tarefa["dias"][0]["total_horas"] == 4.0
    assert tarefa["descricao"] is not None
    assert tarefa["anexos"] == []
    assert round(sum(d["total_horas"] for d in tarefa["dias"]), 2) == tarefa["total_horas"]


def test_relatorio_sem_detalhamento_para_fechamento_antigo(
    client, headers, created_cliente, created_tarefa_pronta, created_apontamento_passado
):
    """Snapshots gravados antes do detalhamento seguem sem `dias`.

    Simula o relatório legado convertendo o payload lido removendo o campo.
    """
    fechado = fechar_mes(
        client, headers, created_cliente["id"], [created_tarefa_pronta["id"]]
    ).json()
    relatorio = obtem_relatorio(client, headers, fechado["id"]).json()

    legado = dict(relatorio)
    legado["projetos"] = [
        {
            **p,
            "tarefas": [
                {
                    "tarefa_id": t["tarefa_id"],
                    "titulo": t["titulo"],
                    "total_horas": t["total_horas"],
                }
                for t in p["tarefas"]
            ],
        }
        for p in relatorio["projetos"]
    ]

    from app.domain.schemas import RelatorioResponse

    assert RelatorioResponse.model_validate(legado).projetos[0].tarefas[0].dias == []


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
    assert len(data) == 2
    ids = [t["id"] for t in data]
    assert created_tarefa_pronta["id"] in ids
    assert sem_apontamento["id"] in ids

    response = client.get(
        f"/api/v1/tarefas?projeto_id={created_projeto['id']}", headers=headers
    )
    assert len(response.json()) == 2


def test_tarefa_com_apontamento_em_outro_mes_fica_oculta(
    client,
    headers,
    created_projeto,
    created_tarefa_pronta,
    created_apontamento_passado,
):
    response = client.get(
        f"/api/v1/tarefas?projeto_id={created_projeto['id']}&mes=6&ano={ANO}",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == []

    response = client.get(
        f"/api/v1/tarefas?projeto_id={created_projeto['id']}&mes={MES}&ano=2024",
        headers=headers,
    )
    assert response.json() == []


def test_tarefa_sem_apontamento_aparece_em_qualquer_competencia(
    client,
    headers,
    created_projeto,
):
    sem_apontamento = client.post(
        "/api/v1/tarefas",
        json={"projeto_id": created_projeto["id"], "titulo": "Nova sem apontamento"},
        headers=headers,
    ).json()

    for mes in (5, 6, 12):
        response = client.get(
            f"/api/v1/tarefas?projeto_id={created_projeto['id']}&mes={mes}&ano={ANO}",
            headers=headers,
        )
        assert response.status_code == 200
        assert [t["id"] for t in response.json()] == [sem_apontamento["id"]]


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
