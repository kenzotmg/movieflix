CREATE SCHEMA IF NOT EXISTS dm;

CREATE OR REPLACE VIEW dm.v_top15_votes AS
SELECT title, year, votes, imdb_rating
FROM dw.movies_clean
ORDER BY votes DESC
LIMIT 15;

CREATE OR REPLACE VIEW dm.v_director_avg AS
SELECT
  director,
  ROUND(AVG(imdb_rating)::numeric, 2) AS avg_rating,
  COUNT(*) AS num_movies
FROM dw.movies_clean
GROUP BY director
ORDER BY avg_rating DESC, num_movies DESC;

CREATE OR REPLACE VIEW dm.v_runtime_by_decade AS
WITH base AS (
  SELECT
    CASE WHEN year IS NULL THEN NULL
         ELSE (year/10)*10 END AS decade,
    runtime_min
  FROM dw.movies_clean
)
SELECT decade::int AS decade,
       ROUND(AVG(runtime_min)::numeric, 1) AS avg_runtime_min,
       COUNT(*) AS n
FROM base
WHERE decade IS NOT NULL
GROUP BY decade
ORDER BY decade;

CREATE OR REPLACE VIEW dm.v_genre_avg AS
WITH exploded AS (
  SELECT
    title,
    trim(unnest(string_to_array(genre_raw, ','))) AS genre,
    imdb_rating
  FROM dw.movies_clean
)
SELECT
  genre,
  ROUND(AVG(imdb_rating)::numeric, 2) AS avg_rating,
  COUNT(*) AS n_titles
FROM exploded
WHERE genre <> ''
GROUP BY genre
ORDER BY avg_rating DESC, n_titles DESC;
