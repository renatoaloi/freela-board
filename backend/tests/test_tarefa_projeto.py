import pytest

from app.core.config import settings


def mover(client, headers, tarefa_id, projeto_id):
    return client.patch(
        f"/api/v1/tarefas/{tarefa_id}/projeto",
        json={"projeto_id": projeto_id},
        headers=headers,
    )


def test_move_tarefa_para_projeto_do_mesmo_cliente(
    client, headers, created_projeto_destino, created_tarefa
):
    response = mover(client, headers, created_tarefa["id"], created_projeto_destino["id"])
    assert response.status_code == 200
    assert response.json()["projeto_id"] == created_projeto_destino["id"]

    tarefa = client.get(
        f"/api/v1/tarefas/{created_tarefa['id']}", headers=headers
    ).json()
    assert tarefa["projeto_id"] == created_projeto_destino["id"]


def test_move_mantem_apontamentos(
    client, headers, created_projeto_destino, created_tarefa, created_apontamento
):
    total_antes = client.get(
        f"/api/v1/apontamentos?tarefa_id={created_tarefa['id']}", headers=headers
    ).json()

    assert mover(
        client, headers, created_tarefa["id"], created_projeto_destino["id"]
    ).status_code == 200

    depois = client.get(
        f"/api/v1/apontamentos?tarefa_id={created_tarefa['id']}", headers=headers
    ).json()
    assert len(depois) == len(total_antes) == 1
    assert depois[0]["total_horas"] == total_antes[0]["total_horas"]


def test_move_rejeita_projeto_de_outro_cliente(
    client, headers, created_projeto, created_tarefa, sample_cliente_data
):
    outro = dict(sample_cliente_data)
    outro["documento"] = "55666777000188"
    outro_cliente = client.post("/api/v1/clientes", json=outro, headers=headers).json()
    projeto_outro_cliente = client.post(
        "/api/v1/projetos",
        json={"cliente_id": outro_cliente["id"], "titulo": "Projeto alheio", "valor_por_hora": 50.0},
        headers=headers,
    ).json()

    response = mover(client, headers, created_tarefa["id"], projeto_outro_cliente["id"])
    assert response.status_code == 400

    tarefa = client.get(
        f"/api/v1/tarefas/{created_tarefa['id']}", headers=headers
    ).json()
    assert tarefa["projeto_id"] == created_projeto["id"]


def test_move_projeto_destino_inexistente(client, headers, created_tarefa):
    response = mover(client, headers, created_tarefa["id"], "nao-existe")
    assert response.status_code == 404


def test_move_tarefa_inexistente(client, headers, created_projeto_destino):
    response = mover(client, headers, "nao-existe", created_projeto_destino["id"])
    assert response.status_code == 404


def test_move_para_o_mesmo_projeto(client, headers, created_projeto, created_tarefa):
    response = mover(client, headers, created_tarefa["id"], created_projeto["id"])
    assert response.status_code == 400

    tarefa = client.get(
        f"/api/v1/tarefas/{created_tarefa['id']}", headers=headers
    ).json()
    assert tarefa["projeto_id"] == created_projeto["id"]


def test_move_tarefa_fechada(client, headers, created_projeto, created_projeto_destino, created_tarefa):
    client.put(
        f"/api/v1/tarefas/{created_tarefa['id']}",
        json={"status": "fechada"},
        headers=headers,
    )
    response = mover(client, headers, created_tarefa["id"], created_projeto_destino["id"])
    assert response.status_code == 409

    tarefa = client.get(
        f"/api/v1/tarefas/{created_tarefa['id']}", headers=headers
    ).json()
    assert tarefa["projeto_id"] == created_projeto["id"]


def test_move_tarefa_em_relatorio_fechado(
    client, headers, created_cliente, created_projeto_destino, created_tarefa_pronta, created_apontamento_passado
):
    fechado = client.post(
        "/api/v1/fechamentos",
        json={
            "cliente_id": created_cliente["id"],
            "mes": 5,
            "ano": 2025,
            "tarefa_ids": [created_tarefa_pronta["id"]],
        },
        headers=headers,
    )
    assert fechado.status_code == 201

    response = mover(
        client, headers, created_tarefa_pronta["id"], created_projeto_destino["id"]
    )
    assert response.status_code == 409


def test_move_sem_autenticacao(client, created_projeto_destino, created_tarefa):
    response = mover(client, {}, created_tarefa["id"], created_projeto_destino["id"])
    assert response.status_code == 422

    response = mover(
        client,
        {"X-API-Key": "errada"},
        created_tarefa["id"],
        created_projeto_destino["id"],
    )
    assert response.status_code == 401


@pytest.fixture
def tarefa_com_anexo(client, headers, created_tarefa, monkeypatch, tmp_path):
    storage = tmp_path / "uploads"
    storage.mkdir()
    monkeypatch.setattr(settings, "STORAGE_PATH", str(storage))

    files = {"file": ("evidencia.txt", b"conteudo", "text/plain")}
    response = client.post(
        f"/api/v1/upload/{created_tarefa['id']}", files=files, headers=headers
    )
    assert response.status_code == 200
    return created_tarefa, response.json()["filenames"][0], storage


def test_move_realoca_anexos_no_storage(
    client, headers, created_cliente, created_projeto, created_projeto_destino, tarefa_com_anexo
):
    tarefa, filename, storage = tarefa_com_anexo
    cliente_id = created_projeto["cliente_id"]

    origem = storage / cliente_id / created_projeto["id"] / tarefa["id"]
    destino = storage / cliente_id / created_projeto_destino["id"] / tarefa["id"]
    assert (origem / filename).exists()

    response = mover(client, headers, tarefa["id"], created_projeto_destino["id"])
    assert response.status_code == 200

    assert (destino / filename).exists()
    assert not (origem / filename).exists()
    assert not origem.exists()

    download = client.get(
        f"/api/v1/upload/{tarefa['id']}/{filename}", headers=headers
    )
    assert download.status_code == 200
    assert download.content == b"conteudo"


def test_move_tarefa_sem_anexos_nao_cria_pastas(
    client, headers, created_cliente, created_projeto, created_projeto_destino, created_tarefa, monkeypatch, tmp_path
):
    storage = tmp_path / "uploads"
    storage.mkdir()
    monkeypatch.setattr(settings, "STORAGE_PATH", str(storage))

    response = mover(client, headers, created_tarefa["id"], created_projeto_destino["id"])
    assert response.status_code == 200

    cliente_id = created_projeto["cliente_id"]
    assert not (storage / cliente_id / created_projeto["id"] / created_tarefa["id"]).exists()
    assert not (storage / cliente_id / created_projeto_destino["id"] / created_tarefa["id"]).exists()
