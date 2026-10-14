from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.models import ApontamentoModel, TarefaModel
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
        self,
        projeto_id: Optional[str] = None,
        status: Optional[str] = None,
        mes: Optional[int] = None,
        ano: Optional[int] = None,
    ) -> list[TarefaModel]:
        use_competencia = mes is not None or ano is not None
        query = self.db.query(TarefaModel)
        if projeto_id is not None:
            query = query.filter(TarefaModel.projeto_id == projeto_id)
        if status is not None:
            query = query.filter(TarefaModel.status == status)
        if use_competencia:
            query = query.join(
                ApontamentoModel, ApontamentoModel.tarefa_id == TarefaModel.id
            )
            if mes is not None:
                query = query.filter(
                    func.strftime("%m", ApontamentoModel.data) == f"{mes:02d}"
                )
            if ano is not None:
                query = query.filter(
                    func.strftime("%Y", ApontamentoModel.data) == str(ano)
                )
            query = query.distinct()
        return query.all()
