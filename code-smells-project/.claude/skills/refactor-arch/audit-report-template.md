# Template de Relatório de Auditoria

Use este template na Fase 2 para gerar o relatório de auditoria.

---

## Formato do Relatório

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework e versão se disponível>
Dependencies:  <lista de dependências principais>
Domain:        <domínio inferido da aplicação>
Architecture:  <descrição da arquitetura atual>
Source files:  <N> files analyzed
DB tables:     <tabelas detectadas, se aplicável>
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome do projeto>
Stack:   <linguagem> + <framework>
Files:   <N> analyzed | ~<X> lines of code

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings

### [<SEVERIDADE>] <Título do Problema>
File: <caminho do arquivo>:<linha ou intervalo>
Description: <descrição clara do problema>
Impact: <impacto no sistema>
Recommendation: <recomendação de correção>
Deprecated API: <se aplicável, qual API deprecated e alternativa moderna>

[... repetir para cada finding ...]

================================
Total: <N> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

---

## Regras de Formatação

1. **Ordenação:** Findings ordenados por severidade (CRITICAL → HIGH → MEDIUM → LOW)
2. **Localização:** Cada finding DEVE ter arquivo e linha(s) exata(s)
3. **Descrição:** Clara e específica — não usar "código ruim", usar "query SQL construída por concatenação de strings na linha 45"
4. **Impacto:** Descrever consequência prática, não teórica
5. **Recomendação:** Ação concreta e específica
6. **Deprecated API:** Incluir se aplicável, com alternativa moderna recomendada

---

## Exemplo Completo

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] SQL Injection
File: models.py:25-30
Description: Queries SQL construídas por concatenação de f-strings em todas as operações de CRUD.
Impact: Login bypassável com `' OR 1=1 --`, dados podem ser extraídos ou deletados por qualquer usuário.
Recommendation: Usar parameterized queries com placeholders `?` em todas as operações SQL.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como string literal no código-fonte.
Impact: Permite forjar tokens de sessão se sessions/JWT forem implementados.
Recommendation: Mover para variável de ambiente via os.environ.get('SECRET_KEY').

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Arbitrary SQL Execution
File: app.py:45-52
Description: Endpoint /admin/query aceita qualquer SQL via POST sem autenticação.
Impact: Atacante pode executar DROP TABLE, ler dados sensíveis ou modificar registros.
Recommendation: Remover endpoint ou proteger com autenticação admin e whitelist de queries.

### [HIGH] Senhas em Texto Plano
File: models.py:80-85
Description: Senhas gravadas sem hash. Endpoint GET /usuarios retorna todas as senhas.
Impact: Senhas de todos os usuários expostas via API.
Recommendation: Usar bcrypt ou arggon2 para hash de senhas. Remover campo password de respostas da API.

### [HIGH] Zero Authentication
File: app.py (todas as rotas)
Description: Nenhum endpoint exige autenticação. Rotas de DELETE, POST e admin estão abertas.
Impact: Qualquer pessoa pode criar admin, deletar dados ou resetar o banco.
Recommendation: Implementar JWT/session auth e middleware de proteção.

### [HIGH] Business Logic in Routes
File: controllers.py:30-60
Description: Rotas contêm lógica de negócio complexa, cálculos e acesso direto ao banco.
Impact: Impossível testar lógica sem subir o servidor. Viola separação de responsabilidades.
Recommendation: Extrair lógica para camada de services/controllers dedicada.

### [HIGH] Password Exposed in JSON
File: models.py:15-20
Description: Método to_dict() do model User inclui campo password na serialização JSON.
Impact: Senha de cada usuário retornada em toda resposta da API.
Recommendation: Remover password do to_dict() ou usar campo separado para serialização pública.

### [HIGH] No Input Validation
File: controllers.py (todas as rotas)
Description: Parâmetros do request.json usados diretamente sem validação de tipo, formato ou sanitização.
Impact: Dados inválidos causam bugs, SQL injection, comportamento imprevisível.
Recommendation: Implementar validação com schema para cada endpoint.

### [MEDIUM] N+1 Queries
File: models.py:100-115
Description: Listagem de pedidos executa 1 + N + N queries (pedidos, itens, produtos em loop separado).
Impact: Performance degrada linearmente com o número de pedidos.
Recommendation: Usar JOINs ou queries batch para buscar dados relacionados de uma vez.

### [MEDIUM] Debug Mode Active
File: app.py:120
Description: DEBUG = True e host = '0.0.0.0' hardcoded no app.run().
Impact: Stack traces expostos, servidor aberto para todas as interfaces de rede.
Recommendation: Configurar via variável de ambiente. Usar WSGI server em produção.

### [LOW] Magic Numbers
File: controllers.py:45,72
Description: Valores literais como 200, 404, 500 usados sem constante nomeada.
Impact: Reduz legibilidade.
Recommendation: Usar constantes nomeadas ou enums para status codes.

### [LOW] Hardcoded Secret Key
File: app.py:5
Description: SECRET_KEY = 'minha-chave-super-secreta-123' como string fixa.
Impact: Permite forjar tokens se sessions/JWT forem usados.
Recommendation: Carregar de variável de ambiente.

### [LOW] Health Check Leaks Secrets
File: app.py:95-100
Description: Endpoint /health retorna secret_key, debug e db_path sem autenticação.
Impact: Informações sensíveis do servidor expostas publicamente.
Recommendation: Remover dados sensíveis do health check ou proteger com auth.

================================
Total: 14 findings
================================
```
