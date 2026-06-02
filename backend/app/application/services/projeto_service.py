from typing import Optional

from fastapi import HTTPException, status

from app.domain.schemas import ProjetoCreate, ProjetoUpdate
from app.infrastructure.repositories.cliente_repository import ClienteRepository
from app.infrastructure.repositories.projeto_repository import ProjetoRepository


class ProjetoService:
    def __init__(
        self,
        repository: ProjetoRepository,
        cliente_repository: ClienteRepository,
    ):
        self.repository = repository
        self.cliente_repository = cliente_repository

    def create(self, data: ProjetoCreate):
        cliente = self.cliente_repository.get_by_id(data.cliente_id)
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente not found",
            )
        return self.repository.create(**data.model_dump(exclude_unset=True))

    def get_by_id(self, id: str):
        obj = self.repository.get_by_id(id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Projeto not found",
            )
        return obj

    def list_all(self, cliente_id: Optional[str] = None):
        if cliente_id:
            cliente = self.cliente_repository.get_by_id(cliente_id)
            if not cliente:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Cliente not found",
                )
            return self.repository.list_by_cliente(cliente_id)
        return self.repository.list_all()

    def update(self, id: str, data: ProjetoUpdate):
        obj = self.repository.get_by_id(id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Projeto not found",
            )
        updated = self.repository.update(id, **data.model_dump(exclude_unset=True))
        return updated

    def delete(self, id: str):
        obj = self.repository.get_by_id(id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Projeto not found",
            )
        self.repository.delete(id)
        return {"message": "Projeto deleted successfully"}
