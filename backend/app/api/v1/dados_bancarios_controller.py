from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_api_key
from app.domain.schemas import DadosBancariosResponse, DadosBancariosUpdate
from app.application.services.dados_bancarios_service import DadosBancariosService
from app.infrastructure.repositories.dados_bancarios_repository import (
    DadosBancariosRepository,
)

router = APIRouter(
    prefix="/dados-bancarios",
    tags=["dados-bancarios"],
    dependencies=[Depends(get_api_key)],
)


def get_dados_bancarios_service(
    db: Session = Depends(get_db),
) -> DadosBancariosService:
    repository = DadosBancariosRepository(db)
    return DadosBancariosService(repository)


@router.get("", response_model=DadosBancariosResponse)
def get_dados_bancarios(
    service: DadosBancariosService = Depends(get_dados_bancarios_service),
):
    return service.get()


@router.put("", response_model=DadosBancariosResponse)
def update_dados_bancarios(
    data: DadosBancariosUpdate,
    service: DadosBancariosService = Depends(get_dados_bancarios_service),
):
    return service.update(data)