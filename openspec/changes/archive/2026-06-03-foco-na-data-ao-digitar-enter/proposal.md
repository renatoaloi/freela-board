## Why

O formulário de apontamentos exige uso do mouse para clicar no botão de submit após digitar hora_fim, e depois o foco não volta para o campo data, forçando o usuário a clicar novamente no campo data para iniciar o próximo apontamento. Isso quebra o fluxo de digitação contínua e reduz a velocidade de lançamento de múltiplos apontamentos em sequência.

## What Changes

- Adicionar `autoFocus` no campo data do formulário de apontamentos
- Adicionar `useRef` no campo data e, após o salvamento bem-sucedido (dentro do `try`, pós-`await`), executar `dataRef.current?.focus()` para retornar o foco ao campo data
- Manter o comportamento existente de reset dos campos (hora_ini e hora_fim vazios, data = hoje)
- Se o salvamento falhar (cair no `catch`), **não** executar o foco — a mensagem de erro deve permanecer visível sem redirecionar o foco

## Capabilities

### New Capabilities
- `apontamentos-form-keyboard`: Otimização do formulário de apontamentos para entrada rápida via teclado

### Modified Capabilities

- (nenhuma — alteração apenas de UX, sem mudança de requisitos)

## Impact

- **Frontend**: `frontend/src/components/Apontamentos/ApontamentoForm.jsx` — adição de `useRef`, `autoFocus`, e foco pós-submit
- **Backend**: Nenhuma alteração
