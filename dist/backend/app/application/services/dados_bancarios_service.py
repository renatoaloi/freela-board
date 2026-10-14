from app.domain.schemas import DadosBancariosUpdate
from app.infrastructure.repositories.dados_bancarios_repository import (
    DadosBancariosRepository,
)


class DadosBancariosService:
    def __init__(self, repository: DadosBancariosRepository):
        self.repository = repository

    def get(self):
        return self.repository.get_or_create()

    def update(self, data: DadosBancariosUpdate):
        obj = self.repository.get_or_create()
        updated = self.repository.update(obj.id, **data.model_dump(exclude_unset=True))
        return updated