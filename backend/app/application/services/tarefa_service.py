from typing import Optional

from fastapi import HTTPException, status

from app.application.services.upload_service import (
    desfazer_movimento_anexos,
    mover_anexos_tarefa,
)
from app.domain.enums import TarefaStatus
from app.domain.schemas import TarefaCreate, TarefaProjetoUpdate, TarefaUpdate
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

    def mover_projeto(self, id: str, data: TarefaProjetoUpdate):
        tarefa = self.repository.get_com_projeto(id)
        if not tarefa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarefa not found",
            )

        destino = self.projeto_repository.get_by_id(data.projeto_id)
        if not destino:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Projeto not found",
            )

        if destino.id == tarefa.projeto_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A tarefa já está neste projeto",
            )

        projeto_atual = tarefa.projeto
        if destino.cliente_id != projeto_atual.cliente_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O projeto de destino pertence a outro cliente",
            )

        if tarefa.status == TarefaStatus.FECHADA.value:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Tarefa fechada não pode ser transferida",
            )

        if self.repository.vinculada_a_relatorio(tarefa.id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Tarefa vinculada a relatório fechado não pode ser transferida",
            )

        movidos = mover_anexos_tarefa(
            projeto_atual.cliente_id, projeto_atual.id, destino.id, tarefa.id
        )
        try:
            return self.repository.update(id, projeto_id=destino.id)
        except Exception:
            desfazer_movimento_anexos(
                movidos, projeto_atual.cliente_id, destino.id, tarefa.id
            )
            raise

    def delete(self, id: str):
        obj = self.repository.get_by_id(id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarefa not found",
            )
        self.repository.delete(id)
        return {"message": "Tarefa deleted successfully"}
