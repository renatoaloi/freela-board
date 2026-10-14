from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_api_key
from app.domain.schemas import ApontamentoCreate, ApontamentoResponse, ApontamentoUpdate
from app.application.services.apontamento_service import ApontamentoService
from app.infrastructure.repositories.apontamento_repository import ApontamentoRepository
from app.infrastructure.repositories.tarefa_repository import TarefaRepository

router = APIRouter(prefix="/apontamentos", tags=["apontamentos"], dependencies=[Depends(get_api_key)])


def get_apontamento_service(db: Session = Depends(get_db)) -> ApontamentoService:
    repository = ApontamentoRepository(db)
    tarefa_repository = TarefaRepository(db)
    return ApontamentoService(repository, tarefa_repository)


@router.post("", response_model=ApontamentoResponse, status_code=status.HTTP_201_CREATED)
def create_apontamento(
    data: ApontamentoCreate, service: ApontamentoService = Depends(get_apontamento_service)
):
    return service.create(data)


@router.get("", response_model=list[ApontamentoResponse])
def list_apontamentos(
    tarefa_id: Optional[str] = Query(None),
    service: ApontamentoService = Depends(get_apontamento_service),
):
    if tarefa_id:
        return service.list_by_tarefa(tarefa_id)
    return []


@router.put("/{id}", response_model=ApontamentoResponse)
def update_apontamento(
    id: str, data: ApontamentoUpdate, service: ApontamentoService = Depends(get_apontamento_service)
):
    return service.update(id, data)


@router.delete("/{id}")
def delete_apontamento(
    id: str, service: ApontamentoService = Depends(get_apontamento_service)
):
    return service.delete(id)
