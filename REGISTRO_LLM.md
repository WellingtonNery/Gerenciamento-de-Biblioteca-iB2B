# Registro de uso de LLM

Exigido pelo enunciado: registro dos pedidos feitos ao modelo e do que foi aceito, corrigido ou descartado. Também serve como diário detalhado de tudo que o assistente produziu no projeto.

Formato de cada entrada: data, ferramenta, pedido, o que foi produzido (arquivo por arquivo), validação e decisões.

---

## 15/11/2026, Claude (claude.ai), sessão com Wellington

### Pedido 1: visão geral do trabalho e plano em sprints

**Pedido:** com o enunciado, o PDF de soluções do professor e o zip do repositório em mãos, dar a visão geral do projeto (a história), os rumos e uma descrição de cada funcionalidade como sprints.

**Produzido:** análise do estado do repositório (só esqueleto de pastas, nenhum padrão implementado) e proposta de 8 sprints (0 a 7) ordenadas por dependência: State como fundação, Abstract Factory antes da Facade, trio da devolução (Observer, Strategy, Adapter) junto, independentes (Template Method, Composite, Decorator) depois, MySQL e web por último.

**Aceito:** a ordem das sprints foi adotada no planejamento (Pedido 2).

### Pedido 2: planejamento completo de engenharia

**Pedido:** "faça todo o planejamento do projeto. Quero que seja um projeto de engenharia coeso, e não só um projeto que vai mascarar tudo mas estar podre por dentro."

**Produzido:** `docs/planejamento.md`, contendo:
- Visão do produto (narrativa do fluxo de circulação)
- Tabela dos 10 requisitos com padrão e nome do teste
- Premissas adotadas (numRenovacoes < 2, +30 dias por renovação, laudo irrecuperável leva REPARANDO a INCINERADO)
- Arquitetura em camadas (web, tratadores, fachada, domínio, persistência) com 7 regras de coesão:
  1. regra de dependência (domínio não importa nada de fora)
  2. toda operação devolve Resultado, exceção crua não atravessa a fachada
  3. dinheiro sempre Decimal criado de string
  4. fábrica de persistência escolhida uma única vez (composition root)
  5. regra de negócio só no domínio
  6. idempotência por id de solicitação (UUID do cliente)
  7. eventos de devolução síncronos e em processo
- Mapa de pacotes (qual requisito mora em qual pasta)
- Processo: definition of done por sprint (teste passando, rastreabilidade preenchida, registro de LLM, commit)
- Cronograma 15 a 26/11 com divisão entre Wellington e João Pedro (sprints 0 a 3 em par, 4 e 5 em paralelo)
- Tabela de riscos (autorização de Python pendente, arguição cruzada, MySQL na demo, atrasos, State descaracterizado)
- Roteiro da demonstração de 5 minutos

### Pedido 3: executar a Sprint 0

**Pedido:** realizar a Sprint 0 na pasta `C:\Projetos\Gerenciamento de Biblioteca iB2B`.

**Produzido, arquivo por arquivo:**

| Arquivo | Conteúdo |
|---------|----------|
| `biblioteca/dominio/modelos.py` | Entidades `Livro` (id, titulo, autor), `Membro` (id, nome, email), `Emprestimo` (id, ids de livro e membro, datas, num_renovacoes) como dataclasses. `Emprestimo.novo()` calcula a data prevista somando `PRAZO_EMPRESTIMO_DIAS` (30). Constante `MAX_RENOVACOES = 2`. Comentário marca onde o State entra na Sprint 1. |
| `biblioteca/dominio/resultado.py` | `Resultado` (dataclass congelada: sucesso, mensagem, dados) com construtores `ok()` e `recusado()`. É o retorno uniforme de todos os casos de uso. |
| `tests/test_sprint0_fundacoes.py` | 4 testes: Resultado.ok carrega dados, Resultado.recusado tem motivo, Emprestimo.novo calcula prazo de 30 dias, entidades básicas instanciam. |
| `conftest.py` (raiz) | Vazio com docstring; faz o pytest incluir a raiz no sys.path para importar `biblioteca`. |
| `run.py` | Substituído o exemplo do PyCharm por um aviso de que a web chega na Sprint 6. |
| `.gitignore` | Estava vazio; preenchido com `__pycache__/`, `.pytest_cache/`, `.venv/`, `.env`, `.idea/`, `.vscode/`. |
| `__init__.py` novos | `dominio/estados`, `dominio/organizacao`, `circulacao/tratadores`, `circulacao/eventos`, `circulacao/solicitacoes`, `financeiro/multa`, `financeiro/bancos`, `consulta` (faltava). Cada um com docstring de uma linha dizendo qual requisito mora ali. |

**Validação:** suíte executada no ambiente do assistente antes de gravar: 4 testes, todos passando (`4 passed`).

**Decisões tomadas:**
- Entidades como dataclasses simples nesta sprint; comportamento entra junto com os padrões.
- `conftest.py` na raiz em vez de configurar PYTHONPATH ou pacote instalável: solução mais simples que funciona no PyCharm e no terminal.
- Docstrings nos `__init__.py` para cada pacote declarar seu requisito (ajuda na arguição e na rastreabilidade).

**Pendências deixadas para o Wellington:**
- Rodar `pytest` na máquina local para confirmar.
- `git rm -r --cached .idea` (a pasta já estava rastreada antes do .gitignore) e commit.
- Confirmar com o professor, por escrito, a autorização para Python.

### Pedido 4: registro contínuo

**Pedido:** documentar em arquivo, detalhadamente, tudo o que o assistente fizer no projeto.

**Produzido:** este arquivo, preenchido retroativamente com a sessão de hoje. As próximas sessões devem adicionar uma entrada no mesmo formato.

### Pedido 5: executar a Sprint 1 (R1, State)

**Pedido:** "pode começar a Sprint 1".

**Fonte consultada:** páginas 1 a 8 do PDF "Soluções dos problemas de aplicação dos padrões GoF" (Problema 1). O código segue o desenho do professor: 7 estados LIVRE, RESERVADO, EMPRESTADO, RENOVADO, DEVOLVIDO, REPARANDO, INCINERADO (enum `Situacao`); recusa padrão na classe base via `OperacaoInvalidaException` lançada antes de qualquer alteração; `RenovacaoNegadaException` na guarda `numRenovacoes < 2`; estados sem atributos como instâncias únicas (`INSTANCIA`); `Renovado` herda de `Emprestado` para a regra de renovação morar em um único método; `limparCiclo()` zera contador, reservante e vencimento.

**Produzido, arquivo por arquivo:**

| Arquivo | Conteúdo |
|---------|----------|
| `biblioteca/dominio/regras.py` | Constantes `PRAZO_EMPRESTIMO_DIAS`, `PRAZO_RENOVACAO_DIAS`, `MAX_RENOVACOES` em módulo sem dependências (evita import circular entre estados e modelos). |
| `biblioteca/dominio/situacao.py` | Enum `Situacao` com os 7 valores. É o que as camadas externas enxergam; as classes de estado são detalhe interno. |
| `biblioteca/dominio/excecoes.py` | `ErroDeDominio` (base), `OperacaoInvalidaException` (situacao + operacao) e `RenovacaoNegadaException` (id do livro). |
| `biblioteca/dominio/estados/base.py` | `EstadoLivro`: declara os 8 eventos com implementação padrão que recusa sem alterar o livro; `situacao()` abstrato; `_recusa()` monta a exceção. |
| `biblioteca/dominio/estados/concretos.py` | Os 7 estados concretos, cada um sobrescrevendo só o que é válido. Transições via `livro._mudar_para(X.INSTANCIA)`. Tudo em um módulo só porque as transições se referenciam mutuamente (módulos separados dariam import circular). Instâncias únicas criadas no fim do módulo. |
| `biblioteca/dominio/modelos.py` | `Livro` virou o Context: ganhou `vencimento`, `num_renovacoes`, `reservante`, `_estado` (inicia em `Livre.INSTANCIA`) e os métodos de evento que só delegam. Internos `_mudar_para`, `_definir_vencimento_inicial` (hoje + 30), `_prorrogar`, `_limpar_ciclo`. Reexporta as constantes de `regras.py` para os testes da Sprint 0 continuarem passando. |
| `tests/test_R01_ciclo_de_vida_do_livro.py` | 7 testes: fluxo feliz completo; terceira renovação recusada sem alterar vencimento nem contador (cenário do enunciado); reserva recusada em DEVOLVIDO sem inspeção (Figura 1.4); empréstimo por outro membro recusado; laudo irrecuperável leva REPARANDO a INCINERADO; INCINERADO recusa todos os 8 eventos; reparo concluído volta a LIVRE com ciclo limpo. |
| `docs/rastreabilidade.md` | Tabela criada com a linha do R1 preenchida (classes por papel GoF) e os demais requisitos marcados como pendentes com a sprint prevista. |
| `docs/planejamento.md` | Linha do mapa de pacotes ajustada: estados em `base.py` + `concretos.py` em vez de um módulo por estado (motivo: import circular). |

**Decisões tomadas:**
- Nomes de estado idênticos aos do professor (Livre, não "Disponível"; Devolvido cobre o aguardo de inspeção, sem estado "Em Inspeção" separado) para a coerência código x UML valer 15% sem atrito.
- `Membro` mantido no lugar de `Estudante` do modelo do professor (alternativa justificada: papel idêntico de reservante; o enunciado aceita alternativas justificadas).
- Validação "membro cadastrado" ficará no tratador (Sprint 3), como no material; o estado só mantém a defesa contra membro nulo.
- `date.today()` dentro de `_definir_vencimento_inicial`; os testes calculam o esperado a partir de `date.today()` também.
- Correção durante a sessão: `Reparando.situacao()` saiu com uma expressão sem sentido (`INCINERADO if False else REPARANDO`) na primeira versão gerada; corrigido para `return Situacao.REPARANDO` antes de gravar.

**Validação:** `pytest` no ambiente do assistente: 11 testes (4 da Sprint 0 + 7 do R1), todos passando.

**Pendências para a dupla:**
- Rodar `pytest` na máquina local e commitar a sprint.
- Desenhar no Astah o diagrama de classes do State e a máquina de estados (Figuras 1.1 e 1.2 servem de referência).
- Estudar para a arguição: por que a recusa padrão fica na base, por que Renovado herda de Emprestado, por que a guarda vem antes de qualquer alteração.

---

## Sessões anteriores (outra conta, resumo)

- 13/11/2026: análise do zip inicial (esqueleto), definição da estrutura de pastas, criação do README.md provisório com equipe, tabela de requisitos, decisões por padrão e instruções de execução. Orientações sobre requirements.txt, .gitignore, venv e integração do Flask.
