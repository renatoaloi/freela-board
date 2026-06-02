## Context

O app é single-user local, pt-BR, React 18 + Vite SPA. Backend é FastAPI + SQLite. A stack de datas é zero-dep — `new Date(...)` e `toLocaleDateString` são usados sem abstração.

A spec ECMAScript define que `new Date("YYYY-MM-DD")` (string date-only, sem designador de fuso) é interpretado como **UTC**. O backend devolve `date` (não `datetime`) como string `YYYY-MM-DD` no JSON (Pydantic v2). Em qualquer fuso a oeste do UTC, `new Date(iso)` cai em `D-1` localmente, e `toLocaleDateString('pt-BR')` exibe `D-1`. Em BRT (UTC-3), isso vira `21:00` do dia anterior — sempre `D-1`.

Existem 4 sites no frontend com esse padrão. Centralizar em um helper elimina a categoria de bug (qualquer novo site que renderizar data cairá em uma função correta) e remove dependência do fuso do navegador para a renderização. O default do `ApontamentoForm` é um bug secundário simétrico (avança em vez de atrasar, dependendo do horário BRT), resolvido pelo mesmo helper com `getTodayLocalISO()`.

## Goals / Non-Goals

**Goals:**
- Centralizar a regra "string ISO `YYYY-MM-DD` vinda do backend é literal de calendário" em **uma** função importável.
- Eliminar `new Date(string-iso)` no código de apresentação de datas.
- Corrigir os 4 sites de renderização e o 1 site de default de form, com 0 mudanças no backend.
- Manter o wire format `YYYY-MM-DD` (sem alteração de contrato de API).

**Non-Goals:**
- Adicionar biblioteca de datas (date-fns, dayjs, luxon). Não há outra data math no app; uma lib seria peso sem ganho.
- Internacionalizar formato (`dd/MM/yyyy` é consistente com a UI inteira).
- Migrar `apontamento.data` / `data_criacao` para `datetime` com fuso explícito. O domínio é "dia de calendário", `date` é o tipo certo.
- Corrigir comportamento de `created_at`/`updated_at` (que são `datetime` e não estão sendo renderizados com `toLocaleDateString` em lugar nenhum).
- Adicionar testes de frontend (não há infra; o critério de aceitação é manual).

## Decisions

### 1. Helper único em `frontend/src/utils/date.js` (em vez de método em `Common/`, em vez de inline em cada componente)

- **Por quê**: `src/utils/` é o local canônico para funções puras sem JSX. `src/components/Common/` é para componentes React. Manter convenção.
- **Por quê 1 arquivo, não 2**: `formatDateBR` e `getTodayLocalISO` operam sobre o mesmo conceito (data local) e qualquer novo dev vai procurar ambos juntos.
- **Por quê função pura, não classe / hook**: o helper não tem estado, não usa hooks, não precisa ser testado em ambiente React.
- **Alternativas consideradas**:
  - Hook `useFormattedDate` → overhead sem ganho; re-renderiza com input igual não muda nada.
  - Componente `<FormattedDate value={iso} />` → adiciona JSX onde não precisa; cada site vira 1 linha a mais, e datas em prop de objeto (`ap.data`) continuam precisando de extração.
  - Adicionar `date-fns` (`format(parseISO(iso), 'dd/MM/yyyy')`) → 1 dep nova (atualmente zero em datas) para resolver ~15 linhas de código.

### 2. `formatDateBR` faz **string split** em vez de `new Date(y, m-1, d)`

```js
export function formatDateBR(iso) {
  if (!iso) return '';
  const [y, m, d] = iso.split('-');
  return `${d}/${m}/${y}`;
}
```

- **Por quê split, não `new Date`**: split não envolve construtor `Date`, logo não envolve fuso horário em nenhum nível. Garante que `formatDateBR("2026-06-11")` é **sempre** `"11/06/2026"`, em qualquer fuso, em qualquer engine, com ou sem DST, agora e daqui a 10 anos.
- **Alternativa considerada**: `new Date(+y, +m - 1, +d).toLocaleDateString('pt-BR')` — funciona no navegador do usuário, mas introduz dois pontos de fragilidade: (a) o construtor `Date` com args locais é dependente de runtime (funciona no Chrome, mas é menos óbvio em SSR se o app virar SSR no futuro), (b) `toLocaleDateString` com locale string depende de ICU data do navegador, e formatos de data pt-BR podem variar entre versões. Split é trivialmente correto.
- **Alternativa descartada**: `new Date(${iso}T00:00:00).toLocaleDateString('pt-BR')` — depende de nuance da spec ECMAScript (formato com `T` sem `Z` é *implementation-defined* até ES2015; engines modernas tratam como local, mas é "mágico").

### 3. `getTodayLocalISO` usa `getFullYear/getMonth/getDate`, não `toISOString`

```js
export function getTodayLocalISO() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}
```

- **Por quê**: `getFullYear/getMonth/getDate` leem o fuso do navegador; `toISOString` lê UTC. Para "hoje" no calendário do usuário, queremos o fuso local.
- **Bug que resolve**: usuário brasileiro que abre o form após 21h BRT. Antes: `toISOString` → dia seguinte UTC → default aparece como "amanhã". Depois: lê `new Date()` direto e usa getters locais → sempre "hoje" no calendário do usuário.
- **Alternativa descartada**: usar uma lib (`startOfDay(new Date()).toISOString().slice(0, 10)` com date-fns) — mesma razão da decisão 1.

### 4. Sem mudança no backend, mesmo com o backend "correto"

- **Por quê**: o backend já devolve `YYYY-MM-DD` (Pydantic v2 + SQLAlchemy `Date`). Mexer no schema, serializador ou tipo de coluna seria over-engineering para um bug de frontend. O wire format continua sendo o mesmo.
- **Por que NÃO devolver `data_formatada: "dd/MM/yyyy"` no response** (alternativa que apareceu na exploração): vaza apresentação pra dentro do domínio. Próxima vez que alguém quiser `data_formatada_en` ou quiser consumir a data numérica, fica preso.

### 5. Sem teste automatizado (frontend não tem infra)

- **Por quê**: o repo não tem Jest/Vitest/RTL configurado. Adicionar infra de teste só para este fix seria desproporcional (centenas de KB de dev-dep para testar 2 funções puras).
- **Mitigação**: as funções são triviais (split + template string). Validação manual pelo critério de aceitação do proposal ("digitar 11/06, recarregar, ver 11/06") é suficiente.
- **Quem adicionar tests no futuro**: o helper é puro e testável com qualquer runner; pode ser coberto com 1 linha de Vitest quando a infra existir.

## Risks / Trade-offs

- **[Risco] Helper não é importado em algum site novo no futuro** → Mesma categoria de bug ressurge. *Mitigação*: deixar uma regra explícita no `AGENTS.md` ("renderizar datas do backend: use `formatDateBR` de `utils/date.js`; nunca `new Date(iso).toLocaleDateString`"). Considerar lint custom, mas o repo não tem lint config e AGENTS.md diz para não inventar.

- **[Risco] Outro dev assume que `formatDateBR` é locale-aware** → Adiciona prop `locale`, refatora para `toLocaleDateString`, reintroduz o bug. *Mitigação*: comentário no helper explicitando que é pt-BR fixo por design.

- **[Risco] Default do form volta a quebrar se alguém usar `toISOString` de novo** → *Mitigação*: helper `getTodayLocalISO` é a única função para isso no app; comentário no helper e na linha onde é chamado.

- **[Trade-off] Sem teste automatizado** → Aceito. Custo de adicionar infra de teste > benefício de testar 2 funções puras. O critério de aceitação é manual e o teste de aceitação é reproduzível em 30 segundos pelo usuário.

- **[Trade-off] i18n preso em pt-BR** → Aceito. App é single-user local em pt-BR; nenhum outro locale está em uso. Se mudar, é uma change nova ("i18n-datas").
