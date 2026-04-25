# 🤖 Agente Autônomo de Agendamentos (Python + PostgreSQL + Google Calendar)

### 📌 Visão Geral
Este projeto consiste no desenvolvimento de um agente de automação em Python projetado para otimizar fluxos de relacionamento com clientes corporativos (Customer Success). O sistema atua de forma autônoma: extrai dados de clientes VIP diretamente de um banco de dados, verifica a disponibilidade de horários na agenda e realiza o disparo de convites por e-mail com links de reuniões e anexos.

O objetivo principal deste repositório é demonstrar a construção de um pipeline de automação *End-to-End*, aplicando conceitos de integração de APIs, manipulação de dados e boas práticas de Segurança da Informação.

---

### 🚀 Arquitetura e Funcionalidades

*   **Integração Dinâmica de Dados:** Conexão direta com **PostgreSQL** utilizando a biblioteca `psycopg2`, substituindo fontes de dados estáticas (arquivos CSV) por consultas SQL (Queries) para a extração da base de clientes.
*   **Inteligência de Agendamento (FreeBusy):** Integração com a API do Google Calendar para consultar a disponibilidade da agenda em tempo real. O script é capaz de identificar conflitos de horário e evitar sobreposições automaticamente antes de criar o evento.
*   **Comunicação Automatizada:** Disparo de e-mails customizados via protocolo SMTP (Gmail), utilizando a biblioteca `EmailMessage` para suportar formatação em f-strings, formatação correta de caracteres (UTF-8) e anexos de documentos em PDF de forma programática.
*   **Segurança e Boas Práticas:** Implementação rigorosa de isolamento de credenciais. Utilização de variáveis de ambiente (`.env`) e autenticação via OAuth2. Senhas de aplicativo e chaves de API não são expostas no código e estão protegidas no versionamento via `.gitignore`.

---

### 🛠 Tecnologias Utilizadas
*   **Linguagens e Bancos:** Python 3.8+, PostgreSQL
*   **Integrações de Nuvem:** Google Calendar API (OAuth2), Servidor SMTP
*   **Bibliotecas Principais:** `psycopg2`, `google-api-python-client`, `python-dotenv`, `smtplib`

---

### ✨ Evolução Técnica do Projeto (Roadmap)
Este projeto foi construído em etapas incrementais, refletindo o aprimoramento da arquitetura técnica:
- [x] **Fase 1:** Criação da lógica base de envio de e-mails com leitura de dados estáticos (`.csv`).
- [x] **Fase 2:** Migração da fonte de dados para um banco relacional (PostgreSQL).
- [x] **Fase 3:** Implementação de Autenticação OAuth2 e criação de eventos no Google Calendar.
- [x] **Fase 4:** Adição da lógica de verificação de agenda (FreeBusy) para validação autônoma de horários antes da consolidação do agendamento.
