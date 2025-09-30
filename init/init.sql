CREATE TABLE IF NOT EXISTS movies (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  genre TEXT NOT NULL,
  year  INT
);

CREATE TABLE IF NOT EXISTS ratings (
  id SERIAL PRIMARY KEY,
  movie_id INT NOT NULL REFERENCES movies(id),
  rating   SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 10),
  created_at TIMESTAMP DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ratings_movie ON ratings(movie_id);