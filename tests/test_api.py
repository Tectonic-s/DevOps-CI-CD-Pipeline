import pytest
from app import app


@pytest.fixture
def client():
    """Configures a test client for Flask API testing."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_check(client):
    """Test /health endpoint used by Docker and CI/CD probes."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["movies_count"] > 0
    assert data["vectorizer_ready"] is True


def test_index_route(client):
    """Test web UI root route."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"CineMatch AI" in response.data or b"html" in response.data.lower()


def test_get_all_movies(client):
    """Test /api/movies endpoint returns movie catalog."""
    response = client.get("/api/movies")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["count"] > 0
    assert len(data["movies"]) == data["count"]


def test_get_single_movie(client):
    """Test /api/movie/<id> endpoint for found and not-found states."""
    # Existing movie
    response = client.get("/api/movie/1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["movie"]["id"] == 1
    assert "top_keywords" in data["movie"]

    # Non-existent movie
    not_found = client.get("/api/movie/999999")
    assert not_found.status_code == 404


def test_api_recommend_by_movie(client):
    """Test /api/recommend route validations and success responses."""
    # Missing movie_id returns 400
    bad_req = client.get("/api/recommend")
    assert bad_req.status_code == 400

    # Non-existent movie returns 404
    not_found = client.get("/api/recommend?movie_id=999999")
    assert not_found.status_code == 404

    # Valid movie_id
    res = client.get("/api/recommend?movie_id=1&top_n=4")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["count"] == 4
    assert len(data["recommendations"]) == 4


def test_api_recommend_prompt(client):
    """Test /api/recommend-prompt endpoint with valid and empty prompts."""
    # Empty prompt returns 400
    bad_res = client.post("/api/recommend-prompt", json={"prompt": ""})
    assert bad_res.status_code == 400

    # Valid prompt returns recommendations
    good_res = client.post("/api/recommend-prompt", json={
        "prompt": "mind bending psychological thriller with dream manipulation",
        "top_n": 3
    })
    assert good_res.status_code == 200
    data = good_res.get_json()
    assert data["status"] == "success"
    assert len(data["recommendations"]) > 0


def test_api_explain(client):
    """Test /api/explain endpoint for pairwise comparison."""
    # Valid pair
    res = client.get("/api/explain?movie_a=1&movie_b=2")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "cosine_similarity" in data
    assert "similarity_percent" in data
    assert "shared_terms" in data

    # Missing parameters
    bad_res = client.get("/api/explain?movie_a=1")
    assert bad_res.status_code == 400


def test_api_stats(client):
    """Test /api/stats endpoint."""
    res = client.get("/api/stats")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "stats" in data
    assert data["stats"]["total_movies"] > 0
