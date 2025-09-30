from flask import Blueprint, request, render_template, g, redirect, url_for
from .models import Movie, Rating
from sqlalchemy import func
bp = Blueprint("routes", __name__)

# ------------------------
# Landing page
# ------------------------
@bp.get("/")
def index():
    return render_template("index.html")

# ------------------------
# Cadastro de filmes
# ------------------------
@bp.get("/movies/new")
def new_movies():
    return render_template("new.html")

# ------------------------
# Listar filmes e avaliacoes
# ------------------------
@bp.get("/movies")
def list_movies():
    s = g.db

    # Agregados por filme: quantidade e média
    agg = (
        s.query(
            Movie.id,
            Movie.title,
            Movie.year,
            func.count(Rating.id).label("num_ratings"),
            func.avg(Rating.rating).label("avg_rating"),
        )
        .outerjoin(Rating, Rating.movie_id == Movie.id)
        .group_by(Movie.id, Movie.title, Movie.year)
        .order_by(Movie.title.asc())
        .all()
    )

    # Todas as avaliações para listar individualmente
    ratings_rows = (
        s.query(Rating.movie_id, Rating.rating)
        .order_by(Rating.movie_id.asc(), Rating.id.asc())
        .all()
    )

    # Agrupa ratings por filme
    ratings_by_movie = {}
    for r in ratings_rows:
        ratings_by_movie.setdefault(r.movie_id, []).append(r.rating)

    # Constrói o payload para o template
    movies = []
    for row in agg:
        movies.append({
            "id": row.id,
            "title": row.title,
            "year": row.year,
            "num_ratings": row.num_ratings,
            "avg_rating": float(row.avg_rating) if row.avg_rating is not None else None,
        })

    return render_template("movies.html", movies=movies)

# ------------------------
# Cadastro de filmes API
# ------------------------
@bp.post("/movies/new")
def create_new_movie():
    db = g.db
    title = request.form.get("title")
    year = request.form.get("year")
    genre = request.form.get("genre")
    movie = Movie(title=title, year=int(year), genre=genre)
    db.add(movie)
    db.commit()
    return redirect(url_for("routes.index"))

# ------------------------
# Busca de filmes
# ------------------------
@bp.get("/movies/search")
def search_movies():
    db = g.db
    q = request.args.get("q", "").strip()
    movies = []
    if q:
        movies = db.query(Movie).filter(Movie.title.ilike(f"%{q}%")).all()
    return render_template("search.html", query=q, movies=movies)

# ------------------------
# Avaliação de filme
# ------------------------
@bp.route("/movies/<int:movie_id>/rate", methods=["GET", "POST"])
def rate_movie(movie_id):
    db = g.db
    movie = db.query(Movie).filter_by(id=movie_id).first()
    if not movie:
        return "Filme não encontrado", 404

    if request.method == "POST":
        rating = int(request.form.get("rating"))
        db.add(Rating(movie_id=movie.id, rating=rating))
        db.commit()
        return redirect(url_for("routes.index"))

    return render_template("rating.html", movie=movie)