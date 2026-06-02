import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_api_key
from app.domain.models import TarefaModel

router = APIRouter(prefix="/upload", tags=["upload"], dependencies=[Depends(get_api_key)])


def _get_tarefa(db: Session, tarefa_id: str):
    tarefa = db.query(TarefaModel).filter(TarefaModel.id == tarefa_id).first()
    if not tarefa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tarefa not found",
        )
    return tarefa


def _get_storage_path(tarefa) -> Path:
    storage_base = Path(settings.STORAGE_PATH).resolve()
    return storage_base / tarefa.projeto.cliente_id / tarefa.projeto_id / tarefa.id


@router.post("/{tarefa_id}")
async def upload_files(
    tarefa_id: str,
    file: UploadFile,
    db: Session = Depends(get_db),
):
    tarefa = _get_tarefa(db, tarefa_id)
    upload_dir = _get_storage_path(tarefa)
    upload_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename).suffix if file.filename else ""
    unique_name = f"{uuid.uuid4()}{ext}"
    file_path = upload_dir / unique_name
    content = await file.read()
    file_path.write_bytes(content)

    current_anexos = list(tarefa.anexos or [])
    current_anexos.append(unique_name)
    tarefa.anexos = current_anexos
    db.commit()

    return {"filenames": [unique_name]}


@router.get("/{tarefa_id}/{filename}")
def download_file(
    tarefa_id: str,
    filename: str,
    db: Session = Depends(get_db),
):
    tarefa = _get_tarefa(db, tarefa_id)
    upload_dir = _get_storage_path(tarefa)
    file_path = upload_dir / filename

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    return FileResponse(str(file_path), filename=filename)


@router.delete("/{tarefa_id}/{filename}")
def delete_file(
    tarefa_id: str,
    filename: str,
    db: Session = Depends(get_db),
):
    tarefa = _get_tarefa(db, tarefa_id)
    upload_dir = _get_storage_path(tarefa)
    file_path = upload_dir / filename

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    file_path.unlink()

    current_anexos = list(tarefa.anexos or [])
    if filename in current_anexos:
        current_anexos.remove(filename)
        tarefa.anexos = current_anexos
        db.commit()

    return {"message": "File deleted successfully"}
