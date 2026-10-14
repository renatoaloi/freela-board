import uuid
from typing import Optional

from collections import defaultdict

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.domain.enums import TarefaStatus
from app.domain.schemas import (
    FechamentoCreate,
    FechamentoTarefaDisponivel,
    RelatorioApontamentoItem,
    RelatorioClienteInfo,
    RelatorioTarefaDia,
    RelatorioDadosBancariosInfo,
    RelatorioProjetoItem,
    RelatorioResumo,
    RelatorioResponse,
    RelatorioTarefaItem,
    RelatorioTotais,
)
from app.infrastructure.repositories.dados_bancarios_repository import (
    DadosBancariosRepository,
)
from app.infrastructure.repositories.relatorio_repository import RelatorioRepository


class RelatorioService:
    def __init__(
        self,
        repository: RelatorioRepository,
        dados_bancarios_repository: DadosBancariosRepository,
    ):
        self.repository = repository
        self.dados_bancarios_repository = dados_bancarios_repository
        self.db = repository.db

    def fechar(self, data: FechamentoCreate) -> RelatorioResponse:
        cliente = self.repository.get_cliente_info(data.cliente_id)
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente not found",
            )

        ids_selecionados = list(dict.fromkeys(data.tarefa_ids))
        if not ids_selecionados:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Selecione ao menos uma tarefa para o fechamento",
            )

        if self.repository.get_relatorio_by_competencia(
            data.cliente_id, data.mes, data.ano
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe relatório fechado para este cliente neste mês/ano",
            )

        elegiveis = self.repository.get_tarefas_elegiveis_fechamento(
            data.cliente_id, data.mes, data.ano
        )
        elegiveis_por_id = {t["tarefa_id"]: t for t in elegiveis}
        vinculadas = self.repository.tarefas_vinculadas(ids_selecionados)
        invalidas = [
            t for t in ids_selecionados if t not in elegiveis_por_id or t in vinculadas
        ]
        if invalidas:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Tarefas não elegíveis para o fechamento: {', '.join(invalidas)}",
            )

        relatorio = self._build_snapshot(cliente, data, ids_selecionados, elegiveis_por_id)
        tarefas = self.repository.get_tarefas_by_ids(ids_selecionados)

        try:
            self.repository.create_relatorio(
                relatorio_id=relatorio.id,
                cliente_id=cliente.id,
                mes=data.mes,
                ano=data.ano,
                total_horas=relatorio.totais.total_horas,
                total_valor=relatorio.totais.total_valor,
                dados=relatorio.model_dump(mode="json"),
            )
            self.repository.add_tarefas_relatorio(relatorio.id, ids_selecionados)
            for tarefa in tarefas:
                tarefa.status = TarefaStatus.FECHADA.value
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe relatório fechado para este cliente neste mês/ano",
            )

        return relatorio

    def _build_snapshot(
        self,
        cliente,
        data: FechamentoCreate,
        ids_selecionados: list[str],
        elegiveis_por_id: dict[str, dict],
    ) -> RelatorioResponse:
        tarefas = self.repository.get_tarefas_by_ids(ids_selecionados)
        tarefas.sort(key=lambda t: ids_selecionados.index(t.id))
        projetos_info = {
            p.id: p
            for p in self.repository.get_projetos_by_ids(
                list({t.projeto_id for t in tarefas})
            )
        }

        apontamentos = self.repository.get_apontamentos_detalhados_por_tarefas(
            ids_selecionados, data.mes, data.ano
        )
        dias_por_tarefa = self._agrupar_apontamentos_por_dia(apontamentos)

        tarefas_por_projeto: dict[str, list[RelatorioTarefaItem]] = defaultdict(list)
        for tarefa in tarefas:
            tarefas_por_projeto[tarefa.projeto_id].append(
                RelatorioTarefaItem(
                    tarefa_id=tarefa.id,
                    titulo=tarefa.titulo,
                    total_horas=elegiveis_por_id[tarefa.id]["total_horas"],
                    descricao=tarefa.descricao,
                    anexos=list(tarefa.anexos or []),
                    dias=dias_por_tarefa.get(tarefa.id, []),
                )
            )

        projetos: list[RelatorioProjetoItem] = []
        total_geral_horas = 0.0
        total_geral_valor = 0.0
        for projeto_id, tarefas_projeto in tarefas_por_projeto.items():
            projeto = projetos_info.get(projeto_id)
            if not projeto:
                continue
            total_horas_projeto = round(sum(t.total_horas for t in tarefas_projeto), 2)
            valor_total = round(total_horas_projeto * projeto.valor_por_hora, 2)
            projetos.append(
                RelatorioProjetoItem(
                    projeto_id=projeto.id,
                    titulo=projeto.titulo,
                    valor_por_hora=projeto.valor_por_hora,
                    total_horas=total_horas_projeto,
                    valor_total=valor_total,
                    tarefas=tarefas_projeto,
                )
            )
            total_geral_horas += total_horas_projeto
            total_geral_valor += valor_total

        return RelatorioResponse(
            id=str(uuid.uuid4()),
            cliente=RelatorioClienteInfo(
                id=cliente.id,
                nome=cliente.nome,
                razao_social=cliente.razao_social,
                documento=cliente.documento,
                email=cliente.email,
                endereco=cliente.endereco,
                complemento=cliente.complemento,
                bairro=cliente.bairro,
                cidade=cliente.cidade,
                estado=cliente.estado,
                cep=cliente.cep,
            ),
            mes_referencia=f"{data.mes:02d}/{data.ano}",
            totais=RelatorioTotais(
                total_horas=round(total_geral_horas, 2),
                total_valor=round(total_geral_valor, 2),
            ),
            projetos=projetos,
            dados_bancarios=self._build_dados_bancarios(),
        )

    @staticmethod
    def _agrupar_apontamentos_por_dia(
        apontamentos: list[dict],
    ) -> dict[str, list[RelatorioTarefaDia]]:
        por_tarefa: dict[str, dict[str, RelatorioTarefaDia]] = defaultdict(dict)
        for apontamento in apontamentos:
            dia = por_tarefa[apontamento["tarefa_id"]].get(apontamento["data"])
            if not dia:
                dia = RelatorioTarefaDia(data=apontamento["data"], total_horas=0.0)
                por_tarefa[apontamento["tarefa_id"]][apontamento["data"]] = dia
            dia.apontamentos.append(
                RelatorioApontamentoItem(
                    hora_ini=apontamento["hora_ini"],
                    hora_fim=apontamento["hora_fim"],
                    total_horas=apontamento["total_horas"],
                )
            )
            dia.total_horas = round(dia.total_horas + apontamento["total_horas"], 2)

        return {
            tarefa_id: sorted(dias.values(), key=lambda d: d.data)
            for tarefa_id, dias in por_tarefa.items()
        }

    def tarefas_elegiveis(
        self, cliente_id: str, mes: int, ano: int, projeto_id: Optional[str] = None
    ) -> list[FechamentoTarefaDisponivel]:
        rows = self.repository.get_tarefas_elegiveis_fechamento(
            cliente_id, mes, ano, projeto_id
        )
        return [
            FechamentoTarefaDisponivel(
                tarefa_id=r["tarefa_id"],
                titulo=r["titulo"],
                projeto_id=r["projeto_id"],
                projeto_titulo=r["projeto_titulo"],
                status=r["status"],
                total_horas_periodo=r["total_horas"],
            )
            for r in rows
        ]

    def listar(self) -> list[RelatorioResumo]:
        return [RelatorioResumo(**r) for r in self.repository.list_relatorios()]

    def obter(self, relatorio_id: str) -> RelatorioResponse:
        row = self.repository.get_relatorio_by_id(relatorio_id)
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Relatório not found",
            )
        return RelatorioResponse.model_validate(row["dados"])

    def _build_dados_bancarios(self) -> Optional[RelatorioDadosBancariosInfo]:
        obj = self.dados_bancarios_repository.get_or_create()
        if not any(
            [obj.banco_nome, obj.banco_numero, obj.agencia, obj.conta, obj.chave_pix]
        ):
            return None
        return RelatorioDadosBancariosInfo(
            banco_nome=obj.banco_nome,
            banco_numero=obj.banco_numero,
            agencia=obj.agencia,
            conta=obj.conta,
            chave_pix=obj.chave_pix,
            tipo_chave_pix=obj.tipo_chave_pix,
        )


class DashboardService:
    def __init__(self, repository: RelatorioRepository):
        self.repository = repository

    def get_dashboard(self):
        tarefas_por_status = self.repository.get_tarefas_por_status()
        horas_por_cliente_mes = self.repository.get_horas_por_cliente_mes()
        melhores_clientes = self.repository.get_melhores_clientes()
        melhores_projetos = self.repository.get_melhores_projetos()
        ultimos_projetos = self.repository.get_ultimos_projetos()

        return {
            "tarefas_por_status": tarefas_por_status,
            "horas_por_cliente_mes": horas_por_cliente_mes,
            "melhores_clientes": melhores_clientes,
            "melhores_projetos": melhores_projetos,
            "ultimos_projetos": ultimos_projetos,
        }
