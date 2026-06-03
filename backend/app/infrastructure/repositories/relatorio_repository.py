from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.models import (
    ApontamentoModel,
    ClienteModel,
    ProjetoModel,
    TarefaModel,
)


class RelatorioRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_apontamentos_by_cliente_mes_ano(
        self, cliente_id: str, mes: int, ano: int
    ) -> list[dict]:
        results = (
            self.db.query(
                ProjetoModel.id.label("projeto_id"),
                ProjetoModel.titulo.label("projeto_titulo"),
                ProjetoModel.valor_por_hora,
                func.sum(ApontamentoModel.total_horas).label("total_horas"),
            )
            .join(TarefaModel, TarefaModel.projeto_id == ProjetoModel.id)
            .join(ApontamentoModel, ApontamentoModel.tarefa_id == TarefaModel.id)
            .filter(ProjetoModel.cliente_id == cliente_id)
            .filter(func.strftime("%m", ApontamentoModel.data) == f"{mes:02d}")
            .filter(func.strftime("%Y", ApontamentoModel.data) == str(ano))
            .group_by(ProjetoModel.id, ProjetoModel.titulo, ProjetoModel.valor_por_hora)
            .all()
        )
        return [
            {
                "projeto_id": r.projeto_id,
                "projeto_titulo": r.projeto_titulo,
                "valor_por_hora": float(r.valor_por_hora),
                "total_horas": float(r.total_horas),
            }
            for r in results
        ]

    def get_cliente_info(self, cliente_id: str):
        return (
            self.db.query(ClienteModel)
            .filter(ClienteModel.id == cliente_id)
            .first()
        )

    def get_tarefas_by_cliente_mes_ano(
        self, cliente_id: str, mes: int, ano: int
    ) -> list[dict]:
        results = (
            self.db.query(
                TarefaModel.id.label("tarefa_id"),
                TarefaModel.titulo.label("titulo"),
                TarefaModel.projeto_id.label("projeto_id"),
                func.sum(ApontamentoModel.total_horas).label("total_horas"),
            )
            .join(ApontamentoModel, ApontamentoModel.tarefa_id == TarefaModel.id)
            .join(ProjetoModel, ProjetoModel.id == TarefaModel.projeto_id)
            .filter(ProjetoModel.cliente_id == cliente_id)
            .filter(func.strftime("%m", ApontamentoModel.data) == f"{mes:02d}")
            .filter(func.strftime("%Y", ApontamentoModel.data) == str(ano))
            .group_by(TarefaModel.id, TarefaModel.titulo, TarefaModel.projeto_id)
            .all()
        )
        return [
            {
                "projeto_id": r.projeto_id,
                "tarefa_id": r.tarefa_id,
                "titulo": r.titulo,
                "total_horas": float(r.total_horas),
            }
            for r in results
        ]

    def get_tarefas_por_status(self) -> dict[str, int]:
        results = (
            self.db.query(
                TarefaModel.status,
                func.count(TarefaModel.id).label("count"),
            )
            .group_by(TarefaModel.status)
            .all()
        )
        return {r.status: r.count for r in results}

    def get_horas_por_cliente_mes(self, limit: int = 6) -> list[dict]:
        sub = (
            self.db.query(
                ProjetoModel.cliente_id,
                func.strftime("%m", ApontamentoModel.data).label("mes"),
                func.strftime("%Y", ApontamentoModel.data).label("ano"),
                func.sum(ApontamentoModel.total_horas).label("total_horas"),
            )
            .select_from(ApontamentoModel)
            .join(TarefaModel, TarefaModel.id == ApontamentoModel.tarefa_id)
            .join(ProjetoModel, ProjetoModel.id == TarefaModel.projeto_id)
            .group_by(
                ProjetoModel.cliente_id,
                func.strftime("%m", ApontamentoModel.data),
                func.strftime("%Y", ApontamentoModel.data),
            )
            .order_by(
                func.strftime("%Y", ApontamentoModel.data).desc(),
                func.strftime("%m", ApontamentoModel.data).desc(),
            )
            .limit(limit)
        ).subquery()

        results = (
            self.db.query(
                sub.c.cliente_id,
                sub.c.mes,
                sub.c.ano,
                sub.c.total_horas,
                ClienteModel.nome.label("cliente_nome"),
            )
            .join(ClienteModel, ClienteModel.id == sub.c.cliente_id)
            .all()
        )
        return [
            {
                "cliente_id": r.cliente_id,
                "cliente_nome": r.cliente_nome,
                "mes": int(r.mes),
                "ano": int(r.ano),
                "total_horas": float(r.total_horas),
            }
            for r in results
        ]

    def get_melhores_clientes(self, limit: int = 5) -> list[dict]:
        results = (
            self.db.query(
                ProjetoModel.cliente_id,
                ClienteModel.nome.label("cliente_nome"),
                func.sum(ApontamentoModel.total_horas).label("total_horas"),
                (
                    func.sum(ApontamentoModel.total_horas) * ProjetoModel.valor_por_hora
                ).label("total_valor"),
            )
            .select_from(ApontamentoModel)
            .join(TarefaModel, TarefaModel.id == ApontamentoModel.tarefa_id)
            .join(ProjetoModel, ProjetoModel.id == TarefaModel.projeto_id)
            .join(ClienteModel, ClienteModel.id == ProjetoModel.cliente_id)
            .group_by(ProjetoModel.cliente_id, ClienteModel.nome)
            .order_by(func.sum(ApontamentoModel.total_horas).desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "cliente_id": r.cliente_id,
                "cliente_nome": r.cliente_nome,
                "total_horas": float(r.total_horas),
                "total_valor": float(r.total_valor),
            }
            for r in results
        ]

    def get_melhores_projetos(self, limit: int = 5) -> list[dict]:
        results = (
            self.db.query(
                ProjetoModel.id.label("projeto_id"),
                ProjetoModel.titulo.label("projeto_titulo"),
                ClienteModel.nome.label("cliente_nome"),
                func.sum(ApontamentoModel.total_horas).label("total_horas"),
                (
                    func.sum(ApontamentoModel.total_horas) * ProjetoModel.valor_por_hora
                ).label("total_valor"),
            )
            .select_from(ApontamentoModel)
            .join(TarefaModel, TarefaModel.id == ApontamentoModel.tarefa_id)
            .join(ProjetoModel, ProjetoModel.id == TarefaModel.projeto_id)
            .join(ClienteModel, ClienteModel.id == ProjetoModel.cliente_id)
            .group_by(ProjetoModel.id, ProjetoModel.titulo, ClienteModel.nome, ProjetoModel.valor_por_hora)
            .order_by(func.sum(ApontamentoModel.total_horas).desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "projeto_id": r.projeto_id,
                "projeto_titulo": r.projeto_titulo,
                "cliente_nome": r.cliente_nome,
                "total_horas": float(r.total_horas),
                "total_valor": float(r.total_valor),
            }
            for r in results
        ]

    def get_ultimos_projetos(self, limit: int = 5) -> list[dict]:
        results = (
            self.db.query(
                ProjetoModel.id,
                ProjetoModel.titulo,
                ProjetoModel.cliente_id,
                ProjetoModel.data_criacao,
                ClienteModel.nome.label("cliente_nome"),
            )
            .join(ClienteModel, ClienteModel.id == ProjetoModel.cliente_id)
            .order_by(ProjetoModel.data_criacao.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": r.id,
                "titulo": r.titulo,
                "cliente_id": r.cliente_id,
                "cliente_nome": r.cliente_nome,
                "data_criacao": r.data_criacao.isoformat(),
            }
            for r in results
        ]
