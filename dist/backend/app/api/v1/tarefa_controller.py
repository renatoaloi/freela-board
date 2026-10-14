from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_api_key
from app.domain.schemas import TarefaCreate, TarefaResponse, TarefaUpdate
from app.application.services.tarefa_service import TarefaService
from app.infrastructure.repositories.projeto_repository import ProjetoRepository
from app.infrastructure.repositories.tarefa_repository import TarefaRepository

router = APIRouter(prefix="/tarefas", tags=["tarefas"], dependencies=[Depends(get_api_key)])


def get_tarefa_service(db: Session = Depends(get_db)) -> TarefaService:
    repository = TarefaRepository(db)
    projeto_repository = ProjetoRepository(db)
    return TarefaService(repository, projeto_repository)


@router.post("", response_model=TarefaResponse, status_code=status.HTTP_201_CREATED)
def create_tarefa(data: TarefaCreate, service: TarefaService = Depends(get_tarefa_service)):
    return service.create(data)


@router.get("", response_model=list[TarefaResponse])
def list_tarefas(
    projeto_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    mes: Optional[int] = Query(None, ge=1, le=12),
    ano: Optional[int] = Query(None, ge=1900, le=9999),
    service: TarefaService = Depends(get_tarefa_service),
):
    return service.list_all(projeto_id=projeto_id, status=status, mes=mes, ano=ano)


@router.get("/{id}", response_model=TarefaResponse)
def get_tarefa(id: str, service: TarefaService = Depends(get_tarefa_service)):
    return service.get_by_id(id)


@router.put("/{id}", response_model=TarefaResponse)
def update_tarefa(
    id: str, data: TarefaUpdate, service: TarefaService = Depends(get_tarefa_service)
):
    return service.update(id, data)


@router.delete("/{id}")
def delete_tarefa(id: str, service: TarefaService = Depends(get_tarefa_service)):
    return service.delete(id)
