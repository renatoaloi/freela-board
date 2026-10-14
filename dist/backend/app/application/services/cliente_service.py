from typing import Optional

from fastapi import HTTPException, status

from app.domain.schemas import ClienteCreate, ClienteUpdate
from app.infrastructure.repositories.cliente_repository import ClienteRepository


class ClienteService:
    def __init__(self, repository: ClienteRepository):
        self.repository = repository

    def create(self, data: ClienteCreate):
        existing = self.repository.find_by_documento(data.documento)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cliente with this document already exists",
            )
        return self.repository.create(**data.model_dump())

    def get_by_id(self, id: str):
        obj = self.repository.get_by_id(id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente not found",
            )
        return obj

    def list_all(self):
        return self.repository.list_all()

    def update(self, id: str, data: ClienteUpdate):
        obj = self.repository.get_by_id(id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente not found",
            )
        if data.documento is not None:
            existing = self.repository.find_by_documento(data.documento)
            if existing and existing.id != id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Cliente with this document already exists",
                )
        updated = self.repository.update(id, **data.model_dump(exclude_unset=True))
        return updated

    def delete(self, id: str):
        obj = self.repository.get_by_id(id)
        if not obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente not found",
            )
        self.repository.delete(id)
        return {"message": "Cliente deleted successfully"}
