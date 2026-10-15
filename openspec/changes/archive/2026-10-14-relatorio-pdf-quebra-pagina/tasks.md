## 1. Sincronização do contrato

- [x] 1.1 Conferir no template que nenhuma tarefa força `page-break-before` incondicional (classes `.projeto-nova-pagina` e `.tarefa-bloco-nova-pagina` aplicadas por Jinja)
- [x] 1.2 Conferir que o cabeçalho do projeto está envolvido por `.projeto-cabecalho` com `page-break-after: avoid`
- [x] 1.3 Reescrever em `specs/relatorios-pdf/spec.md` o cenário "Uma página por tarefa" refletindo projeto em página nova, primeira tarefa sem quebra e demais tarefas em página própria

## 2. Verificação

- [x] 2.1 Renderizar o template com contexto de exemplo confirmando as classes emitidas (primeiro bloco sem quebra, segundo com quebra, projeto seguinte com quebra)
- [x] 2.2 Rodar `cd backend && pytest -v` (100 passed, 3 skipped — PDF continua atrás do guard `HAS_WEASYPRINT`)
