from fastapi import HTTPException, status

from app.infrastructure.repositories.relatorio_repository import RelatorioRepository


class RelatorioService:
    def __init__(self, repository: RelatorioRepository):
        self.repository = repository

    def generate(self, cliente_id: str, mes: int, ano: int):
        cliente = self.repository.get_cliente_info(cliente_id)
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente not found",
            )

        projetos = self.repository.get_apontamentos_by_cliente_mes_ano(
            cliente_id, mes, ano
        )

        projetos_data = []
        total_geral_horas = 0.0
        total_geral_valor = 0.0

        for p in projetos:
            valor_total = p["total_horas"] * p["valor_por_hora"]
            projetos_data.append(
                {
                    "projeto_id": p["projeto_id"],
                    "projeto_titulo": p["projeto_titulo"],
                    "total_horas": p["total_horas"],
                    "valor_por_hora": p["valor_por_hora"],
                    "valor_total": round(valor_total, 2),
                }
            )
            total_geral_horas += p["total_horas"]
            total_geral_valor += valor_total

        return {
            "cliente_id": cliente.id,
            "cliente_nome": cliente.nome,
            "cliente_documento": cliente.documento,
            "mes_referencia": f"{mes:02d}/{ano}",
            "projetos": projetos_data,
            "total_geral_horas": round(total_geral_horas, 2),
            "total_geral_valor": round(total_geral_valor, 2),
        }


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
