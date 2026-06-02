from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_api_key
from app.application.services.relatorio_service import DashboardService, RelatorioService
from app.infrastructure.repositories.relatorio_repository import RelatorioRepository

router = APIRouter(tags=["relatorios"], dependencies=[Depends(get_api_key)])


def get_relatorio_service(db: Session = Depends(get_db)) -> RelatorioService:
    repository = RelatorioRepository(db)
    return RelatorioService(repository)


def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    repository = RelatorioRepository(db)
    return DashboardService(repository)


@router.get("/relatorios")
def generate_relatorio(
    cliente_id: str = Query(...),
    mes: int = Query(...),
    ano: int = Query(...),
    service: RelatorioService = Depends(get_relatorio_service),
):
    return service.generate(cliente_id, mes, ano)


@router.get("/dashboard")
def get_dashboard(service: DashboardService = Depends(get_dashboard_service)):
    return service.get_dashboard()
