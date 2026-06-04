from enum import Enum


class TarefaStatus(str, Enum):
    NOVA = "nova"
    EM_ANDAMENTO = "em_andamento"
    PRONTA = "pronta"
    FECHADA = "fechada"


class PixKeyType(str, Enum):
    CPF = "cpf"
    CNPJ = "cnpj"
    EMAIL = "email"
    TELEFONE = "telefone"
