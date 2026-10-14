import io

from PIL import Image

from app.application.services.relatorio_pdf_service import (
    MAX_DIMENSAO_IMAGEM,
    _montar_fotos_tarefa,
    _reduzir_imagem,
)
from app.core.config import settings
from app.domain.schemas import RelatorioTarefaItem


def _criar_imagem(caminho, largura, altura):
    Image.new("RGB", (largura, altura), (120, 40, 200)).save(caminho, format="PNG")
    return caminho


def montar_tarefa(tarefa_id, anexos):
    return RelatorioTarefaItem(
        tarefa_id=tarefa_id,
        titulo="Tarefa",
        total_horas=1.0,
        anexos=anexos,
    )


def test_imagem_grande_e_reduzida(monkeypatch, tmp_path):
    storage = tmp_path / "storage"
    pasta = storage / "cliente-1" / "projeto-1" / "tarefa-1"
    pasta.mkdir(parents=True)
    monkeypatch.setattr(settings, "STORAGE_PATH", str(storage))

    _criar_imagem(pasta / "foto.png", 1600, 1200)

    fotos = _montar_fotos_tarefa("cliente-1", "projeto-1", montar_tarefa("tarefa-1", ["foto.png"]))
    assert len(fotos) == 1
    assert fotos[0].startswith("data:image/jpeg;base64,")

    dados = fotos[0].split(",", 1)[1]
    reduzida = Image.open(io.BytesIO(__import__("base64").b64decode(dados)))
    assert max(reduzida.size) == MAX_DIMENSAO_IMAGEM
    assert reduzida.size == (MAX_DIMENSAO_IMAGEM, 300)


def test_imagem_pequena_nao_e_ampliada(monkeypatch, tmp_path):
    storage = tmp_path / "storage"
    pasta = storage / "cliente-1" / "projeto-1" / "tarefa-1"
    pasta.mkdir(parents=True)
    monkeypatch.setattr(settings, "STORAGE_PATH", str(storage))

    _criar_imagem(pasta / "pequena.png", 150, 90)

    conteudo, tipo = _reduzir_imagem(pasta / "pequena.png")
    assert tipo == "image/jpeg"
    assert Image.open(io.BytesIO(conteudo)).size == (150, 90)


def test_imagem_com_transparencia_vira_jpeg(monkeypatch, tmp_path):
    storage = tmp_path / "storage"
    pasta = storage / "cliente-1" / "projeto-1" / "tarefa-1"
    pasta.mkdir(parents=True)
    monkeypatch.setattr(settings, "STORAGE_PATH", str(storage))

    Image.new("RGBA", (800, 600), (10, 20, 30, 0)).save(pasta / "alfa.png")

    conteudo, tipo = _reduzir_imagem(pasta / "alfa.png")
    assert tipo == "image/jpeg"
    assert Image.open(io.BytesIO(conteudo)).mode == "RGB"


def test_svg_segue_sem_reducao(monkeypatch, tmp_path):
    storage = tmp_path / "storage"
    pasta = storage / "cliente-1" / "projeto-1" / "tarefa-1"
    pasta.mkdir(parents=True)
    monkeypatch.setattr(settings, "STORAGE_PATH", str(storage))

    (pasta / "vetor.svg").write_bytes(b"<svg xmlns='http://www.w3.org/2000/svg'></svg>")

    conteudo, tipo = _reduzir_imagem(pasta / "vetor.svg")
    assert tipo == "image/svg+xml"
    assert conteudo.startswith(b"<svg")


def test_mosaico_respeita_limite_de_dez_imagens(monkeypatch, tmp_path):
    storage = tmp_path / "storage"
    pasta = storage / "cliente-1" / "projeto-1" / "tarefa-1"
    pasta.mkdir(parents=True)
    monkeypatch.setattr(settings, "STORAGE_PATH", str(storage))

    nomes = [f"img{i}.png" for i in range(12)]
    for nome in nomes:
        _criar_imagem(pasta / nome, 500, 400)

    fotos = _montar_fotos_tarefa("cliente-1", "projeto-1", montar_tarefa("tarefa-1", nomes))
    assert len(fotos) == 10


def test_anexo_ausente_e_ignorado(monkeypatch, tmp_path):
    storage = tmp_path / "storage"
    (storage / "cliente-1" / "projeto-1" / "tarefa-1").mkdir(parents=True)
    monkeypatch.setattr(settings, "STORAGE_PATH", str(storage))

    fotos = _montar_fotos_tarefa(
        "cliente-1", "projeto-1", montar_tarefa("tarefa-1", ["nao-existe.png"])
    )
    assert fotos == []
