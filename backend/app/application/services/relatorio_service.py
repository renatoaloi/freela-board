from typing import Optional

from collections import defaultdict

from fastapi import HTTPException, status

from app.domain.schemas import (
    RelatorioClienteInfo,
    RelatorioDadosBancariosInfo,
    RelatorioProjetoItem,
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

    def generate(self, cliente_id: str, mes: int, ano: int) -> RelatorioResponse:
        cliente = self.repository.get_cliente_info(cliente_id)
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente not found",
            )

        tarefas_rows = self.repository.get_tarefas_by_cliente_mes_ano(
            cliente_id, mes, ano
        )
        tarefas_por_projeto: dict[str, list[RelatorioTarefaItem]] = defaultdict(list)
        for t in tarefas_rows:
            tarefas_por_projeto[t["projeto_id"]].append(
                RelatorioTarefaItem(
                    tarefa_id=t["tarefa_id"],
                    titulo=t["titulo"],
                    total_horas=t["total_horas"],
                )
            )

        projetos_rows = self.repository.get_apontamentos_by_cliente_mes_ano(
            cliente_id, mes, ano
        )

        projetos: list[RelatorioProjetoItem] = []
        total_geral_horas = 0.0
        total_geral_valor = 0.0

        for p in projetos_rows:
            valor_total = round(p["total_horas"] * p["valor_por_hora"], 2)
            projetos.append(
                RelatorioProjetoItem(
                    projeto_id=p["projeto_id"],
                    titulo=p["projeto_titulo"],
                    valor_por_hora=p["valor_por_hora"],
                    total_horas=p["total_horas"],
                    valor_total=valor_total,
                    tarefas=tarefas_por_projeto.get(p["projeto_id"], []),
                )
            )
            total_geral_horas += p["total_horas"]
            total_geral_valor += valor_total

        return RelatorioResponse(
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
            mes_referencia=f"{mes:02d}/{ano}",
            totais=RelatorioTotais(
                total_horas=round(total_geral_horas, 2),
                total_valor=round(total_geral_valor, 2),
            ),
            projetos=projetos,
            dados_bancarios=self._build_dados_bancarios(),
        )

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
