## 1. Criar componentes de diálogo

- [x] 1.1 Criar `ConfirmModal.jsx` em `src/components/Common/` — compõe `Modal`, renderiza título + mensagem + btn Cancelar (secondary) + btn Confirmar (danger)
- [x] 1.2 Criar `AlertModal.jsx` em `src/components/Common/` — compõe `Modal`, renderiza título + mensagem + btn OK (primary)

## 2. Substituir confirm/alert em ClientesList

- [x] 2.1 Substituir `confirm('Excluir este cliente?...')` por `ConfirmModal` com estado `deleteTarget`
- [x] 2.2 Substituir `alert('Erro ao excluir cliente.')` por `AlertModal` com estado `alertMsg`

## 3. Substituir confirm/alert em ProjetosList

- [x] 3.1 Substituir `confirm('Excluir este projeto?...')` por `ConfirmModal` com estado `deleteTarget`
- [x] 3.2 Substituir `alert('Erro ao excluir projeto.')` por `AlertModal` com estado `alertMsg`

## 4. Substituir confirm/alert em TarefaDetail

- [x] 4.1 Substituir `confirm('Excluir este apontamento?')` por `ConfirmModal`
- [x] 4.2 Substituir `alert('Erro ao excluir apontamento.')` por `AlertModal`

## 5. Substituir confirm/alert em FileUpload

- [x] 5.1 Substituir `confirm('Excluir este arquivo?')` por `ConfirmModal`
- [x] 5.2 Substituir `alert('Erro ao excluir arquivo.')` por `AlertModal`
- [x] 5.3 Substituir `alert('Erro ao fazer upload do arquivo.')` por `AlertModal`

## 6. Substituir alert em Kanban

- [x] 6.1 Substituir `alert('Erro ao atualizar status da tarefa.')` por `AlertModal`

## 7. Corrigir tratamento de erros de validação Pydantic nos forms

- [x] 7.1 Corrigir `ClienteForm.jsx` — tratar `detail` array de erros Pydantic
- [x] 7.2 Corrigir `ProjetoForm.jsx` — mesmo padrão
- [x] 7.3 Corrigir `TarefaForm.jsx` — mesmo padrão
- [x] 7.4 Corrigir `ApontamentoForm.jsx` — mesmo padrão

## 8. Verificação

- [x] 8.1 Executar `pytest -v` no backend para garantir que nada quebrou
- [x] 8.2 Iniciar frontend, testar exclusão de cliente com confirmação + erro
- [x] 8.3 Testar exclusão de projeto com confirmação + erro
- [x] 8.4 Testar exclusão de apontamento com confirmação + erro
- [x] 8.5 Testar exclusão de arquivo com confirmação + erro
- [x] 8.6 Testar upload de arquivo com erro — para testar: pare o backend e tente fazer upload de um arquivo
- [x] 8.7 Testar drag-and-drop no Kanban com erro — para testar: pare o backend e arraste uma tarefa entre colunas
