## 1. Implementar foco automático no formulário de apontamentos

- [x] 1.1 Adicionar `useRef` e `autoFocus` no input de data em `ApontamentoForm.jsx`
- [x] 1.2 Após `await` bem-sucedido no `handleSubmit`, chamar `dataRef.current?.focus()` para retornar foco ao campo data
- [x] 1.3 Garantir que o foco NÃO seja chamado quando o salvamento falhar (dentro do `catch` ou após erro)

## 2. Verificação

- [x] 2.1 Executar `pytest -v` no backend para garantir que nada quebrou
- [x] 2.2 Iniciar frontend e backend, testar fluxo manual: digitar data → hora_ini → hora_fim → Enter → foco volta para data
- [x] 2.3 Testar fluxo de erro: causa erro → foco NÃO volta para data, mensagem de erro permanece visível
