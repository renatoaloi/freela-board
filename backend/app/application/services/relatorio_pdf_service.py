import re
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from app.domain.schemas import RelatorioResponse


TEMPLATE_DIR = Path(__file__).resolve().parent.parent.parent / "templates"


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


def _build_context(data: RelatorioResponse) -> dict[str, Any]:
    cliente = data.cliente
    totais = data.totais

    projetos = []
    for p in data.projetos:
        tarefas = [
            {"titulo": t.titulo, "total_horas": _fmt_horas(t.total_horas)}
            for t in p.tarefas
        ]
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
