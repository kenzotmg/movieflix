import pandas as pd

df = pd.read_csv("data_lake/imdb_top_1000_raw.csv")

# --- Transformações ---
df["Released_Year"] = pd.to_numeric(df["Released_Year"], errors="coerce")
df["Runtime"] = df["Runtime"].str.replace(" min", "").astype(float)
df["Gross"] = df["Gross"].str.replace(",", "").astype(float)

# Salvar versão limpa
df_clean = df[["Series_Title", "Released_Year", "Runtime", "Genre",
               "IMDB_Rating", "Meta_score", "Director",
               "No_of_Votes", "Gross"]]
df_clean.to_csv("data_dw/movies_clean.csv", index=False)

# --- Data Mart 1: média por diretor ---
dm_director = df_clean.groupby("Director").agg(
    avg_rating=("IMDB_Rating", "mean"),
    num_movies=("Series_Title", "count")
).reset_index()
dm_director.to_csv("data_dm/director_avg.csv", index=False)

# --- Data Mart 2: top 10 por votos ---
dm_votes = df_clean.nlargest(10, "No_of_Votes")
dm_votes.to_csv("data_dm/top10_votes.csv", index=False)
