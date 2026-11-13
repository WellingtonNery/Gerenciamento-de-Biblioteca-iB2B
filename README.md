# Gerenciamento de Biblioteca iB2B

Sistema de cadastro, reserva, empréstimo, renovação e devolução de livros, implementado com padrões de projeto GoF.
Trabalho prático de **Modelagem de Sistemas Computacionais** (PUCPR, Prof. Edson Emílio Scalabrin, Turma A, 2S/2026), continuação do Trabalho 02 e da lista "Problemas de aplicação dos padrões GoF".

> **Status:** versão provisória. A estrutura do repositório está definida; a implementação dos requisitos está em andamento (ver [Status dos requisitos](#status-dos-requisitos)).

## Sumário

1. [Equipe](#equipe)
2. [Visão geral](#visão-geral)
3. [Requisitos e padrões GoF](#requisitos-e-padrões-gof)
4. [Status dos requisitos](#status-dos-requisitos)
5. [Arquitetura](#arquitetura)
6. [Estrutura do repositório](#estrutura-do-repositório)
7. [Premissas do domínio](#premissas-do-domínio)
8. [Como executar](#como-executar)
9. [Testes](#testes)
10. [Documentação e modelos UML](#documentação-e-modelos-uml)
11. [Uso de LLMs](#uso-de-llms)
12. [Prazos](#prazos)
13. [Referências](#referências)

## Equipe

| Integrante | Matrícula |
|---|---|
| _a preencher_ | _a preencher_ |

Equipe de até 4 integrantes.

## Visão geral

A empresa iB2B utiliza um sistema desenvolvido pela BCC2022. Os componentes **Acadêmico, RH, Biblioteca e Financeiro** comunicam-se por interfaces; o banco é externo. Este projeto implementa o componente de biblioteca e sua integração com o financeiro, preservando os tratadores, a delegação e os pontos internos de acesso **Acervo**, **Relacionamento** e **Movimentacao** definidos no Trabalho 02.

Funcionalidades cobertas:

- Cadastro de livros, pessoas, estudantes e atendentes.
- Reserva, empréstimo, renovação e devolução de livros, com inspeção posterior.
- Cálculo de multa por atraso, com políticas configuráveis.
- Cobrança e quitação junto a dois bancos com APIs incompatíveis (simulados).
- Consulta ao acervo com medição e cache opcionais.
- Organização hierárquica do acervo (unidades, seções e subseções).

## Requisitos e padrões GoF

Cada requisito aplica um padrão na situação para a qual foi proposto. Cada um é comprovado por um cenário de verificação automatizado.

| Nº | Situação | Padrão | Cenário de verificação |
|---|---|---|---|
| 1 | Ciclo de vida do livro | **State** | A terceira renovação é recusada sem alterar o vencimento; um livro devolvido e ainda não inspecionado não pode ser reservado. |
| 2 | Políticas de cálculo de multa | **Strategy** | Com 5 dias de atraso: R$ 5,00 (original) e R$ 3,00 (tolerância); sem atraso: zero. |
| 3 | Integração com bancos incompatíveis | **Adapter** | A mesma cobrança de R$ 7,00 gera 700 centavos no banco A e 7,00 no banco B; notificação repetida não gera segunda quitação. |
| 4 | Entrada única para as operações de circulação | **Facade** | A efetivação de empréstimo valida a reserva, remove a reserva ativa, cria o empréstimo e atualiza o livro, sem expor coleções à interface. |
| 5 | Reações independentes à devolução | **Observer** | Devolução atrasada alimenta inspeção, multa e indicadores; devolução no prazo não gera multa; o livro permanece DEVOLVIDO até a inspeção. |
| 6 | Solicitações de circulação como objetos | **Command** | Renovação executada duas vezes com o mesmo identificador soma apenas 30 dias; solicitações distintas seguem sujeitas ao limite de duas renovações. |
| 7 | Rotina comum para cadastros | **Template Method** | Estudante duplicado retorna o cadastro existente; estudante com CPF não cadastrado falha antes de qualquer gravação. |
| 8 | Famílias compatíveis de acesso aos dados | **Abstract Factory** | Perfil de teste fornece apenas objetos em memória; perfil de produção fornece repositórios MySQL com a mesma unidade de trabalho. |
| 9 | Serviço de consulta com recursos opcionais | **Decorator** | A segunda consulta usa o cache e ainda gera medição; resultado antigo do cache nunca autoriza reserva de livro que deixou de estar LIVRE. |
| 10 | Organização hierárquica do acervo | **Composite** | Unidade com duas seções (3 e 2 livros) informa 5; mover um livro entre seções não altera id, estado nem empréstimo. |

### Resumo de decisões por padrão

Baseado na proposta de solução (ver [Referências](#referências)); alternativas justificadas são aceitas pelos critérios de avaliação.

- **State:** uma classe por estado (LIVRE, RESERVADO, EMPRESTADO, RENOVADO, DEVOLVIDO, REPARANDO, INCINERADO); eventos não aceitos pelo estado são recusados sem alterar o livro. A guarda de renovação (`numRenovacoes < 2`) é avaliada antes de qualquer alteração.
- **Strategy:** `PoliticaDeMulta` com três implementações; a política vigente vem da configuração administrativa. A multa grava o valor e a política aplicada na emissão e não é recalculada depois.
- **Adapter:** o Financeiro depende apenas de um contrato institucional de cobrança; cada banco tem seu adaptador, que converte valores, documentos, identificadores, situações e notificações. A idempotência da quitação fica no serviço de quitação.
- **Facade:** `iCirculacao` coordena Relacionamento, Movimentacao, Acervo e Livro em operações transacionais, devolvendo comprovantes (DTOs). Os tratadores delegam a ela.
- **Observer:** o evento de devolução carrega vencimento, data de devolução e estudante, e é publicado após a confirmação. A falha de um ouvinte não afeta os demais nem desfaz a devolução.
- **Command:** solicitações com identificador, autor e instante de criação; o executor garante, por registro com chave única, que o mesmo identificador não execute duas vezes. Não há operação de desfazer.
- **Template Method:** método-modelo de inclusão não sobrescrevível, na ordem: buscar existente, validar, verificar pré-requisitos (gancho), criar, armazenar e apresentar. As interfaces `iLivro`, `iPessoa`, `iEstudante` e `iAtendente` são preservadas.
- **Abstract Factory:** uma fábrica por família (memória e relacional), escolhida uma única vez pelo perfil de execução. O Oracle permanece como réplica e não recebe escritas da aplicação.
- **Decorator:** contrato de consulta, implementação original inalterada e decoradores de medição e cache combináveis. O cache guarda apenas metadados; a reserva sempre consulta o estado atual do Livro.
- **Composite:** grupos e itens respondem às mesmas operações de contagem e listagem. O grupo recusa ciclos e livros que já pertencem a outro grupo.

## Status dos requisitos

| Nº | Padrão | Implementação | Teste | UML |
|---|---|---|---|---|
| 1 | State | Pendente | Pendente | Pendente |
| 2 | Strategy | Pendente | Pendente | Pendente |
| 3 | Adapter | Pendente | Pendente | Pendente |
| 4 | Facade | Pendente | Pendente | Pendente |
| 5 | Observer | Pendente | Pendente | Pendente |
| 6 | Command | Pendente | Pendente | Pendente |
| 7 | Template Method | Pendente | Pendente | Pendente |
| 8 | Abstract Factory | Pendente | Pendente | Pendente |
| 9 | Decorator | Pendente | Pendente | Pendente |
| 10 | Composite | Pendente | Pendente | Pendente |

A tabela de rastreabilidade completa (requisito, padrão, classes de cada papel e teste) estará em [`docs/rastreabilidade.md`](docs/rastreabilidade.md).

## Arquitetura

A interface chama apenas os tratadores e não contém regras de domínio. Direção das dependências:

```
web -> tratadores -> fachada (iCirculacao) -> domínio -> persistência
```

- **Persistência:** duas famílias, criadas pela fábrica do requisito 8: em memória (testes) e relacional MySQL (produção). O perfil de execução (`TESTE` ou `PRODUCAO`) é escolhido uma única vez na inicialização; perfil ausente ou desconhecido interrompe a inicialização.
- **Bancos A e B:** simulados por classes que imitam as APIs incompatíveis; o adaptador realiza a conversão.
- **Falhas:** exceções de domínio são convertidas em resultado de recusa pelos tratadores; operações transacionais desfazem todas as escritas se um passo falhar.

## Estrutura do repositório

```
Gerenciamento de Biblioteca iB2B/
├── biblioteca/
│   ├── web/                  # interface; chama apenas tratadores
│   ├── cadastros/            # Template Method
│   ├── circulacao/
│   │   ├── tratadores/       # TratadorDeEmprestimo, TratadorDeDevolucao
│   │   ├── facade/           # iCirculacao, ServicoDeCirculacao, comprovantes
│   │   ├── eventos/          # Observer
│   │   └── solicitacoes/     # Command
│   ├── dominio/
│   │   ├── estados/          # State
│   │   └── organizacao/      # Composite
│   ├── consulta/             # Decorator
│   ├── financeiro/
│   │   ├── multa/            # Strategy
│   │   └── bancos/           # Adapter
│   └── persistencia/         # Abstract Factory
├── tests/                    # um teste por cenário de verificação
├── docs/
│   ├── uml/                  # modelos Astah (.asta) e PDFs
│   └── rastreabilidade.md
├── .env.example
├── README.md
├── REGISTRO_LLM.md
├── requirements.txt
└── run.py
```

`Livro`, `Acervo`, `Relacionamento` e `Movimentacao` ficam em `biblioteca/dominio/`.

## Premissas do domínio

Conforme a lista de problemas:

- **Renovação:** guarda `numRenovacoes < 2` (no máximo duas renovações), cada uma com +30 dias sobre o vencimento atual.
- **Devolução:** conduz o livro a DEVOLVIDO antes da inspeção.
- **Laudo irrecuperável:** o evento `registrarLaudoIrrecuperavel()` leva REPARANDO a INCINERADO.
- **Livro** guarda vencimento, número de renovações e reservante do ciclo atual.
- **Movimentacao** guarda reservas, empréstimos e devoluções em associações distintas.
- **Multa:** dias corridos de atraso; valores monetários com precisão decimal (nunca ponto flutuante).

## Como executar

**Pré-requisitos:** Python (versão a confirmar), MySQL apenas para o perfil de produção.

```bash
# 1. criar e ativar o ambiente virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/macOS

# 2. instalar dependências
pip install -r requirements.txt

# 3. configurar o ambiente
cp .env.example .env          # preencher as variáveis do banco (perfil de produção)

# 4. iniciar a aplicação
python run.py
```

O perfil de testes não exige banco de dados nem configuração além da instalação das dependências.

## Testes

Um teste automatizado por cenário de verificação, com nome que identifica o requisito (por exemplo, `test_R01_terceira_renovacao_recusada`).

```bash
pytest
```

Os dez cenários devem passar na demonstração.

## Documentação e modelos UML

Entregáveis em `docs/`:

- Modelos no Astah (`.asta`) e exportados em PDF: diagrama de classes de cada padrão, máquina de estados de `Livro` e diagramas de sequência dos cenários.
- Tabela de rastreabilidade em `docs/rastreabilidade.md`.

O código deve corresponder aos modelos UML, incluindo a máquina de estados.

## Uso de LLMs

O uso de LLMs é livre; a responsabilidade é da equipe. Todo código deve ser explicável por qualquer integrante.

| Ferramenta e modelo | Partes do sistema | Finalidade |
|---|---|---|
| _a preencher_ | _a preencher_ | _a preencher_ |

O resumo dos pedidos feitos ao modelo e do que foi aceito, corrigido ou descartado está em [`REGISTRO_LLM.md`](REGISTRO_LLM.md).

## Prazos

| Marco | Data |
|---|---|
| Entrega do repositório | 27/11/2026, 09h40 |
| Demonstração (5 minutos por equipe) | 27/11/2026 |

Demonstração: execução dos dez testes, fluxo completo pela interface (reserva, empréstimo, renovação, devolução atrasada e multa), arguição individual e alteração ao vivo.

## Referências

- Trabalho: *Implementação do sistema de empréstimo de livros com padrões GoF*. Prof. Edson Emílio Scalabrin, PUCPR, 2S/2026.
- *Soluções dos problemas de aplicação dos padrões GoF*: sistema de empréstimo de livros, dez situações derivadas do Trabalho 02.
- Gamma, E.; Helm, R.; Johnson, R.; Vlissides, J. *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley, 1994.