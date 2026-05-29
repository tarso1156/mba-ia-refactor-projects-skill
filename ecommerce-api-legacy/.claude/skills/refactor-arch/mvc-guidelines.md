# Guidelines de Arquitetura MVC

## Princípios Fundamentais

O padrão MVC (Model-View-Controller) separa a aplicação em três camadas com responsabilidades distintas.

---

## Camadas e Responsabilidades

### Model

**Responsabilidade:** Dados e regras de negócio do domínio.

- Define a estrutura dos dados (schemas, tabelas, campos)
- Encapsula lógica de acesso a dados (CRUD, queries)
- Contém validações de domínio
- Não conhece HTTP, rotas, ou controllers
- Não contém lógica de apresentação

**Organização:**
- Um arquivo por entidade/domínio: `produto_model.py`, `user_model.js`
- Pasta dedicada: `models/` ou `src/models/`

**Exemplo Python:**
```python
# models/produto_model.py
class ProdutoModel:
    def __init__(self, db):
        self.db = db

    def get_all(self):
        return self.db.execute("SELECT * FROM produtos").fetchall()

    def get_by_id(self, produto_id):
        return self.db.execute(
            "SELECT * FROM produtos WHERE id = ?", (produto_id,)
        ).fetchone()

    def create(self, nome, preco, descricao):
        cursor = self.db.execute(
            "INSERT INTO produtos (nome, preco, descricao) VALUES (?, ?, ?)",
            (nome, preco, descricao)
        )
        self.db.commit()
        return cursor.lastrowid
```

**Exemplo Node.js:**
```javascript
// models/productModel.js
class ProductModel {
  constructor(db) {
    this.db = db;
  }

  async getAll() {
    return this.db.all('SELECT * FROM products');
  }

  async getById(id) {
    return this.db.get('SELECT * FROM products WHERE id = ?', [id]);
  }

  async create({ name, price, description }) {
    const result = await this.db.run(
      'INSERT INTO products (name, price, description) VALUES (?, ?, ?)',
      [name, price, description]
    );
    return result.lastID;
  }
}
```

---

### View / Routes

**Responsabilidade:** Interface de comunicação (API routes e serialização).

- Define endpoints HTTP (rotas)
- Recebe requests e retorna responses
- Faz validação de input da requisição (formato, tipos)
- Delega lógica de negócio para o Controller
- Formata resposta (JSON, status codes)

**Organização:**
- Um arquivo por domínio ou grupo de rotas: `produto_routes.py`, `productRoutes.js`
- Pasta dedicada: `routes/` ou `src/routes/`

**Exemplo Python:**
```python
# routes/produto_routes.py
from flask import Blueprint, request, jsonify
from controllers.produto_controller import ProdutoController

produto_bp = Blueprint('produtos', __name__)

@produto_bp.route('/produtos', methods=['GET'])
def listar_produtos():
    controller = ProdutoController()
    produtos = controller.listar_todos()
    return jsonify(produtos)

@produto_bp.route('/produtos', methods=['POST'])
def criar_produto():
    data = request.get_json()
    if not data or 'nome' not in data:
        return jsonify({'error': 'Nome é obrigatório'}), 400
    controller = ProdutoController()
    produto = controller.criar(data)
    return jsonify(produto), 201
```

**Exemplo Node.js:**
```javascript
// routes/productRoutes.js
const express = require('express');
const router = express.Router();
const productController = require('../controllers/productController');

router.get('/products', async (req, res, next) => {
  try {
    const products = await productController.listAll();
    res.json(products);
  } catch (err) {
    next(err);
  }
});

router.post('/products', async (req, res, next) => {
  try {
    const { name, price } = req.body;
    if (!name || price == null) {
      return res.status(400).json({ error: 'Name and price are required' });
    }
    const product = await productController.create(req.body);
    res.status(201).json(product);
  } catch (err) {
    next(err);
  }
});
```

---

### Controller

**Responsabilidade:** Orquestrar o fluxo entre Views e Models.

- Coordena chamadas entre Models e Views
- Contém lógica de negócio que envolve múltiplos models
- Toma decisões de fluxo (que model chamar, que resposta dar)
- Não acessa o banco diretamente — usa Models
- Não conhece detalhes HTTP — recebe dados e retorna resultados

**Organização:**
- Um arquivo por domínio: `produto_controller.py`, `productController.js`
- Pasta dedicada: `controllers/` ou `src/controllers/`

**Exemplo Python:**
```python
# controllers/produto_controller.py
from models.produto_model import ProdutoModel

class ProdutoController:
    def __init__(self):
        from database import get_db
        self.model = ProdutoModel(get_db())

    def listar_todos(self):
        rows = self.model.get_all()
        return [dict(row) for row in rows]

    def criar(self, data):
        produto_id = self.model.create(
            nome=data['nome'],
            preco=data['preco'],
            descricao=data.get('descricao', '')
        )
        return {'id': produto_id, **data}
```

**Exemplo Node.js:**
```javascript
// controllers/productController.js
const ProductModel = require('../models/productModel');

class ProductController {
  constructor() {
    const { getDb } = require('../database');
    this.model = new ProductModel(getDb());
  }

  async listAll() {
    const rows = await this.model.getAll();
    return rows;
  }

  async create(data) {
    const id = await this.model.create(data);
    return { id, ...data };
  }
}
```

---

## Camadas Adicionais

### Config

**Responsabilidade:** Configuração centralizada.

- Variáveis de ambiente
- Strings de conexão
- Secret keys
- Settings por ambiente (dev, prod, test)

```python
# config/settings.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-prod')
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'database.db')
    DEBUG = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
```

### Middleware

**Responsabilidade:** Cross-cutting concerns.

- Error handling centralizado
- Autenticação/autorização
- CORS
- Logging
- Rate limiting

```python
# middlewares/error_handler.py
from flask import jsonify

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'error': 'Internal server error'}), 500

    @app.errorhandler(Exception)
    def handle_exception(e):
        return jsonify({'error': str(e)}), 500
```

---

## Estrutura de Diretórios Alvo

### Python/Flask

```
src/
├── config/
│   └── settings.py
├── models/
│   ├── __init__.py
│   ├── produto_model.py
│   ├── usuario_model.py
│   └── pedido_model.py
├── controllers/
│   ├── __init__.py
│   ├── produto_controller.py
│   ├── usuario_controller.py
│   └── pedido_controller.py
├── routes/
│   ├── __init__.py
│   ├── produto_routes.py
│   ├── usuario_routes.py
│   └── pedido_routes.py
├── middlewares/
│   ├── __init__.py
│   └── error_handler.py
├── database.py
└── app.py              # Composition root
```

### Node.js/Express

```
src/
├── config/
│   └── settings.js
├── models/
│   ├── productModel.js
│   ├── userModel.js
│   └── orderModel.js
├── controllers/
│   ├── productController.js
│   ├── userController.js
│   └── orderController.js
├── routes/
│   ├── productRoutes.js
│   ├── userRoutes.js
│   └── orderRoutes.js
├── middlewares/
│   └── errorHandler.js
├── database.js
└── app.js              # Composition root
```

---

## Regras de Ouro

1. **Model nunca importa Controller ou Route**
2. **Controller importa Model, nunca Route**
3. **Route importa Controller, nunca Model diretamente**
4. **Config é importado por quem precisa, nunca importa código de negócio**
5. **Entry point (app.py/server.js) apenas orquestra: registra blueprints/routes, middleware, inicializa app**
6. **Toda configuração sensível vem de variáveis de ambiente**
7. **Todo error handling passa por middleware centralizado**
8. **Cada arquivo tem uma responsabilidade clara**
