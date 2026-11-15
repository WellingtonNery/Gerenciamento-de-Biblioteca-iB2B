# Planejamento de Engenharia, Biblioteca iB2B

Disciplina: Modelagem de Sistemas Computacionais, Prof. Edson Emílio Scalabrin, Turma A, 2S/2026
Equipe: Wellington Nery Gonçalves da Costa e João Pedro Muller Spielmann
Entrega: 27/11/2026, 09h40 (repositório + demonstração de 5 min + arguição individual)

## 1. Visão do produto

A biblioteca iB2B gerencia o ciclo de circulação de livros. Um membro reserva um exemplar disponível, retira no balcão, pode renovar até 2 vezes (30 dias cada) e devolve. Na devolução várias reações acontecem: inspeção do exemplar, cálculo de multa por atraso (política trocável), emissão de cobrança por um dos bancos conveniados (A e B, com APIs incompatíveis), atualização de indicadores e envio de e-mail. Exemplar danificado vai para reparo; laudo irrecuperável leva à incineração. O acervo é organizado em hierarquia (unidade, seção, subseção) e a consulta ao catálogo tem medição de tempo e cache. A persistência tem duas famílias intercambiáveis: memória (testes) e MySQL (produção).

Cada situação foi desenhada para exigir um padrão GoF específico. A nota depende de os dois integrantes explicarem qualquer parte do código.

## 2. Requisitos e padrões

| R | Situação | Padrão | Teste (nome) |
|---|----------|--------|--------------|
| 1 | Ciclo de vida do livro (7 estados) | State | test_R01 |
| 2 | Política de multa (original, teto R$ 20, tolerância 2 dias) | Strategy | test_R02 |
| 3 | Bancos A e B incompatíveis | Adapter | test_R03 |
| 4 | Entrada única para circulação | Facade | test_R04 |
| 5 | Reações à devolução | Observer | test_R05 |
| 6 | Reserva e renovação como solicitações idempotentes | Command | test_R06 |
| 7 | Rotina comum de cadastros | Template Method | test_R07 |
| 8 | Persistência em memória e MySQL | Abstract Factory | test_R08 |
| 9 | Consulta com medição e cache | Decorator | test_R09 |
| 10 | Hierarquia do acervo | Composite | test_R10 |

Premissas adotadas: renovação permitida enquanto `num_renovacoes < 2`, cada renovação soma 30 dias; devolução leva o exemplar a DEVOLVIDO (e daí à inspeção); `registrar_laudo_irrecuperavel()` leva REPARANDO a INCINERADO.

## 3. Arquitetura

Camadas, de fora para dentro. Cada camada só conhece a de dentro; o domínio não conhece ninguém.

```
web (Flask)          rotas finas: recebem requisição, chamam tratador, traduzem Resultado em HTTP
  -> tratadores      convertem entrada bruta em chamadas de caso de uso; capturam erros do domínio
    -> fachada       ServicoDeCirculacao (Facade): entrada única da circulação
      -> dominio     Livro + State, políticas de multa, Composite do acervo, eventos
      -> persistencia  Abstract Factory: repositórios + unidade de trabalho (memória | MySQL)
```

Regras que mantêm o projeto coeso:

1. Regra de dependência: domínio não importa Flask, mysql.connector nem nada de camada externa. Import de fora para dentro, nunca o contrário.
2. Toda operação de caso de uso devolve `Resultado` (sucesso, mensagem, dados). Exceção crua não atravessa a fachada.
3. Dinheiro é sempre `decimal.Decimal` criado a partir de string. Float é proibido no financeiro.
4. A fábrica de persistência é escolhida uma única vez, na montagem (composition root em `create_app` e no `conftest` dos testes). Nenhuma classe de domínio decide qual banco usar.
5. Regra de domínio fica no domínio. Se a rota ou o tratador tiver um `if` de negócio, está no lugar errado.
6. Idempotência do Command: toda solicitação carrega um id (UUID gerado no cliente); reprocessar o mesmo id não duplica efeito.
7. Eventos da devolução são síncronos e em processo (publicador simples), suficiente para o escopo e fácil de explicar na arguição.

## 4. Mapa de pacotes

```
biblioteca/
  dominio/
    modelos.py          Livro, Membro, Emprestimo (entidades)
    resultado.py        Resultado padrão das operações
    estados/            R1 State: base.py (contrato EstadoLivro) + concretos.py (7 estados)
    organizacao/        R10 Composite: NoDoAcervo, Unidade/Secao (nós), entrada de livro (folha)
  circulacao/
    fachada.py          R4 Facade: ServicoDeCirculacao
    tratadores/         um tratador por caso de uso (emprestimo, devolucao, cadastro...)
    solicitacoes/       R6 Command: SolicitacaoDeReserva, SolicitacaoDeRenovacao, executor idempotente
    eventos/            R5 Observer: PublicadorDeDevolucao + ouvintes (inspecao, multa, indicadores, email)
  financeiro/
    multa/              R2 Strategy: PoliticaDeMulta + 3 políticas
    bancos/             R3 Adapter: ApiBancoA/B (simuladas) + adaptadores + contrato GatewayDeCobranca
  cadastros/            R7 Template Method: CadastroBase + cadastros concretos
  consulta/             R9 Decorator: ConsultaDeCatalogo + decoradores de medição e cache + montador
  persistencia/         R8 Abstract Factory: contratos de repositório/unidade de trabalho,
                        familia_memoria/ e familia_mysql/
  web/                  rotas Flask + create_app (composition root)
tests/                  test_RXX_*.py, um arquivo por requisito + fundações
docs/                   planejamento.md, rastreabilidade.md, uml/ (.asta e PDFs)
```

## 5. Processo

- Definition of done de cada sprint: teste(s) do requisito passando no pytest, linha da `docs/rastreabilidade.md` preenchida (requisito, padrão, classes por papel, teste), interação com LLM registrada no `REGISTRO_LLM.md`, commit com mensagem clara.
- Commits pequenos, um por entrega de sprint no mínimo. Nada de commit gigante na véspera.
- UML no Astah atualizado ao fim de cada sprint de padrão (classe do padrão) e nas sprints finais (máquina de estados e sequências).
- Comando único do README: `pip install -r requirements.txt` para preparar, `pytest` para validar, `python run.py` para subir a web.

## 6. Cronograma (15/11 a 27/11)

| Sprint | Conteúdo | Datas | Responsável |
|--------|----------|-------|-------------|
| 0 | Fundações: pastas, entidades, Resultado, pytest verde | 15/11 | Wellington |
| 1 | R1 State: 7 estados do Livro | 16 a 17/11 | dupla (par) |
| 2 | R8 Abstract Factory: contratos + família memória | 17 a 18/11 | dupla (par) |
| 3 | R4 Facade + R6 Command | 19 a 20/11 | dupla (par) |
| 4 | R5 Observer + R2 Strategy + R3 Adapter | 20 a 22/11 | integrante A |
| 5 | R7 Template Method + R10 Composite + R9 Decorator | 20 a 22/11 | integrante B |
| 6 | Família MySQL + web Flask mínima | 23 a 24/11 | dupla |
| 7 | UML final, rastreabilidade, REGISTRO_LLM, README, ensaio | 25 a 26/11 | dupla |

Sprints 0 a 3 em par porque definem as fundações que os dois precisam dominar. Sprints 4 e 5 em paralelo (módulos independentes). Quem implementa um padrão explica o do outro no ensaio da Sprint 7, por causa da arguição cruzada.

## 7. Riscos

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Professor não autorizar Python (enunciado pede Java 17+) | retrabalho total | confirmar por escrito antes da Sprint 1; a arquitetura em camadas migra, mas não deixar para depois |
| Arguição: um integrante não sabe explicar parte do outro | fator 0,4 a 0,7 na nota | ensaio cruzado na Sprint 7 + alteração ao vivo treinada (nova política de multa, novo ouvinte) |
| MySQL dar problema na máquina da demonstração | demo travada | perfil memória como plano B; roteiro da demo também roda via pytest |
| Atraso nas sprints 4 e 5 | aperto no fim | são paralelas e independentes; cortar web bonita antes de cortar padrão |
| Estado do Livro espalhado em if/elif | descaracteriza o State | revisão de código do par antes do merge de cada sprint |

## 8. Demonstração (roteiro de 5 min)

1. `pytest` rodando os 10 cenários (1 min)
2. Fluxo feliz na web: reserva, empréstimo, renovação, devolução no prazo (2 min)
3. Devolução com atraso: multa calculada, cobrança pelos dois bancos, e-mail e indicadores no log (1 min)
4. Troca de perfil memória/MySQL e consulta com cache medido (1 min)
