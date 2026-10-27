"""
recommender.py - TF-IDF Movie Recommendation Engine
Implements content-based filtering using Term Frequency-Inverse Document Frequency (TF-IDF)
and Cosine Similarity, with feature explainability.
"""

import os
import re
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.metrics.pairwise import cosine_similarity


class MovieRecommender:
    def __init__(self, dataset_path=None):
        if dataset_path is None:
            dataset_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "movies.csv")
        self.dataset_path = dataset_path
        self.df = None
        self.vectorizer = None
        self.tfidf_matrix = None
        self.cosine_sim = None
        self.indices = {}  # Map movie_id and title to row index
        self.feature_names = []
        self.load_and_fit()

    def _clean_text(self, text):
        if not isinstance(text, str):
            return ""
        # Lowercase and clean special chars
        text = text.lower()
        text = re.sub(r"[^\w\s-]", " ", text)
        return " ".join(text.split())

    def _create_metadata_soup(self, row):
        """
        Creates a weighted content 'soup' combining:
        - Genres (repeated twice for genre affinity)
        - Keywords (repeated twice for thematic affinity)
        - Director (un-joined and underscore-joined for exact entity and name matching)
        - Cast (lead cast members)
        - Overview (narrative plot synopsis)
        """
        raw_genres = [g.strip().lower() for g in str(row.get("genres", "")).split(",") if g.strip()]
        genres_str = " ".join(raw_genres) + " " + " ".join([g.replace(" ", "").replace("-", "") for g in raw_genres])
        
        keywords = self._clean_text(str(row.get("keywords", "")))
        
        director_raw = str(row.get("director", "")).strip()
        director_clean = self._clean_text(director_raw)
        director_token = director_clean.replace(" ", "_")
        
        cast_raw = [self._clean_text(c).strip() for c in str(row.get("cast", "")).split(",")[:4]]
        cast_tokens = " ".join([c.replace(" ", "_") for c in cast_raw])
        cast_names = " ".join(cast_raw)
        
        overview = self._clean_text(str(row.get("overview", "")))

        # Weighted combination to balance narrative semantics with genre/director/cast
        soup = f"{genres_str} {genres_str} {keywords} {keywords} {director_token} {director_token} {director_clean} {cast_tokens} {cast_names} {overview}"
        return soup

    def load_and_fit(self):
        """Loads dataset and fits the TF-IDF vectorizer and cosine similarity matrix."""
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Dataset not found at {self.dataset_path}")

        self.df = pd.read_csv(self.dataset_path)
        # Ensure ID is integer
        self.df["id"] = self.df["id"].astype(int)

        # Generate metadata soup
        self.df["soup"] = self.df.apply(self._create_metadata_soup, axis=1)

        # Build index lookups
        self.indices = {row["id"]: idx for idx, row in self.df.iterrows()}
        self.title_to_id = {row["title"].lower().strip(): row["id"] for _, row in self.df.iterrows()}

        # Movie-specific boilerplate stopwords to discard generic film vocabulary
        custom_stop_words = list(ENGLISH_STOP_WORDS.union({
            "movie", "movies", "film", "films", "story", "stories", "life", "lives",
            "young", "new", "world", "man", "men", "woman", "women", "time", "day",
            "year", "years", "set", "takes", "way", "find", "help", "save"
        }))

        # Initialize TF-IDF Vectorizer
        # max_df=0.45: filters out common words appearing across >45% of films
        # sublinear_tf=True: log-scales term frequency (1 + log(TF))
        self.vectorizer = TfidfVectorizer(
            stop_words=custom_stop_words,
            max_df=0.45,
            min_df=1,
            max_features=6000,
            ngram_range=(1, 2),
            sublinear_tf=True,
            token_pattern=r"(?u)\b[\w-]+\b"
        )

        self.tfidf_matrix = self.vectorizer.fit_transform(self.df["soup"])
        self.cosine_sim = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)
        self.feature_names = np.array(self.vectorizer.get_feature_names_out())

        print(f"TF-IDF Engine fitted successfully. Shape: {self.tfidf_matrix.shape}")

    def get_all_movies(self):
        """Returns lightweight list of all movies for search and dropdowns."""
        return self.df[["id", "title", "year", "genres", "rating", "poster_url", "director"]].to_dict(orient="records")

    def get_movie_by_id(self, movie_id):
        """Fetch complete details of a single movie."""
        if movie_id not in self.indices:
            return None
        idx = self.indices[movie_id]
        movie = self.df.iloc[idx].to_dict()
        movie["top_keywords"] = self.get_top_keywords_for_movie(movie_id, top_n=5)
        return movie

    def get_top_keywords_for_movie(self, movie_id, top_n=5, min_idf=3.6):
        """
        Returns only the most critical, highly rare TF-IDF terms for a movie.
        Ranks candidates by TF-IDF * (IDF ** 1.3) to isolate highly discriminative vocabulary.
        """
        if movie_id not in self.indices:
            return []
        idx = self.indices[movie_id]
        row_vector = self.tfidf_matrix[idx].toarray().flatten()
        idf = self.vectorizer.idf_

        GENERIC_TAGS = {
            "action", "drama", "thriller", "adventure", "sci-fi", "scifi", "comedy",
            "crime", "romance", "action adventure", "adventure thriller", "action scifi",
            "thriller action", "crime drama", "scifi action", "family", "fantasy"
        }

        candidates = []
        for i in range(len(row_vector)):
            if row_vector[i] > 0 and idf[i] >= min_idf:
                term = self.feature_names[i]
                if len(term) > 2 and term not in GENERIC_TAGS:
                    # Rare Critical Metric: TF-IDF score amplified by IDF power
                    crit_score = float(row_vector[i] * (idf[i] ** 1.3))
                    candidates.append((crit_score, row_vector[i], idf[i], term))

        candidates.sort(key=lambda x: x[0], reverse=True)
        results = []
        for crit_score, tfidf, idf_val, term in candidates[:top_n]:
            results.append({
                "term": term,
                "tfidf_score": round(float(tfidf), 4),
                "idf": round(float(idf_val), 2),
                "rarity": "Critical" if idf_val >= 5.0 else "High"
            })
        return results

    def _explain_pair(self, idx_a, idx_b, top_n=4):
        """
        Explains why movie B is similar to movie A using component-wise TF-IDF dot products,
        specifically filtering for rare and critical shared thematic terms.
        """
        vec_a = self.tfidf_matrix[idx_a].toarray().flatten()
        vec_b = self.tfidf_matrix[idx_b].toarray().flatten()
        idf = self.vectorizer.idf_

        shared_scores = vec_a * vec_b
        GENERIC_TAGS = {
            "action", "drama", "thriller", "adventure", "sci-fi", "scifi", "comedy",
            "crime", "romance", "action adventure", "adventure thriller", "action scifi",
            "thriller action", "crime drama", "scifi action"
        }

        scored_shared = []
        for i in range(len(shared_scores)):
            if shared_scores[i] > 0:
                term = self.feature_names[i]
                if term not in GENERIC_TAGS and len(term) > 2:
                    crit_contribution = float(shared_scores[i] * (idf[i] ** 1.2))
                    scored_shared.append((crit_contribution, shared_scores[i], vec_a[i], vec_b[i], term))

        scored_shared.sort(key=lambda x: x[0], reverse=True)

        shared_terms = []
        for crit_contrib, raw_score, w_a, w_b, term in scored_shared[:top_n]:
            shared_terms.append({
                "term": term,
                "weight_a": round(float(w_a), 4),
                "weight_b": round(float(w_b), 4),
                "contribution": round(float(raw_score), 4)
            })
        return shared_terms

    def _generate_one_line_reason(self, source_row, target_row, shared_terms):
        """Generates a concise, informative 1-line explanation of why target_row is similar to source_row."""
        s_dir = str(source_row.get("director", "")).strip()
        t_dir = str(target_row.get("director", "")).strip()
        same_director = s_dir and t_dir and s_dir.lower() == t_dir.lower()

        s_cast = [c.strip() for c in str(source_row.get("cast", "")).split(",") if c.strip()]
        t_cast = [c.strip() for c in str(target_row.get("cast", "")).split(",") if c.strip()]
        shared_actors = [a for a in s_cast if any(a.lower() == b.lower() for b in t_cast)]

        s_genres = [g.strip() for g in str(source_row.get("genres", "")).split(",") if g.strip()]
        t_genres = [g.strip() for g in str(target_row.get("genres", "")).split(",") if g.strip()]
        common_genres = [g for g in s_genres if any(g.lower() == b.lower() for b in t_genres)]

        dir_tokens = set((s_dir + " " + t_dir).lower().split())
        actor_tokens = set((" ".join(shared_actors)).lower().split())

        clean_terms = []
        for item in shared_terms:
            t_str = str(item.get("term", "")).replace("_", " ").strip()
            words = t_str.lower().split()
            if any(w in dir_tokens for w in words):
                continue
            if any(w in actor_tokens for w in words):
                continue
            if len(t_str) > 2 and t_str not in clean_terms:
                clean_terms.append(t_str)

        if same_director:
            if clean_terms:
                return f"Directed by {s_dir} with signature motifs in {clean_terms[0]}."
            return f"Also directed by {s_dir} with a shared cinematic visual style."

        if shared_actors:
            actor = shared_actors[0]
            if clean_terms:
                return f"Stars {actor} with key themes in {clean_terms[0]}."
            return f"Stars {actor} in a high-stakes {common_genres[0] if common_genres else 'narrative'} role."

        if clean_terms and common_genres:
            return f"Shares {common_genres[0]} themes focusing on {clean_terms[0]}."

        if clean_terms:
            return f"Narrative themes centered around {clean_terms[0]}."

        if common_genres:
            return f"Matches key {' & '.join(common_genres[:2])} story arcs and pacing."

        return "Shares narrative themes, tone, and character dynamics."

    def _generate_prompt_reason(self, text_prompt, target_row, matched_terms):
        genres = [g.strip() for g in str(target_row.get("genres", "")).split(",") if g.strip()]
        genre_str = f"{genres[0]} " if genres else ""
        if matched_terms:
            clean_terms = [t.replace("_", " ").strip() for t in matched_terms[:2] if t.strip()]
            return f"Matches your search for \"{text_prompt}\" via {genre_str}themes in {', '.join(clean_terms)}."
        return f"Matches your query tone across {genre_str}storytelling."

    def recommend_by_movie_id(self, movie_id, top_n=8, genre_filter=None, min_rating=0.0):
        """
        Returns top N recommendations for a specific movie ID using Cosine Similarity on TF-IDF.
        Also includes explanation of shared keywords and 1-line reason.
        """
        if movie_id not in self.indices:
            return []

        source_idx = self.indices[movie_id]
        source_row = self.df.iloc[source_idx]
        sim_scores = list(enumerate(self.cosine_sim[source_idx]))

        # Sort by similarity score descending (excluding itself)
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

        recommendations = []
        for idx, score in sim_scores:
            if idx == source_idx:
                continue

            row = self.df.iloc[idx]

            # Apply genre filter if specified
            if genre_filter and genre_filter.lower() != "all":
                genres = [g.strip().lower() for g in str(row["genres"]).split(",")]
                if genre_filter.lower() not in genres:
                    continue

            # Apply rating filter
            if float(row["rating"]) < min_rating:
                continue

            # Explain recommendation
            shared_terms = self._explain_pair(source_idx, idx, top_n=4)
            similarity_reason = self._generate_one_line_reason(source_row, row, shared_terms)

            # Calibrate raw cosine score to human-interpretable percentage match
            # Sparse high-dimensional TF-IDF vectors naturally produce top non-identical scores around 0.25 - 0.50
            calibrated = round(min(98.5, (float(score) / 0.36) ** 0.65 * 80.0), 1) if score > 0.001 else 0.0

            movie_dict = row.to_dict()
            movie_dict["similarity_score"] = round(float(score), 4)
            movie_dict["similarity_percent"] = max(round(float(score) * 100, 1), calibrated)
            movie_dict["shared_terms"] = shared_terms
            movie_dict["similarity_reason"] = similarity_reason
            recommendations.append(movie_dict)

            if len(recommendations) >= top_n:
                break

        return recommendations

    def recommend_by_free_text(self, text_prompt, top_n=8, genre_filter=None, min_rating=0.0):
        """
        Allows users to input natural language plot ideas or mood descriptions.
        Transforms the query vector via fitted TF-IDF and computes cosine similarity against all movies.
        """
        if not text_prompt or not text_prompt.strip():
            return []

        clean_prompt = self._clean_text(text_prompt)
        query_vec = self.vectorizer.transform([clean_prompt])
        cosine_scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        sorted_indices = cosine_scores.argsort()[::-1]

        # Extract non-zero terms in user query
        query_dense = query_vec.toarray().flatten()
        query_term_indices = np.where(query_dense > 0)[0]

        recommendations = []
        for idx in sorted_indices:
            score = float(cosine_scores[idx])
            if score <= 0.001:
                # If similarity is negligible, stop or skip
                continue

            row = self.df.iloc[idx]

            # Genre filter
            if genre_filter and genre_filter.lower() != "all":
                genres = [g.strip().lower() for g in str(row["genres"]).split(",")]
                if genre_filter.lower() not in genres:
                    continue

            # Rating filter
            if float(row["rating"]) < min_rating:
                continue

            # Shared terms calculation between query and movie
            movie_vec = self.tfidf_matrix[idx].toarray().flatten()
            shared_terms = []
            for t_idx in query_term_indices:
                contrib = float(query_dense[t_idx] * movie_vec[t_idx])
                if contrib > 0:
                    shared_terms.append({
                        "term": self.feature_names[t_idx],
                        "contribution": round(contrib, 4)
                    })
            shared_terms = sorted(shared_terms, key=lambda x: x["contribution"], reverse=True)[:4]

            calibrated = round(min(98.5, (float(score) / 0.36) ** 0.65 * 80.0), 1) if score > 0.001 else 0.0

            movie_dict = row.to_dict()
            movie_dict["similarity_score"] = round(score, 4)
            movie_dict["similarity_percent"] = max(round(score * 100, 1), calibrated)
            movie_dict["shared_terms"] = shared_terms
            movie_dict["matched_terms"] = [t["term"] for t in shared_terms]
            movie_dict["similarity_reason"] = self._generate_prompt_reason(text_prompt, row, [t["term"] for t in shared_terms])
            recommendations.append(movie_dict)

            if len(recommendations) >= top_n:
                break

        return recommendations

    def get_corpus_stats(self):
        """Returns analytical statistics about the TF-IDF model."""
        idfs = self.vectorizer.idf_
        top_idf_indices = np.argsort(idfs)[::-1][:15]
        lowest_idf_indices = np.argsort(idfs)[:15]

        top_rare_terms = [{"term": self.feature_names[i], "idf": round(float(idfs[i]), 3)} for i in top_idf_indices]
        most_common_terms = [{"term": self.feature_names[i], "idf": round(float(idfs[i]), 3)} for i in lowest_idf_indices]

        # Extract unique genres
        all_genres = set()
        for g_list in self.df["genres"].dropna():
            for g in str(g_list).split(","):
                all_genres.add(g.strip())

        total_elements = self.tfidf_matrix.shape[0] * self.tfidf_matrix.shape[1]
        non_zero = self.tfidf_matrix.nnz
        sparsity = round((1.0 - (non_zero / total_elements)) * 100, 2)

        return {
            "total_movies": len(self.df),
            "vocab_size": len(self.feature_names),
            "matrix_shape": list(self.tfidf_matrix.shape),
            "sparsity_percent": sparsity,
            "non_zero_elements": int(non_zero),
            "ngram_range": [1, 2],
            "norm": "L2 (Euclidean Hypersphere)",
            "sublinear_tf": True,
            "algorithm": "Term Frequency - Inverse Document Frequency (TF-IDF)",
            "similarity_metric": "Cosine Similarity Kernel (Angular Dot Product)",
            "genres": sorted(list(all_genres)),
            "sample_high_idf_terms": top_rare_terms,
            "sample_common_terms": most_common_terms
        }
