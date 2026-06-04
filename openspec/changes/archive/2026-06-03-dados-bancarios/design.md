## Context

O sistema FreelaBoard atualmente não possui nenhum cadastro de dados bancários. O relatório de horas (JSON + PDF) exibe dados do cliente e totais, mas não inclui informações de pagamento do freelancer. O usuário precisa preencher manualmente esses dados ao enviar o relatório para o cliente.

O backend segue Clean Architecture (Model → Repository → Service → Controller), usa SQLite + SQLAlchemy 2.0, e o frontend usa React com Vite + Tailwind. Não existe página de "configurações" no sistema — este é o primeiro painel desse tipo, e deve ser projetado para ser extensível.

## Goals / Non-Goals

**Goals:**
- Criar tabela `dados_bancarios` com UUID, campos de banco/agência/conta/PIX, timestamps
- Implementar endpoints `GET /api/v1/dados-bancarios` (cria registro vazio se não existir) e `PUT /api/v1/dados-bancarios` (atualiza registro único)
- Implementar página `/configuracoes` com painel de edição de dados bancários
- Adicionar "Configurações" ao menu lateral (sidebar)
- Incluir dados bancários no RelatorioResponse (campo opcional)
- Incluir dados bancários no PDF (entre cliente e resumo)
- Criar migration Alembic para a nova tabela

**Non-Goals:**
- Não terá suporte a múltiplas contas bancárias (sempre um registro único)
- Não terá CREATE/DELETE — apenas GET (cria se vazio) e PUT
- Não terá autenticação diferenciada (mesma X-API-Key do sistema)
- Não terá upload de documentos bancários
- Não terá outras páginas de configuração por enquanto (mas a estrutura permite adicionar)

## Decisions

### 1. Singleton via `get_or_create` no repositório

Em vez de um seed/migration que insere o registro, o repositório `DadosBancariosRepository` terá um método `get_or_create()` que busca o primeiro registro da tabela e, se não existir, cria um com UUID e todos os campos `None`. Isso evita migrações com dados e garante que o registro sempre exista no primeiro acesso.

**Alternativa considerada:** Inserir via migration. Rejeitada porque a migration com dados fixos é frágil (se o registro for deletado manualmente, a migration não roda de novo). `get_or_create` é mais resiliente.

### 2. Tipo da chave PIX como string com enum no backend

O campo `tipo_chave_pix` será `String(20)` no banco, com validação via enum `PixKeyType` (cpf, cnpj, email, telefone) no schema Pydantic. O frontend usará um `<select>` com as opções em português (CPF, CNPJ, E-mail, Telefone), mapeando para os valores do enum.

**Alternativa considerada:** Enum nativo do SQLite. Rejeitado porque SQLite não tem suporte a enum nativo, e manter como string com validação Pydantic segue o padrão usado em `TarefaStatus`.

### 3. Campo `dados_bancarios` opcional no RelatorioResponse

O schema `RelatorioResponse` ganhará um campo `dados_bancarios: Optional[RelatorioDadosBancariosInfo]`. O service de relatório buscará os dados bancários via `DadosBancariosRepository` e incluirá na resposta. Se o registro tiver todos os campos vazios, ainda assim será incluído (para que o frontend e o PDF decidam se exibem ou não). O critério de exibição no frontend/PDF será: exibir se ao menos um campo estiver preenchido.

**Alternativa considerada:** Incluir só se houver dados preenchidos. Rejeitado porque isso quebraria a consistência da resposta — é melhor que o schema seja estável e o frontend decida a exibição.

### 4. Página "Configurações" como rota única com painéis

A rota `/configuracoes` renderizará `Configuracoes.jsx`, que por enquanto terá apenas o painel `DadosBancariosForm`. Futuramente, novos painéis serão adicionados como cards/abas dentro da mesma página. Isso evita criar uma sub-rota para cada tipo de configuração e mantém a navegação simples.

**Alternativa considerada:** Rotas separadas `/configuracoes/dados-bancarios`, `/configuracoes/notificacoes`, etc. Rejeitado por enquanto — overkill até que haja mais de um painel. A página única com painéis é mais simples e extensível.

### 5. Sidebar: Configurações antes de Relatórios

O item "Configurações" será inserido na posição atual de "Relatórios", e "Relatórios" será movido para depois (ou vice-versa). A decisão é: Configurações após Kanban e antes de Relatórios, por ser uma página de administração do sistema.

### 6. PDF: Nova seção "Dados Bancários" renumerando as existentes

O PDF atualmente tem:
- 1. Dados do Cliente
- 2. Resumo
- 3. Detalhamento por Projeto

Com a mudança:
- 1. Dados do Cliente
- 2. Dados Bancários
- 3. Resumo
- 4. Detalhamento por Projeto

A seção de dados bancários só será renderizada se ao menos um campo estiver preenchido.

## Risks / Trade-offs

- **[Risk] Um único registro**: Se por algum motivo o registro for deletado do banco (ex: reset de DB), o sistema recria automaticamente no próximo GET. Isso é desejável. Porém, se houver edição concorrente (improvável em sistema single-user), o último PUT vence.
- **[Risk] Exposição de dados bancários**: Os dados bancários trafegam na resposta do relatório. Como o sistema já exige X-API-Key em todos os endpoints, isso não adiciona risco novo. O frontend armazena em memória (state React), nunca em localStorage.
- **[Trade-off] Sem validação de conta bancária**: Não há validação de dígitos verificadores de agência/conta ou se a chave PIX é válida. O sistema armazena o que o usuário digitar. Isso mantém a implementação simples e evita dependências externas.
