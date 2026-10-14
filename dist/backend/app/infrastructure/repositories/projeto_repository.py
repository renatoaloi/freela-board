from typing import Optional

from sqlalchemy.orm import Session

from app.domain.models import ProjetoModel
from app.infrastructure.repositories.base_repository import BaseRepository


class ProjetoRepository(BaseRepository[ProjetoModel]):
    def __init__(self, db: Session):
        super().__init__(ProjetoModel, db)

    def list_by_cliente(self, cliente_id: str) -> list[ProjetoModel]:
        return (
            self.db.query(ProjetoModel)
            .filter(ProjetoModel.cliente_id == cliente_id)
            .all()
        )
