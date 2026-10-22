"""
app.py - Flask Server for Movie Recommendation System Using TF-IDF
Provides RESTful APIs for content-based recommendations, natural-language query matching,
similarity explainability, and serves the modern frontend UI.
"""

import os
from flask import Flask, render_template, request, jsonify
from recommender import MovieRecommender

app = Flask(__name__)

# Initialize recommendation engine
print("Initializing TF-IDF Movie Recommendation Engine...")
recommender = MovieRecommender()
print("Engine ready.")


@app.route("/")
def index():
    """Serves the main application page."""
    return render_template("index.html")


@app.route("/api/movies", methods=["GET"])
def get_movies():
    """Returns list of all available movies for search and dropdown."""
    movies = recommender.get_all_movies()
    return jsonify({"status": "success", "count": len(movies), "movies": movies})


@app.route("/api/movie/<int:movie_id>", methods=["GET"])
def get_movie(movie_id):
    """Returns detailed information and TF-IDF keywords for a specific movie."""
    movie = recommender.get_movie_by_id(movie_id)
    if not movie:
        return jsonify({"status": "error", "message": f"Movie with id {movie_id} not found"}), 404
    return jsonify({"status": "success", "movie": movie})


@app.route("/api/recommend", methods=["GET"])
def recommend_by_movie():
    """
    Recommends movies similar to a given movie ID using TF-IDF and Cosine Similarity.
    Query params:
        - movie_id (int, required)
        - top_n (int, default 8)
        - genre (str, optional)
        - min_rating (float, optional)
    """
    try:
        movie_id = int(request.args.get("movie_id"))
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "Valid movie_id parameter is required"}), 400

    top_n = int(request.args.get("top_n", 8))
    genre = request.args.get("genre", "All")
    min_rating = float(request.args.get("min_rating", 0.0))

    source_movie = recommender.get_movie_by_id(movie_id)
    if not source_movie:
        return jsonify({"status": "error", "message": "Source movie not found"}), 404

    results = recommender.recommend_by_movie_id(
        movie_id=movie_id,
        top_n=top_n,
        genre_filter=genre,
        min_rating=min_rating
    )

    return jsonify({
        "status": "success",
        "source_movie": source_movie,
        "count": len(results),
        "recommendations": results
    })


@app.route("/api/recommend-prompt", methods=["POST"])
def recommend_by_prompt():
    """
    Recommends movies based on free-text natural language plot description or vibe.
    Vectorizes prompt with fitted TF-IDF and computes Cosine Similarity.
    """
    data = request.get_json(force=True, silent=True) or {}
    prompt = data.get("prompt", "").strip()

    if not prompt:
        return jsonify({"status": "error", "message": "Prompt cannot be empty"}), 400

    top_n = int(data.get("top_n", 8))
    genre = data.get("genre", "All")
    min_rating = float(data.get("min_rating", 0.0))

    results = recommender.recommend_by_free_text(
        text_prompt=prompt,
        top_n=top_n,
        genre_filter=genre,
        min_rating=min_rating
    )

    return jsonify({
        "status": "success",
        "query": prompt,
        "count": len(results),
        "recommendations": results
    })


@app.route("/api/explain", methods=["GET"])
def explain_pair():
    """
    Compares two movies and returns their shared TF-IDF terms and cosine similarity.
    Query params: movie_a, movie_b
    """
    try:
        movie_a = int(request.args.get("movie_a"))
        movie_b = int(request.args.get("movie_b"))
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "Valid movie_a and movie_b IDs are required"}), 400

    if movie_a not in recommender.indices or movie_b not in recommender.indices:
        return jsonify({"status": "error", "message": "One or both movie IDs not found"}), 404

    idx_a = recommender.indices[movie_a]
    idx_b = recommender.indices[movie_b]

    cos_score = float(recommender.cosine_sim[idx_a][idx_b])
    shared_terms = recommender._explain_pair(idx_a, idx_b, top_n=8)

    movie_a_data = recommender.get_movie_by_id(movie_a)
    movie_b_data = recommender.get_movie_by_id(movie_b)

    return jsonify({
        "status": "success",
        "movie_a": {"id": movie_a, "title": movie_a_data["title"]},
        "movie_b": {"id": movie_b, "title": movie_b_data["title"]},
        "cosine_similarity": round(cos_score, 4),
        "similarity_percent": round(cos_score * 100, 1),
        "shared_terms": shared_terms
    })


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Returns analytics and vocabulary stats of the TF-IDF corpus."""
    stats = recommender.get_corpus_stats()
    return jsonify({"status": "success", "stats": stats})


@app.route("/health", methods=["GET"])
def health_check():
    """Liveness and readiness probe for Docker and CI/CD pipelines."""
    is_ready = recommender is not None and getattr(recommender, "df", None) is not None and not recommender.df.empty
    status_code = 200 if is_ready else 503
    return jsonify({
        "status": "healthy" if is_ready else "unhealthy",
        "movies_count": len(recommender.df) if is_ready else 0,
        "vectorizer_ready": getattr(recommender, "vectorizer", None) is not None
    }), status_code


if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5001"))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() in ("true", "1", "t")
    app.run(host=host, port=port, debug=debug)
