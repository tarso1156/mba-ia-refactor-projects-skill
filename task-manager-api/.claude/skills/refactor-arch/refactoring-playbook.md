# Playbook de Refatoração

Padrões concretos de transformação para cada anti-pattern. Cada padrão mostra código antes e depois.

---

## Padrão 1: Parameterized Queries (C-01 SQL Injection)

### Antes

```python
# Python — VULNERÁVEL
def get_usuario(email, senha):
    query = f"SELECT * FROM usuarios WHERE email = '{email}' AND senha = '{senha}'"
    cursor = db.execute(query)
    return cursor.fetchone()
```

```javascript
// Node.js — VULNERÁVEL
async getUser(email, password) {
  const query = `SELECT * FROM users WHERE email = '${email}' AND password = '${password}'`;
  return this.db.get(query);
}
```

### Depois

```python
# Python — SEGURO
def get_usuario(self, email, senha):
    query = "SELECT * FROM usuarios WHERE email = ? AND senha = ?"
    cursor = self.db.execute(query, (email, senha))
    return cursor.fetchone()
```

```javascript
// Node.js — SEGURO
async getUser(email, password) {
  const query = 'SELECT * FROM users WHERE email = ? AND password = ?';
  return this.db.get(query, [email, password]);
}
```

---

## Padrão 2: Configuração por Variáveis de Ambiente (C-02 Credenciais Hardcoded)

### Antes

```python
# Python — CREDENCIAIS EXPOSTAS
app = Flask(__name__)
app.config['SECRET_KEY'] = 'minha-chave-super-secreta-123'
DATABASE = 'ecommerce.db'
SMTP_USER = 'admin@gmail.com'
SMTP_PASS = 'senha123'
```

```javascript
// Node.js — CREDENCIAIS EXPOSTAS
const DB_PASSWORD = 'mypassword123';
const PAYMENT_GATEWAY_KEY = 'sk_live_abc123';
const SMTP_PASS = 'emailpassword';
```

### Depois

```python
# Python — config/settings.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'database.db')
    SMTP_USER = os.environ.get('SMTP_USER')
    SMTP_PASS = os.environ.get('SMTP_PASS')
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'

# app.py
from config.settings import Config
app.config['SECRET_KEY'] = Config.SECRET_KEY
```

```javascript
// Node.js — config/settings.js
module.exports = {
  dbPassword: process.env.DB_PASSWORD,
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY,
  smtpPass: process.env.SMTP_PASS,
  port: process.env.PORT || 3000,
  nodeEnv: process.env.NODE_ENV || 'development'
};
```

---

## Padrão 3: Separação por Domínio (C-03 God Class)

### Antes

```python
# models.py — 350 LINHAS, 4 DOMÍNIOS MISTURADOS
class Database:
    def get_all_produtos(self): ...
    def create_produto(self, ...): ...
    def get_all_usuarios(self): ...
    def create_usuario(self, ...): ...
    def get_all_pedidos(self): ...
    def create_pedido(self, ...): ...
    def login(self, ...): ...
    # + validação + formatação para tudo
```

### Depois

```python
# models/produto_model.py
class ProdutoModel:
    def __init__(self, db):
        self.db = db
    def get_all(self): ...
    def get_by_id(self, id): ...
    def create(self, nome, preco, descricao): ...

# models/usuario_model.py
class UsuarioModel:
    def __init__(self, db):
        self.db = db
    def get_all(self): ...
    def get_by_email(self, email): ...
    def create(self, nome, email, senha): ...

# models/pedido_model.py
class PedidoModel:
    def __init__(self, db):
        self.db = db
    def get_all(self): ...
    def create(self, usuario_id, itens): ...
```

---

## Padrão 4: Hash Seguro de Senhas (C-05 Hash Inseguro)

### Antes

```python
# Python — MD5 SEM SALT (QUEBRADO)
import hashlib
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()
```

```javascript
// Node.js — BASE64 REVERSÍVEL
function hashPassword(password) {
  return Buffer.from(password).toString('base64');
}
```

### Depois

```python
# Python — BCRYPT
import bcrypt

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
```

```javascript
// Node.js — BCRYPT
const bcrypt = require('bcrypt');

async function hashPassword(password) {
  const salt = await bcrypt.genSalt(10);
  return bcrypt.hash(password, salt);
}

async function verifyPassword(password, hashed) {
  return bcrypt.compare(password, hashed);
}
```

---

## Padrão 5: Autenticação com JWT/Middleware (H-01 Zero Auth)

### Antes

```python
# Python — SEM AUTH
@app.route('/admin/users', methods=['DELETE'])
def delete_user(id):
    db.execute("DELETE FROM usuarios WHERE id = ?", (id,))
    return jsonify({'message': 'Deleted'})

@app.route('/login', methods=['POST'])
def login():
    user = db.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
    return jsonify({'token': f'fake-jwt-token-{user["id"]}'})
```

```javascript
// Node.js — SEM AUTH
app.delete('/api/admin/users/:id', (req, res) => {
  db.run('DELETE FROM users WHERE id = ?', [req.params.id]);
  res.json({ message: 'Deleted' });
});
```

### Depois

```python
# Python — JWT + MIDDLEWARE
import jwt
from functools import wraps
from flask import request, jsonify

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            current_user = UserModel(get_db()).get_by_id(data['user_id'])
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/login', methods=['POST'])
def login():
    user = UserModel(get_db()).get_by_email(request.json['email'])
    if user and verify_password(request.json['password'], user['password']):
        token = jwt.encode(
            {'user_id': user['id'], 'exp': datetime.utcnow() + timedelta(hours=24)},
            Config.SECRET_KEY
        )
        return jsonify({'token': token})
    return jsonify({'error': 'Invalid credentials'}), 401
```

```javascript
// Node.js — JWT + MIDDLEWARE
const jwt = require('jsonwebtoken');

function authMiddleware(req, res, next) {
  const token = (req.headers.authorization || '').replace('Bearer ', '');
  if (!token) return res.status(401).json({ error: 'Token missing' });
  try {
    req.user = jwt.verify(token, config.jwtSecret);
    next();
  } catch {
    res.status(401).json({ error: 'Invalid token' });
  }
}

router.delete('/api/admin/users/:id', authMiddleware, async (req, res) => {
  await userModel.deleteById(req.params.id);
  res.json({ message: 'Deleted' });
});
```

---

## Padrão 6: Serialização Segura (H-02 Senhas Expostas)

### Antes

```python
# Python — SENHA NO JSON
class User:
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'password': self.password  # VAZAMENTO!
        }
```

```javascript
// Node.js — SENHA NO JSON
class User {
  toJSON() {
    return {
      id: this.id,
      name: this.name,
      email: this.email,
      password: this.password  // VAZAMENTO!
    };
  }
}
```

### Depois

```python
# Python — SENHA REMOVIDA
class UserModel:
    def to_public_dict(self, user_row):
        """Serialização pública — sem campos sensíveis"""
        return {
            'id': user_row['id'],
            'nome': user_row['nome'],
            'email': user_row['email'],
        }
```

```javascript
// Node.js — SENHA REMOVIDA
class UserModel {
  toPublicJSON(userRow) {
    const { password, ...publicData } = userRow;
    return publicData;
  }
}
```

---

## Padrão 7: Queries Batch / JOINs (M-01 N+1)

### Antes

```python
# Python — N+1 QUERIES
def get_pedidos():
    pedidos = db.execute("SELECT * FROM pedidos").fetchall()
    resultado = []
    for pedido in pedidos:
        itens = db.execute("SELECT * FROM itens_pedido WHERE pedido_id = ?",
                          (pedido['id'],)).fetchall()
        for item in itens:
            produto = db.execute("SELECT * FROM produtos WHERE id = ?",
                                (item['produto_id'],)).fetchone()
            item['produto'] = dict(produto)
        pedido['itens'] = [dict(i) for i in itens]
        resultado.append(dict(pedido))
    return resultado
```

### Depois

```python
# Python — JOIN ÚNICO
def get_pedidos_com_itens(self):
    query = """
        SELECT p.*, ip.id as item_id, ip.quantidade, ip.preco_unitario,
               pr.id as produto_id, pr.nome as produto_nome, pr.descricao
        FROM pedidos p
        LEFT JOIN itens_pedido ip ON p.id = ip.pedido_id
        LEFT JOIN produtos pr ON ip.produto_id = pr.id
        ORDER BY p.id
    """
    rows = self.db.execute(query).fetchall()
    # Agrupar por pedido
    pedidos = {}
    for row in rows:
        pid = row['id']
        if pid not in pedidos:
            pedidos[pid] = dict(row)
            pedidos[pid]['itens'] = []
        if row['item_id']:
            pedidos[pid]['itens'].append({
                'id': row['item_id'],
                'quantidade': row['quantidade'],
                'preco_unitario': row['preco_unitario'],
                'produto': {
                    'id': row['produto_id'],
                    'nome': row['produto_nome'],
                    'descricao': row['descricao']
                }
            })
    return list(pedidos.values())
```

---

## Padrão 8: Error Handling Centralizado (M-04)

### Antes

```python
# Python — ERROS NÃO TRATADOS
@app.route('/produtos/<int:id>')
def get_produto(id):
    produto = db.execute("SELECT * FROM produtos WHERE id = ?", (id,)).fetchone()
    if not produto:
        return "Produto não encontrado"  # Sem status code, sem JSON
    return jsonify(dict(produto))

@app.route('/produtos', methods=['POST'])
def criar_produto():
    nome = request.json['nome']  # KeyError se nome ausente, crash
    db.execute("INSERT INTO produtos (nome) VALUES (?)", (nome,))
    return "OK"
```

```javascript
// Node.js — ERROS NÃO TRATADOS
app.get('/products/:id', (req, res) => {
  const product = db.get('SELECT * FROM products WHERE id = ?', [req.params.id]);
  if (!product) res.send('Not found'); // Sem status code
  res.json(product);
});
```

### Depois

```python
# Python — ERROR HANDLER CENTRALIZADO
# middlewares/error_handler.py
from flask import jsonify
import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'error': 'Bad request', 'message': str(e)}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"Internal error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

# routes/produto_routes.py
@produto_bp.route('/produtos/<int:id>')
def get_produto(id):
    controller = ProdutoController()
    produto = controller.buscar_por_id(id)
    if not produto:
        abort(404)
    return jsonify(produto)

@produto_bp.route('/produtos', methods=['POST'])
def criar_produto():
    data = request.get_json()
    if not data or 'nome' not in data:
        return jsonify({'error': 'Nome é obrigatório'}), 400
    controller = ProdutoController()
    produto = controller.criar(data)
    return jsonify(produto), 201
```

```javascript
// Node.js — ERROR HANDLER CENTRALIZADO
// middlewares/errorHandler.js
function errorHandler(err, req, res, next) {
  console.error(err.stack);
  const status = err.status || 500;
  const message = status === 500 ? 'Internal server error' : err.message;
  res.status(status).json({ error: message });
}

function asyncHandler(fn) {
  return (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);
}

module.exports = { errorHandler, asyncHandler };

// app.js
const { errorHandler } = require('./middlewares/errorHandler');
app.use(errorHandler);
```

---

## Padrão Adicional: Remoção de Endpoints Perigosos (C-04 Execução Arbitrária)

### Antes

```python
# Python — EXECUÇÃO ARBITRÁRIA
@app.route('/admin/query', methods=['POST'])
def execute_query():
    query = request.json['query']
    result = db.execute(query).fetchall()
    return jsonify([dict(row) for row in result])
```

### Depois

```python
# REMOVER endpoint completamente.
# Se necessário, proteger com auth admin + whitelist:
@app.route('/admin/query', methods=['POST'])
@token_required
@admin_required
def execute_query(current_user):
    # Apenas SELECT permitido
    query = request.json.get('query', '').strip()
    if not query.upper().startswith('SELECT'):
        return jsonify({'error': 'Only SELECT queries allowed'}), 403
    # Whitelist de tabelas permitidas
    allowed_tables = ['produtos', 'pedidos']
    # ... validação adicional ...
    result = db.execute(query).fetchall()
    return jsonify([dict(row) for row in result])
```
