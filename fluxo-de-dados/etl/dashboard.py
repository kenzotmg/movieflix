import os
import pathlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # headless (salva PNG sem abrir janela)
import matplotlib.pyplot as plt
import psycopg

# --------- Config de conexão (lendo secrets *_FILE se existirem) ---------
def _read_secret_file(env_key: str):
    p = os.getenv(env_key)
    if p and pathlib.Path(p).exists():
        return pathlib.Path(p).read_text().strip()
    return None

DB_HOST = os.getenv("DB_HOST", "db-dw")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = _read_secret_file("DB_NAME_FILE")
DB_USER = _read_secret_file("DB_USER_FILE")
DB_PASS = _read_secret_file("DB_PASSWORD_FILE")

if not DB_USER or not DB_PASS:
    raise RuntimeError("Credenciais ausentes. Defina DB_USER/DB_PASSWORD ou *_FILE.")

# --------- Saída ---------
OUT_DIR = "/output/"

def q(sql: str) -> pd.DataFrame:
    conn_str = f"dbname={DB_NAME} user={DB_USER} password={DB_PASS} host={DB_HOST} port={DB_PORT}"
    with psycopg.connect(conn_str) as conn:
        return pd.read_sql(sql, conn)

def save_df(df: pd.DataFrame, name: str):
    df.to_csv(OUT_DIR + f"{name}.csv", index=False)

def save_fig(name: str):
    plt.tight_layout()
    plt.savefig(OUT_DIR + f"{name}.png", dpi=120, bbox_inches="tight")
    plt.close()

def main():
    # ---------- 1) Top 15 por votos ----------
    df_top = q("SELECT * FROM dm.v_top15_votes;")
    save_df(df_top, "dm_v_top15_votes")

    # gráfico (Top 10 por legibilidade)
    top10 = df_top.head(10).copy()
    # usa numpy para normalizar votos (exemplo de uso)
    votes = top10["votes"].to_numpy(dtype=float)
    norm = votes / np.max(votes) if votes.size else votes

    plt.figure(figsize=(10, 5))
    plt.bar(top10["title"], norm)
    plt.xticks(rotation=45, ha="right")
    plt.title("Top 10 filmes por nº de votos")
    plt.ylabel("Votos (abs)  —  barra mais alta = 100%")
    save_fig("top10_votes")

    # ---------- 2) Duração média por década ----------
    df_dec = q("SELECT * FROM dm.v_runtime_by_decade;")
    save_df(df_dec, "dm_v_runtime_by_decade")

    plt.figure(figsize=(8, 4))
    labels = df_dec["decade"].astype(str) + "s"
    y = df_dec["avg_runtime_min"]

    plt.plot(labels, y, marker="o")
    plt.title("Duração média por década (min)")
    plt.xlabel("Década")
    plt.ylabel("Minutos")

    # adiciona valores em cima de cada ponto
    for i, val in enumerate(y):
        plt.text(i, val + 1, f"{val:.1f}", ha="center", va="bottom", fontsize=9)

    save_fig("runtime_by_decade")

    # ---------- 3) Média por gênero (Top 12) ----------
    df_genre = q(
        "SELECT * FROM dm.v_genre_avg ORDER BY avg_rating DESC, n_titles DESC LIMIT 12;"
    )
    save_df(df_genre, "dm_v_genre_avg_top12")

    plt.figure(figsize=(10, 5))
    g = df_genre.iloc[::-1]  # invertido p/ barh crescer pra direita
    bars = plt.barh(g["genre"], g["avg_rating"])
    plt.title("Média de rating por gênero (Top 12)")
    plt.xlabel("IMDB Rating médio")
    plt.bar_label(bars, labels=[f"{v:.2f}" for v in g["avg_rating"]], padding=3)
    save_fig("genre_avg_top12")

    # ---------- 4) Média por diretor (Top 15) ----------
    df_dir = q(
        "SELECT * FROM dm.v_director_avg ORDER BY avg_rating DESC, num_movies DESC LIMIT 15;"
    )
    save_df(df_dir, "dm_v_director_avg_top15")

    plt.figure(figsize=(10, 6))
    d = df_dir.iloc[::-1]
    bars = plt.barh(d["director"], d["avg_rating"])
    plt.title("Média de rating por diretor (Top 15)")
    plt.xlabel("IMDB Rating médio")
    plt.bar_label(bars, labels=[f"{v:.2f}" for v in d["avg_rating"]], padding=3)
    save_fig("director_avg_top15")

    print("Dashboard gerado em:", OUT_DIR)

if __name__ == "__main__":
    main()
