-- dw/schema.sql
CREATE SCHEMA IF NOT EXISTS dw;

-- Tabela única (desnormalizada) para simplificar o MVP:
CREATE TABLE IF NOT EXISTS dw.movies_clean (
  id            BIGSERIAL PRIMARY KEY,
  title         TEXT NOT NULL,
  year          INT,
  runtime_min   INT,
  imdb_rating   NUMERIC(3,1),
  meta_score    INT,
  director      TEXT,
  votes         BIGINT,
  gross_usd     BIGINT,
  genre_raw     TEXT  -- ex: "Action, Adventure, Sci-Fi"
);