# Tabela de rastreabilidade

Requisito, padrão aplicado, classes por papel GoF e teste que verifica o cenário.

| R | Padrão | Classes (papel GoF) | Teste |
|---|--------|---------------------|-------|
| 1 | State | `Livro` (Context: guarda vencimento, num_renovacoes, reservante e delega eventos); `EstadoLivro` (State: declara os eventos, recusa por padrão com `OperacaoInvalidaException`); `Livre`, `Reservado`, `Emprestado`, `Renovado`, `Devolvido`, `Reparando`, `Incinerado` (ConcreteState, instâncias únicas; `Renovado` herda de `Emprestado`); `RenovacaoNegadaException` (guarda da renovação) | `tests/test_R01_ciclo_de_vida_do_livro.py` |
| 2 | Strategy | pendente (Sprint 4) | |
| 3 | Adapter | pendente (Sprint 4) | |
| 4 | Facade | pendente (Sprint 3) | |
| 5 | Observer | pendente (Sprint 4) | |
| 6 | Command | pendente (Sprint 3) | |
| 7 | Template Method | pendente (Sprint 5) | |
| 8 | Abstract Factory | pendente (Sprint 2) | |
| 9 | Decorator | pendente (Sprint 5) | |
| 10 | Composite | pendente (Sprint 5) | |
