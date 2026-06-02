from typing import Optional

from sqlalchemy.orm import Session

from app.domain.models import TarefaModel
from app.infrastructure.repositories.base_repository import BaseRepository


class TarefaRepository(BaseRepository[TarefaModel]):
    def __init__(self, db: Session):
        super().__init__(TarefaModel, db)

    def list_by_projeto(self, projeto_id: str) -> list[TarefaModel]:
        return (
            self.db.query(TarefaModel)
            .filter(TarefaModel.projeto_id == projeto_id)
            .all()
        )

    def list_by_projeto_and_status(
        self, projeto_id: str, status: str
    ) -> list[TarefaModel]:
        return (
            self.db.query(TarefaModel)
            .filter(
                TarefaModel.projeto_id == projeto_id,
                TarefaModel.status == status,
            )
            .all()
        )

    def list_all_filtered(
        self, projeto_id: Optional[str] = None, status: Optional[str] = None
    ) -> list[TarefaModel]:
        query = self.db.query(TarefaModel)
        if projeto_id is not None:
            query = query.filter(TarefaModel.projeto_id == projeto_id)
        if status is not None:
            query = query.filter(TarefaModel.status == status)
        return query.all()
