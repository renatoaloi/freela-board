import re
from datetime import date, datetime
from typing import Any, Optional

from pydantic import field_validator, model_validator
from pydantic import BaseModel, Field

from app.domain.enums import TarefaStatus


def validate_hhmm(v: str) -> str:
    if not re.match(r"^([01]\d|2[0-3]):([0-5]\d)$", v):
        raise ValueError(f"Invalid time format: {v}. Use HH:MM")
    return v


def _format_cep(v: str) -> str:
    cleaned = re.sub(r"\D", "", v)
    if len(cleaned) != 8:
        raise ValueError("CEP must have exactly 8 digits")
    return f"{cleaned[:5]}-{cleaned[5:]}"


class ClienteCreate(BaseModel):
    nome: str = Field(..., max_length=255)
    razao_social: str = Field(..., max_length=255)
    email: str = Field(..., max_length=255)
    documento: str = Field(..., min_length=14, max_length=14)
    endereco: str = Field(..., max_length=500)
    complemento: Optional[str] = Field(None, max_length=255)
    bairro: str = Field(..., max_length=255)
    cidade: str = Field(..., max_length=255)
    estado: str = Field(..., min_length=2, max_length=2)
    cep: str = Field(..., min_length=8, max_length=9)

    @field_validator("cep")
    @classmethod
    def validate_cep(cls, v: str) -> str:
        return _format_cep(v)

    @field_validator("documento")
    @classmethod
    def validate_documento(cls, v: str) -> str:
        cleaned = re.sub(r"\D", "", v)
        if len(cleaned) != 14:
            raise ValueError("CNPJ must have exactly 14 digits")
        if cleaned == cleaned[0] * 14:
            raise ValueError("CNPJ cannot have all digits equal")
        return cleaned

    @field_validator("estado")
    @classmethod
    def validate_estado(cls, v: str) -> str:
        return v.upper()


class ClienteUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=255)
    razao_social: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    documento: Optional[str] = Field(None, min_length=14, max_length=14)
    endereco: Optional[str] = Field(None, max_length=500)
    complemento: Optional[str] = Field(None, max_length=255)
    bairro: Optional[str] = Field(None, max_length=255)
    cidade: Optional[str] = Field(None, max_length=255)
    estado: Optional[str] = Field(None, min_length=2, max_length=2)
    cep: Optional[str] = Field(None, min_length=8, max_length=9)

    @field_validator("cep")
    @classmethod
    def validate_cep(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return _format_cep(v)

    @field_validator("documento")
    @classmethod
    def validate_documento(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        cleaned = re.sub(r"\D", "", v)
        if len(cleaned) != 14:
            raise ValueError("CNPJ must have exactly 14 digits")
        if cleaned == cleaned[0] * 14:
            raise ValueError("CNPJ cannot have all digits equal")
        return cleaned

    @field_validator("estado")
    @classmethod
    def validate_estado(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        return v.upper()


class ClienteResponse(BaseModel):
    id: str
    nome: str
    razao_social: str
    email: str
    documento: str
    endereco: str
    complemento: Optional[str] = None
    bairro: str
    cidade: str
    estado: str
    cep: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjetoCreate(BaseModel):
    cliente_id: str
    titulo: str = Field(..., max_length=255)
    descricao: Optional[str] = Field(None, max_length=1000)
    data_criacao: Optional[date] = None
    valor_por_hora: float = Field(..., ge=0)


class ProjetoUpdate(BaseModel):
    titulo: Optional[str] = Field(None, max_length=255)
    descricao: Optional[str] = Field(None, max_length=1000)
    data_criacao: Optional[date] = None
    valor_por_hora: Optional[float] = Field(None, ge=0)


class ProjetoResponse(BaseModel):
    id: str
    cliente_id: str
    titulo: str
    descricao: Optional[str] = None
    data_criacao: date
    valor_por_hora: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TarefaCreate(BaseModel):
    projeto_id: str
    titulo: str = Field(..., max_length=255)
    descricao: Optional[str] = Field(None, max_length=1000)
    status: TarefaStatus = TarefaStatus.NOVA
    data_criacao: Optional[date] = None
    anexos: Optional[list[str]] = None


class TarefaUpdate(BaseModel):
    titulo: Optional[str] = Field(None, max_length=255)
    descricao: Optional[str] = Field(None, max_length=1000)
    status: Optional[TarefaStatus] = None
    data_criacao: Optional[date] = None
    anexos: Optional[list[str]] = None


class TarefaResponse(BaseModel):
    id: str
    projeto_id: str
    titulo: str
    descricao: Optional[str] = None
    status: str
    data_criacao: date
    anexos: Optional[list[Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ApontamentoCreate(BaseModel):
    tarefa_id: str
    data: Optional[date] = None
    hora_ini: str = Field(..., pattern=r"^([01]\d|2[0-3]):([0-5]\d)$")
    hora_fim: str = Field(..., pattern=r"^([01]\d|2[0-3]):([0-5]\d)$")

    @model_validator(mode="after")
    def validate_hours(self) -> "ApontamentoCreate":
        h1, m1 = map(int, self.hora_ini.split(":"))
        h2, m2 = map(int, self.hora_fim.split(":"))
        total1 = h1 * 60 + m1
        total2 = h2 * 60 + m2
        if total2 <= total1:
            raise ValueError("hora_fim must be after hora_ini")
        return self


class ApontamentoUpdate(BaseModel):
    data: Optional[date] = None
    hora_ini: Optional[str] = Field(None, pattern=r"^([01]\d|2[0-3]):([0-5]\d)$")
    hora_fim: Optional[str] = Field(None, pattern=r"^([01]\d|2[0-3]):([0-5]\d)$")


class ApontamentoResponse(BaseModel):
    id: str
    tarefa_id: str
    data: date
    hora_ini: str
    hora_fim: str
    total_horas: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjetoRelatorioItem(BaseModel):
    projeto_id: str
    projeto_titulo: str
    total_horas: float
    valor_por_hora: float
    valor_total: float


class RelatorioClienteInfo(BaseModel):
    id: str
    nome: str
    razao_social: str
    documento: str
    email: str
    endereco: str
    complemento: Optional[str] = None
    bairro: str
    cidade: str
    estado: str
    cep: str


class RelatorioTarefaItem(BaseModel):
    tarefa_id: str
    titulo: str
    total_horas: float


class RelatorioProjetoItem(BaseModel):
    projeto_id: str
    titulo: str
    valor_por_hora: float
    total_horas: float
    valor_total: float
    tarefas: list[RelatorioTarefaItem] = Field(default_factory=list)


class RelatorioTotais(BaseModel):
    total_horas: float
    total_valor: float


class RelatorioResponse(BaseModel):
    cliente: RelatorioClienteInfo
    mes_referencia: str
    totais: RelatorioTotais
    projetos: list[RelatorioProjetoItem]


class HorasPorClienteMes(BaseModel):
    cliente_id: str
    cliente_nome: str
    mes: int
    ano: int
    total_horas: float


class MelhorCliente(BaseModel):
    cliente_id: str
    cliente_nome: str
    total_horas: float
    total_valor: float


class MelhorProjeto(BaseModel):
    projeto_id: str
    projeto_titulo: str
    cliente_nome: str
    total_horas: float
    total_valor: float


class UltimoProjeto(BaseModel):
    id: str
    titulo: str
    cliente_id: str
    cliente_nome: str
    data_criacao: date


class DashboardResponse(BaseModel):
    tarefas_por_status: dict[str, int]
    horas_por_cliente_mes: list[HorasPorClienteMes]
    melhores_clientes: list[MelhorCliente]
    melhores_projetos: list[MelhorProjeto]
    ultimos_projetos: list[UltimoProjeto]
