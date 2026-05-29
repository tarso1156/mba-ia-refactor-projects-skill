# Análise de Projeto — Heurísticas de Detecção

## 1. Detecção de Linguagem

| Sinal | Linguagem |
|-------|-----------|
| `requirements.txt`, `setup.py`, `pyproject.toml`, arquivos `.py` | Python |
| `package.json`, `package-lock.json`, arquivos `.js`/`.ts` | Node.js/TypeScript |
| `Gemfile`, arquivos `.rb` | Ruby |
| `pom.xml`, `build.gradle`, arquivos `.java` | Java |
| `composer.json`, arquivos `.php` | PHP |
| `go.mod`, arquivos `.go` | Go |

### Procedimento

1. Listar arquivos raiz do projeto
2. Verificar existência dos arquivos de configuração acima
3. Contar extensões de arquivo para confirmar
4. Se ambíguo, priorizar pelo arquivo de configuração mais específico

---

## 2. Detecção de Framework

### Python

| Framework | Sinais de Detecção |
|-----------|-------------------|
| Flask | `from flask import`, `Flask(__name__)`, `flask` em requirements.txt |
| Django | `from django`, `DJANGO_SETTINGS_MODULE`, `django` em requirements.txt |
| FastAPI | `from fastapi import`, `FastAPI()`, `fastapi` em requirements.txt |

### Node.js

| Framework | Sinais de Detecção |
|-----------|-------------------|
| Express | `require('express')`, `express()`, `express` em package.json |
| Koa | `require('koa')`, `new Koa()`, `koa` em package.json |
| NestJS | `@nestjs/core`, `nest` em package.json |
| Hapi | `require('@hapi/hapi')`, `hapi` em package.json |

### Versão

- Python: verificar `requirements.txt` para versão do framework (ex: `flask==3.1.1`)
- Node.js: verificar `package.json` → `dependencies` para versão

---

## 3. Detecção de Banco de Dados

| Sinal | Banco |
|-------|-------|
| `import sqlite3`, `.db`, `.sqlite` | SQLite |
| `import psycopg2`, `postgresql://` | PostgreSQL |
| `import mysql`, `mysql://` | MySQL |
| `import pymongo`, `mongodb://` | MongoDB |
| `require('sequelize')`, `Sequelize` | Sequelize (ORM) |
| `require('prisma')`, `schema.prisma` | Prisma (ORM) |
| `import sqlalchemy`, `SQLAlchemy` | SQLAlchemy (ORM) |

### Detecção de Tabelas

- SQLite: `SELECT name FROM sqlite_master WHERE type='table'`
- Verificar strings SQL no código: `CREATE TABLE`, `INSERT INTO`, `SELECT.*FROM`
- Verificar nomes de models/coleções para inferir entidades

---

## 4. Mapeamento de Arquitetura

### Classificação de Estrutura

| Tipo | Sinais |
|------|--------|
| **Monolítica (flat)** | Todos os arquivos na raiz, sem subdiretórios de código |
| **Parcialmente organizada** | Alguns diretórios (models/, routes/) mas sem separação clara |
| **MVC** | Diretórios models/, views/ (ou routes/), controllers/ separados |
| **Em camadas** | Diretório src/ com subdiretórios por camada |

### Procedimento

1. Listar árvore de diretórios (excluindo node_modules, __pycache__, .git, venv)
2. Identificar subdiretórios de código
3. Verificar separação de responsabilidades entre arquivos
4. Classificar a arquitetura atual
5. Identificar o entry point principal (app.py, server.js, index.js, main.py)

---

## 5. Identificação de Domínio

Analise os seguintes sinais para inferir o domínio da aplicação:

- **Nomes de rotas/endpoints:** `/products`, `/users`, `/orders` → E-commerce
- **Nomes de models/tabelas:** `Task`, `User`, `Category` → Task Manager
- **Nomes de funções:** `checkout`, `payment`, `enrollment` → LMS/Pagamento
- **Comentários e docstrings**
- **Nome do projeto no package.json ou README**

Formato de saída: `"<domínio> API (<entidades principais>)"`

Exemplo: `"E-commerce API (produtos, pedidos, usuários)"`

---

## 6. Contagem de Arquivos Fonte

### Incluir

- `.py`, `.js`, `.ts`, `.rb`, `.java`, `.php`, `.go`
- Arquivos de configuração relevantes (requirements.txt, package.json)

### Excluir

- `node_modules/`, `__pycache__/`, `.git/`, `venv/`, `.env/`
- Lock files (package-lock.json, yarn.lock)
- Arquivos binários
- Diretórios de build/dist

### Procedimento

1. `find . -type f` com filtros de extensão
2. Excluir paths de dependências e cache
3. Contar total de arquivos analisados
