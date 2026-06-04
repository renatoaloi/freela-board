def test_get_cria_registro_automaticamente(client, headers):
    response = client.get("/api/v1/dados-bancarios", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] is not None
    assert data["banco_nome"] is None
    assert data["banco_numero"] is None
    assert data["agencia"] is None
    assert data["conta"] is None
    assert data["chave_pix"] is None
    assert data["tipo_chave_pix"] is None


def test_get_retorna_mesmo_registro(client, headers, created_dados_bancarios):
    response = client.get("/api/v1/dados-bancarios", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == created_dados_bancarios["id"]


def test_put_atualizacao_parcial(client, headers):
    client.get("/api/v1/dados-bancarios", headers=headers)
    payload = {"banco_nome": "Nubank", "chave_pix": "123.456.789-00", "tipo_chave_pix": "cpf"}
    response = client.put("/api/v1/dados-bancarios", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["banco_nome"] == "Nubank"
    assert data["chave_pix"] == "123.456.789-00"
    assert data["tipo_chave_pix"] == "cpf"


def test_put_atualizacao_completa(client, headers):
    client.get("/api/v1/dados-bancarios", headers=headers)
    payload = {
        "banco_nome": "Banco do Brasil",
        "banco_numero": "001",
        "agencia": "1234-5",
        "conta": "67890-1",
        "chave_pix": "freela@email.com",
        "tipo_chave_pix": "email",
    }
    response = client.put("/api/v1/dados-bancarios", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["banco_nome"] == "Banco do Brasil"
    assert data["banco_numero"] == "001"
    assert data["agencia"] == "1234-5"
    assert data["conta"] == "67890-1"
    assert data["chave_pix"] == "freela@email.com"
    assert data["tipo_chave_pix"] == "email"


def test_put_tipo_chave_pix_invalido(client, headers):
    client.get("/api/v1/dados-bancarios", headers=headers)
    payload = {"tipo_chave_pix": "invalido"}
    response = client.put("/api/v1/dados-bancarios", json=payload, headers=headers)
    assert response.status_code == 422


def test_get_header_ausente_retorna_422(client):
    response = client.get("/api/v1/dados-bancarios")
    assert response.status_code == 422


def test_get_api_key_invalida_retorna_401(client):
    response = client.get("/api/v1/dados-bancarios", headers={"X-API-Key": "wrong-key"})
    assert response.status_code == 401


def test_put_header_ausente_retorna_422(client):
    response = client.put("/api/v1/dados-bancarios", json={"banco_nome": "Teste"})
    assert response.status_code == 422


def test_put_api_key_invalida_retorna_401(client):
    response = client.put(
        "/api/v1/dados-bancarios",
        json={"banco_nome": "Teste"},
        headers={"X-API-Key": "wrong-key"},
    )
    assert response.status_code == 401
