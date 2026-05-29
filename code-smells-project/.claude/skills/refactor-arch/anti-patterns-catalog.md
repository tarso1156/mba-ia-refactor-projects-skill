# Catálogo de Anti-Patterns

Cada anti-pattern contém: nome, severidade, sinais de detecção, descrição, impacto e **como resolver**.

---

## Ordem de Prioridade na Resolução

Resolver na ordem abaixo. Severidade alta = risco real de segurança ou bloqueio de manutenção. Severidade baixa = melhoria de qualidade.

```
CRITICAL → HIGH → MEDIUM → LOW
```

**CRITICAL** — Risco de segurança ativo. Resolver **antes** de qualquer outro. Pode causar vazamento de dados, invasão ou perda de dados em produção.

**HIGH** — Problema arquitetural grave que compromete integridade ou testabilidade. Resolver logo após CRITICALs.

**MEDIUM** — Code smell que degrada performance ou manutenibilidade. Resolver como melhoria de sprint.

**LOW** — Questão de estilo ou boas práticas. Resolver quando conveniente, não bloqueia releases.

---

## CRITICAL

### C-01: SQL Injection

**Severidade:** CRITICAL
**Prioridade de resolução:** 1ª — resolver imediatamente, antes de qualquer deploy.

**Sinais de detecção:**
- Concatenação de strings em queries SQL: `f"SELECT * FROM {table}"`, `"SELECT * FROM " + table`
- Formatação com `%s` ou `.format()` em SQL: `"WHERE name = '%s'" % name`
- Uso de f-strings em queries: `f"WHERE id = {id}"`
- Templates string com interpolação: `` `WHERE id = ${id}` ``

**Descrição:** Queries SQL construídas por concatenação de strings permitem injeção de código malicioso.
**Impacto:** Acesso não autorizado a dados, bypass de autenticação, drop de tabelas.

**Como resolver:**
1. Substituir **toda** concatenação de strings em SQL por parameterized queries (placeholders `?` para SQLite, `%s` para PostgreSQL com psycopg2).
2. Nunca interpolar input do usuário diretamente no SQL.
3. Se precisar de queries dinâmicas (nomes de tabela/coluna), usar whitelist de valores permitidos.

**Antes:**
```python
# Python/SQLite — VULNERÁVEL
cursor.execute(f"SELECT * FROM usuarios WHERE email = '{email}'")
cursor.execute("SELECT * FROM " + table + " WHERE id = " + str(id))
```

**Depois:**
```python
# Python/SQLite — SEGURO
cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
# Para nomes dinâmicos de tabela/coluna — whitelist
ALLOWED_TABLES = {"produtos", "usuarios", "pedidos"}
if table not in ALLOWED_TABLES:
    raise ValueError("Invalid table")
cursor.execute(f"SELECT * FROM {table} WHERE id = ?", (id,))  # nome seguro, valor parametrizado
```

```javascript
// Node.js/Express com mysql2 — VULNERÁVEL
db.query(`SELECT * FROM users WHERE email = '${email}'`);
```
```javascript
// Node.js/Express com mysql2 — SEGURO
db.query("SELECT * FROM users WHERE email = ?", [email]);
```

---

### C-02: Credenciais Hardcoded

**Severidade:** CRITICAL
**Prioridade de resolução:** 1ª — resolver imediatamente, antes de qualquer deploy.

**Sinais de detecção:**
- Strings literais com senhas: `password = 'minha-senha'`, `"password": "123456"`
- Secret keys fixas: `SECRET_KEY = 'chave-secreta'`, `secretKey: 'abc123'`
- Connection strings com credenciais: `mysql://user:pass@host`
- Tokens/API keys no código: `API_KEY = 'sk-...'`
- Credenciais SMTP hardcoded: `smtp_user = 'email'`, `smtp_pass = 'senha'`

**Descrição:** Credenciais e segredos hardcoded no código-fonte.
**Impacto:** Exposição de dados sensíveis, acesso não autorizado a sistemas.

**Como resolver:**
1. Mover **todo** segredo para variável de ambiente (`os.environ.get()` / `process.env`).
2. Usar arquivo `.env` local (nunca commitado) para desenvolvimento — `.env` deve estar no `.gitignore`.
3. Fazer a aplicação **falhar ao iniciar** se segredos obrigatórios não estiverem definidos em produção.
4. Gerar valores default seguros apenas para ambiente de dev.

**Antes:**
```python
# Python/Flask — VULNERÁVEL
SECRET_KEY = 'minha-chave-super-secreta-123'
DATABASE_URL = 'postgresql://admin:password123@localhost/mydb'
```

**Depois:**
```python
# Python/Flask — SEGURO
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DATABASE_URL = os.environ.get('DATABASE_URL')

    @classmethod
    def validate(cls):
        """Falha fast em produção se segredos faltam."""
        if not cls.SECRET_KEY:
            raise RuntimeError("SECRET_KEY environment variable is required")
        if not cls.DATABASE_URL:
            raise RuntimeError("DATABASE_URL environment variable is required")
```

```javascript
// Node.js — SEGURO
const config = {
  secretKey: process.env.SECRET_KEY || (() => {
    if (process.env.NODE_ENV === 'production') {
      throw new Error('SECRET_KEY is required in production');
    }
    return 'dev-only-secret';
  })(),
};
```

---

### C-03: God Class / God Method

**Severidade:** CRITICAL
**Prioridade de resolução:** 2ª — resolver logo após problemas de segurança. Pré-requisito para refatoração MVC.

**Sinais de detecção:**
- Arquivo único com >200 linhas contendo múltiplas responsabilidades
- Classe/função que mistura lógica de negócio, acesso a dados, roteamento e formatação
- Múltiplos domínios atendidos por um único arquivo
- Funções com >50 linhas que fazem mais de uma coisa

**Descrição:** Arquivo ou classe que concentra responsabilidades demais, violando SRP.
**Impacto:** Impossível testar em isolamento, mudanças causam efeitos colaterais imprevisíveis.

**Como resolver:**
1. Identificar as responsabilidades distintas no arquivo (ex: CRUD de produtos + CRUD de usuários + lógica de pedidos).
2. Separar em arquivos por domínio — um model e um controller por entidade.
3. Extrair lógica de negócio dos controllers para services se necessário.
4. Cada arquivo resultante deve ter uma única responsabilidade (SRP).

**Antes:**
```python
# models.py — GOD CLASS com 350+ linhas
class Database:
    def get_produtos(self): ...
    def create_produto(self, nome, preco): ...
    def get_usuarios(self): ...
    def verify_login(self, email, senha): ...
    def criar_pedido(self, usuario_id, itens): ...
    def calcular_desconto(self, total): ...
    def formatar_relatorio(self, dados): ...
```

**Depois:**
```
models/
  produto_model.py   # Apenas acesso a dados de produtos
  usuario_model.py   # Apenas acesso a dados de usuários
  pedido_model.py    # Apenas acesso a dados de pedidos
controllers/
  produto_controller.py  # Validação e orquestração de produtos
  usuario_controller.py  # Validação e orquestração de usuários
  pedido_controller.py   # Lógica de negócio de pedidos (desconto, cálculo)
```

---

### C-04: Execução Arbitrária de Código/SQL

**Severidade:** CRITICAL
**Prioridade de resolução:** 1ª — resolver imediatamente, antes de qualquer deploy.

**Sinais de detecção:**
- Endpoints que aceitam SQL raw via parâmetro: `request.json['query']`
- `eval()` ou `exec()` com input do usuário
- Rotas admin sem autenticação que executam operações perigosas
- Endpoints de "debug" ou "admin" expostos em produção

**Descrição:** Endpoints que permitem execução arbitrária de SQL ou código sem restrição.
**Impacto:** Controle total do banco de dados ou servidor por atacante.

**Como resolver:**
1. **Remover** endpoints que aceitam SQL ou código arbitrário. Não existem casos legítimos em produção.
2. Substituir `eval()`/`exec()` por alternativas seguras (AST parsing, funções mapeadas em dict).
3. Se um endpoint admin é necessário, proteger com autenticação + autorização admin + rate limiting.
4. Nunca expor endpoints de debug em produção — usar feature flag ou environment check.

**Antes:**
```python
# VULNERÁVEL — endpoint de admin sem proteção
@app.route('/admin/query', methods=['POST'])
def run_query():
    sql = request.json['query']  # Qualquer SQL é executado
    result = db.execute(sql)
    return jsonify({"result": [dict(row) for row in result]})
```

**Depois:**
```python
# SEGURO — endpoint removido ou protegido
# Opção 1: Remover completamente (recomendado)
# Opção 2: Se necessário, proteger rigorosamente
@app.route('/admin/query', methods=['POST'])
@admin_required  # Middleware de auth admin
def run_query():
    # Whitelist de queries permitidas
    ALLOWED_QUERIES = {
        'count_users': 'SELECT COUNT(*) FROM usuarios',
        'count_orders': 'SELECT COUNT(*) FROM pedidos',
    }
    query_key = request.json.get('query_key')
    if query_key not in ALLOWED_QUERIES:
        return jsonify({"erro": "Query não permitida"}), 403
    result = db.execute(ALLOWED_QUERIES[query_key])
    return jsonify({"result": [dict(row) for row in result]})
```

---

### C-05: Hash de Senhas Inseguro

**Severidade:** CRITICAL
**Prioridade de resolução:** 1ª — resolver imediatamente. Senhas em texto plano ou hash fraco = vazamento garantido em breach.

**Sinais de detecção:**
- Senhas armazenadas em texto plano
- Uso de MD5 para hash: `hashlib.md5(password.encode())`
- Uso de SHA1 para hash: `hashlib.sha1(password.encode())`
- Funções customizadas de "hash" que são reversíveis (base64, XOR)
- Hash sem salt

**Descrição:** Senhas protegidas com algoritmos criptograficamente quebrados ou sem salt.
**Impacto:** Senhas podem ser recuperadas via rainbow tables ou ataque direto.

**Como resolver:**
1. Usar biblioteca de hash dedicada — nunca `hashlib` direto para senhas.
2. Python: `werkzeug.security.generate_password_hash` / `check_password_hash` (já incluído no Flask) ou `bcrypt` / `argon2-cffi`.
3. Node.js: `bcrypt` ou `argon2`.
4. Migração de senhas existentes: hashear no próximo login do usuário (lazy migration).

**Antes:**
```python
# VULNERÁVEL — texto plano ou hash fraco
senha = dados['senha']  # salvo direto no banco
hash = hashlib.md5(senha.encode()).hexdigest()  # MD5 quebrado
```

**Depois:**
```python
# SEGURO — werkzeug (padrão Flask)
from werkzeug.security import generate_password_hash, check_password_hash

# Ao criar usuário
hashed = generate_password_hash(senha)  # usa pbkdf2 com salt automático

# Ao verificar login
if check_password_hash(user['senha'], senha_fornecida):
    # login OK
```

```python
# SEGURO — bcrypt (alternativa)
import bcrypt
hashed = bcrypt.hashpw(senha.encode(), bcrypt.gensalt())
if bcrypt.checkpw(senha.encode(), hashed):
    # login OK
```

---

## HIGH

### H-01: Zero Autenticação/Autorização

**Severidade:** HIGH
**Prioridade de resolução:** 2ª — resolver logo após CRITICALs. Sem auth, qualquer endpoint é público.

**Sinais de detecção:**
- Nenhuma middleware de autenticação
- Rotas de DELETE, PUT, POST sem verificação de identidade
- Rotas admin acessíveis sem login
- Tokens hardcoded ou fake: `'fake-jwt-token-' + str(id)`
- Middleware de auth existe mas não é aplicado nas rotas

**Descrição:** Nenhum endpoint exige autenticação ou autorização real.
**Impacto:** Qualquer pessoa pode executar qualquer operação, incluindo admin.

**Como resolver:**
1. Implementar middleware de autenticação (JWT ou session-based).
2. Proteger **todos** endpoints de escrita (POST, PUT, DELETE).
3. Implementar autorização por papel (admin vs cliente).
4. Rotas admin devem exigir papel admin.
5. Adicionar decorator ou middleware que verifica token/papel antes de cada handler.

**Antes:**
```python
# SEM PROTEÇÃO
@bp.route('/produtos', methods=['DELETE'])
def deletar_produto(produto_id):
    # qualquer um pode deletar
    ...
```

**Depois:**
```python
# COM PROTEÇÃO
from functools import wraps
from flask import request, jsonify
import jwt

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({"erro": "Token requerido"}), 401
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            request.current_user = payload
        except jwt.InvalidTokenError:
            return jsonify({"erro": "Token inválido"}), 401
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    @auth_required
    def decorated(*args, **kwargs):
        if request.current_user.get('tipo') != 'admin':
            return jsonify({"erro": "Acesso restrito a admins"}), 403
        return f(*args, **kwargs)
    return decorated

# Uso
@bp.route('/produtos/<int:produto_id>', methods=['DELETE'])
@admin_required
def deletar_produto(produto_id):
    ...
```

---

### H-02: Senhas Expostas em Respostas

**Severidade:** HIGH
**Prioridade de resolução:** 2ª — resolver junto com H-01. Senhas em resposta = vazamento por design.

**Sinais de detecção:**
- Campos `password` incluídos em serialização: `to_dict()` que inclui `password`
- Endpoints de listagem de usuários que retornam senhas
- `SELECT *` em tabelas de usuários que incluem campo de senha
- APIs que retornam objetos completos sem filtrar campos sensíveis

**Descrição:** Senhas ou dados sensíveis retornados em endpoints de API.
**Impacto:** Vazamento de senhas para qualquer consumidor da API.

**Como resolver:**
1. Nunca incluir campo de senha na serialização pública.
2. Criar método `_to_public()` ou `to_dict()` que exclui campos sensíveis.
3. Nunca usar `SELECT *` em tabelas com senha — selecionar colunas explicitamente OU filtrar na serialização.
4. Validar com teste que nenhum endpoint retorna campo senha.

**Antes:**
```python
# VULNERÁVEL — SELECT * + serialização sem filtro
def get_all(self):
    cursor = self.db.execute("SELECT * FROM usuarios")
    return [dict(row) for row in cursor.fetchall()]  # inclui senha!

def to_dict(self):
    return {"id": self.id, "nome": self.nome, "senha": self.senha}  # expõe!
```

**Depois:**
```python
# SEGURO — serialização com filtro
@staticmethod
def _to_public(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"]
        # campo "senha" intencionalmente omitido
    }

def get_all(self):
    cursor = self.db.execute("SELECT * FROM usuarios")
    return [self._to_public(row) for row in cursor.fetchall()]
```

---

### H-03: Nenhuma Validação de Entrada

**Severidade:** HIGH
**Prioridade de resolução:** 2ª — resolver junto com H-01. Input não validado = bugs + potencial injection.

**Sinais de detecção:**
- Parâmetros do request usados diretamente: `request.json['name']` sem validação
- Ausência de schema validation
- Tipos não verificados antes de uso
- Ausência de sanitização para dados que vão para SQL ou HTML

**Descrição:** Input do usuário usado sem validação ou sanitização.
**Impacto:** Dados inválidos causam bugs, injection, ou comportamento imprevisível.

**Como resolver:**
1. Validar **antes** de passar ao controller — validação é responsabilidade da rota/controller.
2. Verificar campos obrigatórios, tipos e ranges.
3. Retornar 400 com mensagem clara para input inválido.
4. Para projetos maiores, usar biblioteca de validação (marshmallow, pydantic).

**Antes:**
```python
# SEM VALIDAÇÃO — KeyError vira 500
@bp.route('/produtos', methods=['POST'])
def criar_produto():
    dados = request.get_json()
    controller.criar(dados)  # dados pode ser None, sem campos, tipos errados
```

**Depois:**
```python
# COM VALIDAÇÃO
@bp.route('/produtos', methods=['POST'])
def criar_produto():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "JSON body obrigatório"}), 400

    campos_obrigatorios = ["nome", "preco", "estoque"]
    for campo in campos_obrigatorios:
        if campo not in dados:
            return jsonify({"erro": f"Campo '{campo}' é obrigatório"}), 400

    if not isinstance(dados["preco"], (int, float)) or dados["preco"] < 0:
        return jsonify({"erro": "Preço deve ser número positivo"}), 400

    controller.criar(dados)
```

---

### H-04: Lógica de Negócio nos Controllers/Routes

**Severidade:** HIGH
**Prioridade de resolução:** 3ª — resolver após segurança. Pré-requisito para testabilidade.

**Sinais de detecção:**
- Rotas com lógica de negócio complexa (>10 linhas de lógica além de validação/retorno)
- Queries SQL diretamente em handlers de rota
- Cálculos, transformações e regras de negócio dentro de callbacks de rota
- Controllers que acessam o banco diretamente

**Descrição:** Lógica de negócio pesada presa na camada de roteamento/controller.
**Impacto:** Difícil testar, difícil reutilizar, viola separação de responsabilidades.

**Como resolver:**
1. Rotas devem apenas: receber request → chamar controller → formatar response.
2. Controllers devem: validar input → orquestrar models → aplicar regras de negócio.
3. Models devem: acessar banco de dados (queries).
4. Se controller fica complexo, extrair lógica para service layer.

**Antes:**
```python
# ROTA com lógica de negócio
@bp.route('/pedidos', methods=['POST'])
def criar_pedido():
    dados = request.get_json()
    # 30 linhas de cálculo de total, verificação de estoque, desconto...
    total = 0
    for item in itens:
        produto = db.execute("SELECT * FROM produtos WHERE id = ?", (item["produto_id"],)).fetchone()
        if produto["estoque"] < item["quantidade"]:
            return jsonify({"erro": "Sem estoque"}), 400
        total += produto["preco"] * item["quantidade"]
    # ... mais lógica
```

**Depois:**
```python
# ROTA limpa
@bp.route('/pedidos', methods=['POST'])
def criar_pedido():
    dados = request.get_json()
    resultado = controller.criar(dados)
    return jsonify({"dados": resultado}), 201

# CONTROLLER com regra de negócio
class PedidoController:
    def criar(self, dados):
        self._validar_itens(dados["itens"])
        produtos = self._buscar_produtos(dados["itens"])
        self._verificar_estoque(dados["itens"], produtos)
        total = self._calcular_total(dados["itens"], produtos)
        return self.model.criar(dados["usuario_id"], itens, total)
```

---

## MEDIUM

### M-01: Queries N+1

**Severidade:** MEDIUM
**Prioridade de resolução:** 3ª — resolver quando performance for prioridade. Impacto escala com volume.

**Sinais de detecção:**
- Queries SQL dentro de loops: `for item in items: db.execute("SELECT ...")`
- Múltiplas queries relacionadas executadas sequencialmente quando poderiam ser uma
- Acesso lazy a relacionamentos dentro de loops

**Descrição:** Padrão N+1 onde 1 query busca N registros e depois N queries buscam dados relacionados.
**Impacto:** Performance degrada linearmente com o volume de dados.

**Como resolver:**
1. Identificar loops com queries dentro.
2. Substituir por JOINs ou queries batch (WHERE id IN (...)).
3. Buscar todos os dados relacionados em uma query, depois mapear em memória.

**Antes:**
```python
# N+1 — 1 query + N queries
pedidos = db.execute("SELECT * FROM pedidos").fetchall()
for pedido in pedidos:
    itens = db.execute("SELECT * FROM itens_pedido WHERE pedido_id = ?", (pedido["id"],)).fetchall()
    pedido["itens"] = itens
```

**Depois:**
```python
# 2 queries batch (ou 1 JOIN)
pedidos = db.execute("SELECT * FROM pedidos").fetchall()
ids = [p["id"] for p in pedidos]
placeholders = ",".join("?" * len(ids))
itens = db.execute(
    f"SELECT * FROM itens_pedido WHERE pedido_id IN ({placeholders})", ids
).fetchall()
# mapear em memória
itens_por_pedido = {}
for item in itens:
    itens_por_pedido.setdefault(item["pedido_id"], []).append(item)
for pedido in pedidos:
    pedido["itens"] = itens_por_pedido.get(pedido["id"], [])
```

---

### M-02: Debug Mode em Produção

**Severidade:** MEDIUM
**Prioridade de resolução:** 3ª — resolver junto com configuração de ambiente.

**Sinais de detecção:**
- `debug=True` ou `DEBUG = True` no código
- `host='0.0.0.0'` hardcoded (abre para todas as interfaces)
- Stack traces detalhados expostos ao usuário
- Modo verboso de logging ativado em produção

**Descrição:** Modo debug ativado em ambiente de produção.
**Impacto:** Expõe stack traces, abre servidor para todas as interfaces, facilita ataques.

**Como resolver:**
1. DEBUG deve vir de variável de ambiente, nunca hardcoded.
2. Usar parser robusto para booleanos de env var.
3. Em produção, usar WSGI server (gunicorn, waitress), nunca `app.run()`.
4. Nunca fazer bind em `0.0.0.0` em produção.

**Antes:**
```python
# FRÁGIL
DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'  # '1' ou 'yes' não funcionam
app.run(debug=True, host='0.0.0.0')
```

**Depois:**
```python
# ROBUSTO
def _parse_bool(value):
    return value.lower() in ('true', '1', 'yes')

DEBUG = _parse_bool(os.environ.get('FLASK_DEBUG', 'false'))

# Em produção: gunicorn -w 4 -b 127.0.0.1:5000 app:application
```

---

### M-03: Código Duplicado

**Severidade:** MEDIUM
**Prioridade de resolução:** 4ª — resolver quando tocar nas áreas afetadas (boy scout rule).

**Sinais de detecção:**
- Blocos de código idênticos ou quase idênticos em múltiplos locais
- Lógica de cálculo repetida em diferentes rotas
- Queries SQL similares copiadas entre funções
- Serialização manual repetida

**Descrição:** Lógica duplicada que deveria estar em um único lugar.
**Impacto:** Mudanças precisam ser feitas em múltiplos locais, risco de inconsistência.

**Como resolver:**
1. Extrair lógica repetida para função/método compartilhado.
2. Para padrões de resposta da API, criar helper ou base response class.
3. Para queries repetidas, adicionar método no model correspondente.
4. Para serialização, usar `_serialize()` ou `_to_public()` consistente.

**Antes:**
```python
# Repetido em 5 rotas diferentes
try:
    resultado = controller.algo()
    return jsonify({"dados": resultado, "sucesso": True}), 200
except ValueError as e:
    return jsonify({"erro": str(e)}), 400
```

**Depois:**
```python
# Helper centralizado
def ok(data, status=200, message=None):
    response = {"dados": data, "sucesso": True}
    if message:
        response["mensagem"] = message
    return jsonify(response), status

def erro(message, status=400):
    return jsonify({"erro": message, "sucesso": False}), status

# Uso nas rotas
@bp.route('/produtos', methods=['GET'])
def listar():
    return ok(controller.listar_todos())
```

---

### M-04: Falta de Tratamento de Erros

**Severidade:** MEDIUM
**Prioridade de resolução:** 3ª — resolver junto com error handler centralizado.

**Sinais de detecção:**
- Ausência de try/except em operações de banco
- Erros retornados como strings genéricas sem status code adequado
- Nenhum middleware global de error handling
- `except:` vazio que engole erros silenciosamente
- Erros de DB propagados diretamente para o cliente

**Descrição:** Erros não tratados ou tratados de forma inadequada.
**Impacto:** Experiência ruim para o consumidor da API, difícil debugging, possível vazamento de informações.

**Como resolver:**
1. Registrar error handlers globais no Flask (`@app.errorhandler`).
2. Criar classes de exceção customizadas para erros de negócio (ex: `ValidationError`, `NotFoundError`).
3. Nunca usar `except:` vazio — sempre logar o erro.
4. Em produção, nunca expor stack trace ou detalhes internos.

**Antes:**
```python
# SEM tratamento — erro do SQLite vira 500 genérico
@app.route('/produtos/<int:id>')
def get_produto(id):
    produto = db.execute("SELECT * FROM produtos WHERE id = ?", (id,)).fetchone()
    return jsonify(dict(produto))  # se produto é None → TypeError → 500 confuso
```

**Depois:**
```python
# COM tratamento centralizado
# Exceções customizadas
class NotFoundError(Exception): pass
class ValidationError(Exception): pass

# Error handlers globais
def register_error_handlers(app):
    @app.errorhandler(NotFoundError)
    def handle_not_found(e):
        return jsonify({"erro": str(e), "sucesso": False}), 404

    @app.errorhandler(ValidationError)
    def handle_validation(e):
        return jsonify({"erro": str(e), "sucesso": False}), 400

    @app.errorhandler(Exception)
    def handle_generic(e):
        logger.error("Unhandled: %s", e, exc_info=True)
        return jsonify({"erro": "Internal server error"}), 500

# Uso no controller
def buscar_por_id(self, produto_id):
    produto = self.model.get_by_id(produto_id)
    if not produto:
        raise NotFoundError(f"Produto {produto_id} não encontrado")
    return produto
```

---

## LOW

### L-01: Magic Numbers

**Severidade:** LOW
**Prioridade de resolução:** 5ª — resolver por conveniência de leitura. Sem impacto funcional.

**Sinais de detecção:**
- Números literais sem contexto: `if status == 3`, `limit = 50`
- Valores hardcoded que deveriam ser constantes nomeadas
- Códigos de status HTTP como números: `return '', 201` sem comentário

**Descrição:** Valores numéricos literais sem nome explicativo.
**Impacto:** Código difícil de entender e manter.

**Como resolver:**
1. Extrair valores literais para constantes nomeadas.
2. Nomes devem expressar intenção/Significado do valor.
3. Agrupar constantes relacionadas juntas (ex: no config ou topo do controller).

**Antes:**
```python
DESCONTO_TIERS = [
    (10000, 0.10),
    (5000, 0.05),
    (1000, 0.02),
]
```

**Depois:**
```python
# Constantes com significado
LIMITE_DESCONTO_PLATINA = 10_000
LIMITE_DESCONTO_OURO = 5_000
LIMITE_DESCONTO_PRATA = 1_000

TAXA_DESCONTO_PLATINA = 0.10  # 10%
TAXA_DESCONTO_OURO = 0.05     # 5%
TAXA_DESCONTO_PRATA = 0.02    # 2%

DESCONTO_TIERS = [
    (LIMITE_DESCONTO_PLATINA, TAXA_DESCONTO_PLATINA),
    (LIMITE_DESCONTO_OURO, TAXA_DESCONTO_OURO),
    (LIMITE_DESCONTO_PRATA, TAXA_DESCONTO_PRATA),
]
```

---

### L-02: Nomenclatura Ruim

**Severidade:** LOW
**Prioridade de resolução:** 5ª — resolver ao tocar no código. Sem impacto funcional.

**Sinais de detecção:**
- Variáveis com nomes obscuros: `x`, `y`, `aux`, `tmp`, `data2`
- Funções com nomes genéricos: `process()`, `handle()`, `do_stuff()`
- Abreviações inconsistentes: `usr`, `prod`, `qty`
- Nomes em idiomas misturados

**Descrição:** Nomes de variáveis, funções ou classes que não expressam intenção.
**Impacto:** Reduz legibilidade e aumenta curva de aprendizado.

**Como resolver:**
1. Renomear para nomes que expressem **intenção** e **conteúdo**.
2. Manter idioma consistente (tudo em português ou tudo em inglês).
3. Evitar abreviações não óbvias.
4. Se uma variável precisa de comentário para explicar, o nome provavelmente está ruim.

**Antes:**
```python
def proc(d):
    x = d.get('n')
    aux = calc(x)
    return aux
```

**Depois:**
```python
def calcular_desconto_total(dados_pedido):
    nome_produto = dados_pedido.get('nome')
    desconto = calcular_desconto_por_produto(nome_produto)
    return desconto
```

---

### L-03: API Deprecated

**Severidade:** LOW
**Prioridade de resolução:** 5ª — resolver em passos de modernização. Sem urgência.

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

**Como resolver:**
1. Consultar documentação atual do framework para APIs modernas equivalentes.
2. Atualizar incrementalmente — não é urgente, mas evite acumular dívida técnica.

**Antes (Flask):**
```python
from flask import jsonify
return jsonify({"dados": resultado}), 200
```

**Depois (Flask 2.2+):**
```python
return {"dados": resultado}, 200  # Flask auto-serializa dicts
```

**Antes (Express):**
```javascript
const bodyParser = require('body-parser');
app.use(bodyParser.json());
```

**Depois (Express 4.16+):**
```javascript
app.use(express.json());
```

---

### L-04: Logs Sensíveis no Console

**Severidade:** LOW
**Prioridade de resolução:** 5ª — resolver ao revisar módulos de logging. Risco baixo se logs não são expostos externamente.

**Sinais de detecção:**
- `console.log()` com dados sensíveis: senhas, tokens, cartões
- `print()` de dados sensíveis em Python
- Logs de requisições que incluem headers de autorização
- Chaves de API ou gateway impressas em log

**Descrição:** Informações sensíveis registradas em logs de console.
**Impacto:** Dados sensíveis podem ser acessados por quem tem acesso aos logs.

**Como resolver:**
1. Nunca logar senhas, tokens ou dados pessoais.
2. Se precisar logar para debug, logar apenas identificadores (id, email mascarado).
3. Usar biblioteca de logging com níveis (DEBUG em dev, WARNING+ em produção).
4. Filtrar campos sensíveis antes de logar qualquer objeto.

**Antes:**
```python
print(f"Login: email={email}, senha={senha}")  # VAZAMENTO
logger.info(f"Request body: {request.json}")    # pode conter senha
```

**Depois:**
```python
logger.info(f"Login attempt: email={email}")
logger.debug(f"User created: id={user_id}")  # apenas identificadores
```
