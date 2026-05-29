# Catálogo de Anti-Patterns

Cada anti-pattern contém: nome, severidade, sinais de detecção, descrição e impacto.

---

## CRITICAL

### C-01: SQL Injection

**Severidade:** CRITICAL
**Sinais de detecção:**
- Concatenação de strings em queries SQL: `f"SELECT * FROM {table}"`, `"SELECT * FROM " + table`
- Formatação com `%s` ou `.format()` em SQL: `"WHERE name = '%s'" % name`
- Uso de f-strings em queries: `f"WHERE id = {id}"`
- Templates string com interpolação: `` `WHERE id = ${id}` ``

**Descrição:** Queries SQL construídas por concatenação de strings permitem injeção de código malicioso.
**Impacto:** Acesso não autorizado a dados, bypass de autenticação, drop de tabelas.

---

### C-02: Credenciais Hardcoded

**Severidade:** CRITICAL
**Sinais de detecção:**
- Strings literais com senhas: `password = 'minha-senha'`, `"password": "123456"`
- Secret keys fixas: `SECRET_KEY = 'chave-secreta'`, `secretKey: 'abc123'`
- Connection strings com credenciais: `mysql://user:pass@host`
- Tokens/API keys no código: `API_KEY = 'sk-...'`
- Credenciais SMTP hardcoded: `smtp_user = 'email'`, `smtp_pass = 'senha'`

**Descrição:** Credenciais e segredos hardcoded no código-fonte.
**Impacto:** Exposição de dados sensíveis, acesso não autorizado a sistemas.

---

### C-03: God Class / God Method

**Severidade:** CRITICAL
**Sinais de detecção:**
- Arquivo único com >200 linhas contendo múltiplas responsabilidades
- Classe/função que mistura lógica de negócio, acesso a dados, roteamento e formatação
- Múltiplos domínios atendidos por um único arquivo
- Funções com >50 linhas que fazem mais de uma coisa

**Descrição:** Arquivo ou classe que concentra responsabilidades demais, violando SRP.
**Impacto:** Impossível testar em isolamento, mudanças causam efeitos colaterais imprevisíveis.

---

### C-04: Execução Arbitrária de Código/SQL

**Severidade:** CRITICAL
**Sinais de detecção:**
- Endpoints que aceitam SQL raw via parâmetro: `request.json['query']`
- `eval()` ou `exec()` com input do usuário
- Rotas admin sem autenticação que executam operações perigosas
- Endpoints de "debug" ou "admin" expostos em produção

**Descrição:** Endpoints que permitem execução arbitrária de SQL ou código sem restrição.
**Impacto:** Controle total do banco de dados ou servidor por atacante.

---

### C-05: Hash de Senhas Inseguro

**Severidade:** CRITICAL
**Sinais de detecção:**
- Senhas armazenadas em texto plano
- Uso de MD5 para hash: `hashlib.md5(password.encode())`
- Uso de SHA1 para hash: `hashlib.sha1(password.encode())`
- Funções customizadas de "hash" que são reversíveis (base64, XOR)
- Hash sem salt

**Descrição:** Senhas protegidas com algoritmos criptograficamente quebrados ou sem salt.
**Impacto:** Senhas podem ser recuperadas via rainbow tables ou ataque direto.

---

## HIGH

### H-01: Zero Autenticação/Autorização

**Severidade:** HIGH
**Sinais de detecção:**
- Nenhuma middleware de autenticação
- Rotas de DELETE, PUT, POST sem verificação de identidade
- Rotas admin acessíveis sem login
- Tokens hardcoded ou fake: `'fake-jwt-token-' + str(id)`
- Middleware de auth existe mas não é aplicado nas rotas

**Descrição:** Nenhum endpoint exige autenticação ou autorização real.
**Impacto:** Qualquer pessoa pode executar qualquer operação, incluindo admin.

---

### H-02: Senhas Expostas em Respostas

**Severidade:** HIGH
**Sinais de detecção:**
- Campos `password` incluídos em serialização: `to_dict()` que inclui `password`
- Endpoints de listagem de usuários que retornam senhas
- `SELECT *` em tabelas de usuários que incluem campo de senha
- APIs que retornam objetos completos sem filtrar campos sensíveis

**Descrição:** Senhas ou dados sensíveis retornados em endpoints de API.
**Impacto:** Vazamento de senhas para qualquer consumidor da API.

---

### H-03: Nenhuma Validação de Entrada

**Severidade:** HIGH
**Sinais de detecção:**
- Parâmetros do request usados diretamente: `request.json['name']` sem validação
- Ausência de schema validation
- Tipos não verificados antes de uso
- Ausência de sanitização para dados que vão para SQL ou HTML

**Descrição:** Input do usuário usado sem validação ou sanitização.
**Impacto:** Dados inválidos causam bugs, injection, ou comportamento imprevisível.

---

### H-04: Lógica de Negócio nos Controllers/Routes

**Severidade:** HIGH
**Sinais de detecção:**
- Rotas com lógica de negócio complexa (>10 linhas de lógica além de validação/retorno)
- Queries SQL diretamente em handlers de rota
- Cálculos, transformações e regras de negócio dentro de callbacks de rota
- Controllers que acessam o banco diretamente

**Descrição:** Lógica de negócio pesada presa na camada de roteamento/controller.
**Impacto:** Difícil testar, difícil reutilizar, viola separação de responsabilidades.

---

## MEDIUM

### M-01: Queries N+1

**Severidade:** MEDIUM
**Sinais de detecção:**
- Queries SQL dentro de loops: `for item in items: db.execute("SELECT ...")`
- Múltiplas queries relacionadas executadas sequencialmente quando poderiam ser uma
- Acesso lazy a relacionamentos dentro de loops

**Descrição:** Padrão N+1 onde 1 query busca N registros e depois N queries buscam dados relacionados.
**Impacto:** Performance degrada linearmente com o volume de dados.

---

### M-02: Debug Mode em Produção

**Severidade:** MEDIUM
**Sinais de detecção:**
- `debug=True` ou `DEBUG = True` no código
- `host='0.0.0.0'` hardcoded (abre para todas as interfaces)
- Stack traces detalhados expostos ao usuário
- Modo verboso de logging ativado em produção

**Descrição:** Modo debug ativado em ambiente de produção.
**Impacto:** Expõe stack traces, abre servidor para todas as interfaces, facilita ataques.

---

### M-03: Código Duplicado

**Severidade:** MEDIUM
**Sinais de detecção:**
- Blocos de código idênticos ou quase idênticos em múltiplos locais
- Lógica de cálculo repetida em diferentes rotas
- Queries SQL similares copiadas entre funções
- Serialização manual repetida

**Descrição:** Lógica duplicada que deveria estar em um único lugar.
**Impacto:** Mudanças precisam ser feitas em múltiplos locais, risco de inconsistência.

---

### M-04: Falta de Tratamento de Erros

**Severidade:** MEDIUM
**Sinais de detecção:**
- Ausência de try/except em operações de banco
- Erros retornados como strings genéricas sem status code adequado
- Nenhum middleware global de error handling
- `except:` vazio que engole erros silenciosamente
- Erros de DB propagados diretamente para o cliente

**Descrição:** Erros não tratados ou tratados de forma inadequada.
**Impacto:** Experiência ruim para o consumidor da API, difícil debugging, possível vazamento de informações.

---

## LOW

### L-01: Magic Numbers

**Severidade:** LOW
**Sinais de detecção:**
- Números literais sem contexto: `if status == 3`, `limit = 50`
- Valores hardcoded que deveriam ser constantes nomeadas
- Códigos de status HTTP como números: `return '', 201` sem comentário

**Descrição:** Valores numéricos literais sem nome explicativo.
**Impacto:** Código difícil de entender e manter.

---

### L-02: Nomenclatura Ruim

**Severidade:** LOW
**Sinais de detecção:**
- Variáveis com nomes obscuros: `x`, `y`, `aux`, `tmp`, `data2`
- Funções com nomes genéricos: `process()`, `handle()`, `do_stuff()`
- Abreviações inconsistentes: `usr`, `prod`, `qty`
- Nomes em idiomas misturados

**Descrição:** Nomes de variáveis, funções ou classes que não expressam intenção.
**Impacto:** Reduz legibilidade e aumenta curva de aprendizado.

---

### L-03: API Deprecated

**Severidade:** LOW
**Sinais de detecção:**

**Python/Flask:**
- `flask.jsonify` → preferir `flask.json` (Flask 2.2+)
- `app.run(debug=True)` → usar servidor WSGI em produção
- `@app.errorhandler` sem tipo → especificar tipo de exceção
- `request.get_json(force=True)` → `request.get_json()` com validação

**Node.js/Express:**
- `require()` em projetos que já usam ESM
- `app.use(bodyParser.json())` → `express.json()` (body-parser deprecated, integrado ao Express 4.16+)
- `res.send(status)` → `res.sendStatus(status)` ou `res.status(code).json()`
- `app.listen()` sem error handling
- Callbacks onde async/await seria mais claro

**Descrição:** Uso de APIs ou padrões obsoletos do framework.
**Impacto:** Código pode quebrar em futuras versões, perde melhorias de performance/segurança.

---

### L-04: Logs Sensíveis no Console

**Severidade:** LOW
**Sinais de detecção:**
- `console.log()` com dados sensíveis: senhas, tokens, cartões
- `print()` de dados sensíveis em Python
- Logs de requisições que incluem headers de autorização
- Chaves de API ou gateway impressas em log

**Descrição:** Informações sensíveis registradas em logs de console.
**Impacto:** Dados sensíveis podem ser acessados por quem tem acesso aos logs.
