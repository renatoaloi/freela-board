from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_api_key
from app.domain.schemas import RelatorioResponse
from app.application.services.relatorio_service import DashboardService, RelatorioService
from app.application.services.relatorio_pdf_service import RelatorioPdfService
from app.infrastructure.repositories.relatorio_repository import RelatorioRepository

router = APIRouter(tags=["relatorios"], dependencies=[Depends(get_api_key)])


def get_relatorio_service(db: Session = Depends(get_db)) -> RelatorioService:
    repository = RelatorioRepository(db)
    return RelatorioService(repository)


def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    repository = RelatorioRepository(db)
    return DashboardService(repository)


def get_relatorio_pdf_service() -> RelatorioPdfService:
    return RelatorioPdfService()


@router.get("/relatorios", response_model=RelatorioResponse)
def generate_relatorio(
    cliente_id: str = Query(...),
    mes: int = Query(...),
    ano: int = Query(...),
    service: RelatorioService = Depends(get_relatorio_service),
) -> RelatorioResponse:
    return service.generate(cliente_id, mes, ano)


@router.get("/relatorios/pdf")
def generate_relatorio_pdf(
    cliente_id: str = Query(...),
    mes: int = Query(...),
    ano: int = Query(...),
    relatorio_service: RelatorioService = Depends(get_relatorio_service),
    pdf_service: RelatorioPdfService = Depends(get_relatorio_pdf_service),
):
    data = relatorio_service.generate(cliente_id, mes, ano)
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
