from typing import Optional

from sqlalchemy.orm import Session

from app.domain.models import ClienteModel
from app.infrastructure.repositories.base_repository import BaseRepository


class ClienteRepository(BaseRepository[ClienteModel]):
    def __init__(self, db: Session):
        super().__init__(ClienteModel, db)

    def find_by_documento(self, documento: str) -> Optional[ClienteModel]:
        return self.db.query(ClienteModel).filter(ClienteModel.documento == documento).first()
