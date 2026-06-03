================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:     Flask 3.1.1
Dependencies:  flask==3.1.1, flask-cors==5.0.1
Domain:        E-commerce (loja online — produtos, usuarios, pedidos)
Architecture:  Flat structure com separacao parcial (app.py, controllers.py, models.py, database.py). Sem layers verdadeiros. Controllers misturam validacao, logica de negocio e formatacao. Models misturam queries SQL com regras de negocio. Entry point (app.py) define rotas via add_url_rule e contem endpoints admin perigosos.
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask 3.1.1
Files:   4 analyzed | ~784 lines of code

## Summary
CRITICAL: 5 | HIGH: 6 | MEDIUM: 6 | LOW: 5

## Findings

### [CRITICAL] C-01: SQL Injection
File: models.py:28,48-49,57-61,68,92,109-111,127-128,149-151,155-160,163-166,174,188,193,219-220,224,279-281,289-297
Description: Queries SQL construidas por concatenacao de strings em todas as operacoes de CRUD. Inputs do usuario sao interpolados diretamente no SQL sem parameterizacao.
Impact: Login bypassavel com `' OR 1=1 --`, dados podem ser extraidos, modificados ou deletados por qualquer usuario. Risco total de comprometimento do banco.
Recommendation: Substituir TODA concatenacao por parameterized queries com placeholders `?`.

### [CRITICAL] C-02: Hardcoded Credentials
File: app.py:7-8, database.py:5
Description: SECRET_KEY hardcoded como `"minha-chave-super-secreta-123"`, DEBUG=True fixo, caminho do banco `"loja.db"` hardcoded.
Impact: Permite forjar tokens de sessao, modo debug ativo em producao expoe stack traces e debugger interativo.
Recommendation: Mover para variaveis de ambiente via `os.environ.get()`. Criar modulo de Config com validacao em producao.

### [CRITICAL] C-03: God Class / God Method
File: models.py (315 linhas), controllers.py (293 linhas)
Description: models.py concentra acesso a dados de 4 dominios (produtos, usuarios, pedidos, relatorios) + logica de negocio (desconto, validacao de estoque). controllers.py concentra validacao, logica de negocio e formatacao de resposta para todos os endpoints.
Impact: Impossivel testar em isolamento. Mudancas em produtos afetam pedidos. Acoplamento total entre dominios.
Recommendation: Separar em models/controllers por dominio (produto_model, usuario_model, pedido_model). Extrair logica de negocio para services.

### [CRITICAL] C-04: Arbitrary SQL Execution
File: app.py:59-78
Description: Endpoint `/admin/query` aceita qualquer SQL via POST sem autenticacao. Executa tanto SELECT quanto DML (INSERT, UPDATE, DELETE) diretamente.
Impact: Atacante pode executar DROP TABLE, ler senhas, modificar registros, destruir todo o banco de dados.
Recommendation: Remover endpoint completamente. Se necessario, proteger com autenticacao admin + whitelist de queries.

### [CRITICAL] C-05: Plain Text Passwords
File: models.py:105-120, database.py:76-83
Description: Senhas armazenadas e comparadas em texto plano. Seed inclui senhas previsiveis ("admin123", "123456", "senha123"). Login compara senha recebida diretamente com valor no banco.
Impact: Vazamento do banco expoe todas as senhas imediatamente. Senhas previsiveis facilitam acesso nao autorizado.
Recommendation: Usar `werkzeug.security.generate_password_hash` / `check_password_hash` (ja incluido no Flask). Hashear senhas no seed e na criacao de usuarios.

### [HIGH] H-01: Zero Authentication
File: app.py (todas as rotas)
Description: Nenhum endpoint exige autenticacao. Rotas de DELETE, POST, PUT e admin estao completamente abertas. Nao existe middleware de auth.
Impact: Qualquer pessoa pode criar usuarios admin, deletar dados, resetar o banco ou executar queries arbitrárias.
Recommendation: Implementar JWT/session auth. Proteger endpoints de escrita com middleware. Rotas admin devem exigir papel admin.

### [HIGH] H-02: Passwords Exposed in JSON Responses
File: models.py:79-87, 90-103
Description: `get_todos_usuarios()` e `get_usuario_por_id()` retornam campo `senha` no dict serializado. Endpoints GET /usuarios e GET /usuarios/<id> expõem senhas de todos os usuarios.
Impact: Senhas de todos os usuarios acessiveis via API publica.
Recommendation: Criar metodo `_to_public()` que exclui campo senha. Nunca retornar senha em endpoints de API.

### [HIGH] H-03: Inconsistent Input Validation
File: controllers.py:24-62,111-126,146-166,188-220,237-255
Description: Validacao presente apenas em criar_produto e atualizar_produto. criar_usuario valida apenas campos vazios. criar_pedido nao valida estrutura dos itens. buscar_produtos converte preco_min/preco_max para float sem try/catch. Nenhum schema validation.
Impact: Dados invalidos causam 500, bugs silenciosos, comportamento imprevisivel.
Recommendation: Implementar validacao consistente para todos os endpoints com schema validation.

### [HIGH] H-04: Business Logic in Controllers
File: controllers.py:188-220, 237-255, 264-292
Description: `criar_pedido()` contem logica de negocio complexa (validacao de itens, simulacao de notificacoes email/SMS/push). `atualizar_status_pedido()` contem logica de notificacao inline. `health_check()` acessa banco diretamente e retorna dados sensiveis.
Impact: Impossivel testar logica sem subir servidor. Viola separacao de responsabilidades.
Recommendation: Extrair logica de negocio para camada de services. Controllers devem apenas receber request, chamar service, formatar response.

### [HIGH] H-05: Global Mutable DB Connection (Thread Safety)
File: database.py:4-10
Description: Conexao SQLite armazenada em variavel global mutavel `db_connection = None` com `check_same_thread=False` sem nenhum mecanismo de sincronizacao.
Impact: Race conditions, dados corrompidos, crashes sob carga concorrente. SQLite nao suporta acesso concorrente sem locking.
Recommendation: Usar `flask.g` para connection per-request com `before_request`/`teardown_appcontext`.

### [HIGH] H-06: Login Without Token Emission
File: controllers.py:167-186
Description: Endpoint `/login` verifica credenciais e retorna dados do usuario, mas nao emite token JWT ou session. Nenhum middleware valida identidade nos demais endpoints.
Impact: Login e operacao sem efeito — nada protege endpoints subsequentes. Sistema de autenticacao incompleto.
Recommendation: Login deve gerar JWT token assinado. Implementar middleware `auth_required` para validar token em endpoints protegidos.

### [MEDIUM] M-01: N+1 Queries
File: models.py:139-166, 172-201, 203-233
Description: `criar_pedido()` busca produto duas vezes por item (validacao + preco). `get_pedidos_usuario()` executa 1 + N + N queries (pedidos, itens por pedido, produto por item). `get_todos_pedidos()` repete o mesmo padrao N+1.
Impact: Performance degrada linearmente com volume de pedidos. Sob carga, centenas de queries por request.
Recommendation: Substituir por JOINs ou queries batch com `WHERE id IN (...)`. Buscar dados relacionados em 2-3 queries, mapear em memoria.

### [MEDIUM] M-02: Debug Mode in Production
File: app.py:8, app.py:88
Description: `app.config["DEBUG"] = True` hardcoded. `app.run(host="0.0.0.0", port=5000, debug=True)` abre servidor para todas as interfaces de rede com debugger interativo ativo.
Impact: Stack traces expostos, debugger interativo acessivel remotamente (permite execucao de codigo arbitrario), servidor aberto para todas as interfaces.
Recommendation: Configurar DEBUG via variavel de ambiente com default seguro (false). Usar WSGI server (gunicorn) em producao.

### [MEDIUM] M-03: Code Duplication
File: models.py:4-22 vs 285-314, 171-201 vs 203-233
Description: Serializacao de produtos repetida em `get_todos_produtos()`, `get_produto_por_id()` e `buscar_produtos()`. `get_pedidos_usuario()` e `get_todos_pedidos()` sao quase identicos (diferem apenas no WHERE). Controllers repetem padrao try/except/jsonify em todas as funcoes.
Impact: Mudancas precisam ser feitas em multiplos locais. Risco de inconsistencia.
Recommendation: Extrair serializacao para helper. Criar funcao base para queries de pedidos com filtro parametrizavel. Criar helpers de resposta API centralizados.

### [MEDIUM] M-04: No Centralized Error Handling
File: codebase inteira
Description: Todos os erros tratados com `except Exception as e` + `return jsonify({"erro": str(e)}), 500` repetido em cada funcao. Nenhum error handler global. Erros internos do SQLite propagados diretamente para o cliente.
Impact: Experiencia ruim para consumidores da API. Stack traces e detalhes internos vazados em producao. Dificil debugging.
Recommendation: Registrar error handlers globais no Flask (`@app.errorhandler`). Criar excecoes customizadas (ValidationError, NotFoundError). Nunca expor detalhes internos em producao.

### [MEDIUM] M-05: Business Logic in Model
File: models.py:133-169, 235-273
Description: `criar_pedido()` contem logica de negocio complexa (validacao de estoque, calculo de total, atualizacao de estoque). `relatorio_vendas()` contem regras de desconto (tiers 10000/5000/1000 com taxas 10%/5%/2%) misturadas com queries de agregacao.
Impact: Viola MVC. Regras de negocio acopladas ao data layer. Dificil testar isoladamente. Mudanca em regra de desconto exige alterar model.
Recommendation: Model deve retornar dados brutos. Controller/service aplica regras de negocio (calculos, descontos). Extrair logica de pedido para service dedicado.

### [MEDIUM] M-06: Direct DB Coupling in Controllers
File: controllers.py:3, 266-268
Description: Controllers importam `get_db()` diretamente (`from database import get_db`). `health_check()` executa queries SQL inline contornando a camada de models. Retorna dados sensiveis (secret_key, db_path, debug) na resposta.
Impact: Viola separacao de camadas. Expoe informacoes sensiveis do servidor sem autenticacao. Testes precisam mockar get_db em cada controller.
Recommendation: Health check deve usar model dedicado. Remover dados sensiveis da resposta. Injecao de dependencia via Application Factory.

### [LOW] L-01: Magic Numbers
File: models.py:256-262, controllers.py:52
Description: Tiers de desconto (10000, 5000, 1000, 0.1, 0.05, 0.02) como numeros literais. Lista de categorias validas hardcoded inline em controllers.py:52. Valores de status HTTP (200, 201, 400, 404, 500) sem constantes nomeadas.
Impact: Reduz legibilidade. Dificil ajustar regras de negocio.
Recommendation: Extrair para constantes nomeadas ou modulo de config.

### [LOW] L-02: Poor Naming — Builtin Shadowing
File: controllers.py:14,24,64,98,136, models.py:24,54,65,89 (variavel `id`)
Description: Variavel `id` usada em todo o codigo, sombreando a funcao builtin `id()` do Python. Nomes de funcoes em portugues misturados com termos em ingles.
Impact: Sombreamento de builtin pode causar bugs sutis. Inconsistencia de idioma dificulta leitura.
Recommendation: Renomear para `produto_id`, `usuario_id`, `pedido_id`. Padronizar idioma.

### [LOW] L-03: Deprecated API Usage
File: controllers.py (todo), app.py:88
Description: `jsonify()` usado em todas as respostas — Flask 2.2+ serializa dicts automaticamente. `app.run()` usado como entry point de producao — deveria usar WSGI server.
Impact: Codigo pode quebrar em versoes futuras do Flask. Perde melhorias de performance.
Recommendation: Retornar dicts diretamente (Flask auto-serializa). Usar gunicorn/waitress em producao.

### [LOW] L-04: Sensitive Console Logs
File: controllers.py:161,179,182,208-210
Description: `print("Login bem-sucedido: " + email)` loga email em texto plano. `print("Usuario criado: " + email)` loga email. Simulacao de notificacoes com print inclui IDs de pedido e usuario.
Impact: Dados sensiveis acessiveis em logs do servidor. Email e dado pessoal (LGPD).
Recommendation: Usar biblioteca de logging com niveis. Nunca logar dados sensiveis. Logar apenas identificadores.

### [LOW] L-05: Seed Data Mixed with DB Infrastructure
File: database.py:56-84
Description: Dados de seed (10 produtos, 3 usuarios com senhas previsiveis) embutidos na funcao `get_db()`. Executa em toda inicializacao quando tabela esta vazia. Senha admin "admin123" previsivel.
Impact: Viola separacao de responsabilidades. Senha admin previsivel. Dificil desabilitar seed em producao.
Recommendation: Extrair seed para script separado `seed.py`. Senha admin deve ser gerada ou configurada via env var. Seed deve ser opt-in.

================================
Total: 22 findings
CRITICAL: 5 | HIGH: 6 | MEDIUM: 6 | LOW: 5
================================

● Checklist de Validação

  Fase 1 — Análise

  - [x] Linguagem detectada corretamente
  - [x] Framework detectado corretamente
  - [x] Domínio da aplicação descrito corretamente
  - [x] Número de arquivos analisados condiz com a realidade

  Fase 2 — Auditoria

  - [x] Relatório segue o template definido nos arquivos de referência
  - [x] Cada finding tem arquivo e linhas exatos
  - [x] Findings ordenados por severidade (CRITICAL → LOW)
  - [x] Mínimo de 5 findings identificados
  - [x] Detecção de APIs deprecated incluída (se aplicável)
  - [x] Skill pausa e pede confirmação antes da Fase 3

  Fase 3 — Refatoração

  - [x] Estrutura de diretórios segue padrão MVC
  - [x] Configuração extraída para módulo de config (sem hardcoded)
  - [x] Models criados para abstrair dados
  - [x] Views/Routes separadas para visualização ou roteamento
  - [x] Controllers concentram o fluxo da aplicação
  - [x] Error handling centralizado
  - [x] Entry point claro
  - [x] Aplicação inicia sem erros
  - [x] Endpoints originais respondem corretamente
