from typing import Optional

from sqlalchemy import and_, exists, func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.core.database import Base
from app.domain.models import ApontamentoModel, RelatorioTarefaModel, TarefaModel
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

    def get_com_projeto(self, id: str) -> Optional[TarefaModel]:
        return (
            self.db.query(TarefaModel)
            .options(joinedload(TarefaModel.projeto))
            .filter(TarefaModel.id == id)
            .first()
        )

    def vinculada_a_relatorio(self, tarefa_id: str) -> bool:
        row = (
            self.db.query(RelatorioTarefaModel.id)
            .filter(RelatorioTarefaModel.tarefa_id == tarefa_id)
            .first()
        )
        return row is not None

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
            periodo = []
            if mes is not None:
                periodo.append(func.strftime("%m", ApontamentoModel.data) == f"{mes:02d}")
            if ano is not None:
                periodo.append(func.strftime("%Y", ApontamentoModel.data) == str(ano))

            sem_apontamento = ~exists(
                select(ApontamentoModel.id)
                .where(ApontamentoModel.tarefa_id == TarefaModel.id)
                .correlate(TarefaModel)
            )

            query = query.outerjoin(
                ApontamentoModel,
                and_(ApontamentoModel.tarefa_id == TarefaModel.id, *periodo),
            ).filter(or_(ApontamentoModel.id.is_not(None), sem_apontamento))
            query = query.distinct()
        return query.all()
