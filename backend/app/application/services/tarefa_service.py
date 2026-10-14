from typing import Optional

from fastapi import HTTPException, status

from app.domain.enums import TarefaStatus
from app.domain.schemas import TarefaCreate, TarefaUpdate
from app.infrastructure.repositories.projeto_repository import ProjetoRepository
from app.infrastructure.repositories.tarefa_repository import TarefaRepository


class TarefaService:
    def __init__(
        self,
        repository: TarefaRepository,
        projeto_repository: ProjetoRepository,
    ):
        self.repository = repository
        self.projeto_repository = projeto_repository

    def create(self, data: TarefaCreate):
        projeto = self.projeto_repository.get_by_id(data.projeto_id)
        if not projeto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Projeto not found",
            )
        return self.repository.create(**data.model_dump(exclude_unset=True))

    def get_by_id(self, id: str):
        obj = self.repository.get_by_id(id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarefa not found",
            )
        return obj

    def list_all(
        self,
        projeto_id: Optional[str] = None,
        status: Optional[str] = None,
        mes: Optional[int] = None,
        ano: Optional[int] = None,
    ):
        return self.repository.list_all_filtered(
            projeto_id=projeto_id, status=status, mes=mes, ano=ano
        )

    def update(self, id: str, data: TarefaUpdate):
        obj = self.repository.get_by_id(id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarefa not found",
            )
        update_data = data.model_dump(exclude_unset=True)
        if "status" in update_data and update_data["status"] is not None:
            new_status = update_data["status"]
            valid_statuses = [s.value for s in TarefaStatus]
            if new_status not in valid_statuses:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid status. Must be one of: {valid_statuses}",
                )
        updated = self.repository.update(id, **update_data)
        return updated

    def delete(self, id: str):
        obj = self.repository.get_by_id(id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarefa not found",
            )
        self.repository.delete(id)
        return {"message": "Tarefa deleted successfully"}
