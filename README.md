# 💡 FlowBit - 2025.1

> Projeto desenvolvido para a disciplina **Desenvolvimento Ágil (EC46C)**  

![Logo](assets/logo.png)

---

## 👥 Integrantes

| Nome                          | RA        | GitHub                                       |
|-------------------------------|-----------|----------------------------------------------|
| Gabriel Augusto Morisaki Rita | 2268191   | [gasakiri](https://github.com/gasakiri)      |
| Jefhter Rodrigues Cabral      | 2565390   | [Jefhter](https://github.com/Jefhter)        |
| Kaique Tavares Zambrano       | 2313073   | [KaiqueZambrano](https://github.com/KaiqueZambrano) |
| Letícia Esteves Rosa Pereira  | 2312107   | [Noracai03](https://github.com/Noracai03) |
| Luigi Augusto Rovani          | 2266474   | [luigirovani](https://github.com/luigirovani) |

---

## 📌 Descrição

- O **FlowBit** é um **habit tracker** desenvolvido para facilitar a criação e o acompanhamento 
de hábitos diários de forma simples e visual. Ele ajuda a manter a consistência e promover melhorias na rotina.
- As principais funcionalidades do FlowBit são:
  - Criar, editar, visualizar e buscar hábitos
  - Marcar hábitos como concluídos
  - Enviar lembretes personalizados
- O **público alvo** é qualquer pessoa que queira organizar melhor sua rotina, manter hábitos saudáveis ou melhorar sua produtividade.

---

## 📂 Documentação

> **TODO**: Adicionar os documentos abaixo com links (ao serem criados).  

---

## 🚧 Status

> Em desenvolvimento

## 🚀 Como usar

### 🌐 Acesso online
> Acesse: [https://flowbit.site/](https://flowbit.site/)

### 🔧 Instalação local

```bash
# 1. Clone o repositório
git clone https://github.com/Jefhter/FlowBit-2025.1.git
cd FlowBit-2025.1

# 2. Crie e ative um ambiente virtual
python -m venv env
# Linux/macOS:
source env/bin/activate
# Windows:
env\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute o servidor
python run.py
```

### ⚙️ Configuração de banco de dados
Por padrão, o sqlite engine será usado como banco de dados
Você pode utilizar outros bancos compatíveis: **MariaDB**, **MySQL** ou **PostgreSQL**.

#### 🔌 Exemplo com MariaDB:

1. Instale o driver:

```bash
pip install mariadb
```

## No .env

```bash
DB_ENGINE=mariadb
DB_USER=flwobit_user
DB_PASSWORD=flowbit_senha
DB_HOST=
DB_NAME=flwobit_database
```

### 🪵 Configuração de logs
```bash
LOG_LEVEL=DEBUG         # Nível global de logs (DEBUG, INFO, WARNING, ERROR)
DB_LOG_LEVEL=ERROR      # Nível de logs para o banco de dados
LOG_FILE=false          # Se 'true', escreve logs em arquivo
```

⚠️ Importante: Para usar LOG_FILE=true  com múltiplos workers, é necessário instalar concurrent-log-handler

🐳 Executando com Docker
Build da imagem:
```bash
docker build -t flowbit .
```
executar

```bash
docker run -p 8080:8080 flowbit
```

ou com docker compose 
```bash
docker-compose up --build
```
