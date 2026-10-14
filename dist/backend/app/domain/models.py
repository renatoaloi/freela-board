import uuid
from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ClienteModel(Base):
    __tablename__ = "clientes"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    razao_social: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    documento: Mapped[str] = mapped_column(String(14), unique=True, nullable=False, index=True)
    endereco: Mapped[str] = mapped_column(String(500), nullable=False)
    complemento: Mapped[str] = mapped_column(String(255), nullable=True)
    bairro: Mapped[str] = mapped_column(String(255), nullable=False)
    cidade: Mapped[str] = mapped_column(String(255), nullable=False)
    estado: Mapped[str] = mapped_column(String(2), nullable=False)
    cep: Mapped[str] = mapped_column(String(9), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    projetos = relationship("ProjetoModel", back_populates="cliente", cascade="all, delete-orphan")


class ProjetoModel(Base):
    __tablename__ = "projetos"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    cliente_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("clientes.id"), nullable=False, index=True
    )
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str] = mapped_column(String(1000), nullable=True)
    data_criacao: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    valor_por_hora: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    cliente = relationship("ClienteModel", back_populates="projetos")
    tarefas = relationship("TarefaModel", back_populates="projeto", cascade="all, delete-orphan")


class TarefaModel(Base):
    __tablename__ = "tarefas"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    projeto_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projetos.id"), nullable=False, index=True
    )
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    descricao: Mapped[str] = mapped_column(String(1000), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="nova")
    data_criacao: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    anexos = mapped_column(JSON, nullable=True, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    projeto = relationship("ProjetoModel", back_populates="tarefas")
    apontamentos = relationship(
        "ApontamentoModel", back_populates="tarefa", cascade="all, delete-orphan"
    )


class ApontamentoModel(Base):
    __tablename__ = "apontamentos"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    tarefa_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tarefas.id"), nullable=False, index=True
    )
    data: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
    hora_ini: Mapped[str] = mapped_column(String(5), nullable=False)
    hora_fim: Mapped[str] = mapped_column(String(5), nullable=False)
    total_horas: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    tarefa = relationship("TarefaModel", back_populates="apontamentos")


class RelatorioModel(Base):
    __tablename__ = "relatorios"
    __table_args__ = (
        UniqueConstraint("cliente_id", "mes", "ano", name="uq_relatorio_competencia"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    cliente_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("clientes.id"), nullable=False, index=True
    )
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    ano: Mapped[int] = mapped_column(Integer, nullable=False)
    total_horas: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_valor: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    data_fechamento: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )
    dados: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    cliente = relationship("ClienteModel")
    tarefas = relationship(
        "RelatorioTarefaModel", back_populates="relatorio", cascade="all, delete-orphan"
    )


class RelatorioTarefaModel(Base):
    __tablename__ = "relatorio_tarefas"
    __table_args__ = (
        UniqueConstraint("relatorio_id", "tarefa_id", name="uq_relatorio_tarefa"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    relatorio_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("relatorios.id"), nullable=False, index=True
    )
    tarefa_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tarefas.id"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    relatorio = relationship("RelatorioModel", back_populates="tarefas")


class DadosBancariosModel(Base):
    __tablename__ = "dados_bancarios"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    banco_nome: Mapped[str] = mapped_column(String(255), nullable=True)
    banco_numero: Mapped[str] = mapped_column(String(20), nullable=True)
    agencia: Mapped[str] = mapped_column(String(20), nullable=True)
    conta: Mapped[str] = mapped_column(String(30), nullable=True)
    chave_pix: Mapped[str] = mapped_column(String(255), nullable=True)
    tipo_chave_pix: Mapped[str] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), nullable=False
    )
