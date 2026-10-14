import base64
import io
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from app.core.config import settings
from app.domain.schemas import RelatorioResponse


TEMPLATE_DIR = Path(__file__).resolve().parent.parent.parent / "templates"

MAX_IMAGENS_POR_TAREFA = 10
MAX_DIMENSAO_IMAGEM = 400
QUALIDADE_JPEG = 75

IMAGE_EXTS = ("jpg", "jpeg", "png", "gif", "webp", "svg", "bmp", "ico")


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[áàâãä]", "a", text)
    text = re.sub(r"[éèêë]", "e", text)
    text = re.sub(r"[íìîï]", "i", text)
    text = re.sub(r"[óòôõö]", "o", text)
    text = re.sub(r"[úùûü]", "u", text)
    text = re.sub(r"[ç]", "c", text)
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text)
    return text.strip("-")


def _fmt_horas(valor: float) -> str:
    return f"{valor:.2f}".replace(".", ",")


def _fmt_moeda(valor: float) -> str:
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _fmt_cnpj(doc: str) -> str:
    digits = re.sub(r"\D", "", doc)
    if len(digits) == 14:
        return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"
    return doc


def _fmt_data_geracao() -> str:
    return datetime.now().strftime("%d/%m/%Y às %H:%M")


def _fmt_data(data: str) -> str:
    try:
        ano, mes, dia = data.split("-")
    except ValueError:
        return data
    return f"{dia}/{mes}/{ano}"


def _is_image(filename: str) -> bool:
    return filename.lower().split(".")[-1] in IMAGE_EXTS


def _reduzir_imagem(caminho: Path) -> tuple[bytes, str]:
    """Reduz a imagem para caber em MAX_DIMENSAO_IMAGEM e devolve (bytes, mime).

    SVG segue sem alteração (já é vetorial). Imagens menores não são ampliadas.
    """
    if caminho.suffix.lower() == ".svg":
        return caminho.read_bytes(), "image/svg+xml"

    from PIL import Image

    with Image.open(caminho) as imagem:
        imagem.thumbnail(
            (MAX_DIMENSAO_IMAGEM, MAX_DIMENSAO_IMAGEM), Image.Resampling.LANCZOS
        )
        if imagem.mode in ("RGBA", "LA", "P"):
            imagem = imagem.convert("RGB")
        buffer = io.BytesIO()
        imagem.save(buffer, format="JPEG", quality=QUALIDADE_JPEG, optimize=True)
        return buffer.getvalue(), "image/jpeg"


def _data_uri(caminho: Path) -> str:
    conteudo, tipo = _reduzir_imagem(caminho)
    return f"data:{tipo};base64,{base64.b64encode(conteudo).decode('ascii')}"


def _montar_fotos_tarefa(cliente_id: str, projeto_id: str, tarefa) -> list[str]:
    imagens = [a for a in (tarefa.anexos or []) if _is_image(a)][:MAX_IMAGENS_POR_TAREFA]
    if not imagens:
        return []

    pasta = (
        Path(settings.STORAGE_PATH).resolve() / cliente_id / projeto_id / tarefa.tarefa_id
    )
    fotos = []
    for nome in imagens:
        caminho = pasta / nome
        if not caminho.is_file():
            continue
        fotos.append(_data_uri(caminho))
    return fotos


def _colunas_imagens(quantidade: int) -> int:
    if quantidade <= 1:
        return 1
    if quantidade == 2:
        return 2
    if quantidade <= 4:
        return 2
    return 3


def _build_context(data: RelatorioResponse) -> dict[str, Any]:
    cliente = data.cliente
    totais = data.totais

    projetos = []
    for p in data.projetos:
        tarefas = []
        for t in p.tarefas:
            fotos = _montar_fotos_tarefa(cliente.id, p.projeto_id, t)
            tarefas.append(
                {
                    "titulo": t.titulo,
                    "total_horas": _fmt_horas(t.total_horas),
                    "descricao": t.descricao or "",
                    "dias": [
                        {
                            "data_formatada": _fmt_data(d.data),
                            "total_horas": _fmt_horas(d.total_horas),
                            "apontamentos": [
                                {
                                    "hora_ini": a.hora_ini,
                                    "hora_fim": a.hora_fim,
                                    "total_horas": _fmt_horas(a.total_horas),
                                }
                                for a in d.apontamentos
                            ],
                        }
                        for d in t.dias
                    ],
                    "tem_dias": bool(t.dias),
                    "imagens": fotos,
                    "tem_imagens": bool(fotos),
                    "colunas_imagens": _colunas_imagens(len(fotos)),
                }
            )
        projetos.append(
            {
                "titulo": p.titulo,
                "valor_por_hora": _fmt_moeda(p.valor_por_hora),
                "total_horas": _fmt_horas(p.total_horas),
                "valor_total": _fmt_moeda(p.valor_total),
                "tarefas": tarefas,
                "tem_tarefas": bool(tarefas),
            }
        )

    dados_bancarios = data.dados_bancarios
    tem_dados_bancarios = bool(
        dados_bancarios
        and any(
            [
                dados_bancarios.banco_nome,
                dados_bancarios.banco_numero,
                dados_bancarios.agencia,
                dados_bancarios.conta,
                dados_bancarios.chave_pix,
            ]
        )
    )

    return {
        "mes_referencia": data.mes_referencia,
        "cliente": {
            "razao_social": cliente.razao_social,
            "nome": cliente.nome,
            "documento": _fmt_cnpj(cliente.documento),
            "endereco": cliente.endereco,
            "complemento": cliente.complemento or "",
            "bairro": cliente.bairro,
            "cidade": cliente.cidade,
            "estado": cliente.estado,
            "cep": cliente.cep,
            "email": cliente.email,
        },
        "dados_bancarios": {
            "banco_nome": dados_bancarios.banco_nome if dados_bancarios else "",
            "banco_numero": dados_bancarios.banco_numero if dados_bancarios else "",
            "agencia": dados_bancarios.agencia if dados_bancarios else "",
            "conta": dados_bancarios.conta if dados_bancarios else "",
            "chave_pix": dados_bancarios.chave_pix if dados_bancarios else "",
            "tipo_chave_pix": dados_bancarios.tipo_chave_pix if dados_bancarios else "",
        },
        "tem_dados_bancarios": tem_dados_bancarios,
        "totais": {
            "total_horas": _fmt_horas(totais.total_horas),
            "total_valor": _fmt_moeda(totais.total_valor),
        },
        "projetos": projetos,
        "data_geracao": _fmt_data_geracao(),
    }


class RelatorioPdfService:
    def __init__(self) -> None:
        self._env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))

    def generate(self, data: RelatorioResponse) -> bytes:
        from weasyprint import HTML

        context = _build_context(data)
        template = self._env.get_template("relatorio_pdf.html")
        html = template.render(**context)
        return HTML(string=html).write_pdf()

    def filename(self, data: RelatorioResponse) -> str:
        slug = _slugify(data.cliente.nome)
        if not slug:
            slug = re.sub(r"[^a-zA-Z0-9]", "", data.cliente.nome).lower()[:20] or "cliente"
        mes, ano = data.mes_referencia.split("/")
        return f"{ano}-{mes}-relatorio-{slug}.pdf"
