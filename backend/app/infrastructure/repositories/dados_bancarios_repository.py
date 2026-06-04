from sqlalchemy.orm import Session

from app.domain.models import DadosBancariosModel
from app.infrastructure.repositories.base_repository import BaseRepository


class DadosBancariosRepository(BaseRepository[DadosBancariosModel]):
    def __init__(self, db: Session):
        super().__init__(DadosBancariosModel, db)

    def get_or_create(self) -> DadosBancariosModel:
        obj = self.db.query(DadosBancariosModel).first()
        if not obj:
            obj = self.create()
        return obj