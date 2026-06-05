================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      JavaScript (Node.js)
Framework:     Express ^4.18.2
Dependencies:  express ^4.18.2, sqlite3 ^5.1.6
Domain:        E-commerce LMS — courses, enrollments, payments, checkout
Architecture:  Flat monolith. God Class (AppManager) concentra DB init, rotas, lógica de negócio e queries. Utils com config hardcoded e crypto inseguro. Diretórios MVC vazios sugerem tentativa abortada de refatoração.
Source files:  3 files analyzed (~180 lines)
DB tables:     users, courses, enrollments, payments, audit_logs
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript + Express
Files:   3 analyzed | ~180 lines of code

## Project Structure
.
├── src
│   ├── config        (empty)
│   ├── controllers   (empty)
│   ├── database      (empty)
│   ├── middlewares   (empty)
│   ├── models        (empty)
│   ├── routes        (empty)
│   ├── services      (empty)
│   ├── app.js
│   ├── AppManager.js
│   └── utils.js
├── api.http
├── package.json
├── package-lock.json
└── README.md

8 directories, 7 files

## Summary
CRITICAL: 3 | HIGH: 3 | MEDIUM: 4 | LOW: 4

## Findings

### [CRITICAL] C-02: Credenciais Hardcoded
File: src/utils.js:2-7
Description: Senha de banco, chave de gateway de pagamento e credenciais SMTP hardcoded como string literal no código-fonte. Valores incluem `senha_super_secreta_prod_123`, `pk_live_1234567890abcdef` e email SMTP.
Impact: Qualquer acesso ao repositório expõe credenciais de produção. Vazamento em logs, forks ou deploys sem env vars.
Recommendation: Mover todos os segredos para variáveis de ambiente via `process.env`. Aplicação deve falhar ao iniciar se segredos obrigatórios não estiverem definidos em produção.

### [CRITICAL] C-03: God Class / God Method
File: src/AppManager.js:1-141
Description: Classe AppManager (141 linhas) concentra inicialização do banco, criação de schema, seed de dados, definição de 3 rotas com lógica de negócio complexa, queries SQL inline, e múltiplos domínios (users, courses, enrollments, payments, audit_logs).
Impact: Impossível testar em isolamento. Mudança em checkout quebra risk em financial-report. Callback hell de 5 níveis na linha 28-78.
Recommendation: Separar em models por domínio (UserModel, CourseModel, EnrollmentModel, PaymentModel), controllers (CheckoutController, ReportController), e routes dedicadas. Cada arquivo com responsabilidade única (SRP).

### [CRITICAL] C-05: Hash de Senhas Inseguro
File: src/utils.js:17-23
Description: Função `badCrypto()` itera 10000x concatenando base64 da senha, depois trunca para 10 chars. Base64 é encoding reversível, não hash criptográfico. Seed data (AppManager.js:19) armazena senha em texto plano `'123'`.
Impact: Senhas podem ser revertidas para original. Atacante com acesso ao DB recupera todas as senhas.
Recommendation: Usar `bcrypt` para hash de senhas com salt automático. Migrar senhas existentes com lazy migration no próximo login.

### [HIGH] H-01: Zero Autenticação/Autorização
File: src/AppManager.js (todas as rotas), src/app.js
Description: Nenhuma middleware de autenticação. Endpoints de POST (checkout), DELETE (users) e GET (admin/financial-report) estão completamente abertos sem verificação de identidade.
Impact: Qualquer pessoa pode deletar usuários, processar pagamentos e acessar relatórios financeiros.
Recommendation: Implementar middleware JWT. Proteger todos endpoints de escrita. Rotas admin devem exigir role admin.

### [HIGH] H-03: Nenhuma Validação de Entrada
File: src/AppManager.js:29-34
Description: Campos do request body (`usr`, `eml`, `pwd`, `c_id`, `card`) usados diretamente sem validação de tipo, formato ou sanitização. Email não validado, card number aceita qualquer string, course_id não é validado como integer.
Impact: Dados inválidos causam comportamento imprevisível. Card number `'abc'` seria aceito e processado.
Recommendation: Validar campos obrigatórios, tipos e formatos antes de processar. Verificar email formato, card number como string numérica, course_id como integer.

### [HIGH] H-04: Lógica de Negócio nos Routes
File: src/AppManager.js:28-78
Description: Rota `/api/checkout` contém processamento de pagamento, criação de usuário, hash de senha, matrícula, registro de pagamento e audit logging — tudo em um único callback com 5 níveis de nesting.
Impact: Impossível testar lógica de checkout sem subir servidor. Viola separação de responsabilidades MVC.
Recommendation: Extrair lógica para camada de service/controller dedicada. Rota deve apenas receber request, chamar controller, formatar response.

### [MEDIUM] M-01: Queries N+1
File: src/AppManager.js:80-129
Description: Endpoint `/api/admin/financial-report` executa padrão N+1: 1 query para courses → N queries para enrollments → N queries para users + N queries para payments. Para 2 courses, são ~7 queries; para 100 courses, seriam ~300.
Impact: Performance degrada linearmente. Resposta lenta com volume crescente de dados.
Recommendation: Substituir por queries com JOINs ou batch queries com `WHERE id IN (...)` para buscar dados relacionados em única query.

### [MEDIUM] M-09: Logs Sensíveis no Console
File: src/AppManager.js:45
Description: `console.log` imprime número do cartão de crédito e chave do gateway de pagamento: `Processando cartão 4111222233334444 na chave pk_live_1234567890abcdef`.
Impact: Dados de cartão e chaves de API expostos em logs. Viola PCI-DSS para dados de cartão.
Recommendation: Nunca logar dados de cartão ou chaves. Logar apenas identificadores (user_id, enrollment_id).

### [MEDIUM] M-10: Delete sem Cascata / Dados Órfãos
File: src/AppManager.js:131-137
Description: DELETE de usuário remove apenas da tabela `users`. Enrollments, payments e audit_logs referenciando esse user_id permanecem como órfãos. A própria resposta confirma: "matrículas e pagamentos ficaram sujos no banco".
Impact: Integridade referencial comprometida. Relatórios financeiros mostram pagamentos sem usuário associado.
Recommendation: Implementar delete em cascata dentro de transação: remover payments → enrollments → audit_logs → user, ou usar ON DELETE CASCADE nas FKs.

### [MEDIUM] M-04: Falta de Tratamento de Erros
File: src/AppManager.js (todas as rotas)
Description: Erros retornados como strings genéricas (`"Erro DB"`, `"Erro Matrícula"`, `"Erro Pagamento"`) sem estrutura JSON consistente. Nenhum middleware global de error handling. Erros do SQLite propagados diretamente.
Impact: Consumidor da API recebe mensagens inconsistentes (string vs JSON). Difícil debugging em produção.
Recommendation: Implementar middleware global de error handling no Express. Criar respostas de erro padronizadas em JSON. Nunca expor detalhes internos.

### [LOW] L-02: Nomenclatura Ruim
File: src/AppManager.js:29-33
Description: Variáveis de request com nomes crípticos: `u` (userName), `e` (email), `p` (password), `cid` (courseId), `cc` (creditCard). Variáveis internas `self`, `enrPending`, `coursesPending` dificultam leitura.
Impact: Reduz legibilidade. Novo desenvolvedor precisa mapear abreviações.
Recommendation: Renomear para nomes descritivos: `userName`, `email`, `password`, `courseId`, `creditCard`.

### [LOW] L-05: Seed Data Misturado com Infraestrutura de DB
File: src/AppManager.js:11-22
Description: Dados de seed (INSERT de usuários, courses, enrollments, payments) misturados com CREATE TABLE no método `initDb()`. Senha de seed `'123'` em texto plano. Seed executa em toda inicialização.
Impact: Viola separação de responsabilidades. Senha admin previsível. Impossível desabilitar seed em produção.
Recommendation: Extrair seed para arquivo separado (`src/database/seed.js`). Senha admin deve ser hasheada. Seed deve ser opt-in via flag.

### [LOW] L-06: Ausência de Middleware de Segurança
File: src/app.js:1-14
Description: Nenhum middleware de segurança: sem CORS restritivo, sem rate limiting, sem helmet/security headers, sem limite de tamanho de payload em `express.json()`.
Impact: Superfície de ataque ampliada. CSRF, DDoS por payload gigante, clickjacking facilitado.
Recommendation: Adicionar `helmet` para security headers, `cors` com whitelist, `express-rate-limit` em endpoints sensíveis, `express.json({ limit: '10kb' })`.

### [LOW] L-03: API Deprecated / Padrão Obsoleto
File: src/AppManager.js (todas as rotas)
Description: API do sqlite3 usada exclusivamente com callbacks aninhados (5 níveis em checkout). Padrão obsoleto dificulta error handling e leitura. `app.listen()` sem error handling.
Impact: Callback hell dificulta manutenção. Erros silenciosos em operações async. Risco de unhandled rejections.
Recommendation: Promisificar API do sqlite3 ou usar driver com suporte nativo a Promises (ex: `sqlite` npm package). Usar async/await nas rotas.

================================
Total: 14 findings
================================
