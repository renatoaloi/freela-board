# Spec: dialogs

> Capability: `dialogs` — componentes de diálogo (ConfirmModal + AlertModal) que seguem o design system do site, substituindo `window.confirm()` e `window.alert()`.

## Purpose

O site usava `window.confirm()` e `window.alert()` — diálogos nativos do navegador que fogem completamente do design system (dark theme, glass-card, accent colors). Eram bloqueantes e quebravam a imersão visual. Esta capability estabelece componentes de diálogo temáticos que mantêm consistência visual e permitem entrada rápida via teclado.

## Requirements

### Requirement: ConfirmModal para ações destrutivas

O sistema SHALL exibir um `ConfirmModal` estilizado com o design system do site quando o usuário clicar em uma ação destrutiva (excluir cliente, projeto, apontamento ou arquivo). O modal SHALL substituir o uso de `window.confirm()`.

#### Scenario: ConfirmModal aparece ao clicar em excluir
- **WHEN** o usuário clica no ícone de excluir (TrashIcon) em ClientesList, ProjetosList, TarefaDetail ou FileUpload
- **THEN** um `ConfirmModal` é exibido com título, mensagem explicativa, botão "Cancelar" e botão de confirmação (Excluir)
- **AND** o `window.confirm()` NÃO é chamado

#### Scenario: ConfirmModal executa ação ao confirmar
- **WHEN** o usuário clica no botão de confirmação (Excluir) no `ConfirmModal`
- **THEN** a ação de exclusão é executada (chamada à API)
- **AND** o modal é fechado

#### Scenario: ConfirmModal fecha sem ação ao cancelar
- **WHEN** o usuário clica em "Cancelar", no backdrop, ou pressiona Escape
- **THEN** o modal é fechado
- **AND** a ação de exclusão NÃO é executada

### Requirement: AlertModal para notificações de erro

O sistema SHALL exibir um `AlertModal` estilizado com o design system do site quando ocorrer um erro em operações (excluir, upload, atualizar status). O modal SHALL substituir o uso de `window.alert()`.

#### Scenario: AlertModal aparece ao ocorrer erro
- **WHEN** uma operação (excluir, upload, atualizar status) falha e cai no `catch`
- **THEN** um `AlertModal` é exibido com título "Erro", mensagem descritiva do erro e botão "OK"
- **AND** o `window.alert()` NÃO é chamado

#### Scenario: AlertModal fecha ao clicar OK
- **WHEN** o usuário clica em "OK", no backdrop, ou pressiona Escape
- **THEN** o modal é fechado

### Requirement: Componentes reutilizáveis e consistentes

Os componentes `ConfirmModal` e `AlertModal` SHALL compor o `Modal` existente e seguir o design system (glass-card, btn-primary, btn-danger, btn-secondary).

#### Scenario: ConfirmModal usa classes do design system
- **WHEN** o `ConfirmModal` é renderizado
- **THEN** o botão de confirmação usa `btn-danger` e o botão de cancelar usa `btn-secondary`

#### Scenario: AlertModal usa classes do design system
- **WHEN** o `AlertModal` é renderizado
- **THEN** o botão OK usa `btn-primary`
