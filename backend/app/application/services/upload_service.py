import shutil
from pathlib import Path

from app.core.config import settings


def _caminho_anexos(cliente_id: str, projeto_id: str, tarefa_id: str) -> Path:
    base = Path(settings.STORAGE_PATH).resolve()
    return base / cliente_id / projeto_id / tarefa_id


def mover_anexos_tarefa(
    cliente_id: str,
    projeto_origem_id: str,
    projeto_destino_id: str,
    tarefa_id: str,
) -> list[tuple[Path, Path]]:
    """Move os anexos da tarefa para a pasta do projeto de destino.

    Retorna a lista de pares (novo_caminho, caminho_original) para permitir
    desfazer o movimento caso a persistência falhe.
    """
    origem = _caminho_anexos(cliente_id, projeto_origem_id, tarefa_id)
    destino = _caminho_anexos(cliente_id, projeto_destino_id, tarefa_id)

    if not origem.exists() or not origem.is_dir():
        return []

    destino.mkdir(parents=True, exist_ok=True)
    movidos: list[tuple[Path, Path]] = []
    for arquivo in origem.iterdir():
        if not arquivo.is_file():
            continue
        novo_caminho = destino / arquivo.name
        shutil.move(str(arquivo), str(novo_caminho))
        movidos.append((novo_caminho, arquivo))

    _remover_se_vazia(origem)
    return movidos


def desfazer_movimento_anexos(
    movidos: list[tuple[Path, Path]], cliente_id: str, projeto_destino_id: str, tarefa_id: str
) -> None:
    for novo_caminho, caminho_original in movidos:
        if novo_caminho.exists():
            shutil.move(str(novo_caminho), str(caminho_original))
    _remover_se_vazia(_caminho_anexos(cliente_id, projeto_destino_id, tarefa_id))


def _remover_se_vazia(diretorio: Path) -> None:
    if not diretorio.exists() or not diretorio.is_dir():
        return
    try:
        diretorio.rmdir()
    except OSError:
        pass
