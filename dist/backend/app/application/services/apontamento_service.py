from datetime import datetime

from fastapi import HTTPException, status

from app.domain.schemas import ApontamentoCreate, ApontamentoUpdate
from app.infrastructure.repositories.apontamento_repository import ApontamentoRepository
from app.infrastructure.repositories.tarefa_repository import TarefaRepository


class ApontamentoService:
    def __init__(
        self,
        repository: ApontamentoRepository,
        tarefa_repository: TarefaRepository,
    ):
        self.repository = repository
        self.tarefa_repository = tarefa_repository

    def _compute_total_horas(self, hora_ini: str, hora_fim: str) -> float:
        h1, m1 = map(int, hora_ini.split(":"))
        h2, m2 = map(int, hora_fim.split(":"))
        total_minutes = (h2 * 60 + m2) - (h1 * 60 + m1)
        return round(total_minutes / 60.0, 2)

    def create(self, data: ApontamentoCreate):
        tarefa = self.tarefa_repository.get_by_id(data.tarefa_id)
        if not tarefa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarefa not found",
            )
        total_horas = self._compute_total_horas(data.hora_ini, data.hora_fim)
        return self.repository.create(
            **data.model_dump(exclude_unset=True),
            total_horas=total_horas,
        )

    def get_by_id(self, id: str):
        obj = self.repository.get_by_id(id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Apontamento not found",
            )
        return obj

    def list_by_tarefa(self, tarefa_id: str):
        tarefa = self.tarefa_repository.get_by_id(tarefa_id)
        if not tarefa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tarefa not found",
            )
        return self.repository.list_by_tarefa(tarefa_id)

    def update(self, id: str, data: ApontamentoUpdate):
        obj = self.repository.get_by_id(id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Apontamento not found",
            )
        update_data = data.model_dump(exclude_unset=True)
        hora_ini = update_data.get("hora_ini", obj.hora_ini)
        hora_fim = update_data.get("hora_fim", obj.hora_fim)
        update_data["total_horas"] = self._compute_total_horas(hora_ini, hora_fim)
        updated = self.repository.update(id, **update_data)
        return updated

    def delete(self, id: str):
        obj = self.repository.get_by_id(id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Apontamento not found",
            )
        self.repository.delete(id)
        return {"message": "Apontamento deleted successfully"}
