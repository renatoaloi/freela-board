from sqlalchemy.orm import Session

from app.domain.models import ApontamentoModel
from app.infrastructure.repositories.base_repository import BaseRepository


class ApontamentoRepository(BaseRepository[ApontamentoModel]):
    def __init__(self, db: Session):
        super().__init__(ApontamentoModel, db)

    def list_by_tarefa(self, tarefa_id: str) -> list[ApontamentoModel]:
        return (
            self.db.query(ApontamentoModel)
            .filter(ApontamentoModel.tarefa_id == tarefa_id)
            .all()
        )
