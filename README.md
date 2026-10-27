# 🎬 CineMatch AI — Movie Recommendation System Using TF-IDF Algorithm

A modern, full-stack Python web application that implements a **Content-Based Movie Recommendation System** powered by **Natural Language Processing (NLP)**, **TF-IDF Vectorization**, and **Cosine Similarity**, paired with a dark-mode **Glassmorphic Web Interface**. Fully configured for seamless **Vercel** serverless deployment.

---

## 🌟 Key Features

1. **Content-Based Filtering via TF-IDF**:
   - Converts multi-field textual metadata (*synopsis, genres, director, lead actors, themes, and keywords*) into high-dimensional numerical feature vectors.
   - Uses **Sublinear Term Frequency** ($1 + \log(\text{TF})$) to prevent high-frequency words from drowning out subtle thematic keywords.
   - Incorporates unigram and bigram tokens ($1\text{--}2\text{-grams}$) to capture key phrases like *"time travel"*, *"serial killer"*, *"black hole"*, and *"space exploration"*.

2. **Mathematical Explainability**:
   - Every recommendation explains **why** it was suggested.
   - Calculates the component-wise dot product contribution of individual TF-IDF terms ($TF\text{-}IDF_A(t) \times TF\text{-}IDF_B(t)$), exposing the exact keywords linking the films.

3. **Free-Text AI Story & Prompt Search**:
   - Input any custom natural language prompt or plot idea (e.g., *"mind-bending space exploration with wormhole, black hole, and father daughter bond"*).
   - The engine vectorizes the text in real-time and computes cosine similarity against the entire movie corpus.

4. **Pairwise Movie Comparator**:
   - Compare any two movies side-by-side.
   - Visualizes the pairwise cosine similarity score and an interactive breakdown table of shared TF-IDF terms.

5. **TF-IDF Algorithm Visualizer**:
   - Educational explainer section covering the mathematics of Term Frequency, Inverse Document Frequency, and Cosine Vector Norms.
   - Live vocabulary inspector showing high-IDF (distinctive) and low-IDF (ubiquitous) tokens across the dataset.

6. **Interactive Glassmorphic UI**:
   - Modern dark mode with frosted glass cards, dynamic ambient glows, and responsive layout.
   - Instant autocomplete search bar with poster previews.
   - Dynamic filters by genre, IMDb rating threshold, and result count.
   - Client-side persistent **Watchlist** saved in browser `localStorage`.
   - Detailed modal preview with full metadata and top TF-IDF feature weights.

---

## 📐 Mathematical Formulation

### 1. Term Frequency (TF)
$$\text{TF}(t, d) = \begin{cases} 1 + \log(\text{count}(t, d)) & \text{if } \text{count}(t, d) > 0 \\ 0 & \text{otherwise} \end{cases}$$

### 2. Inverse Document Frequency (IDF)
$$\text{IDF}(t, D) = \log\left(\frac{1 + N}{1 + \text{DF}(t)}\right) + 1$$
Where:
- $N$ is the total number of movies in the dataset.
- $\text{DF}(t)$ is the number of movies containing term $t$.

### 3. TF-IDF Weight
$$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \text{IDF}(t, D)$$

### 4. Cosine Similarity
$$\text{Cosine Similarity}(\mathbf{u}, \mathbf{v}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2} = \frac{\sum_{i=1}^{V} u_i v_i}{\sqrt{\sum_{i=1}^{V} u_i^2} \sqrt{\sum_{i=1}^{V} v_i^2}}$$

Because vectors are $L_2$-normalized:
$$\text{Cosine Similarity}(\mathbf{u}, \mathbf{v}) = \sum_{t \in V} u_t v_t$$

---

## 📁 Project Structure

```
Movie-Recommender/
├── api/
│   └── index.py               # Vercel Serverless Function entry point
├── app.py                     # Flask application & RESTful API routes
├── recommender.py             # TF-IDF Engine, Vectorizer, and Explainability Logic
├── vercel.json                # Vercel deployment & URL rewrite routing
├── .vercelignore              # Deployment exclusion rules
├── requirements.txt           # Lean Python dependencies for Vercel
├── run.sh                     # Quick start local launch script
├── PRESENTATION.md            # Slide-by-slide presentation deck notes
├── data/
│   ├── build_expanded_dataset.py # Script to rebuild/expand movie dataset
│   └── movies.csv             # 247+ movie dataset with authentic IMDb posters
├── static/
│   ├── css/
│   │   └── style.css          # Glassmorphic dark design system & responsive layout
│   └── js/
│       └── app.js             # Client application logic, search, and state
├── templates/
│   └── index.html             # Single-Page Web Application template
└── tests/
    ├── test_recommender.py    # Unit tests for TF-IDF algorithm and explainability
    └── test_api.py            # Integration tests for REST API endpoints
```

---

## 🚀 Quick Start Guide (Local Development)

### 1. Prerequisites
- Python 3.9+ (Python 3.10, 3.11, 3.12, 3.13, 3.14 supported)
- `pip` package manager

### 2. Setup & Run Using `run.sh`
The fastest way to run the project locally is using the automated launch script:
```bash
./run.sh
```

### 3. Manual Setup (Alternative)
```bash
# 1. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start Flask server
python3 app.py
```

Open your web browser and navigate to:
```
http://127.0.0.1:5001
```

---

## ☁️ Vercel Deployment

This project is pre-configured for one-click or CLI deployment on **Vercel** via Serverless Python Functions.

### Option A: Deploy via GitHub (Recommended)
1. Push your repository to GitHub:
   ```bash
   git add .
   git commit -m "Configure project for Vercel serverless deployment"
   git push origin main
   ```
2. Go to [vercel.com](https://vercel.com) and click **"Add New Project"**.
3. Import your GitHub repository.
4. Vercel automatically detects the Python runtime, `api/index.py`, and `vercel.json`.
5. Click **Deploy**. Your app will be live with a free SSL `.vercel.app` URL!

### Option B: Deploy via Vercel CLI
1. Install Vercel CLI globally (if not already installed):
   ```bash
   npm install -g vercel
   ```
2. Log in and deploy from project directory:
   ```bash
   vercel
   ```
3. For production deployment:
   ```bash
   vercel --prod
   ```

---

## 🔌 REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Serves the web UI |
| `GET` | `/health` | Application liveness and health check probe |
| `GET` | `/api/movies` | Returns full list of movies for client-side search |
| `GET` | `/api/movie/<id>` | Returns metadata + top TF-IDF terms for a movie |
| `GET` | `/api/recommend?movie_id=1&top_n=8&genre=All&min_rating=7.0` | Recommends movies similar to `movie_id` with explainability |
| `POST`| `/api/recommend-prompt` | Recommends movies matching free-text natural language query |
| `GET` | `/api/explain?movie_a=1&movie_b=2` | Returns pairwise cosine similarity and overlapping term weights |
| `GET` | `/api/stats` | Returns vocabulary size, matrix shape, and sample IDF terms |

---

## 🧪 Testing

Run the automated test suite with pytest:
```bash
source .venv/bin/activate
pytest -v
```
