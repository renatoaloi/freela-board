## Context

O frontend usa `window.confirm()` em 4 lugares e `window.alert()` em 6 lugares para ações destrutivas e notificações de erro. O `Modal.jsx` já existe em `src/components/Common/` como um contêiner genérico com backdrop, header e scroll body. Não há componentes de diálogo especializados (confirm/alert) que aproveitem esse Modal e o design system do site (glass-card, btn-primary, btn-danger, btn-secondary).

## Goals / Non-Goals

**Goals:**
- Criar `ConfirmModal` e `AlertModal` como componentes reutilizáveis
- Substituir todas as 4 ocorrências de `confirm()` por `ConfirmModal`
- Substituir todas as 6 ocorrências de `alert()` por `AlertModal`
- Manter o comportamento exato: ação destrutiva só executa após confirmação explícita; erro é exibido até o usuário dispensar

**Non-Goals:**
- Não adicionar sistema de toast/notificação (escopo futuro)
- Não alterar a lógica de negócio dos handlers de delete
- Não modificar o `Modal.jsx` existente
- Não adicionar animações de entrada/saída

## Decisions

| Decisão | Alternativa | Rationale |
|---|---|---|
| **Dois componentes separados** (ConfirmModal + AlertModal) | Um único Dialog com props de variante | Separação mais clara. ConfirmModal tem 2 ações (cancelar/confirmar), AlertModal tem 1 ação (OK). Props diferentes. |
| **Ambos compõem o Modal existente** | Cada um ter seu próprio overlay | Reuso do Modal já testado (Escape, backdrop, body scroll lock). Consistência visual. |
| **Estado de delete gerenciado com `useState` local** (ex: `deleteTarget`) | Context global ou reducer | É estado de UI local a cada tela. Não precisa ser global. |
| **ConfirmModal usa `btn-danger` para confirmar** | btn-primary | Ação é destrutiva (excluir). Deve usar a cor de perigo do design system (`accent-pink`). |
| **AlertModal usa `btn-primary` para OK** | btn-secondary | É o botão de ação principal do diálogo. Deve destacar. |
| **ConfirmModal não tem X nem fecha no backdrop** (herda do Modal) | Sobrescrever comportamento | Diálogo de confirmação deve forçar decisão explícita. Mas o Modal já fecha no backdrop/Escape — isso é aceitável pois cancelar é equivalente a fechar. |
| **Substituição é one-to-one** (cada confirm/alert vira um modal separado) | Agrupar múltiplos alertas | Cada erro é independente. Modal com 1 OK é suficiente. |

## Component API

```jsx
// ConfirmModal
<ConfirmModal
  isOpen={boolean}
  title="Excluir Cliente"
  message="Tem certeza que deseja excluir?"
  confirmLabel="Excluir"        // default: "Confirmar"
  onConfirm={fn}
  onCancel={fn}
/>

// AlertModal
<AlertModal
  isOpen={boolean}
  title="Erro"                  // default: "Aviso"
  message="Erro ao excluir."
  onClose={fn}
/>
```

## Risks / Trade-offs

- **[Baixo] Fechar no backdrop/Escape em ConfirmModal** → Usuário pode fechar sem querer. Mas o Modal já tem esse comportamento, e cancelar é equivalente a fechar. Mesmo assim, ConfirmModal poderia ser configurado para não fechar no backdrop no futuro se necessário.
- **[Baixo] Múltiplos modais abertos** → O Modal atual sobrescreve body overflow, mas se dois modais forem abertos, ao fechar o primeiro o scroll é restaurado. Como confirm/alert são mutuamente exclusivos (nunca abertos simultaneamente), não há risco real.
- **[Médio] Regressão visual** → Os modais novos precisam ficar idênticos em estilo ao Modal existente. Revisar após implementação.
