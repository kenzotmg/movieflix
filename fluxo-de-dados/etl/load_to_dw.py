# etl/load_to_dw.py
import os, pathlib, pandas as pd, numpy as np
import psycopg
from psycopg import sql
import io

def _read_secret(path_env: str):
    path = os.getenv(path_env)
    if path and pathlib.Path(path).exists():
        return pathlib.Path(path).read_text().strip()
    return None

DB_HOST = os.getenv("DB_HOST", "db-dw")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = _read_secret("DB_NAME_FILE")
DB_USER = _read_secret("DB_USER_FILE")
DB_PASS = _read_secret("DB_PASSWORD_FILE")

CSV_PATH = os.getenv("IMDB_CSV", "/data_lake/imdb_top_1000_raw.csv")


def parse_runtime(val):
    if isinstance(val, str):
        val = val.strip().lower().replace("min", "").strip()
    try:
        return int(float(val))
    except:
        return None

def parse_gross(val):
    if val is None or (isinstance(val, float) and np.isnan(val)): return None
    try:
        return int(str(val).replace(",", "").strip())
    except:
        return None

def load_dataframe(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    # Renomeie conforme seu CSV exato
    df["Released_Year"] = pd.to_numeric(df["Released_Year"], errors="coerce")
    df["Runtime_min"]   = df["Runtime"].apply(parse_runtime)
    df["Gross_usd"]     = df["Gross"].apply(parse_gross)

    clean = df.rename(columns={
        "Series_Title": "title",
        "Released_Year": "year",
        "IMDB_Rating": "imdb_rating",
        "Meta_score": "meta_score",
        "Director": "director",
        "No_of_Votes": "votes",
        "Gross_usd": "gross_usd",
        "Genre": "genre_raw"
    })[["title","year","Runtime_min","imdb_rating","meta_score","director","votes","gross_usd","genre_raw"]]

    clean = clean.rename(columns={"Runtime_min": "runtime_min"})
    print(clean)
    print(clean.columns)

    return clean

def upsert_dw(conn, df: pd.DataFrame):
    cols = ["title","year","runtime_min","imdb_rating","meta_score",
            "director","votes","gross_usd","genre_raw"]

    tmp = df[cols].copy()

    # 1) Tipagem correta
    # inteiros (nullable): virarão 'Int64' (pandas) -> CSV sem ".0"
    for c in ["year", "runtime_min", "meta_score", "votes", "gross_usd"]:
        tmp[c] = pd.to_numeric(tmp[c], errors="coerce").astype("Int64")

    # float 1 casa para imdb_rating
    tmp["imdb_rating"] = pd.to_numeric(tmp["imdb_rating"], errors="coerce").round(1)

    # 2) CSV em memória (pandas faz o quoting/escape)
    buf = io.StringIO()
    # na_rep="" mantém vazio para NULL no COPY (ver opção NULL '' abaixo)
    tmp.to_csv(buf, index=False, na_rep="")
    buf.seek(0)

    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE dw.movies_clean;")
        copy_sql = sql.SQL(
            # CSV + HEADER + tratar vazio como NULL
            "COPY dw.movies_clean ({}) FROM STDIN WITH (FORMAT CSV, HEADER TRUE, NULL '')"
        ).format(sql.SQL(',').join(map(sql.Identifier, cols)))

        with cur.copy(copy_sql) as cp:
            cp.write(buf.read())

def main():
    df = load_dataframe(CSV_PATH)
    conn_str = f"dbname={DB_NAME} user={DB_USER} password={DB_PASS} host={DB_HOST} port={DB_PORT}"
    with psycopg.connect(conn_str) as conn:
        upsert_dw(conn, df)
        conn.commit()
    print("DW carregado com sucesso.")

if __name__ == "__main__":
    main()
