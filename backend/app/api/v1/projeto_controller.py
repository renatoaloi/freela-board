from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_api_key
from app.domain.schemas import ProjetoCreate, ProjetoResponse, ProjetoUpdate
from app.application.services.projeto_service import ProjetoService
from app.infrastructure.repositories.cliente_repository import ClienteRepository
from app.infrastructure.repositories.projeto_repository import ProjetoRepository

router = APIRouter(prefix="/projetos", tags=["projetos"], dependencies=[Depends(get_api_key)])


def get_projeto_service(db: Session = Depends(get_db)) -> ProjetoService:
    repository = ProjetoRepository(db)
    cliente_repository = ClienteRepository(db)
    return ProjetoService(repository, cliente_repository)


@router.post("", response_model=ProjetoResponse, status_code=status.HTTP_201_CREATED)
def create_projeto(data: ProjetoCreate, service: ProjetoService = Depends(get_projeto_service)):
    return service.create(data)


@router.get("", response_model=list[ProjetoResponse])
def list_projetos(
    cliente_id: Optional[str] = Query(None),
    service: ProjetoService = Depends(get_projeto_service),
):
    return service.list_all(cliente_id=cliente_id)


@router.get("/{id}", response_model=ProjetoResponse)
def get_projeto(id: str, service: ProjetoService = Depends(get_projeto_service)):
    return service.get_by_id(id)


@router.put("/{id}", response_model=ProjetoResponse)
def update_projeto(
    id: str, data: ProjetoUpdate, service: ProjetoService = Depends(get_projeto_service)
):
    return service.update(id, data)


@router.delete("/{id}")
def delete_projeto(id: str, service: ProjetoService = Depends(get_projeto_service)):
    return service.delete(id)
