## Why

O site ainda usa `window.confirm()` e `window.alert()` — diálogos nativos do navegador que fogem completamente do design system (dark theme, glass-card, accent colors). São bloqueantes, feios e quebram a imersão visual. Substituir por modais temáticos melhora a experiência e mantém a consistência visual em toda a aplicação.

## What Changes

- Criar `ConfirmModal` — modal de confirmação com título, mensagem, btn Cancelar (secondary) e btn Confirmar (danger)
- Criar `AlertModal` — modal informativo com título, mensagem e btn OK (primary)
- Substituir 4 chamadas de `confirm()` por `ConfirmModal`
- Substituir 6 chamadas de `alert()` por `AlertModal`
- Remover todo uso de `window.confirm()` e `window.alert()` do frontend

## Capabilities

### New Capabilities
- `dialogs`: Componentes de diálogo (ConfirmModal + AlertModal) que seguem o design system do site

### Modified Capabilities
- (nenhuma — capability nova, sem impacto em specs existentes)

## Impact

- **Frontend — novo**: `src/components/Common/ConfirmModal.jsx`, `src/components/Common/AlertModal.jsx`
- **Frontend — modificado**: `ClientesList.jsx`, `ProjetosList.jsx`, `TarefaDetail.jsx`, `FileUpload.jsx`, `Kanban.jsx`
- **Backend**: Nenhuma alteração
