import pytest
from recommender import MovieRecommender


@pytest.fixture(scope="module")
def recommender_engine():
    """Initializes and caches the TF-IDF recommendation engine for test suite."""
    engine = MovieRecommender()
    return engine


def test_recommender_initialization(recommender_engine):
    """Ensure dataset and TF-IDF matrix are properly loaded and fitted."""
    assert recommender_engine.df is not None
    assert len(recommender_engine.df) > 0
    assert recommender_engine.tfidf_matrix is not None
    assert recommender_engine.tfidf_matrix.shape[0] == len(recommender_engine.df)
    assert recommender_engine.cosine_sim is not None


def test_recommend_by_movie_id(recommender_engine):
    """Test movie recommendation logic, count, sorting, and self-exclusion."""
    source_id = 1  # Inception
    top_n = 5
    recommendations = recommender_engine.recommend_by_movie_id(movie_id=source_id, top_n=top_n)

    assert len(recommendations) == top_n
    # Verify that source movie is not recommended to itself
    assert all(r["id"] != source_id for r in recommendations)
    # Verify similarity scores are sorted in descending order
    scores = [r["similarity_score"] for r in recommendations]
    assert scores == sorted(scores, reverse=True)
    # Check explainability payload
    for r in recommendations:
        assert "shared_terms" in r
        assert isinstance(r["shared_terms"], list)


def test_recommend_by_movie_id_filters(recommender_engine):
    """Test filtering by genre and rating."""
    recommendations = recommender_engine.recommend_by_movie_id(
        movie_id=1,
        top_n=10,
        genre_filter="Sci-Fi",
        min_rating=7.5
    )
    for r in recommendations:
        genres = [g.strip().lower() for g in str(r["genres"]).split(",")]
        assert "sci-fi" in genres
        assert float(r["rating"]) >= 7.5


def test_recommend_by_free_text(recommender_engine):
    """Test natural language prompt vectorization matching."""
    # Empty query should return empty list
    assert recommender_engine.recommend_by_free_text("") == []
    assert recommender_engine.recommend_by_free_text("   ") == []

    # Query with strong semantic signal
    results = recommender_engine.recommend_by_free_text("black hole space travel wormhole relativity", top_n=5)
    assert len(results) > 0
    movie_titles = [m["title"] for m in results]
    assert "Interstellar" in movie_titles


def test_corpus_stats(recommender_engine):
    """Test corpus analytics and vocabulary distribution stats."""
    stats = recommender_engine.get_corpus_stats()
    assert "total_movies" in stats
    assert "vocab_size" in stats
    assert "matrix_shape" in stats
    assert "genres" in stats
    assert stats["total_movies"] > 0
    assert stats["vocab_size"] > 0
    assert len(stats["genres"]) > 0
