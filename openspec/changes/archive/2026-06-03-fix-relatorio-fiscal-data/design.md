## Context

O relatório de horas é gerado sob demanda pelo usuário via `GET /api/v1/relatorios?cliente_id=...&mes=...&ano=...`. O fluxo é: usuário escolhe cliente/mês/ano na UI, frontend chama o endpoint, exibe o JSON bruto mapeado em cards. Hoje a UI tem 3 cards: "Dados do Cliente", "Resumo" (totais) e "Detalhamento por Projeto" — e um quarto bloco "Tarefas" órfão (sempre vazio, porque o backend nunca envia `tarefas`).

A stack é monorepo Python/FastAPI + React/Vite single-user local, com SQLite. O schema Pydantic `RelatorioResponse` está definido em `backend/app/domain/schemas.py:195-202` mas **não está sendo usado** — o `relatorio_controller` retorna o `dict` do service sem `response_model`. Isso significa que o schema serve só de documentação mental; mudanças no service não são validadas contra ele. O repositório (`relatorio_repository.py:18-44`) já tem a query certa para projetos (agregada por mês/ano via `strftime`), mas não tem query para tarefas.

A mudança é de **escopo duplo**: (1) corrigir um bug latente de contrato (frontend lê `cliente.nome`, backend envia `cliente_nome`); (2) ampliar o conjunto de dados do relatório para suportar uso fiscal (NF). O escopo fiscal é o que faz a mudança valer a pena: sem ele, o relatório fica cosmeticamente igual mas o contador não tem o que precisa.

A app é single-user local, então breaking changes no wire format são toleráveis — só existe 1 consumer (o `RelatorioView.jsx`). Vamos refatorar limpo em vez de manter compatibilidade.

## Goals / Non-Goals

**Goals:**
- Schema do relatório aninhado e semanticamente claro (`cliente: {...}`, `totais: {...}`, `projetos: [{tarefas: [...]}]`).
- Dados fiscais completos do tomador (razao_social, documento, endereço completo, UF) suficientes para o contador emitir NF.
- Detalhamento por tarefa agrupado dentro de cada projeto (sub-bloco), para o freelancer ver onde gastou o tempo.
- `response_model=RelatorioResponse` no controller (validação OpenAPI + Swagger preciso).
- Test cobrindo mês/ano passado (regressão do `strftime`).
- Wire format breaking change, mas localizado (único consumer atualizado na mesma change).

**Non-Goals:**
- Geração de PDF server-side (`reportlab`, `weasyprint`, `jsPDF`) — fica para change separada. Por enquanto, `window.print()` resolve.
- Envio de NF eletrônica (integração com prefeitura) — fora de escopo desta change e do app como um todo.
- Caching do relatório — é gerado sob demanda, sem hot path.
- Internacionalização (formato de moeda/data) — app é pt-BR.
- Manter compatibilidade com o schema antigo (sem aliases, sem `Deprecated`). É breaking clean.
- Adicionar campos ao ClienteModel (todos os campos fiscais já existem; só não eram serializados).

## Decisions

### 1. Service retorna o Pydantic model `RelatorioResponse`, não `dict`

```python
# relatorio_service.py
def generate(self, cliente_id: str, mes: int, ano: int) -> RelatorioResponse:
    ...
    return RelatorioResponse(
        cliente=RelatorioClienteInfo(
            id=cliente.id,
            nome=cliente.nome,
            razao_social=cliente.razao_social,
            ...
        ),
        mes_referencia=f"{mes:02d}/{ano}",
        totais=RelatorioTotais(total_horas=..., total_valor=...),
        projetos=[RelatorioProjetoItem(...)],
    )
```

- **Por quê**: ganha validação automática do schema no controller (`response_model=RelatorioResponse`), o tipo aparece corretamente no Swagger, e o Pydantic cuida de serialização de `Optional`/tipos.
- **Alternativa descartada**: continuar retornando `dict` e validar manualmente — perde a validação automática e o type safety.
- **Alternativa descartada**: usar `response_model_exclude_unset=True` ou similar — over-engineering; o schema é fixo.

### 2. Schema do relatório: 4 sub-schemas + 1 raiz

```python
class RelatorioClienteInfo(BaseModel):
    id: str
    nome: str
    razao_social: str
    documento: str
    email: Optional[str] = None
    endereco: str
    complemento: Optional[str] = None
    bairro: str
    cidade: str
    estado: str

class RelatorioTarefaItem(BaseModel):
    tarefa_id: str
    titulo: str
    total_horas: float

class RelatorioProjetoItem(BaseModel):
    projeto_id: str
    titulo: str  # renomeado de projeto_titulo
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
```

- **Por quê sub-schemas**: cada sub-objeto tem responsabilidade clara,Swagger gera nomes de schema, e o service compõe o response de forma type-safe.
- **Por quê `cliente.nome` e `cliente.razao_social` separados (não só um)**: o usuário pode ter cadastrado "Imediatum" como `nome` (fantasia) e "Imediatum Tecnologia LTDA" como `razao_social` (fiscal). Na NF vai a razao_social. Na UI vai os dois lado a lado para conferência.
- **Por quê `email: Optional[str] = None` mas `endereco: str` (não Optional)**: o `ClienteModel` tem `endereco: Mapped[str] = mapped_column(String(500), nullable=False)` — é `NOT NULL` no banco. Tratar como obrigatório no response. `email` também é `NOT NULL` no model (`Mapped[str] = mapped_column(String(255), nullable=False)`), mas o frontend pode não usar — vou marcar como `str` (não `Optional`) para refletir a realidade do banco e evitar a impressão errada de que pode ser nulo. **Decisão revisada abaixo.**
- **Por quê `tarefas: list[...] = Field(default_factory=list)` (não `Optional`)**: o frontend faz `proj.tarefas.length` / `proj.tarefas.map(...)` sem guard; lista vazia é o caso comum quando o relatório tem só 1 tarefa ou 0, e simplifica a UI.

**Correção de decisão sobre `email`**: o `ClienteModel.email` é `nullable=False`. Vou marcar como `str` (não `Optional`). Mesma coisa para `endereco`, `bairro`, `cidade`, `estado`. `complemento` é `nullable=True`, então fica `Optional[str] = None`.

### 3. Repository: novo método `get_tarefas_by_cliente_mes_ano`, query separada (não subquery na de projetos)

```python
def get_tarefas_by_cliente_mes_ano(
    self, cliente_id: str, mes: int, ano: int
) -> list[dict]:
    results = (
        self.db.query(
            TarefaModel.id.label("tarefa_id"),
            TarefaModel.titulo.label("titulo"),
            TarefaModel.projeto_id.label("projeto_id"),
            func.sum(ApontamentoModel.total_horas).label("total_horas"),
        )
        .join(ApontamentoModel, ApontamentoModel.tarefa_id == TarefaModel.id)
        .join(ProjetoModel, ProjetoModel.id == TarefaModel.projeto_id)
        .filter(ProjetoModel.cliente_id == cliente_id)
        .filter(func.strftime("%m", ApontamentoModel.data) == f"{mes:02d}")
        .filter(func.strftime("%Y", ApontamentoModel.data) == str(ano))
        .group_by(TarefaModel.id, TarefaModel.titulo, TarefaModel.projeto_id)
        .all()
    )
    return [
        {
            "projeto_id": r.projeto_id,
            "tarefa_id": r.tarefa_id,
            "titulo": r.titulo,
            "total_horas": float(r.total_horas),
        }
        for r in results
    ]
```

- **Por quê query separada, não estender a de projetos**: o `get_apontamentos_by_cliente_mes_ano` (existente) agrupa por projeto, retornando totais. A de tarefas agrupa por tarefa. Combinar em uma única query com `grouping sets` ou `union` ficaria mais complexo sem ganho real (são 2 chamadas por geração de relatório, sob demanda do usuário, custo desprezível).
- **Por quê mesmo padrão de `strftime`**: a query de projetos já usa e funciona (verificado por spike). Replicar a forma reduz risco de inconsistência.
- **Alternativa descartada**: agrupar tudo no service depois de puxar apontamentos brutos — traria muito mais dados do banco do que o necessário.
- **Alternativa descartada**: `relationship` com `lazyload` ou `joinedload` — o SQLAlchemy já faz isso de forma natural via `select_from(ApontamentoModel)`, mas a forma explícita (join + group_by) é consistente com a query de projetos.

### 4. Service: zip projetos ↔ tarefas por `projeto_id` em Python

```python
# relatorio_service.py
tarefas_por_projeto: dict[str, list[RelatorioTarefaItem]] = defaultdict(list)
for t in repo.get_tarefas_by_cliente_mes_ano(cliente_id, mes, ano):
    tarefas_por_projeto[t["projeto_id"]].append(
        RelatorioTarefaItem(tarefa_id=t["tarefa_id"], titulo=t["titulo"], total_horas=t["total_horas"])
    )

for p in repo.get_apontamentos_by_cliente_mes_ano(cliente_id, mes, ano):
    projetos_data.append(
        RelatorioProjetoItem(
            projeto_id=p["projeto_id"],
            titulo=p["projeto_titulo"],
            valor_por_hora=p["valor_por_hora"],
            total_horas=p["total_horas"],
            valor_total=round(p["total_horas"] * p["valor_por_hora"], 2),
            tarefas=tarefas_por_projeto.get(p["projeto_id"], []),
        )
    )
```

- **Por quê `defaultdict(list)` em vez de um loop `for t: if t.projeto_id == p.projeto_id`**: O(n) vs O(n²). Para 4 apontamentos não importa, mas o padrão é mais limpo e escalável.
- **Por quê `projeto_titulo` ainda existe no dict retornado pelo repository (não renomeei no nível do repo)**: o repository é um detalhe de infraestrutura; o "projeto_titulo" é só um label da query. A renomeação para `titulo` acontece no momento de construir o `RelatorioProjetoItem`, no service. Mantém a fronteira `repo (dicts) → service (models) → controller (json)` clara.

### 5. Controller: adicionar `response_model=RelatorioResponse`

```python
@router.get("/relatorios", response_model=RelatorioResponse)
def generate_relatorio(...): ...
```

- **Por quê**: o schema passa a ser contrato real, não documentação. FastAPI valida o retorno. Swagger fica preciso.
- **Risco**: se o service esquecer de popular algum campo, o endpoint retorna 500 em vez de retornar um JSON parcial. **Mitigação**: o Pydantic dá erro claro, fácil de detectar em dev. Os testes existentes vão pegar.

### 6. Frontend: 3 mudanças no `RelatorioView.jsx`

1. **Card "Dados do Cliente"**: passa a ler `result.cliente.nome` (em vez de `result.cliente?.nome`), adiciona linha para `result.cliente.razao_social`, mostra `endereco + complemento + bairro` em uma linha, `cidade/estado` em outra, e `email` em uma terceira linha. Layout em lista vertical, não grid.
2. **Card "Resumo"**: passa a ler `result.totais.total_horas` e `result.totais.total_valor` (em vez de `result.total_horas_geral` / `result.valor_total_geral`).
3. **Bloco "Detalhamento por Projeto"**: dentro de cada projeto, sub-bloco opcional "Tarefas" (só renderiza se `proj.tarefas.length > 0`). Cada linha: `tarefa.titulo` (esq), `tarefa.total_horas`h (dir). Remove o bloco órfão "Tarefas" antigo (que ficava no nível do relatório, depois de "Detalhamento por Projeto").

- **Por quê remover o bloco órfão**: ele nunca apareceu (backend não enviava `tarefas` no nível raiz) e o novo sub-bloco dentro de cada projeto é o lugar semanticamente correto.
- **Por que `result.cliente?.nome` (optional chaining)**: defensivo — se `result.cliente` vier `undefined` por algum erro no backend, a UI não quebra; mostra `—`.

### 7. Test: criar apontamento em mês/ano passado + pedir o relatório

```python
def test_relatorio_mes_passado(client, headers, created_cliente, created_projeto, created_tarefa):
    data_passada = date(2025, 5, 15)
    apontamento_data = {
        "tarefa_id": created_tarefa["id"],
        "data": data_passada.isoformat(),
        "hora_ini": "08:00",
        "hora_fim": "12:00",
    }
    client.post("/api/v1/apontamentos", json=apontamento_data, headers=headers)

    response = client.get(
        f"/api/v1/relatorios?cliente_id={created_cliente['id']}&mes=5&ano=2025",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["cliente"]["id"] == created_cliente["id"]
    assert data["totais"]["total_horas"] == 4.0
    assert len(data["projetos"]) == 1
    assert data["projetos"][0]["total_horas"] == 4.0
    assert len(data["projetos"][0]["tarefas"]) == 1
    assert data["projetos"][0]["tarefas"][0]["total_horas"] == 4.0
```

- **Por quê data fixa em 2025-05**: garante que o `strftime` continua funcionando para datas que não sejam o mês atual (o test existente só testa `date.today()`).
- **Por que `2025` em vez de `2024` ou mês `1`**: 2025-05 é razoavelmente recente (não conflita com fixtures antigas hipotéticas em outros tests) e o mês 5 não é corner case.
- **Por que verificar `projetos[0].tarefas`**: garante que a nova query + agrupamento no service estão funcionando.

### 8. Atualizar o test existente `test_relatorio_generation`

Trocar as assertions de chaves achatadas para as novas chaves aninhadas. Mudança mecânica:

```python
# antes
assert data["cliente_id"] == created_cliente["id"]
assert data["cliente_documento"] == created_cliente["documento"]
assert data["total_geral_horas"] == 4.0
valor_esperado = 4.0 * created_projeto["valor_por_hora"]
assert data["total_geral_valor"] == valor_esperado

# depois
assert data["cliente"]["id"] == created_cliente["id"]
assert data["cliente"]["documento"] == created_cliente["documento"]
assert data["totais"]["total_horas"] == 4.0
valor_esperado = 4.0 * created_projeto["valor_por_hora"]
assert data["totais"]["total_valor"] == valor_esperado
```

## Risks / Trade-offs

- **[Risco] `response_model=RelatorioResponse` quebra se o service esquecer de popular algum campo** → Mitigação: rodar o test suite completo (38 tests) cobre o caminho feliz; Pydantic dá mensagem clara se algo faltar. Aceito o risco.

- **[Risco] Frontend mostra campos `undefined` se o backend estiver fora de sincronia** → Mitigação: usar optional chaining (`result.cliente?.nome`) e fallbacks nos sites onde o valor é exibido. Vai mostrar `—` em vez de quebrar a renderização. Adicionalmente, a change atualiza ambos os lados atomicamente.

- **[Risco] Query de tarefas duplica a lógica de filtro por mês/ano** → Mitigação: replicar a forma da query de projetos (mesmo `strftime`) é deliberado — fica explícito e legível. Se um dia mudar (ex.: Postgres), muda nos dois lugares, mas o test pega.

- **[Trade-off] Wire format breaking change** → Aceito. Único consumer é o frontend, atualizado na mesma change. Sem aliases/dual-format — refatoração limpa.

- **[Trade-off] PDF não incluso** → Aceito. `window.print()` resolve o caso de uso imediato (contador recebe o HTML e imprime da máquina dele). Geração de PDF server-side é change separada.

- **[Trade-off] Sem teste E2E do frontend** → Aceito. O critério de aceitação manual é o mesmo de costume (abrir o relatório, conferir que os campos fiscais aparecem, conferir que o total bate). Não há infra de teste de frontend no repo.

- **[Trade-off] `tarefas: list[RelatorioTarefaItem] = Field(default_factory=list)` mesmo quando vazio** → Aceito. Mantém a UI simples (não precisa de `if proj.tarefas && proj.tarefas.length`). Custo: o JSON do relatório inclui `tarefas: []` em todos os projetos. Tamanho desprezível.
