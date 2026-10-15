from typing import Optional

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_api_key
from app.domain.schemas import (
    FechamentoCreate,
    FechamentoTarefaDisponivel,
    RelatorioResumo,
    RelatorioResponse,
)
from app.application.services.relatorio_service import DashboardService, RelatorioService
from app.application.services.relatorio_pdf_service import RelatorioPdfService
from app.infrastructure.repositories.dados_bancarios_repository import (
    DadosBancariosRepository,
)
from app.infrastructure.repositories.relatorio_repository import RelatorioRepository

router = APIRouter(tags=["relatorios"], dependencies=[Depends(get_api_key)])


def get_relatorio_service(db: Session = Depends(get_db)) -> RelatorioService:
    repository = RelatorioRepository(db)
    dados_bancarios_repository = DadosBancariosRepository(db)
    return RelatorioService(repository, dados_bancarios_repository)


def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    repository = RelatorioRepository(db)
    return DashboardService(repository)


def get_relatorio_pdf_service() -> RelatorioPdfService:
    return RelatorioPdfService()


@router.get(
    "/fechamentos/tarefas-elegiveis", response_model=list[FechamentoTarefaDisponivel]
)
def list_tarefas_elegiveis(
    cliente_id: str,
    mes: int,
    ano: int,
    projeto_id: Optional[str] = None,
    service: RelatorioService = Depends(get_relatorio_service),
):
    return service.tarefas_elegiveis(cliente_id, mes, ano, projeto_id)


@router.post("/fechamentos", response_model=RelatorioResponse, status_code=201)
def fechar_mes(
    data: FechamentoCreate,
    service: RelatorioService = Depends(get_relatorio_service),
):
    return service.fechar(data)


@router.get("/relatorios", response_model=list[RelatorioResumo])
def list_relatorios(service: RelatorioService = Depends(get_relatorio_service)):
    return service.listar()


@router.get("/relatorios/{id}", response_model=RelatorioResponse)
def get_relatorio(
    id: str,
    service: RelatorioService = Depends(get_relatorio_service),
):
    return service.obter(id)


@router.delete("/relatorios/{id}", status_code=204)
def reverter_relatorio(
    id: str,
    service: RelatorioService = Depends(get_relatorio_service),
):
    service.reverter(id)


@router.get("/relatorios/{id}/pdf")
def get_relatorio_pdf(
    id: str,
    service: RelatorioService = Depends(get_relatorio_service),
    pdf_service: RelatorioPdfService = Depends(get_relatorio_pdf_service),
):
    data = service.obter(id)
    pdf_bytes = pdf_service.generate(data)
    filename = pdf_service.filename(data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/dashboard")
def get_dashboard(service: DashboardService = Depends(get_dashboard_service)):
    return service.get_dashboard()
