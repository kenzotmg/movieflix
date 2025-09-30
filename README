# ADA Projeto Final - Movieflix Analytics

Plataforma de avaliação de filmes com arquitetura baseada em containers.  
O projeto é dividido em **dois módulos principais**:

1. **APP** — aplicação web (Flask + Gunicorn), servida por **Nginx** e com banco **Postgres** próprio.
2. **ETL** — pipeline de **Extração, Transformação e Carga**, que lê datasets CSV do Data Lake, carrega em um **Data Warehouse (DW)** Postgres, cria **views analíticas (Data Marts)** e gera **dashboards**.

---

## Arquitetura

### APP
Browser -> Nginx (proxy reverso) -> Guicorn/Flask -> PostgreSQL
- **Nginx** → atua como proxy reverso, recebendo requisições HTTP e repassando para o Gunicorn.  
- **Flask + Gunicorn** → camada de aplicação, responsável por cadastrar e avaliar filmes, exposta como uma imagem Docker própria (`movieflix-app`).  
- **Postgres (db_app)** → banco da aplicação, armazena os filmes e avaliações.  

**Endpoints principais:**
- `GET /health` → healthcheck simples (`200 OK`).
- `GET /movies` → lista filmes e avaliações.
- `POST /movies/new` → cadastra filmes.

---

### ETL
Data Lake (CSV) --> ETL (Python) --> DW (Postgres schema dw)
--> DM (views no schema dm)
--> Dashboards (PNG/CSVs)
- **Data Lake** → arquivos CSV brutos.  
- **ETL (Python)** → executa:
  - Extração do CSV;
  - Limpeza e transformação (ajuste de tipos, remoção de nulos);
  - Carga para tabela `dw.movies_clean` no Postgres DW;
  - Aplicação das views do **Data Mart** (SQL em `dm/views.sql`);
  - Geração de dashboards com **matplotlib/numpy** em `output/`.
- **DW (Data Warehouse)** → banco Postgres (`db_dw`) com dados limpos, pronto para análises.  
- **DM (Data Mart)** → conjunto de **views analíticas**:
  - `dm.v_top15_votes` → top 15 filmes por votos;
  - `dm.v_avg_by_director` → média de rating por diretor;
  - `dm.v_runtime_by_decade` → duração média por década;
  - `dm.v_avg_by_genre` → média de rating por gênero.

---

## Como rodar

### Pré-requisitos
- Docker + Docker Compose
---

### APP
Suba a stack de aplicação (app + db + nginx):

```bash
docker compose -f docker-compose.app.yml up -d
```

Acesse:

App (via Nginx): http://localhost:8080
Healthcheck: http://localhost:8080/health

### ETL
```bash
docker compose -f docker-compose.etl.yml up -d
```
***isso deixará o container do banco rodando***

Acesse ```/fluxo-de-dados/output```


