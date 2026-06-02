from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_api_key
from app.domain.schemas import ClienteCreate, ClienteResponse, ClienteUpdate
from app.application.services.cliente_service import ClienteService
from app.infrastructure.repositories.cliente_repository import ClienteRepository

router = APIRouter(prefix="/clientes", tags=["clientes"], dependencies=[Depends(get_api_key)])


def get_cliente_service(db: Session = Depends(get_db)) -> ClienteService:
    repository = ClienteRepository(db)
    return ClienteService(repository)


@router.post("", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def create_cliente(data: ClienteCreate, service: ClienteService = Depends(get_cliente_service)):
    return service.create(data)


@router.get("", response_model=list[ClienteResponse])
def list_clientes(service: ClienteService = Depends(get_cliente_service)):
    return service.list_all()


@router.get("/{id}", response_model=ClienteResponse)
def get_cliente(id: str, service: ClienteService = Depends(get_cliente_service)):
    return service.get_by_id(id)


@router.put("/{id}", response_model=ClienteResponse)
def update_cliente(
    id: str, data: ClienteUpdate, service: ClienteService = Depends(get_cliente_service)
):
    return service.update(id, data)


@router.delete("/{id}")
def delete_cliente(id: str, service: ClienteService = Depends(get_cliente_service)):
    return service.delete(id)
