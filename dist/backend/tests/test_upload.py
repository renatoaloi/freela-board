import io

import pytest

from app.core.config import settings


@pytest.fixture
def upload_storage(monkeypatch, tmp_path):
    storage = tmp_path / "uploads"
    storage.mkdir()
    monkeypatch.setattr(settings, "STORAGE_PATH", str(storage))
    return storage


def test_upload_succeeds(client, headers, created_tarefa, upload_storage):
    tarefa_id = created_tarefa["id"]
    files = {"file": ("a.txt", io.BytesIO(b"hello world"), "text/plain")}
    response = client.post(f"/api/v1/upload/{tarefa_id}", files=files, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "filenames" in data
    assert len(data["filenames"]) == 1
    saved = data["filenames"][0]
    assert saved.endswith(".txt")

    on_disk = list(upload_storage.rglob(saved))
    assert len(on_disk) == 1
    assert on_disk[0].read_bytes() == b"hello world"

    tarefa_resp = client.get(f"/api/v1/tarefas/{tarefa_id}", headers=headers)
    assert tarefa_resp.status_code == 200
    assert saved in (tarefa_resp.json().get("anexos") or [])


def test_upload_wrong_field_returns_422(client, headers, created_tarefa, upload_storage):
    tarefa_id = created_tarefa["id"]
    files = {"files": ("a.txt", io.BytesIO(b"x"), "text/plain")}
    response = client.post(f"/api/v1/upload/{tarefa_id}", files=files, headers=headers)
    assert response.status_code == 422


def test_upload_missing_tarefa_returns_404(client, headers, upload_storage):
    response = client.post(
        "/api/v1/upload/00000000-0000-0000-0000-000000000000",
        files={"file": ("a.txt", io.BytesIO(b"x"), "text/plain")},
        headers=headers,
    )
    assert response.status_code == 404


def test_upload_invalid_api_key_returns_401(client, created_tarefa, upload_storage):
    tarefa_id = created_tarefa["id"]
    files = {"file": ("a.txt", io.BytesIO(b"x"), "text/plain")}
    response = client.post(
        f"/api/v1/upload/{tarefa_id}",
        files=files,
        headers={"X-API-Key": "chave-invalida"},
    )
    assert response.status_code == 401


def test_download_after_upload_returns_content(
    client, headers, created_tarefa, upload_storage
):
    tarefa_id = created_tarefa["id"]
    payload = b"binary-bytes"
    up = client.post(
        f"/api/v1/upload/{tarefa_id}",
        files={"file": ("blob.bin", io.BytesIO(payload), "application/octet-stream")},
        headers=headers,
    )
    assert up.status_code == 200
    saved = up.json()["filenames"][0]

    down = client.get(f"/api/v1/upload/{tarefa_id}/{saved}", headers=headers)
    assert down.status_code == 200
    assert down.content == payload


def test_delete_removes_file_and_anexo(
    client, headers, created_tarefa, upload_storage
):
    tarefa_id = created_tarefa["id"]
    up = client.post(
        f"/api/v1/upload/{tarefa_id}",
        files={"file": ("x.txt", io.BytesIO(b"x"), "text/plain")},
        headers=headers,
    )
    saved = up.json()["filenames"][0]
    on_disk = list(upload_storage.rglob(saved))
    assert on_disk and on_disk[0].exists()

    delete = client.delete(f"/api/v1/upload/{tarefa_id}/{saved}", headers=headers)
    assert delete.status_code == 200

    assert not on_disk[0].exists()

    tarefa_resp = client.get(f"/api/v1/tarefas/{tarefa_id}", headers=headers)
    assert saved not in (tarefa_resp.json().get("anexos") or [])
