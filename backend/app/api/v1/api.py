from fastapi import APIRouter

from app.api.v1.cliente_controller import router as cliente_router
from app.api.v1.projeto_controller import router as projeto_router
from app.api.v1.tarefa_controller import router as tarefa_router
from app.api.v1.apontamento_controller import router as apontamento_router
from app.api.v1.relatorio_controller import router as relatorio_router
from app.api.v1.upload_controller import router as upload_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(cliente_router)
api_router.include_router(projeto_router)
api_router.include_router(tarefa_router)
api_router.include_router(apontamento_router)
api_router.include_router(relatorio_router)
api_router.include_router(upload_router)
