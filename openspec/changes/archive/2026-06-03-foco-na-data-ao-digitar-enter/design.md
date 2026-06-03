## Context

O formulário de apontamentos (`ApontamentoForm.jsx`) usa três inputs (data, hora_ini, hora_fim) com um botão de submit. Atualmente não há gerenciamento de foco — sem `useRef`, sem `autoFocus`. Após o submit bem-sucedido, os campos são resetados mas o foco é perdido (vai para o body), exigindo clique do mouse para continuar digitando.

## Goals / Non-Goals

**Goals:**
- Após submit bem-sucedido (Enter ou clique), focar automaticamente no campo data
- Campo data deve receber `autoFocus` ao montar o componente
- Se o submit falhar, não redirecionar o foco (manter a mensagem de erro visível)

**Non-Goals:**
- Não alterar comportamento de reset dos campos (hora_ini/hora_fim -> '', data -> hoje)
- Não alterar layout, validação, ou fluxo de dados
- Não modificar o backend
- Não adicionar tratamento de atalhos de teclado além do Enter nativo do HTML form

## Decisions

| Decisão | Alternativa | Rationale |
|---|---|---|
| **`useRef` + `focus()`** no campo data | `useRef` com `useEffect` para focar após estado resetar | O `focus()` chamado imediatamente após `setData/setHoraIni/setHoraFim` funciona porque o DOM já foi atualizado síncronamente no mesmo evento. O React batching (18) não interfere porque o foco é um efeito colateral do DOM, não do estado React. |
| **`autoFocus` no JSX** | Focar via `useEffect` no mount | `autoFocus` é mais declarativo e não requer `useEffect`. É suportado por todos os navegadores modernos. |
| **Foco só no `try` bem-sucedido** | Foco sempre (no `finally`) | Se falhar, o usuário precisa ver a mensagem de erro. Redirecionar o foco para a data esconderia o erro visualmente. |
| **Não resetar `data`** (manter comportamento atual) | Resetar só hora_ini/hora_fim | O usuário pediu explicitamente para NÃO mudar o comportamento de reset. |

## Risks / Trade-offs

- **[Baixo] React Strict Mode** → `autoFocus` pode disparar duas vezes em dev (sem impacto em prod)
- **[Baixo] Foco em formulário aninhado em tab** → Se o form estiver numa tab não-visível, `autoFocus` será ignorado pelo navegador (comportamento esperado)
