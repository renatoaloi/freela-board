import pytest

from app.core.config import settings

MES = 5
ANO = 2025


def fechar(client, headers, cliente_id, tarefa_ids, mes=MES, ano=ANO):
    return client.post(
        "/api/v1/fechamentos",
        json={
            "cliente_id": cliente_id,
            "mes": mes,
            "ano": ano,
            "tarefa_ids": tarefa_ids,
        },
        headers=headers,
    )


def elegiveis(client, headers, cliente_id, mes=MES, ano=ANO, projeto_id=None):
    params = f"cliente_id={cliente_id}&mes={mes}&ano={ano}"
    if projeto_id:
        params += f"&projeto_id={projeto_id}"
    return client.get(f"/api/v1/fechamentos/tarefas-elegiveis?{params}", headers=headers)


def test_tarefas_elegiveis_apenas_prontas_com_apontamento_no_mes(
    client, headers, created_cliente, created_tarefa_pronta, created_apontamento_passado
):
    response = elegiveis(client, headers, created_cliente["id"])
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["tarefa_id"] == created_tarefa_pronta["id"]
    assert data[0]["status"] == "pronta"
    assert data[0]["total_horas_periodo"] == 4.0


def test_tarefas_elegiveis_ignora_tarefa_fora_do_status_pronta(
    client, headers, created_cliente, created_tarefa, created_apontamento_passado
):
    assert created_tarefa["status"] == "nova"
    response = elegiveis(client, headers, created_cliente["id"])
    assert response.status_code == 200
    assert response.json() == []


def test_tarefas_elegiveis_ignora_mes_diferente(
    client, headers, created_cliente, created_tarefa_pronta, created_apontamento_passado
):
    response = elegiveis(client, headers, created_cliente["id"], mes=6, ano=ANO)
    assert response.status_code == 200
    assert response.json() == []


def test_tarefas_elegiveis_filtra_por_projeto(
    client,
    headers,
    created_cliente,
    created_projeto,
    created_tarefa_pronta,
    created_apontamento_passado,
):
    response = elegiveis(
        client, headers, created_cliente["id"], projeto_id=created_projeto["id"]
    )
    assert response.status_code == 200
    assert len(response.json()) == 1

    response = elegiveis(
        client, headers, created_cliente["id"], projeto_id="outro-projeto"
    )
    assert response.status_code == 200
    assert response.json() == []


def test_fechar_cria_relatorio_com_snapshot(
    client, headers, created_cliente, created_projeto, created_tarefa_pronta, created_apontamento_passado
):
    response = fechar(client, headers, created_cliente["id"], [created_tarefa_pronta["id"]])
    assert response.status_code == 201
    data = response.json()
    assert data["id"]
    assert data["mes_referencia"] == f"{MES:02d}/{ANO}"
    assert data["cliente"]["id"] == created_cliente["id"]
    assert data["totais"]["total_horas"] == 4.0
    assert data["totais"]["total_valor"] == 4.0 * created_projeto["valor_por_hora"]
    assert len(data["projetos"]) == 1
    assert data["projetos"][0]["titulo"] == created_projeto["titulo"]
    assert len(data["projetos"][0]["tarefas"]) == 1
    assert data["projetos"][0]["tarefas"][0]["total_horas"] == 4.0


def test_fechar_marca_tarefas_como_fechadas(
    client, headers, created_cliente, created_tarefa_pronta, created_apontamento_passado
):
    fechar(client, headers, created_cliente["id"], [created_tarefa_pronta["id"]])
    response = client.get(
        f"/api/v1/tarefas/{created_tarefa_pronta['id']}", headers=headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "fechada"


def test_fechar_snapshot_ignora_apontamento_posterior(
    client, headers, created_cliente, created_tarefa_pronta, created_apontamento_passado
):
    created = fechar(
        client, headers, created_cliente["id"], [created_tarefa_pronta["id"]]
    ).json()

    client.put(
        f"/api/v1/tarefas/{created_tarefa_pronta['id']}",
        json={"status": "pronta"},
        headers=headers,
    )
    client.post(
        "/api/v1/apontamentos",
        json={
            "tarefa_id": created_tarefa_pronta["id"],
            "data": f"{ANO}-0{MES}-20",
            "hora_ini": "08:00",
            "hora_fim": "18:00",
        },
        headers=headers,
    )

    response = client.get(f"/api/v1/relatorios/{created['id']}", headers=headers)
    assert response.status_code == 200
    assert response.json()["totais"]["total_horas"] == 4.0


def test_fechar_cliente_inexistente(client, headers):
    response = fechar(client, headers, "nonexistent", ["qualquer"])
    assert response.status_code == 404


def test_fechar_sem_tarefas(client, headers, created_cliente):
    response = fechar(client, headers, created_cliente["id"], [])
    assert response.status_code == 422


def test_fechar_tarefa_nao_elegivel(
    client, headers, created_cliente, created_tarefa, created_apontamento_passado
):
    response = fechar(client, headers, created_cliente["id"], [created_tarefa["id"]])
    assert response.status_code == 422
    tarefa = client.get(
        f"/api/v1/tarefas/{created_tarefa['id']}", headers=headers
    ).json()
    assert tarefa["status"] == "nova"


def test_fechar_tarefa_de_outro_cliente(
    client,
    headers,
    created_cliente,
    created_tarefa_pronta,
    created_apontamento_passado,
    sample_cliente_data,
):
    outro = dict(sample_cliente_data)
    outro["documento"] = "99888777000166"
    outro_cliente = client.post("/api/v1/clientes", json=outro, headers=headers).json()

    response = fechar(client, headers, outro_cliente["id"], [created_tarefa_pronta["id"]])
    assert response.status_code == 422


def test_multiplos_fechamentos_no_mesmo_cliente_e_competencia(
    client,
    headers,
    created_cliente,
    created_projeto,
    created_tarefa_pronta,
    created_apontamento_passado,
):
    """Mais de um relatório por cliente/mês passa a ser permitido."""
    primeira = client.post(
        "/api/v1/tarefas",
        json={"projeto_id": created_projeto["id"], "titulo": "Outra tarefa do mes"},
        headers=headers,
    ).json()
    client.put(
        f"/api/v1/tarefas/{primeira['id']}",
        json={"status": "pronta"},
        headers=headers,
    )
    client.post(
        "/api/v1/apontamentos",
        json={
            "tarefa_id": primeira["id"],
            "data": f"{ANO}-0{MES}-18",
            "hora_ini": "09:00",
            "hora_fim": "11:00",
        },
        headers=headers,
    )

    primeiro = fechar(
        client, headers, created_cliente["id"], [created_tarefa_pronta["id"]]
    )
    assert primeiro.status_code == 201
    assert primeiro.json()["numero"] == 1

    segundo = fechar(client, headers, created_cliente["id"], [primeira["id"]])
    assert segundo.status_code == 201
    assert segundo.json()["numero"] == 2

    lista = client.get("/api/v1/relatorios", headers=headers).json()
    assert len(lista) == 2
    assert {r["numero"] for r in lista} == {1, 2}


def test_tarefa_ja_faturada_nao_entra_em_outro_relatorio(
    client, headers, created_cliente, created_tarefa_pronta, created_apontamento_passado
):
    primeiro = fechar(
        client, headers, created_cliente["id"], [created_tarefa_pronta["id"]]
    )
    assert primeiro.status_code == 201

    segundo = fechar(
        client, headers, created_cliente["id"], [created_tarefa_pronta["id"]]
    )
    assert segundo.status_code == 422

    lista = client.get("/api/v1/relatorios", headers=headers).json()
    assert len(lista) == 1


def test_numeracao_e_independente_por_competencia(
    client,
    headers,
    created_cliente,
    created_projeto,
    created_tarefa_pronta,
    created_apontamento_passado,
):
    """Cada mês/ano tem sua própria contagem começando em 1."""
    tarefa_junho = client.post(
        "/api/v1/tarefas",
        json={"projeto_id": created_projeto["id"], "titulo": "Tarefa de junho"},
        headers=headers,
    ).json()
    client.put(
        f"/api/v1/tarefas/{tarefa_junho['id']}",
        json={"status": "pronta"},
        headers=headers,
    )
    client.post(
        "/api/v1/apontamentos",
        json={
            "tarefa_id": tarefa_junho["id"],
            "data": f"{ANO}-06-10",
            "hora_ini": "08:00",
            "hora_fim": "10:00",
        },
        headers=headers,
    )

    assert (
        fechar(
            client, headers, created_cliente["id"], [created_tarefa_pronta["id"]]
        ).json()["numero"]
        == 1
    )
    assert (
        fechar(
            client, headers, created_cliente["id"], [tarefa_junho["id"]], mes=6
        ).json()["numero"]
        == 1
    )


def test_fechar_mesmo_cliente_em_competencias_diferentes(
    client,
    headers,
    created_cliente,
    created_projeto,
    created_tarefa_pronta,
    created_apontamento_passado,
):
    primeiro = fechar(
        client, headers, created_cliente["id"], [created_tarefa_pronta["id"]]
    )
    assert primeiro.status_code == 201

    tarefa_junho = client.post(
        "/api/v1/tarefas",
        json={"projeto_id": created_projeto["id"], "titulo": "Tarefa de junho"},
        headers=headers,
    ).json()
    client.put(
        f"/api/v1/tarefas/{tarefa_junho['id']}",
        json={"status": "pronta"},
        headers=headers,
    )
    client.post(
        "/api/v1/apontamentos",
        json={
            "tarefa_id": tarefa_junho["id"],
            "data": f"{ANO}-06-10",
            "hora_ini": "08:00",
            "hora_fim": "10:00",
        },
        headers=headers,
    )

    segundo = fechar(
        client, headers, created_cliente["id"], [tarefa_junho["id"]], mes=6
    )
    assert segundo.status_code == 201
    assert segundo.json()["mes_referencia"] == f"06/{ANO}"

    lista = client.get("/api/v1/relatorios", headers=headers).json()
    assert len(lista) == 2
    assert lista[0]["ano"] == ANO and lista[0]["mes"] == 6


def test_fechar_sem_autenticacao(client, created_cliente, created_tarefa_pronta, created_apontamento_passado):
    response = fechar(client, {}, created_cliente["id"], [created_tarefa_pronta["id"]])
    assert response.status_code == 422

    response = client.post(
        "/api/v1/fechamentos",
        json={
            "cliente_id": created_cliente["id"],
            "mes": MES,
            "ano": ANO,
            "tarefa_ids": [created_tarefa_pronta["id"]],
        },
        headers={"X-API-Key": "errada"},
    )
    assert response.status_code == 401


def test_mes_invalido(
    client, headers, created_cliente, created_tarefa_pronta, created_apontamento_passado
):
    response = fechar(
        client, headers, created_cliente["id"], [created_tarefa_pronta["id"]], mes=13
    )
    assert response.status_code == 422


def test_projeto_sem_tarefa_selecionada_nao_entra_no_relatorio(
    client,
    headers,
    created_cliente,
    created_projeto,
    created_tarefa_pronta,
    created_apontamento_passado,
):
    outro_projeto = client.post(
        "/api/v1/projetos",
        json={
            "cliente_id": created_cliente["id"],
            "titulo": "Projeto Sem Seleção",
            "valor_por_hora": 100.0,
        },
        headers=headers,
    ).json()
    outra_tarefa = client.post(
        "/api/v1/tarefas",
        json={"projeto_id": outro_projeto["id"], "titulo": "Tarefa ignorada"},
        headers=headers,
    ).json()
    client.put(
        f"/api/v1/tarefas/{outra_tarefa['id']}",
        json={"status": "pronta"},
        headers=headers,
    )
    client.post(
        "/api/v1/apontamentos",
        json={
            "tarefa_id": outra_tarefa["id"],
            "data": f"{ANO}-0{MES}-10",
            "hora_ini": "08:00",
            "hora_fim": "10:00",
        },
        headers=headers,
    )

    response = fechar(
        client, headers, created_cliente["id"], [created_tarefa_pronta["id"]]
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data["projetos"]) == 1
    assert data["projetos"][0]["projeto_id"] == created_projeto["id"]
    assert data["totais"]["total_horas"] == 4.0


def test_snapshot_traz_dias_descricao_e_anexos(
    client, headers, created_cliente, created_tarefa_pronta, created_apontamento_passado
):
    client.put(
        f"/api/v1/tarefas/{created_tarefa_pronta['id']}",
        json={"descricao": "Revisao do sistema"},
        headers=headers,
    )
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

    fechado = fechar(
        client, headers, created_cliente["id"], [created_tarefa_pronta["id"]]
    ).json()
    tarefa = fechado["projetos"][0]["tarefas"][0]

    assert tarefa["descricao"] == "Revisao do sistema"
    assert tarefa["anexos"] == []
    assert [d["data"] for d in tarefa["dias"]] == [
        f"{ANO}-0{MES}-15",
        f"{ANO}-0{MES}-20",
    ]
    assert tarefa["dias"][0]["apontamentos"] == [
        {"hora_ini": "08:00", "hora_fim": "12:00", "total_horas": 4.0}
    ]
    assert tarefa["dias"][1]["total_horas"] == 2.0
    assert tarefa["total_horas"] == 6.0


def test_snapshot_ignora_apontamento_fora_da_competencia(
    client, headers, created_cliente, created_tarefa_pronta, created_apontamento_passado
):
    client.post(
        "/api/v1/apontamentos",
        json={
            "tarefa_id": created_tarefa_pronta["id"],
            "data": f"{ANO}-06-10",
            "hora_ini": "08:00",
            "hora_fim": "10:00",
        },
        headers=headers,
    )

    fechado = fechar(
        client, headers, created_cliente["id"], [created_tarefa_pronta["id"]]
    ).json()
    tarefa = fechado["projetos"][0]["tarefas"][0]

    assert [d["data"] for d in tarefa["dias"]] == [f"{ANO}-0{MES}-15"]
    assert tarefa["total_horas"] == 4.0


def test_snapshot_registra_anexos_da_tarefa(
    client,
    headers,
    created_cliente,
    created_tarefa_pronta,
    created_apontamento_passado,
    monkeypatch,
    tmp_path,
):
    storage = tmp_path / "uploads"
    storage.mkdir()
    monkeypatch.setattr(settings, "STORAGE_PATH", str(storage))

    files = {"file": ("evidencia.png", b"conteudo-binario", "image/png")}
    upload = client.post(
        f"/api/v1/upload/{created_tarefa_pronta['id']}", files=files, headers=headers
    )
    assert upload.status_code == 200

    fechado = fechar(
        client, headers, created_cliente["id"], [created_tarefa_pronta["id"]]
    ).json()
    anexos = fechado["projetos"][0]["tarefas"][0]["anexos"]
    assert len(anexos) == 1
    assert anexos[0].endswith(".png")
