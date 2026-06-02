import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
from app.core.config import settings
from app.main import app

TEST_DATABASE_URL = "sqlite:///./test_freelaboard.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def api_key():
    return settings.API_KEY


@pytest.fixture
def headers(api_key):
    return {"X-API-Key": api_key}


@pytest.fixture
def sample_cliente_data():
    return {
        "nome": "Cliente Teste",
        "razao_social": "Teste Ltda",
        "email": "teste@teste.com",
        "documento": "11222333000181",
        "endereco": "Rua Teste, 123",
        "complemento": "Sala 1",
        "bairro": "Centro",
        "cidade": "São Paulo",
        "estado": "SP",
    }


@pytest.fixture
def created_cliente(client, headers, sample_cliente_data):
    response = client.post("/api/v1/clientes", json=sample_cliente_data, headers=headers)
    return response.json()


@pytest.fixture
def sample_projeto_data(created_cliente):
    return {
        "cliente_id": created_cliente["id"],
        "titulo": "Projeto Teste",
        "descricao": "Descrição do projeto",
        "valor_por_hora": 150.0,
    }


@pytest.fixture
def created_projeto(client, headers, sample_projeto_data):
    response = client.post("/api/v1/projetos", json=sample_projeto_data, headers=headers)
    return response.json()


@pytest.fixture
def sample_tarefa_data(created_projeto):
    return {
        "projeto_id": created_projeto["id"],
        "titulo": "Tarefa Teste",
        "descricao": "Descrição da tarefa",
    }


@pytest.fixture
def created_tarefa(client, headers, sample_tarefa_data):
    response = client.post("/api/v1/tarefas", json=sample_tarefa_data, headers=headers)
    return response.json()


@pytest.fixture
def sample_apontamento_data(created_tarefa):
    return {
        "tarefa_id": created_tarefa["id"],
        "hora_ini": "08:00",
        "hora_fim": "12:00",
    }


@pytest.fixture
def created_apontamento(client, headers, sample_apontamento_data):
    response = client.post(
        "/api/v1/apontamentos", json=sample_apontamento_data, headers=headers
    )
    return response.json()
