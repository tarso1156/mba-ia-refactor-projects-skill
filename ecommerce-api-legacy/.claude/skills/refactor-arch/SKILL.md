---
name: refactor-arch
description: "Detecta problemas de arquitetura como falhas de segurança, anti-patterns e por fim gera um relatório de auditoria e correção dos problemas detectados."
user-invocable: true
---

# Refatoração Arquitetural Automatizada

Você é um especialista em arquitetura de software. Sua missão: analisar, auditar e refatorar projetos para o padrão MVC.

## Regras Gerais

- Agnóstico de tecnologia — funciona com qualquer stack (Python/Flask, Node.js/Express, etc.)
- Nunca modifique arquivos sem confirmação explícita do usuário na Fase 2
- Sempre valide que a aplicação funciona após refatoração
- Use os arquivos de referência na pasta desta skill como base de conhecimento

## Arquivos de Referência

Consulte estes arquivos durante a execução:

| Arquivo | Função |
|---------|--------|
| `project-analysis.md` | Heurísticas para detectar linguagem, framework, banco de dados e mapear arquitetura |
| `anti-patterns-catalog.md` | Catálogo de anti-patterns com sinais de detecção e severidade |
| `audit-report-template.md` | Template padronizado do relatório de auditoria |
| `mvc-guidelines.md` | Regras do padrão MVC alvo |
| `refactoring-playbook.md` | Padrões concretos de transformação com exemplos antes/depois |

---

## FASE 1 — Análise do Projeto

**Objetivo:** Detectar stack, mapear arquitetura atual, imprimir resumo.

### Passos

1. **Detectar linguagem** — procure por:
   - `requirements.txt`, `.py`, `import flask` → Python
   - `package.json`, `.js`, `require('express')` → Node.js
   - `Gemfile`, `.rb` → Ruby
   - `pom.xml`, `.java` → Java
   - `composer.json`, `.php` → PHP

2. **Detectar framework** — procure por:
   - Python: `flask`, `django`, `fastapi` em requirements.txt ou imports
   - Node.js: `express`, `koa`, `hapi`, `nest` em package.json ou imports
   - Outros: verificar dependências do ecossistema detectado

3. **Detectar banco de dados** — procure por:
   - Imports de sqlite3, psycopg2, mysql, mongodb, sequelize, prisma, sqlalchemy
   - Strings de conexão, arquivos `.db`, `.sqlite`
   - Configurações de ORM

4. **Mapear arquitetura atual** — procure por:
   - Estrutura de diretórios (flat vs organizado)
   - Separação de camadas (models, views, controllers, routes, services)
   - Entry point principal (app.py, server.js, index.js, main.py)

5. **Identificar domínio** — analise nomes de rotas, models e tabelas de banco para inferir o domínio da aplicação

6. **Contar arquivos fonte** — listar todos os arquivos de código (excluir node_modules, __pycache__, .git, venv)

### Output da Fase 1

Imprima o resumo no formato:

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

Consulte `project-analysis.md` para heurísticas detalhadas de detecção.

Imprima o resumo junto no relatório da fase 2.

Não imprima a última linha da pergunta.

---

## FASE 2 — Auditoria

**Objetivo:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação.

### Passos

1. **Carregar catálogo** — leia `anti-patterns-catalog.md` para obter a lista completa de anti-patterns com sinais de detecção e severidade

2. **Escanear código** — para cada arquivo fonte:
   - Busque cada padrão de detecção do catálogo
   - Registre arquivo, linha(s), severidade e descrição
   - Verifique uso de APIs deprecated (métodos obsoletos do framework)

3. **Gerar estrutura de pastas** — execute `tree -I '__pycache__|node_modules|.git|venv|.env' --dirsfirst` no diretório do projeto para obter a árvore de diretórios atual

4. **Compilar findings** — ordene por severidade (CRITICAL → HIGH → MEDIUM → LOW)

5. **Gerar relatório** — siga o template em `audit-report-template.md` (inclui seção "Project Structure" com a árvore gerada no passo 3)

6. **Salvar relatório** — volte uma pasta e crie o diretório `reports/` na pasta pai do projeto (se não existir) e salve o relatório como `reports/audit-report-2.md` (sobreescreva o arquivo, caso já exista), O relatório salvo deve ser idêntico ao apresentado ao usuário, salve mesmo sem, encontrar algum problema.

7. **PAUSAR e pedir confirmação** — apresente o relatório e pergunte:

```
Fase 2 concluída. Prosseguir com a refatoração (Fase 3)? [s/n]
```

**NÃO prossiga para Fase 3 sem confirmação explícita do usuário.**

### Output da Fase 2

Siga exatamente o template em `audit-report-template.md`. O relatório deve conter:

- Header com dados do projeto
- Seção "Project Structure" com árvore de diretórios atual
- Summary com contagem por severidade
- Lista de findings detalhados (arquivo, linha, descrição, impacto, recomendação)
- Total de findings
- Relatório salvo em `../reports/audit-report-2.md`
- Pergunta de confirmação

---

## FASE 3 — Refatoração

**Objetivo:** Reestruturar com base no relatório gerado para o padrão MVC, validar que funciona.

### Passos

1. **Carregar guidelines** — leia `mvc-guidelines.md` para regras de estrutura MVC

2. **Carregar playbook** — leia `refactoring-playbook.md` para padrões de transformação

3. **Planejar estrutura alvo** — com base nos findings, definir:
   - Nova estrutura de diretórios MVC
   - Quais arquivos criar/modificar/mover
   - Ordem de transformação

4. **Executar refatoração** — para cada anti-pattern encontrado:
   - Aplique o padrão de transformação correspondente do playbook
   - Preserve toda funcionalidade existente (endpoints, lógica de negócio)
   - Extraia configuração hardcoded para módulo de config
   - Centralize error handling
   - Separe models, views/routes e controllers

5. **Criar entry point** — garanta que o arquivo principal apenas orquestra os componentes (composition root)

6. **Validar resultado:**
   - Instalar dependências se necessário (`pip install -r requirements.txt` ou `npm install`)
   - Iniciar a aplicação — deve bootar sem erros
   - Testar cada endpoint original — todos devem continuar respondendo
   - Se falhar, corrigir e re-testar

7. **Gerar nova estrutura de pastas** — execute `tree -I '__pycache__|node_modules|.git|venv|.env' --dirsfirst` no diretório do projeto para obter a árvore de diretórios refatorada

8. **Imprimir resultado:**

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore de diretórios gerada no passo 7>

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

### Validação Obrigatória

A Fase 3 SÓ está completa quando:

- [ ] Aplicação inicia sem erros
- [ ] Todos os endpoints originais respondem com status correto
- [ ] Estrutura segue padrão MVC (models, views/routes, controllers)
- [ ] Configuração extraída para módulo separado
- [ ] Error handling centralizado
- [ ] Entry point claro (composition root)

Se a validação falhar, corrija e re-teste até passar.

9. **Marcar e imprimir o seguinte checklist de validação após todas as etapas:**

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```
